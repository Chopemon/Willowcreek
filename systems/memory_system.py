# systems/memory_system.py
import math
import random


class MemoryEntry:
    """
    Represents a single remembered event.

    Each memory carries:
    - text (description)
    - emotion tag (fear, shame, desire, joy, anger, neutral)
    - intensity (0–1)
    - strength (0–1 decayable)
    - day_formed
    - cluster_key (auto-generated category)
    """

    def __init__(self, text: str, emotion: str, intensity: float, day_formed: int):
        self.text = text
        self.emotion = emotion or "neutral"
        self.intensity = max(0.0, min(1.0, intensity))
        self.day_formed = day_formed

        # Strength starts based on emotional peak
        self.strength = 0.6 + (self.intensity * 0.4)

        # Auto clustering by simple keyword detection
        lowered = text.lower()
        if "mother" in lowered or "family" in lowered:
            self.cluster_key = "family"
        elif "fight" in lowered or "argu" in lowered:
            self.cluster_key = "conflict"
        elif "secret" in lowered or "shame" in lowered:
            self.cluster_key = "shame"
        elif "kiss" in lowered or "touch" in lowered or "flirt" in lowered:
            self.cluster_key = "desire"
        elif "school" in lowered or "class" in lowered:
            self.cluster_key = "school"
        else:
            self.cluster_key = "general"

    def decay(self):
        """Decay natural memory strength over time."""
        # Emotional memories decay slower
        if self.emotion in ("trauma", "fear", "shame"):
            decay_rate = 0.01
        else:
            decay_rate = 0.03

        self.strength = max(0.0, self.strength - decay_rate)

    def reinforce(self):
        """Strengthen memory when referenced or emotionally triggered."""
        self.strength = min(1.0, self.strength + 0.25)

    def is_forgotten(self):
        """A memory is forgotten once strength falls below a threshold."""
        return self.strength <= 0.05


class MemorySystem:
    """
    Advanced cognitive memory model for Willow Creek NPCs.
    - Short-term → long-term conversion
    - Clustering
    - Emotional tagging
    - Retrieval bias
    - Personality-aware decay
    """

    MAX_SHORT = 15
    MAX_LONG = 120

    def __init__(self):
        # npc_name -> List[MemoryEntry]
        self.short_term = {}
        self.long_term = {}

        # Last consolidation day
        self.last_day = -1

    # ------------------------------------------------------
    # Initialization
    # ------------------------------------------------------
    def initialize_npc_memory(self, npc_name: str):
        if npc_name not in self.short_term:
            self.short_term[npc_name] = []
        if npc_name not in self.long_term:
            self.long_term[npc_name] = []

    # ------------------------------------------------------
    # Recording Memory
    # ------------------------------------------------------
    def remember(self, npc_name: str, text: str, emotion: str = "neutral", intensity: float = 0.4, day: int = 0):
        """Create a new short-term memory with emotional tagging."""
        self.initialize_npc_memory(npc_name)

        entry = MemoryEntry(text, emotion, intensity, day)
        self.short_term[npc_name].append(entry)

        # Enforce short-term cap
        if len(self.short_term[npc_name]) > self.MAX_SHORT:
            self.short_term[npc_name] = self.short_term[npc_name][-self.MAX_SHORT:]

    # ------------------------------------------------------
    # Consolidation Pipeline
    # ------------------------------------------------------
    def consolidate_memories(self, current_day: int):
        """
        Called once per simulation day.
        Handles:
        - decay
        - traumatic persistence
        - clustering
        - short → long-term moves
        - pruning forgotten memories
        OPTIMIZED: Lazy processing - skips NPCs with empty memory banks.
        """

        if self.last_day == current_day:
            return
        self.last_day = current_day

        # Process NPC by NPC - OPTIMIZATION: Only process NPCs with actual memories
        for npc_name in list(self.short_term.keys()):
            st = self.short_term[npc_name]
            lt = self.long_term.get(npc_name, [])

            # OPTIMIZATION: Skip NPCs with no memories at all
            if not st and not lt:
                continue

            # Step 1: Decay existing memories
            for m in st:
                m.decay()
            for m in lt:
                m.decay()

            # Step 2: Short-term → Long-term transfer
            # Strongest memories always become long-term
            for m in st:
                if m.strength >= 0.25 or m.intensity >= 0.7:
                    lt.append(m)

            # Clear short-term
            self.short_term[npc_name] = []

            # Step 3: Cluster-based reinforcement - OPTIMIZATION: Skip if too few memories
            if len(lt) >= 4:
                cluster_groups = {}
                for m in lt:
                    cluster_groups.setdefault(m.cluster_key, []).append(m)

                for cluster, group in cluster_groups.items():
                    if len(group) >= 4:  # recurring theme
                        for m in group:
                            m.reinforce()

            # Step 4: Forgetting weak memories
            lt[:] = [m for m in lt if not m.is_forgotten()]

            # Step 5: Cap long-term memory
            if len(lt) > self.MAX_LONG:
                # Remove oldest weakest memories
                lt.sort(key=lambda x: (x.strength, x.day_formed))
                overflow = len(lt) - self.MAX_LONG
                del lt[:overflow]

            # Update long-term reference
            self.long_term[npc_name] = lt

    # ------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------
    def get_relevant_memories(self, npc_name: str, topic: str):
        """
        Returns memories biased by:
        - emotional relevance
        - cluster similarity
        - recency
        """

        st = self.short_term.get(npc_name, [])
        lt = self.long_term.get(npc_name, [])

        all_mems = st + lt
        topic = topic.lower()

        scored = []
        for m in all_mems:
            score = 0

            # Topic match
            if topic in m.text.lower():
                score += 2

            # Cluster match
            if topic in m.cluster_key:
                score += 1.5

            # Emotional weight
            score += m.intensity * 2

            # Strength effects
            score += m.strength

            if score > 1.5:
                scored.append((score, m))

        # Sort by score (descending)
        scored.sort(key=lambda x: -x[0])
        return [m for _, m in scored[:5]]

    # ------------------------------------------------------
    # Debug Access
    # ------------------------------------------------------
    def debug_summary(self, npc_name: str):
        """Returns a text summary for debugging overlays."""
        st = self.short_term.get(npc_name, [])
        lt = self.long_term.get(npc_name, [])
        return {
            "short_term_count": len(st),
            "long_term_count": len(lt),
            "clusters": list({m.cluster_key for m in lt})
        }
