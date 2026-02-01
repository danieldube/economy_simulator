from __future__ import annotations

from pathlib import Path
from typing import Any, Type

try:
    import yaml
except ImportError:  # pragma: no cover - fallback when PyYAML isn't installed
    yaml = None
    import json

from wealth_sim_germany.config.schemas import ScenarioConfig


def _validate_model(model_cls: Type[ScenarioConfig], payload: Any) -> ScenarioConfig:
    return model_cls.from_dict(payload)


def load_scenario_config(path: str | Path) -> ScenarioConfig:
    config_path = Path(path)
    raw_text = config_path.read_text()
    if yaml is not None:
        raw = yaml.safe_load(raw_text)
    else:
        raw = json.loads(raw_text)
    return _validate_model(ScenarioConfig, raw)
