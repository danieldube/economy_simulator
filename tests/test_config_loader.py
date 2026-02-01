import pytest
import json

from wealth_sim_germany.config.loader import load_scenario_config
from wealth_sim_germany.utils.types import GovFunction


def test_load_scenario_config_parses_nested_models(tmp_path):
    scenario_data = {
        "name": "baseline",
        "start_year": 2020,
        "years": 2,
        "tax": {
            "income_tax_rate": 0.2,
            "capital_gains_rate": 0.25,
            "social_contrib_rate": 0.15,
        },
        "government": {
            "deficit_limit": 0.03,
            "spending_shares": {
                "education": 0.2,
                "social_protection": 0.5,
                "defence": 0.1,
            },
        },
        "population": {"total_population": 1000000, "synthetic_n": 1000},
        "macro": {"gdp_growth": 0.02, "inflation": 0.01},
    }
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text(json.dumps(scenario_data))

    scenario = load_scenario_config(config_path)

    assert scenario.name == "baseline"
    assert scenario.tax.income_tax_rate == pytest.approx(0.2)
    assert scenario.government.deficit_limit == pytest.approx(0.03)
    assert scenario.government.spending_shares[GovFunction.EDUCATION] == pytest.approx(0.2)


def test_load_scenario_config_rejects_extra_keys(tmp_path):
    scenario_data = {
        "name": "invalid",
        "start_year": 2020,
        "years": 1,
        "tax": {
            "income_tax_rate": 0.2,
            "capital_gains_rate": 0.25,
            "social_contrib_rate": 0.15,
        },
        "government": {
            "deficit_limit": 0.03,
            "spending_shares": {"education": 1.0},
        },
        "population": {"total_population": 1000, "synthetic_n": 10},
        "macro": {"gdp_growth": 0.02, "inflation": 0.01},
        "unexpected": "not allowed",
    }
    config_path = tmp_path / "scenario.yaml"
    config_path.write_text(json.dumps(scenario_data))

    with pytest.raises(Exception):
        load_scenario_config(config_path)
