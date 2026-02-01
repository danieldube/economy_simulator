from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import random


DistributionCallable = Callable[[random.Random, dict | None], float]


@dataclass
class EmpiricalDistribution:
    records: list[dict]

    def sample(self, rng: random.Random, conditions: dict | None = None) -> float:
        if not self.records:
            raise ValueError("Empirical distribution has no records")
        if not conditions:
            record = rng.choice(self.records)
            return float(record["value"])
        candidates = []
        for record in self.records:
            record_conditions = record.get("conditions", {})
            if all(record_conditions.get(key) == value for key, value in conditions.items()):
                candidates.append(record)
        if not candidates:
            raise ValueError("No matching records for conditions")
        record = rng.choice(candidates)
        return float(record["value"])


@dataclass
class DistributionFactory:
    _parametric: dict[str, DistributionCallable] = field(default_factory=dict)
    _empirical: dict[str, EmpiricalDistribution] = field(default_factory=dict)

    def register(self, name: str, sampler: DistributionCallable) -> None:
        self._parametric[name] = sampler

    def register_empirical(self, name: str, records: list[dict]) -> None:
        self._empirical[name] = EmpiricalDistribution(records=records)

    def sample(self, name: str, rng: random.Random, conditions: dict | None = None) -> float:
        if name in self._parametric:
            return float(self._parametric[name](rng, conditions))
        if name in self._empirical:
            return self._empirical[name].sample(rng, conditions)
        raise KeyError(f"Distribution '{name}' not registered")
