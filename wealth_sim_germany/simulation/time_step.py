from __future__ import annotations

import random
from dataclasses import dataclass

from wealth_sim_germany.config.schemas import ScenarioConfig
from wealth_sim_germany.models.government import Government, TransferRule
from wealth_sim_germany.models.income import IncomeModel
from wealth_sim_germany.models.person import Person
from wealth_sim_germany.models.tax import TaxCalculator
from wealth_sim_germany.models.wealth import WealthModel


@dataclass
class SimulationContext:
    income_model: IncomeModel
    wealth_model: WealthModel
    tax_calculator: TaxCalculator
    transfer_rule: TransferRule
    rng: random.Random


def run_single_year(
    ctx: SimulationContext,
    persons: list[Person],
    government: Government,
    year: int,
    scenario: ScenarioConfig,
) -> tuple[list[Person], Government]:
    for person in persons:
        ctx.income_model.sample_labor_income(person, ctx.rng)
        ctx.income_model.sample_capital_income(person, ctx.rng)
        person.compute_total_gross_income()

    for person in persons:
        tax_result = ctx.tax_calculator.compute_all_taxes(person)
        person.apply_tax_result(
            income_tax=tax_result.income_tax,
            social_contrib=tax_result.social_contrib,
            capital_tax=tax_result.capital_tax,
        )

    government.collect_taxes_from_population(persons)
    government.allocate_expenditure()

    government.pay_transfers(persons, ctx.transfer_rule)
    for person in persons:
        person.compute_total_gross_income()
        person.net_income = person.total_income - person.taxes - person.social_contrib

    for person in persons:
        ctx.wealth_model.evolve_wealth(person, ctx.rng, scenario.macro)

    government.apply_fiscal_rules()
    return persons, government
