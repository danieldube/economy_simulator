from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Protocol, cast

from wealth_sim_germany.config.schemas import ScenarioConfig


class YamlModule(Protocol):
    def safe_load(self, stream: str) -> Any: ...


yaml_module: YamlModule | None

try:
    yaml_module = cast(YamlModule, importlib.import_module("yaml"))
except ModuleNotFoundError:  # pragma: no cover - fallback when PyYAML isn't installed
    yaml_module = None


def _validate_model(model_cls: type[ScenarioConfig], payload: Any) -> ScenarioConfig:
    return model_cls.from_dict(payload)


def load_scenario_config(path: str | Path) -> ScenarioConfig:
    config_path = Path(path)
    raw_text = config_path.read_text()
    raw = yaml_module.safe_load(raw_text) if yaml_module is not None else json.loads(raw_text)
    return _validate_model(ScenarioConfig, raw)
