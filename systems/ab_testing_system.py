# systems/ab_testing_system.py
# A/B testing framework for simulation variants.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExperimentVariant:
    name: str
    metrics: Dict[str, List[float]] = field(default_factory=dict)


class ABTestingSystem:
    def __init__(self):
        self.variants: Dict[str, ExperimentVariant] = {}
        self.active_variant: Optional[str] = None

    def register_variant(self, name: str) -> ExperimentVariant:
        variant = ExperimentVariant(name=name)
        self.variants[name] = variant
        if self.active_variant is None:
            self.active_variant = name
        return variant

    def record_metric(self, name: str, value: float, variant: Optional[str] = None) -> None:
        target = variant or self.active_variant
        if not target:
            return
        var = self.variants.setdefault(target, ExperimentVariant(name=target))
        var.metrics.setdefault(name, []).append(value)

    def compare(self) -> Dict[str, float]:
        comparison: Dict[str, float] = {}
        for variant_name, variant in self.variants.items():
            for metric, values in variant.metrics.items():
                avg = sum(values) / max(1, len(values))
                comparison[f"{variant_name}:{metric}"] = avg
        return comparison
