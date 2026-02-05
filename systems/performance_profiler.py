# systems/performance_profiler.py
# Lightweight performance profiler.

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List


@dataclass
class TimingEntry:
    name: str
    duration_ms: float


class PerformanceProfiler:
    def __init__(self):
        self.timings: Dict[str, List[TimingEntry]] = {}

    @contextmanager
    def track(self, name: str):
        start = perf_counter()
        try:
            yield
        finally:
            duration_ms = (perf_counter() - start) * 1000
            self.timings.setdefault(name, []).append(TimingEntry(name=name, duration_ms=duration_ms))

    def summary(self) -> Dict[str, float]:
        return {
            name: sum(entry.duration_ms for entry in entries) / max(1, len(entries))
            for name, entries in self.timings.items()
        }
