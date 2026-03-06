#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHANNEL_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DOMAIN_RE = re.compile(r"^[a-z][a-z0-9]*$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def is_valid_channel(value: str) -> bool:
    return bool(CHANNEL_RE.fullmatch(value))


def is_valid_domain(value: str) -> bool:
    return bool(DOMAIN_RE.fullmatch(value))


def is_valid_slug(value: str) -> bool:
    return bool(SLUG_RE.fullmatch(value))


def slug_to_name(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def build_skill_id(domain: str, slug: str) -> str:
    return f"{domain}.{slug}"


def build_skill_path(base: Path, channel: str, domain: str, slug: str) -> Path:
    return base / "skills" / channel / domain / slug / "skill.yaml"


def render_skill_yaml(skill_id: str, human_name: str) -> str:
    return (
        f"id: {skill_id}\n"
        f"version: 0.1.0\n"
        f"name: {human_name}\n"
        f"description: Describe what this skill does.\n"
        f"\n"
        f"inputs: {{}}\n"
        f"\n"
        f"outputs: {{}}\n"
        f"\n"
        f"steps: []\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new skill skeleton in the Agent Skill Registry."
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="Registry channel (e.g. official, community, experimental)",
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Skill domain (e.g. text, web, data)",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Skill slug used in the repository path (e.g. simple-summarize)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    channel = args.channel.strip()
    domain = args.domain.strip()
    slug = args.slug.strip()

    errors: list[str] = []

    if not is_valid_channel(channel):
        errors.append(
            "Invalid --channel value. Expected lowercase letters, numbers, or hyphens."
        )

    if not is_valid_domain(domain):
        errors.append(
            "Invalid --domain value. Expected lowercase letters and numbers, starting with a letter."
        )

    if not is_valid_slug(slug):
        errors.append(
            "Invalid --slug value. Expected lowercase letters, numbers, or hyphens."
        )

    if errors:
        print("SKILL CREATION FAILED\n")
        for error in errors:
            print(f"- {error}")
        return 1

    base = Path.cwd()
    skill_id = build_skill_id(domain, slug)
    human_name = slug_to_name(slug)
    target_path = build_skill_path(base, channel, domain, slug)

    if target_path.exists():
        print("SKILL CREATION FAILED\n")
        print(f"- Destination already exists: {target_path}")
        return 1

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(render_skill_yaml(skill_id, human_name), encoding="utf-8", newline="\n")

    print("SKILL CREATED")
    print(f"ID: {skill_id}")
    print(f"Location: {target_path.relative_to(base).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())