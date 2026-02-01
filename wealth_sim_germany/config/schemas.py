from __future__ import annotations

from dataclasses import dataclass

from wealth_sim_germany.utils.types import GovFunction


class ConfigError(ValueError):
    pass


def _ensure_keys(data: dict, required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing = required - data.keys()
    if missing:
        raise ConfigError(f"Missing required keys: {sorted(missing)}")
    extra = data.keys() - required - optional
    if extra:
        raise ConfigError(f"Unexpected keys: {sorted(extra)}")


@dataclass(frozen=True)
class TaxConfig:
    income_tax_rate: float
    capital_gains_rate: float
    social_contrib_rate: float

    @classmethod
    def from_dict(cls, data: dict) -> TaxConfig:
        _ensure_keys(data, {"income_tax_rate", "capital_gains_rate", "social_contrib_rate"})
        income_tax_rate = float(data["income_tax_rate"])
        capital_gains_rate = float(data["capital_gains_rate"])
        social_contrib_rate = float(data["social_contrib_rate"])
        for value, name in (
            (income_tax_rate, "income_tax_rate"),
            (capital_gains_rate, "capital_gains_rate"),
            (social_contrib_rate, "social_contrib_rate"),
        ):
            if not 0.0 <= value <= 1.0:
                raise ConfigError(f"{name} must be between 0 and 1")
        return cls(
            income_tax_rate=income_tax_rate,
            capital_gains_rate=capital_gains_rate,
            social_contrib_rate=social_contrib_rate,
        )


@dataclass(frozen=True)
class GovernmentSpendingConfig:
    spending_shares: dict[GovFunction, float]
    deficit_limit: float

    @classmethod
    def from_dict(cls, data: dict) -> GovernmentSpendingConfig:
        _ensure_keys(data, {"spending_shares", "deficit_limit"})
        spending_shares_raw = data["spending_shares"]
        if not isinstance(spending_shares_raw, dict):
            raise ConfigError("spending_shares must be a mapping")
        spending_shares: dict[GovFunction, float] = {}
        for key, value in spending_shares_raw.items():
            try:
                enum_key = GovFunction(key)
            except ValueError as exc:
                raise ConfigError(f"Unknown government function: {key}") from exc
            spending_shares[enum_key] = float(value)
        deficit_limit = float(data["deficit_limit"])
        if deficit_limit < 0:
            raise ConfigError("deficit_limit must be non-negative")
        return cls(spending_shares=spending_shares, deficit_limit=deficit_limit)


@dataclass(frozen=True)
class PopulationConfig:
    total_population: int
    synthetic_n: int

    @classmethod
    def from_dict(cls, data: dict) -> PopulationConfig:
        _ensure_keys(data, {"total_population", "synthetic_n"})
        total_population = int(data["total_population"])
        synthetic_n = int(data["synthetic_n"])
        if total_population <= 0 or synthetic_n <= 0:
            raise ConfigError("population sizes must be positive")
        return cls(total_population=total_population, synthetic_n=synthetic_n)


@dataclass(frozen=True)
class MacroParams:
    gdp_growth: float
    inflation: float

    @classmethod
    def from_dict(cls, data: dict) -> MacroParams:
        _ensure_keys(data, {"gdp_growth", "inflation"})
        return cls(gdp_growth=float(data["gdp_growth"]), inflation=float(data["inflation"]))


@dataclass(frozen=True)
class BacktestConfig:
    reference_year: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> BacktestConfig:
        _ensure_keys(data, {"reference_year"}, optional=set())
        reference_year = data.get("reference_year")
        if reference_year is not None:
            reference_year = int(reference_year)
        return cls(reference_year=reference_year)


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    start_year: int
    years: int
    tax: TaxConfig
    government: GovernmentSpendingConfig
    population: PopulationConfig
    macro: MacroParams
    backtest: BacktestConfig | None = None

    @classmethod
    def from_dict(cls, data: dict) -> ScenarioConfig:
        _ensure_keys(
            data,
            {"name", "start_year", "years", "tax", "government", "population", "macro"},
            optional={"backtest"},
        )
        years = int(data["years"])
        if years <= 0:
            raise ConfigError("years must be positive")
        backtest_raw = data.get("backtest")
        backtest = BacktestConfig.from_dict(backtest_raw) if backtest_raw else None
        return cls(
            name=str(data["name"]),
            start_year=int(data["start_year"]),
            years=years,
            tax=TaxConfig.from_dict(data["tax"]),
            government=GovernmentSpendingConfig.from_dict(data["government"]),
            population=PopulationConfig.from_dict(data["population"]),
            macro=MacroParams.from_dict(data["macro"]),
            backtest=backtest,
        )
