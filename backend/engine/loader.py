from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .gadget import Gadget, GadgetRule


try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_system(system_id: str, base_dir: Path | None = None) -> list[GadgetRule]:
    base_dir = base_dir or Path(__file__).resolve().parents[1]
    system_path = base_dir / "systems" / f"{system_id}.yaml"
    system = _read_yaml(system_path)
    rules: list[GadgetRule] = []
    for gadget_name in system.get("gadgets", []):
        gadget_path = base_dir / "gadgets" / Path(*gadget_name.split("."))
        gadget = _load_gadget(gadget_path)
        rules.extend(gadget.rules)
    return rules


def _load_gadget(gadget_path: Path) -> Gadget:
    if gadget_path.is_dir():
        metadata = _read_yaml(gadget_path / "gadget.yaml")
        rule_data: list[dict[str, Any]] = []
        for path in sorted(gadget_path.glob("*.yaml")):
            if path.name == "gadget.yaml":
                continue
            content = _read_yaml(path)
            rule_data.extend(content.get("rules", []) or [])
        return Gadget.from_parts(metadata, rule_data)

    gadget_file = gadget_path.with_suffix(".yaml")
    return Gadget.from_dict(_read_yaml(gadget_file))


def _read_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return json.loads(text)
    return yaml.safe_load(text) or {}
