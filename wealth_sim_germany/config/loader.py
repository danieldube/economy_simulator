from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - fallback when PyYAML isn't installed
    yaml = None
    import json

from wealth_sim_germany.config.schemas import ScenarioConfig


def _validate_model(model_cls: type[ScenarioConfig], payload: Any) -> ScenarioConfig:
    return model_cls.from_dict(payload)


def load_scenario_config(path: str | Path) -> ScenarioConfig:
    config_path = Path(path)
    raw_text = config_path.read_text()
    raw = yaml.safe_load(raw_text) if yaml is not None else json.loads(raw_text)
    return _validate_model(ScenarioConfig, raw)
