from __future__ import annotations

import random

from wealth_sim_germany.config.schemas import MacroParams
from wealth_sim_germany.data.distributions import DistributionFactory
from wealth_sim_germany.models.income import IncomeModel
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.models.wealth import WealthModel
from wealth_sim_germany.utils.types import EducationLevel, Region, Sex


def test_income_model_samples_and_updates_person() -> None:
    factory = DistributionFactory()
    captured: dict[str, dict | None] = {}

    def labor_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        captured["labor"] = conditions
        return 55_000.0

    def capital_sampler(rng: random.Random, conditions: dict | None = None) -> float:
        captured["capital"] = conditions
        return 7_500.0

    factory.register("labor_income", labor_sampler)
    factory.register("capital_income", capital_sampler)
    model = IncomeModel(factory)
    person = Person(
        age=45,
        sex=Sex.MALE,
        education=EducationLevel.HIGH,
        region=Region.WEST,
    )

    labor_income = model.sample_labor_income(person, random.Random(0))
    capital_income = model.sample_capital_income(person, random.Random(1))

    assert labor_income == 55_000.0
    assert capital_income == 7_500.0
    assert person.labor_income == 55_000.0
    assert person.capital_income == 7_500.0
    assert captured["labor"] == {
        "age": 45,
        "sex": "male",
        "education": "high",
        "region": "west",
    }
    assert captured["capital"] == captured["labor"]


def test_wealth_model_initialises_assets_and_net_wealth() -> None:
    factory = DistributionFactory()
    captured: dict[str, dict | None] = {}

    def sampler_factory(key: str, value: float):
        def _sampler(rng: random.Random, conditions: dict | None = None) -> float:
            captured[key] = conditions
            return value

        return _sampler

    factory.register("liquid_assets", sampler_factory("liquid", 12_000.0))
    factory.register("illiquid_assets", sampler_factory("illiquid", 25_000.0))
    factory.register("debt", sampler_factory("debt", 5_000.0))
    factory.register("stocks", sampler_factory("stocks", 3_000.0))
    model = WealthModel(factory)
    person = Person(
        age=32,
        sex=Sex.FEMALE,
        education=EducationLevel.MEDIUM,
        region=Region.NORTH,
    )

    model.initialise_wealth(person, random.Random(2))

    assert person.liquid_assets == 12_000.0
    assert person.illiquid_assets == 25_000.0
    assert person.debt == 5_000.0
    assert person.stocks == 3_000.0
    assert person.net_wealth == 35_000.0
    assert captured["liquid"] == {
        "age": 32,
        "sex": "female",
        "education": "medium",
        "region": "north",
    }
    assert captured["illiquid"] == captured["liquid"]
    assert captured["debt"] == captured["liquid"]
    assert captured["stocks"] == captured["liquid"]


def test_wealth_model_evolves_assets_with_macro_params() -> None:
    factory = DistributionFactory()
    factory.register("savings_rate", lambda rng, conditions=None: 0.1)
    factory.register("labor_return", lambda rng, conditions=None: 0.02)
    factory.register("capital_return", lambda rng, conditions=None: 0.03)
    model = WealthModel(factory)
    person = Person(
        age=50,
        sex=Sex.MALE,
        education=EducationLevel.LOW,
        region=Region.EAST,
        net_income=10_000.0,
        liquid_assets=1_000.0,
        illiquid_assets=2_000.0,
    )
    macro_params = MacroParams(gdp_growth=0.01, inflation=0.02)

    model.evolve_wealth(person, random.Random(3), macro_params)

    assert person.liquid_assets == 2_030.0
    assert person.illiquid_assets == 2_120.0
    assert person.net_wealth == 4_150.0
