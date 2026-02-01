from __future__ import annotations

import random
from dataclasses import dataclass

from wealth_sim_germany.config.schemas import MacroParams
from wealth_sim_germany.data.distributions import DistributionFactory
from wealth_sim_germany.models.person import Person


@dataclass
class WealthModel:
    distribution_factory: DistributionFactory
    liquid_assets_distribution: str = "liquid_assets"
    illiquid_assets_distribution: str = "illiquid_assets"
    debt_distribution: str = "debt"
    stocks_distribution: str = "stocks"
    savings_rate_distribution: str = "savings_rate"
    labor_return_distribution: str = "labor_return"
    capital_return_distribution: str = "capital_return"

    def _conditions(self, person: Person) -> dict:
        return {
            "age": person.age,
            "sex": person.sex.value,
            "education": person.education.value,
            "region": person.region.value,
        }

    def initialise_wealth(self, person: Person, rng: random.Random) -> None:
        conditions = self._conditions(person)
        person.liquid_assets = self.distribution_factory.sample(
            self.liquid_assets_distribution,
            rng,
            conditions=conditions,
        )
        person.illiquid_assets = self.distribution_factory.sample(
            self.illiquid_assets_distribution,
            rng,
            conditions=conditions,
        )
        person.debt = self.distribution_factory.sample(
            self.debt_distribution,
            rng,
            conditions=conditions,
        )
        person.stocks = self.distribution_factory.sample(
            self.stocks_distribution,
            rng,
            conditions=conditions,
        )
        person.net_wealth = (
            person.liquid_assets + person.illiquid_assets + person.stocks - person.debt
        )

    def evolve_wealth(self, person: Person, rng: random.Random, macro_params: MacroParams) -> None:
        conditions = self._conditions(person)
        savings_rate = self.distribution_factory.sample(
            self.savings_rate_distribution,
            rng,
            conditions=conditions,
        )
        labor_return_rate = self.distribution_factory.sample(
            self.labor_return_distribution,
            rng,
            conditions=conditions,
        )
        capital_return_rate = self.distribution_factory.sample(
            self.capital_return_distribution,
            rng,
            conditions=conditions,
        )
        labor_return_rate += macro_params.gdp_growth
        capital_return_rate += macro_params.gdp_growth + macro_params.inflation
        person.update_wealth(
            savings_rate=savings_rate,
            labor_return_rate=labor_return_rate,
            capital_return_rate=capital_return_rate,
        )
