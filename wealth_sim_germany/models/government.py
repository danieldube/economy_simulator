from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from wealth_sim_germany.models.person import Person
from wealth_sim_germany.utils.types import GovFunction


class TransferRule(Protocol):
    def compute_transfer(self, person: Person, government: Government) -> float: ...


@dataclass
class Government:
    spending_shares: dict[GovFunction, float]
    deficit_limit: float
    gdp: float
    tax_revenue: float = 0.0
    social_contributions: float = 0.0
    total_revenue: float = 0.0
    expenditure: dict[GovFunction, float] = field(default_factory=dict)
    debt: float = 0.0
    deficit: float = 0.0

    def collect_taxes_from_population(self, persons: list[Person]) -> None:
        self.tax_revenue = sum(person.taxes for person in persons)
        self.social_contributions = sum(person.social_contrib for person in persons)
        self.total_revenue = self.tax_revenue + self.social_contributions

    def allocate_expenditure(
        self,
        policy_overrides: dict[GovFunction, float] | None = None,
    ) -> None:
        spending_shares = dict(self.spending_shares)
        if policy_overrides:
            spending_shares.update(policy_overrides)
        self.expenditure = {
            function: self.total_revenue * share for function, share in spending_shares.items()
        }

    def apply_fiscal_rules(self) -> None:
        if self.gdp <= 0:
            return
        max_deficit = self.gdp * self.deficit_limit
        if self.deficit > max_deficit:
            self.deficit = max_deficit

    def pay_transfers(self, persons: list[Person], transfer_rule: TransferRule) -> None:
        for person in persons:
            transfer = transfer_rule.compute_transfer(person, self)
            person.transfers += transfer
