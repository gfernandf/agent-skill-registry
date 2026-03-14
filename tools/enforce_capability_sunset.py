#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def _default_base() -> Path:
    # Resolve repo root from this script location to avoid cwd-dependent writes.
    return Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _iter_capability_files(base: Path) -> list[Path]:
    cap_dir = base / "capabilities"
    if not cap_dir.exists():
        return []
    return sorted(path for path in cap_dir.glob("*.yaml") if path.name != "_index.yaml")


def validate_sunset(base: Path, minimum_window_days: int) -> tuple[list[str], int]:
    errors: list[str] = []
    deprecated_count = 0
    today = date.today()

    for path in _iter_capability_files(base):
        raw = _load_yaml(path)
        if not isinstance(raw, dict):
            continue

        cap_id = raw.get("id", path.stem)
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        status = metadata.get("status") if isinstance(metadata, dict) else None
        deprecated_flag = raw.get("deprecated") is True

        if status != "deprecated" and not deprecated_flag:
            continue

        deprecated_count += 1

        replacement = raw.get("replacement")
        if not isinstance(replacement, str) or not replacement:
            errors.append(f"{cap_id}: deprecated capability must define non-empty replacement")

        deprecation_date = _parse_iso_date(metadata.get("deprecation_date"))
        sunset_date = _parse_iso_date(metadata.get("sunset_date"))

        if deprecation_date is None:
            errors.append(f"{cap_id}: metadata.deprecation_date must be YYYY-MM-DD")
        if sunset_date is None:
            errors.append(f"{cap_id}: metadata.sunset_date must be YYYY-MM-DD")

        if deprecation_date is not None and sunset_date is not None:
            if sunset_date <= deprecation_date:
                errors.append(f"{cap_id}: sunset_date must be after deprecation_date")
            else:
                window = (sunset_date - deprecation_date).days
                if window < minimum_window_days:
                    errors.append(
                        f"{cap_id}: sunset window must be at least {minimum_window_days} days (found {window})"
                    )

            if sunset_date < today:
                errors.append(
                    f"{cap_id}: sunset_date {sunset_date.isoformat()} is expired; remove or extend with documented exception"
                )

    return errors, deprecated_count


def main() -> int:
    parser = argparse.ArgumentParser(prog="enforce_capability_sunset")
    parser.add_argument(
        "--base",
        type=Path,
        default=_default_base(),
        help="Repository root (default: script-relative repo root).",
    )
    parser.add_argument("--minimum-window-days", type=int, default=30)
    args = parser.parse_args()

    if args.minimum_window_days < 1:
        print("SUNSET ENFORCEMENT FAILED: --minimum-window-days must be >= 1")
        return 1

    base = args.base.resolve()
    errors, deprecated_count = validate_sunset(base, args.minimum_window_days)

    if errors:
        print("SUNSET ENFORCEMENT FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SUNSET ENFORCEMENT PASSED")
    print(f"Deprecated capabilities checked: {deprecated_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
