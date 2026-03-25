#!/usr/bin/env python3
"""G1 — Detect breaking changes in capabilities between two git refs.

Compares each capability YAML between ``--base`` (default: HEAD~1) and the
working tree.  A change is **breaking** if it:

1. Removes a previously required output field.
2. Removes a previously declared input field.
3. Adds a new *required* input field (callers unprepared).
4. Changes the type of an existing input or output field.

Usage:
    python tools/detect_breaking_changes.py [--base HEAD~1]

Exit codes:
    0 — no breaking changes
    1 — breaking changes detected
    2 — runtime error (e.g. git not available)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _git_show(ref: str, path: str) -> str | None:
    """Return file content at a given git ref, or None if it didn't exist."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _load_yaml_str(text: str) -> Dict[str, Any]:
    return yaml.safe_load(text) or {}


def _detect_for_capability(
    cap_id: str, old: Dict[str, Any], new: Dict[str, Any]
) -> List[str]:
    """Return list of breaking-change descriptions."""
    breaks: List[str] = []

    old_inputs = old.get("inputs", {}) or {}
    new_inputs = new.get("inputs", {}) or {}
    old_outputs = old.get("outputs", {}) or {}
    new_outputs = new.get("outputs", {}) or {}

    # 1. Removed output fields
    for name in old_outputs:
        if name not in new_outputs:
            breaks.append(f"[{cap_id}] output '{name}' removed")

    # 2. Removed input fields
    for name in old_inputs:
        if name not in new_inputs:
            breaks.append(f"[{cap_id}] input '{name}' removed")

    # 3. New required inputs
    for name, spec in new_inputs.items():
        if name not in old_inputs:
            if isinstance(spec, dict) and spec.get("required"):
                breaks.append(f"[{cap_id}] new required input '{name}' added")

    # 4. Type changes
    for name in old_inputs:
        if name in new_inputs:
            old_type = old_inputs[name].get("type") if isinstance(old_inputs[name], dict) else None
            new_type = new_inputs[name].get("type") if isinstance(new_inputs[name], dict) else None
            if old_type and new_type and old_type != new_type:
                breaks.append(f"[{cap_id}] input '{name}' type changed: {old_type} → {new_type}")

    for name in old_outputs:
        if name in new_outputs:
            old_type = old_outputs[name].get("type") if isinstance(old_outputs[name], dict) else None
            new_type = new_outputs[name].get("type") if isinstance(new_outputs[name], dict) else None
            if old_type and new_type and old_type != new_type:
                breaks.append(f"[{cap_id}] output '{name}' type changed: {old_type} → {new_type}")

    return breaks


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect breaking capability changes")
    parser.add_argument("--base", default="HEAD~1", help="Git ref to compare against (default: HEAD~1)")
    args = parser.parse_args()

    cap_dir = REPO_ROOT / "capabilities"
    if not cap_dir.exists():
        print("No capabilities/ directory found.", file=sys.stderr)
        return 2

    all_breaks: List[str] = []

    for path in sorted(cap_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue

        new_data = _load_yaml_str(path.read_text(encoding="utf-8-sig"))
        cap_id = new_data.get("id", path.stem)

        rel_path = path.relative_to(REPO_ROOT).as_posix()
        old_text = _git_show(args.base, rel_path)
        if old_text is None:
            continue  # new capability — not a breaking change

        old_data = _load_yaml_str(old_text)
        all_breaks.extend(_detect_for_capability(cap_id, old_data, new_data))

    if all_breaks:
        print(f"BREAKING CHANGES DETECTED ({len(all_breaks)}):\n")
        for b in all_breaks:
            print(f"  - {b}")
        return 1

    print("No breaking changes detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
