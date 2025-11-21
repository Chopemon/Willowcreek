# utils/token_counter.py
# Simple token counting utility for monitoring API costs

def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Uses rough heuristic: 1 token ≈ 4 characters
    For more accurate counting, could integrate tiktoken library.
    """
    return len(text) // 4


def count_message_tokens(messages: list) -> dict:
    """
    Count tokens in a list of message dicts.
    Returns breakdown by role and total.
    """
    counts = {
        "system": 0,
        "user": 0,
        "assistant": 0,
        "total": 0
    }

    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        token_count = estimate_tokens(content)

        if role in counts:
            counts[role] += token_count
        counts["total"] += token_count

    return counts


def format_token_report(counts: dict) -> str:
    """Format token counts as a readable report."""
    return (
        f"Token Usage:\n"
        f"  System: {counts['system']:,} tokens\n"
        f"  User: {counts['user']:,} tokens\n"
        f"  Assistant: {counts['assistant']:,} tokens\n"
        f"  TOTAL: {counts['total']:,} tokens"
    )


class TokenTracker:
    """Track token usage across multiple API calls."""

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

    def log_call(self, input_tokens: int, output_tokens: int):
        """Log a single API call."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.call_count += 1

    def get_stats(self) -> dict:
        """Get usage statistics."""
        total = self.total_input_tokens + self.total_output_tokens
        avg_per_call = total / self.call_count if self.call_count > 0 else 0

        return {
            "total_input": self.total_input_tokens,
            "total_output": self.total_output_tokens,
            "total": total,
            "call_count": self.call_count,
            "avg_per_call": avg_per_call
        }

    def format_stats(self) -> str:
        """Format statistics as readable string."""
        stats = self.get_stats()
        return (
            f"API Token Usage Stats:\n"
            f"  Calls: {stats['call_count']}\n"
            f"  Input: {stats['total_input']:,} tokens\n"
            f"  Output: {stats['total_output']:,} tokens\n"
            f"  Total: {stats['total']:,} tokens\n"
            f"  Avg/call: {stats['avg_per_call']:.0f} tokens"
        )


# Global tracker instance
global_tracker = TokenTracker()
