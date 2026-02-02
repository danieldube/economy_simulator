from __future__ import annotations

import random
from dataclasses import dataclass

from wealth_sim_germany.analysis.aggregations import (
    aggregate_by_group,
    build_aggregates,
    gini,
    weighted_mean,
)
from wealth_sim_germany.config.schemas import (
    GovernmentSpendingConfig,
    MacroParams,
    PopulationConfig,
    ScenarioConfig,
    TaxConfig,
)
from wealth_sim_germany.data.distributions import DistributionFactory
from wealth_sim_germany.models.government import Government
from wealth_sim_germany.models.income import IncomeModel
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.models.tax import TaxCalculator
from wealth_sim_germany.models.wealth import WealthModel
from wealth_sim_germany.simulation.engine import SimulationController
from wealth_sim_germany.simulation.time_step import SimulationContext, run_single_year
from wealth_sim_germany.utils.types import EducationLevel, GovFunction, Region, Sex


@dataclass(frozen=True)
class FlatTransferRule:
    amount: float

    def compute_transfer(self, person: Person, government: Government) -> float:
        return self.amount


def _build_scenario() -> ScenarioConfig:
    return ScenarioConfig(
        name="test",
        start_year=2020,
        years=1,
        tax=TaxConfig(income_tax_rate=0.1, capital_gains_rate=0.2, social_contrib_rate=0.05),
        government=GovernmentSpendingConfig(
            spending_shares={
                GovFunction.EDUCATION: 0.5,
                GovFunction.SOCIAL_PROTECTION: 0.5,
            },
            deficit_limit=0.1,
        ),
        population=PopulationConfig(total_population=100, synthetic_n=1),
        macro=MacroParams(gdp_growth=0.01, inflation=0.02),
    )


def test_run_single_year_updates_agents() -> None:
    factory = DistributionFactory()

    def labor_income_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 100.0

    def capital_income_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 50.0

    def savings_rate_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.1

    def labor_return_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.01

    def capital_return_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.02

    factory.register("labor_income", labor_income_sampler)
    factory.register("capital_income", capital_income_sampler)
    factory.register("savings_rate", savings_rate_sampler)
    factory.register("labor_return", labor_return_sampler)
    factory.register("capital_return", capital_return_sampler)

    income_model = IncomeModel(factory)
    wealth_model = WealthModel(factory)
    tax_calculator = TaxCalculator(_build_scenario().tax)
    transfer_rule = FlatTransferRule(amount=10.0)
    ctx = SimulationContext(
        income_model=income_model,
        wealth_model=wealth_model,
        tax_calculator=tax_calculator,
        transfer_rule=transfer_rule,
        rng=random.Random(0),
    )

    persons = [
        Person(
            age=40,
            sex=Sex.FEMALE,
            education=EducationLevel.HIGH,
            region=Region.SOUTH,
            liquid_assets=100.0,
            illiquid_assets=200.0,
        )
    ]
    government = Government(
        spending_shares=_build_scenario().government.spending_shares,
        deficit_limit=_build_scenario().government.deficit_limit,
        gdp=1_000.0,
    )

    scenario = _build_scenario()

    run_single_year(ctx, persons, government, scenario.start_year, scenario)

    person = persons[0]
    assert person.labor_income == 100.0
    assert person.capital_income == 50.0
    assert person.transfers == 10.0
    assert person.total_income == 160.0
    assert person.taxes == 20.0
    assert person.social_contrib == 7.5
    assert person.net_income == 132.5
    assert person.liquid_assets == 115.25
    assert person.illiquid_assets == 210.0
    assert person.net_wealth == 325.25

    assert government.total_revenue == 27.5
    assert government.expenditure[GovFunction.EDUCATION] == 13.75
    assert government.expenditure[GovFunction.SOCIAL_PROTECTION] == 13.75
    assert government.deficit == 0.0


def test_analytics_helpers() -> None:
    assert weighted_mean([10.0, 20.0], [1.0, 3.0]) == 17.5
    assert gini([10.0, 10.0, 10.0], [1.0, 1.0, 1.0]) == 0.0
    assert gini([0.0, 10.0], [1.0, 1.0]) == 0.5

    persons = [
        Person(
            age=30,
            sex=Sex.MALE,
            education=EducationLevel.LOW,
            region=Region.NORTH,
            net_income=100.0,
            weight=1.0,
        ),
        Person(
            age=30,
            sex=Sex.FEMALE,
            education=EducationLevel.LOW,
            region=Region.NORTH,
            net_income=200.0,
            weight=3.0,
        ),
        Person(
            age=30,
            sex=Sex.FEMALE,
            education=EducationLevel.LOW,
            region=Region.SOUTH,
            net_income=50.0,
            weight=2.0,
        ),
    ]

    grouped = aggregate_by_group(persons, "region", "net_income")
    assert grouped[Region.NORTH] == 175.0
    assert grouped[Region.SOUTH] == 50.0

    government = Government(
        spending_shares={GovFunction.EDUCATION: 1.0},
        deficit_limit=0.1,
        gdp=1_000.0,
        total_revenue=0.0,
        debt=10.0,
        deficit=1.0,
    )
    result = build_aggregates(persons, government, 2020)
    assert result["year"] == 2020
    assert result["population"] == 6.0
    assert result["avg_net_income"] == 133.33333333333334
    assert result["gini_net_income"] == 0.2708333333333333


def test_simulation_controller_runs_and_returns_results() -> None:
    scenario = _build_scenario()
    factory = DistributionFactory()

    def labor_income_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 20.0

    def capital_income_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 5.0

    def savings_rate_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.1

    def labor_return_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.0

    def capital_return_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        return 0.0

    factory.register("labor_income", labor_income_sampler)
    factory.register("capital_income", capital_income_sampler)
    factory.register("savings_rate", savings_rate_sampler)
    factory.register("labor_return", labor_return_sampler)
    factory.register("capital_return", capital_return_sampler)

    controller = SimulationController(
        scenario=scenario,
        distribution_factory=factory,
        transfer_rule=FlatTransferRule(amount=0.0),
        rng=random.Random(1),
    )

    result = controller.run()

    assert result.years == 1
    assert result.yearly[0]["year"] == 2020
    assert result.yearly[0]["total_gross_income"] == 25.0
