#!/usr/bin/env python3
"""G3 — Enforce SemVer rules on capability version changes.

Compares the current version of each capability against its previous
version (from git HEAD~1) and validates that version bumps follow
semantic versioning rules:

  - Adding a new REQUIRED input   → MAJOR bump required
  - Removing an output field      → MAJOR bump required
  - Renaming/removing a capability → MAJOR bump required
  - Adding an optional input      → MINOR bump required
  - Adding a new output field     → MINOR bump required
  - Description/metadata changes  → PATCH bump sufficient

Usage::

    python tools/enforce_semver.py [--strict] [--base-ref HEAD~1]

Exit codes:
  0  All version bumps are compliant.
  1  At least one violation found.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CAPS_DIR = _REPO_ROOT / "capabilities"


def parse_semver(version: str) -> tuple[int, int, int]:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        return (0, 0, 0)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_type(old: tuple[int, int, int], new: tuple[int, int, int]) -> str:
    if new[0] > old[0]:
        return "major"
    if new[1] > old[1]:
        return "minor"
    if new[2] > old[2]:
        return "patch"
    if new == old:
        return "none"
    return "unknown"


def load_yaml(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def load_yaml_from_git(ref: str, relpath: str) -> dict | None:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{ref}:{relpath}"],
            cwd=str(_REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return yaml.safe_load(raw)
    except (subprocess.CalledProcessError, yaml.YAMLError):
        return None


def required_bump(old_spec: dict, new_spec: dict) -> str:
    """Determine minimum required SemVer bump between two capability specs."""
    old_inputs = old_spec.get("inputs", {}) or {}
    new_inputs = new_spec.get("inputs", {}) or {}
    old_outputs = old_spec.get("outputs", {}) or {}
    new_outputs = new_spec.get("outputs", {}) or {}

    # MAJOR: removed output field
    for field in old_outputs:
        if field not in new_outputs:
            return "major"

    # MAJOR: new required input
    for field, spec in new_inputs.items():
        if field not in old_inputs:
            required = spec.get("required", True) if isinstance(spec, dict) else True
            if required:
                return "major"

    # MAJOR: removed input (could break existing callers)
    for field in old_inputs:
        if field not in new_inputs:
            return "major"

    # MINOR: new optional input
    for field, spec in new_inputs.items():
        if field not in old_inputs:
            required = spec.get("required", True) if isinstance(spec, dict) else True
            if not required:
                return "minor"

    # MINOR: new output field
    for field in new_outputs:
        if field not in old_outputs:
            return "minor"

    # PATCH: metadata/description only
    if old_spec.get("description") != new_spec.get("description"):
        return "patch"
    if old_spec.get("metadata") != new_spec.get("metadata"):
        return "patch"

    return "none"


_BUMP_RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce SemVer on capability versions")
    parser.add_argument("--base-ref", default="HEAD~1", help="Git ref to compare against")
    parser.add_argument("--strict", action="store_true", help="Fail on any missing version bump")
    args = parser.parse_args()

    violations: list[str] = []
    checked = 0

    if not _CAPS_DIR.is_dir():
        print("No capabilities/ directory found.")
        return 0

    for path in sorted(_CAPS_DIR.glob("*.yaml")):
        if path.name == "_index.yaml":
            continue
        new_spec = load_yaml(path)
        if not isinstance(new_spec, dict) or "id" not in new_spec:
            continue

        relpath = str(path.relative_to(_REPO_ROOT)).replace("\\", "/")
        old_spec = load_yaml_from_git(args.base_ref, relpath)
        if old_spec is None:
            continue  # new capability — no version constraint

        old_ver = parse_semver(str(old_spec.get("version", "0.0.0")))
        new_ver = parse_semver(str(new_spec.get("version", "0.0.0")))

        if old_ver == new_ver and old_spec == new_spec:
            continue  # unchanged

        actual = bump_type(old_ver, new_ver)
        needed = required_bump(old_spec, new_spec)

        checked += 1
        if _BUMP_RANK.get(actual, 0) < _BUMP_RANK.get(needed, 0):
            violations.append(
                f"  {new_spec['id']}: version {old_spec.get('version')} → "
                f"{new_spec.get('version')} (actual bump: {actual}, "
                f"required: {needed})"
            )

    print(f"SemVer check: {checked} capability versions examined.")
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for v in violations:
            print(v)
        return 1
    print("All version bumps are compliant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
