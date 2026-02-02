from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from wealth_sim_germany.models.government import Government
from wealth_sim_germany.models.person import Person


def weighted_mean(values: Iterable[float], weights: Iterable[float]) -> float:
    total_weight = 0.0
    total_value = 0.0
    for value, weight in zip(values, weights, strict=False):
        total_weight += weight
        total_value += value * weight
    if total_weight == 0:
        return 0.0
    return total_value / total_weight


def gini(values: Iterable[float], weights: Iterable[float]) -> float:
    pairs = [(float(value), float(weight)) for value, weight in zip(values, weights, strict=False)]
    if not pairs:
        return 0.0
    total_weight = sum(weight for _, weight in pairs)
    if total_weight == 0:
        return 0.0
    mean = sum(value * weight for value, weight in pairs) / total_weight
    if mean == 0:
        return 0.0
    pairs.sort(key=lambda item: item[0])
    cumulative_weight = 0.0
    numerator = 0.0
    for value, weight in pairs:
        cumulative_weight += weight
        numerator += weight * (2 * cumulative_weight - total_weight - weight) * value
    return numerator / (total_weight**2 * mean)


def aggregate_by_group(
    persons: Iterable[Person],
    group_field: str,
    value_field: str,
) -> dict[object, float]:
    grouped_values: dict[object, list[float]] = defaultdict(list)
    grouped_weights: dict[object, list[float]] = defaultdict(list)
    for person in persons:
        group_value = getattr(person, group_field)
        grouped_values[group_value].append(getattr(person, value_field))
        grouped_weights[group_value].append(person.weight)
    return {
        group: weighted_mean(values, grouped_weights[group])
        for group, values in grouped_values.items()
    }


def build_aggregates(
    persons: Iterable[Person],
    government: Government,
    year: int,
) -> dict[str, float]:
    persons_list = list(persons)
    weights = [person.weight for person in persons_list]
    total_income = sum(person.total_income * person.weight for person in persons_list)
    total_net_income = sum(person.net_income * person.weight for person in persons_list)
    total_taxes = sum(
        (person.taxes + person.social_contrib) * person.weight for person in persons_list
    )
    return {
        "year": year,
        "population": sum(weights),
        "total_gross_income": total_income,
        "total_net_income": total_net_income,
        "total_taxes": total_taxes,
        "avg_net_income": weighted_mean([person.net_income for person in persons_list], weights),
        "gini_net_income": gini([person.net_income for person in persons_list], weights),
        "government_revenue": government.total_revenue,
        "government_deficit": government.deficit,
        "government_debt": government.debt,
    }
