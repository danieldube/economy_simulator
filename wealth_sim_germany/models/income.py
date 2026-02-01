from __future__ import annotations

import random
from dataclasses import dataclass

from wealth_sim_germany.data.distributions import DistributionFactory
from wealth_sim_germany.models.person import Person


@dataclass
class IncomeModel:
    distribution_factory: DistributionFactory
    labor_distribution: str = "labor_income"
    capital_distribution: str = "capital_income"

    def _conditions(self, person: Person) -> dict:
        return {
            "age": person.age,
            "sex": person.sex.value,
            "education": person.education.value,
            "region": person.region.value,
        }

    def sample_labor_income(self, person: Person, rng: random.Random) -> float:
        labor_income = self.distribution_factory.sample(
            self.labor_distribution,
            rng,
            conditions=self._conditions(person),
        )
        person.labor_income = labor_income
        return labor_income

    def sample_capital_income(self, person: Person, rng: random.Random) -> float:
        capital_income = self.distribution_factory.sample(
            self.capital_distribution,
            rng,
            conditions=self._conditions(person),
        )
        person.capital_income = capital_income
        return capital_income
