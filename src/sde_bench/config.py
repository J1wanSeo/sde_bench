from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from importlib import resources


DEFAULT_AXES = [
    "fidelity",
    "utility",
    "privacy",
    "fairness",
    "diversity",
    "groundedness",
    "domain_consistency",
]


def load_config(config: str | Path | dict[str, Any] | None = None) -> dict[str, Any]:
    """Load a preset/custom evaluation config.

    `config` may be a dict, a JSON file path, or one of the bundled preset names:
    `full_eval`, `fast_eval`, or `privacy_eval`.
    """
    if config is None:
        return {"name": "full_eval", "axes": DEFAULT_AXES}
    if isinstance(config, dict):
        return _normalize(config)
    path = Path(config)
    if not path.exists():
        package_config = resources.files("sde_bench").joinpath("configs", f"{path.stem}.json")
        if package_config.is_file():
            return _normalize(json.loads(package_config.read_text(encoding="utf-8")))
        bundled = Path(__file__).resolve().parents[2] / "configs" / f"{path.stem}.json"
        if bundled.exists():
            path = bundled
    if not path.exists():
        raise FileNotFoundError(f"Evaluation config not found: {config}")
    return _normalize(json.loads(path.read_text(encoding="utf-8")))


def _normalize(config: dict[str, Any]) -> dict[str, Any]:
    axes = config.get("axes") or DEFAULT_AXES
    unknown = [axis for axis in axes if axis not in DEFAULT_AXES]
    if unknown:
        raise ValueError(f"Unknown axes in config: {unknown}")
    return {**config, "axes": list(axes)}
