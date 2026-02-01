from __future__ import annotations

from dataclasses import dataclass, field

from wealth_sim_germany.utils.types import EducationLevel, Region, Sex


@dataclass
class Person:
    age: int
    sex: Sex
    education: EducationLevel
    region: Region
    labor_income: float = 0.0
    capital_income: float = 0.0
    transfers: float = 0.0
    total_income: float = 0.0
    taxes: float = 0.0
    social_contrib: float = 0.0
    net_income: float = 0.0
    liquid_assets: float = 0.0
    illiquid_assets: float = 0.0
    debt: float = 0.0
    stocks: float = 0.0
    net_wealth: float = 0.0
    weight: float = 1.0

    def compute_total_gross_income(self) -> float:
        self.total_income = self.labor_income + self.capital_income + self.transfers
        return self.total_income

    def apply_tax_result(self, income_tax: float, social_contrib: float, capital_tax: float) -> None:
        self.taxes = income_tax + capital_tax
        self.social_contrib = social_contrib
        gross_income = self.total_income or self.compute_total_gross_income()
        self.net_income = gross_income - self.taxes - self.social_contrib

    def update_wealth(self, savings_rate: float, labor_return_rate: float, capital_return_rate: float) -> None:
        savings = self.net_income * savings_rate
        labor_return = self.liquid_assets * labor_return_rate
        capital_return = self.illiquid_assets * capital_return_rate
        self.liquid_assets += savings + labor_return
        self.illiquid_assets += capital_return
        self.net_wealth = self.liquid_assets + self.illiquid_assets + self.stocks - self.debt
