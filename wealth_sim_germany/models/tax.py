from __future__ import annotations

from dataclasses import dataclass

from wealth_sim_germany.config.schemas import TaxConfig
from wealth_sim_germany.models.person import Person


@dataclass(frozen=True)
class TaxResult:
    income_tax: float
    social_contrib: float
    capital_tax: float

    @property
    def total(self) -> float:
        return self.income_tax + self.social_contrib + self.capital_tax


@dataclass(frozen=True)
class TaxCalculator:
    config: TaxConfig

    def compute_income_tax(self, taxable_income: float) -> float:
        taxable_income = max(taxable_income, 0.0)
        return taxable_income * self.config.income_tax_rate

    def compute_capital_tax(self, capital_income: float) -> float:
        capital_income = max(capital_income, 0.0)
        return capital_income * self.config.capital_gains_rate

    def compute_social_contributions(self, gross_income: float) -> float:
        gross_income = max(gross_income, 0.0)
        return gross_income * self.config.social_contrib_rate

    def compute_all_taxes(self, person: Person) -> TaxResult:
        gross_income = person.compute_total_gross_income()
        taxable_income = gross_income - person.capital_income
        income_tax = self.compute_income_tax(taxable_income)
        social_contrib = self.compute_social_contributions(gross_income)
        capital_tax = self.compute_capital_tax(person.capital_income)
        return TaxResult(
            income_tax=income_tax,
            social_contrib=social_contrib,
            capital_tax=capital_tax,
        )
