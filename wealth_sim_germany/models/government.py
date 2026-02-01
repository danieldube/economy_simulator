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
        total_share = sum(spending_shares.values())
        if total_share <= 0:
            self.expenditure = dict.fromkeys(spending_shares, 0.0)
            return
        normalized_shares = {
            function: share / total_share for function, share in spending_shares.items()
        }
        self.expenditure = {
            function: self.total_revenue * share for function, share in normalized_shares.items()
        }

    def apply_fiscal_rules(self) -> None:
        total_expenditure = sum(self.expenditure.values())
        self.deficit = total_expenditure - self.total_revenue
        if self.gdp > 0:
            max_deficit = self.gdp * self.deficit_limit
            if self.deficit > max_deficit and total_expenditure > 0:
                scale = (self.total_revenue + max_deficit) / total_expenditure
                self.expenditure = {
                    function: amount * scale for function, amount in self.expenditure.items()
                }
                self.deficit = max_deficit
        self.debt += self.deficit

    def pay_transfers(self, persons: list[Person], transfer_rule: TransferRule) -> None:
        for person in persons:
            transfer = transfer_rule.compute_transfer(person, self)
            person.transfers += transfer
