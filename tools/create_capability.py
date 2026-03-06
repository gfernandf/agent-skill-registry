#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DOMAIN_RE = re.compile(r"^[a-z][a-z0-9]*$")
NOUN_RE = re.compile(r"^[a-z][a-z0-9-]*$")
VERB_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def is_valid_domain(value: str) -> bool:
    return bool(DOMAIN_RE.fullmatch(value))


def is_valid_noun(value: str) -> bool:
    return bool(NOUN_RE.fullmatch(value))


def is_valid_verb(value: str) -> bool:
    return bool(VERB_RE.fullmatch(value))


def build_capability_id(domain: str, verb: str, noun: str | None = None) -> str:
    if noun:
        return f"{domain}.{noun}.{verb}"
    return f"{domain}.{verb}"


def build_capability_path(base: Path, capability_id: str) -> Path:
    return base / "capabilities" / f"{capability_id}.yaml"


def render_capability_yaml(capability_id: str) -> str:
    return (
        f"id: {capability_id}\n"
        f"version: 1.0.0\n"
        f"description: Describe what this capability does.\n"
        f"\n"
        f"inputs: {{}}\n"
        f"\n"
        f"outputs: {{}}\n"
        f"\n"
        f"properties:\n"
        f"  deterministic: true\n"
        f"  side_effects: false\n"
        f"  idempotent: true\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new capability skeleton in the Agent Skill Registry."
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Capability domain (e.g. text, web, data)",
    )
    parser.add_argument(
        "--verb",
        required=True,
        help="Capability verb (e.g. summarize, fetch, parse)",
    )
    parser.add_argument(
        "--noun",
        required=False,
        help="Optional capability noun for domain.noun.verb form (e.g. json, page, language)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    domain = args.domain.strip()
    verb = args.verb.strip()
    noun = args.noun.strip() if args.noun else None

    errors: list[str] = []

    if not is_valid_domain(domain):
        errors.append(
            "Invalid --domain value. Expected lowercase letters and numbers, starting with a letter."
        )

    if noun is not None and not is_valid_noun(noun):
        errors.append(
            "Invalid --noun value. Expected lowercase letters, numbers, or hyphens."
        )

    if not is_valid_verb(verb):
        errors.append(
            "Invalid --verb value. Expected lowercase letters, numbers, or hyphens."
        )

    if errors:
        print("CAPABILITY CREATION FAILED\n")
        for error in errors:
            print(f"- {error}")
        return 1

    base = Path.cwd()
    capability_id = build_capability_id(domain, verb, noun)
    target_path = build_capability_path(base, capability_id)

    if target_path.exists():
        print("CAPABILITY CREATION FAILED\n")
        print(f"- Destination already exists: {target_path.relative_to(base).as_posix()}")
        return 1

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        render_capability_yaml(capability_id),
        encoding="utf-8",
        newline="\n",
    )

    print("CAPABILITY CREATED")
    print(f"ID: {capability_id}")
    print(f"Location: {target_path.relative_to(base).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())