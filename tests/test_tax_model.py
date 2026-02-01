import pytest

from wealth_sim_germany.config.schemas import TaxConfig
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.models.tax import TaxCalculator
from wealth_sim_germany.utils.types import EducationLevel, Region, Sex


def test_tax_calculator_computes_individual_taxes():
    tax_config = TaxConfig(
        income_tax_rate=0.2,
        capital_gains_rate=0.25,
        social_contrib_rate=0.1,
    )
    calculator = TaxCalculator(tax_config)

    assert calculator.compute_income_tax(50_000.0) == pytest.approx(10_000.0)
    assert calculator.compute_income_tax(-5_000.0) == pytest.approx(0.0)
    assert calculator.compute_capital_tax(4_000.0) == pytest.approx(1_000.0)
    assert calculator.compute_social_contributions(30_000.0) == pytest.approx(3_000.0)


def test_tax_calculator_computes_all_taxes_for_person():
    tax_config = TaxConfig(
        income_tax_rate=0.2,
        capital_gains_rate=0.25,
        social_contrib_rate=0.1,
    )
    calculator = TaxCalculator(tax_config)
    person = Person(
        age=42,
        sex=Sex.FEMALE,
        education=EducationLevel.HIGH,
        region=Region.WEST,
        labor_income=50_000.0,
        capital_income=5_000.0,
        transfers=1_000.0,
    )

    tax_result = calculator.compute_all_taxes(person)

    assert tax_result.income_tax == pytest.approx(10_200.0)
    assert tax_result.capital_tax == pytest.approx(1_250.0)
    assert tax_result.social_contrib == pytest.approx(5_600.0)
    assert tax_result.total == pytest.approx(17_050.0)
