# Architecture Setup for Scalable NPC Cognition

This document maps a practical implementation to the 5-part architecture for large, AI-driven character worlds.

## Step 1: Set up the Central World Engine

Use `CentralWorldEngine` in `systems/ai_orchestrator.py` as the source of truth.

It tracks:
- **Time and physics-adjacent state:** `day`, `hour`, and `weather`
- **Character positions and state machine values:** `location`, `state`, `routine_state`
- **World objects and locations:** object name + location map

## Step 2: Build the Perception System

Use `PerceptionSystem` to generate each character's local text feed.

The output intentionally includes only:
- Character's own location
- Co-located NPCs
- Objects in the same location
- Events in the same location
- Current day/time/weather

This avoids omniscient prompts and keeps token usage bounded.

## Step 3: Create the Memory System (Vector Database)

Use `VectorMemoryStore` for long-term memory retrieval.

- Supports memory insertion by character (`add_memory`)
- Supports relevance-based retrieval (`query`)
- Returns only top-k memories for prompt injection

This implementation uses a lightweight cosine/token strategy. In production, you can swap this class with Pinecone/Milvus while preserving the same interface.

## Step 4: Design the Brain (LLM Routing)

Use `BrainRouter` to enforce consistent prompt and output contracts.

- Persona is part of the prompt
- Prompt includes perception + retrieved memories
- Output must be constrained JSON:
  - `dialogue`
  - `action`
  - `target`
  - `reasoning`

If the LLM fails to produce valid JSON, the router returns a safe fallback action.

## Step 5: Implement an AI Director (The Optimizer)

Use `AIDirector` as the event-driven orchestrator.

- **Background routines** run without LLM calls for low-complexity behavior
- **Event queue** wakes only affected characters
- **Queue throttling** with `max_requests_per_tick` staggers LLM requests

This allows many NPCs to share a single API budget while still reacting believably to world events.

## Suggested integration flow

1. Instantiate `CentralWorldEngine`
2. Register characters and world objects
3. Instantiate `PerceptionSystem`, `VectorMemoryStore`, and `BrainRouter`
4. Wrap them with `AIDirector`
5. On events, call `enqueue_event(...)`
6. Each simulation tick:
   - Run background routines
   - Process queue with a capped request count

## Current repo integration status

- `NarrativeChat` now initializes and uses the orchestrator pipeline when `ENABLE_AI_DIRECTOR` is not set to `0`.
- The director uses the **same configured narrative model** for brain routing by default, so integration does not require adding another LLM service.
- Per-tick NPC decision calls are rate-limited with `DIRECTOR_MAX_REQUESTS_PER_TICK` (default: `2`).
