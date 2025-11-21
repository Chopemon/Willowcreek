# utils/batch_processor.py
"""
Batch processing utilities for NPC updates and other expensive operations.
Reduces redundant API calls by batching similar requests.
"""

from typing import List, Dict, Any, Callable, Optional
from collections import defaultdict
import asyncio


class NPCBatchProcessor:
    """
    Batches NPC state updates to reduce API calls.

    Instead of processing NPCs one-by-one, this groups NPCs by:
    - Location (process all NPCs in same location together)
    - Activity type (process similar activities together)
    - Time of day (process NPCs active at same time)
    """

    def __init__(self):
        self.pending_updates: Dict[str, List[Any]] = defaultdict(list)
        self.batch_size = 5  # Process up to 5 NPCs at once

    def add_npc_update(self, npc: Any, update_type: str, context: Dict[str, Any]):
        """Queue an NPC for batch processing"""
        batch_key = f"{update_type}_{context.get('location', 'unknown')}"
        self.pending_updates[batch_key].append((npc, context))

    def get_batches(self) -> Dict[str, List[tuple]]:
        """Get all pending batches"""
        return dict(self.pending_updates)

    def clear_batch(self, batch_key: str):
        """Clear a specific batch after processing"""
        if batch_key in self.pending_updates:
            del self.pending_updates[batch_key]

    def clear_all(self):
        """Clear all pending batches"""
        self.pending_updates.clear()

    def should_process_batch(self, batch_key: str) -> bool:
        """Check if a batch is ready to process"""
        return len(self.pending_updates.get(batch_key, [])) >= self.batch_size

    def process_batch(
        self,
        batch_key: str,
        processor_func: Callable[[List[tuple]], Any]
    ) -> Optional[Any]:
        """
        Process a batch of NPCs using the provided function.

        Args:
            batch_key: The batch identifier
            processor_func: Function that takes list of (npc, context) tuples
                           and processes them together

        Returns:
            Result from processor_func, or None if batch is empty
        """
        if batch_key not in self.pending_updates:
            return None

        batch = self.pending_updates[batch_key]
        if not batch:
            return None

        # Process the batch
        result = processor_func(batch)

        # Clear processed batch
        self.clear_batch(batch_key)

        return result


class RequestCoalescer:
    """
    Coalesces multiple similar requests into single batch requests.
    Useful for reducing redundant LLM API calls.
    """

    def __init__(self, wait_time_ms: int = 100):
        self.wait_time = wait_time_ms / 1000  # Convert to seconds
        self.pending_requests: Dict[str, List[Dict]] = defaultdict(list)
        self.results: Dict[str, Any] = {}

    async def coalesce_request(
        self,
        request_type: str,
        request_data: Dict,
        processor: Callable[[List[Dict]], List[Any]]
    ) -> Any:
        """
        Add a request to the coalescing queue.

        Multiple requests of the same type received within wait_time
        will be batched into a single processor call.

        Args:
            request_type: Type of request (e.g., "npc_update", "location_check")
            request_data: Data for this specific request
            processor: Async function that processes a batch of requests

        Returns:
            Result for this specific request
        """
        request_id = id(request_data)
        self.pending_requests[request_type].append({
            "id": request_id,
            "data": request_data
        })

        # Wait for potential additional requests
        await asyncio.sleep(self.wait_time)

        # Check if this request is still pending (might have been processed already)
        if request_id in self.results:
            result = self.results[request_id]
            del self.results[request_id]
            return result

        # Process all pending requests of this type
        pending = self.pending_requests[request_type]
        if not pending:
            return None

        # Clear pending for this type
        self.pending_requests[request_type] = []

        # Process batch
        results = await processor([req["data"] for req in pending])

        # Store results
        for req, result in zip(pending, results):
            self.results[req["id"]] = result

        # Return result for this request
        return self.results.pop(request_id, None)


# Global batch processor instance
npc_batch_processor = NPCBatchProcessor()


def example_batch_npc_updates(npcs_batch: List[tuple]) -> str:
    """
    Example function showing how to batch process NPC updates.

    Instead of calling LLM for each NPC individually, this creates
    a single prompt that processes all NPCs at once.

    Args:
        npcs_batch: List of (npc, context) tuples

    Returns:
        Combined result string
    """
    npc_names = [npc.full_name for npc, _ in npcs_batch]
    location = npcs_batch[0][1].get('location', 'unknown')

    # Create batched prompt (example)
    batch_prompt = f"Update the following NPCs at {location}: {', '.join(npc_names)}"

    # TODO: Call LLM once with batch_prompt instead of N times

    return f"Processed {len(npcs_batch)} NPCs in one call"
