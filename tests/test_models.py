from __future__ import annotations

from dataclasses import dataclass

import pytest

from wealth_sim_germany.models.government import Government
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.utils.types import EducationLevel, GovFunction, Region, Sex


def test_person_income_and_tax_flow():
    person = Person(
        age=40,
        sex=Sex.FEMALE,
        education=EducationLevel.HIGH,
        region=Region.SOUTH,
        labor_income=50_000.0,
        capital_income=5_000.0,
        transfers=1_000.0,
    )

    total_income = person.compute_total_gross_income()
    assert total_income == pytest.approx(56_000.0)

    person.apply_tax_result(income_tax=10_000.0, social_contrib=2_000.0, capital_tax=500.0)

    assert person.taxes == pytest.approx(10_500.0)
    assert person.net_income == pytest.approx(43_500.0)


def test_person_update_wealth_tracks_assets_and_debt():
    person = Person(
        age=30,
        sex=Sex.MALE,
        education=EducationLevel.MEDIUM,
        region=Region.NORTH,
        labor_income=30_000.0,
        capital_income=2_000.0,
        transfers=0.0,
        liquid_assets=10_000.0,
        illiquid_assets=20_000.0,
        debt=5_000.0,
        net_income=25_000.0,
    )

    person.update_wealth(savings_rate=0.1, labor_return_rate=0.02, capital_return_rate=0.03)

    assert person.liquid_assets == pytest.approx(12_700.0)
    assert person.illiquid_assets == pytest.approx(20_600.0)
    assert person.debt == pytest.approx(5_000.0)
    assert person.net_wealth == pytest.approx(28_300.0)


def test_government_collects_taxes_and_allocates_expenditure():
    persons = [
        Person(
            age=25,
            sex=Sex.FEMALE,
            education=EducationLevel.LOW,
            region=Region.EAST,
            taxes=2_000.0,
            social_contrib=500.0,
        ),
        Person(
            age=50,
            sex=Sex.MALE,
            education=EducationLevel.MEDIUM,
            region=Region.WEST,
            taxes=3_000.0,
            social_contrib=800.0,
        ),
    ]
    government = Government(
        spending_shares={
            GovFunction.EDUCATION: 0.2,
            GovFunction.SOCIAL_PROTECTION: 0.5,
            GovFunction.DEFENCE: 0.3,
        },
        deficit_limit=0.03,
        gdp=100_000.0,
    )

    government.collect_taxes_from_population(persons)

    assert government.tax_revenue == pytest.approx(5_000.0)
    assert government.social_contributions == pytest.approx(1_300.0)
    assert government.total_revenue == pytest.approx(6_300.0)

    government.allocate_expenditure()

    assert government.expenditure[GovFunction.EDUCATION] == pytest.approx(1_260.0)
    assert government.expenditure[GovFunction.SOCIAL_PROTECTION] == pytest.approx(3_150.0)
    assert government.expenditure[GovFunction.DEFENCE] == pytest.approx(1_890.0)


def test_government_pays_transfers():
    @dataclass(frozen=True)
    class FlatTransferRule:
        amount: float

        def compute_transfer(self, person: Person, government: Government) -> float:
            return self.amount

    persons = [
        Person(age=20, sex=Sex.OTHER, education=EducationLevel.LOW, region=Region.NORTH),
        Person(age=70, sex=Sex.FEMALE, education=EducationLevel.HIGH, region=Region.SOUTH),
    ]
    government = Government(
        spending_shares={GovFunction.SOCIAL_PROTECTION: 1.0},
        deficit_limit=0.03,
        gdp=0.0,
    )
    transfer_rule = FlatTransferRule(amount=500.0)

    government.pay_transfers(persons, transfer_rule)

    assert persons[0].transfers == pytest.approx(500.0)
    assert persons[1].transfers == pytest.approx(500.0)
