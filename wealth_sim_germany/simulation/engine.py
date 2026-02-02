from __future__ import annotations

import random
from dataclasses import dataclass

from wealth_sim_germany.analysis.aggregations import build_aggregates
from wealth_sim_germany.config.schemas import ScenarioConfig
from wealth_sim_germany.data.distributions import DistributionFactory
from wealth_sim_germany.models.government import Government, TransferRule
from wealth_sim_germany.models.income import IncomeModel
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.models.tax import TaxCalculator
from wealth_sim_germany.models.wealth import WealthModel
from wealth_sim_germany.simulation.time_step import SimulationContext, run_single_year
from wealth_sim_germany.utils.types import EducationLevel, Region, Sex


@dataclass
class SimulationResult:
    scenario_name: str
    start_year: int
    years: int
    yearly: list[dict[str, float]]


def _default_population(size: int) -> list[Person]:
    sexes = list(Sex)
    educations = list(EducationLevel)
    regions = list(Region)
    persons: list[Person] = []
    for idx in range(size):
        persons.append(
            Person(
                age=30 + (idx % 40),
                sex=sexes[idx % len(sexes)],
                education=educations[idx % len(educations)],
                region=regions[idx % len(regions)],
            )
        )
    return persons


class SimulationController:
    def __init__(
        self,
        scenario: ScenarioConfig,
        distribution_factory: DistributionFactory | None = None,
        income_model: IncomeModel | None = None,
        wealth_model: WealthModel | None = None,
        tax_calculator: TaxCalculator | None = None,
        transfer_rule: TransferRule | None = None,
        persons: list[Person] | None = None,
        government: Government | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.scenario = scenario
        self.distribution_factory = distribution_factory or DistributionFactory()
        self.income_model = income_model or IncomeModel(self.distribution_factory)
        self.wealth_model = wealth_model or WealthModel(self.distribution_factory)
        self.tax_calculator = tax_calculator or TaxCalculator(self.scenario.tax)
        if transfer_rule is None:
            raise ValueError("transfer_rule must be provided")
        self.transfer_rule = transfer_rule
        self.persons = persons
        self.government = government
        self.rng = rng or random.Random()

    def initialise(self) -> tuple[list[Person], Government]:
        if self.persons is None:
            self.persons = _default_population(self.scenario.population.synthetic_n)
        if self.government is None:
            self.government = Government(
                spending_shares=self.scenario.government.spending_shares,
                deficit_limit=self.scenario.government.deficit_limit,
                gdp=0.0,
            )
        return self.persons, self.government

    def run(self) -> SimulationResult:
        persons, government = self.initialise()
        ctx = SimulationContext(
            income_model=self.income_model,
            wealth_model=self.wealth_model,
            tax_calculator=self.tax_calculator,
            transfer_rule=self.transfer_rule,
            rng=self.rng,
        )
        yearly_results: list[dict[str, float]] = []
        current_year = self.scenario.start_year
        for _ in range(self.scenario.years):
            persons, government = run_single_year(
                ctx=ctx,
                persons=persons,
                government=government,
                year=current_year,
                scenario=self.scenario,
            )
            yearly_results.append(build_aggregates(persons, government, current_year))
            current_year += 1
        return SimulationResult(
            scenario_name=self.scenario.name,
            start_year=self.scenario.start_year,
            years=self.scenario.years,
            yearly=yearly_results,
        )
