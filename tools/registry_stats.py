#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _default_base() -> Path:
    # Resolve repo root from this script location to avoid cwd-dependent writes.
    return Path(__file__).resolve().parent.parent


DEFAULT_CAPABILITY_METADATA = {
    "tags": [],
    "category": None,
    "status": "unspecified",
    "examples": [],
}

DEFAULT_SKILL_METADATA = {
    "tags": [],
    "category": None,
    "status": "unspecified",
    "use_cases": [],
    "examples": [],
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def sort_counter_desc(counter: Counter[str]) -> dict[str, int]:
    items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return {k: v for k, v in items}


def counter_to_ranked_list(counter: Counter[str]) -> list[dict[str, Any]]:
    items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return [{"id": k, "count": v} for k, v in items]


def is_nondefault_metadata(metadata: Any, defaults: dict[str, Any]) -> bool:
    if not isinstance(metadata, dict):
        return False

    for key, default_value in defaults.items():
        value = metadata.get(key, default_value)
        if value != default_value:
            return True

    extra_keys = set(metadata.keys()) - set(defaults.keys())
    return bool(extra_keys)


def main() -> int:
    base = _default_base()
    catalog_dir = base / "catalog"

    capabilities_path = catalog_dir / "capabilities.json"
    skills_path = catalog_dir / "skills.json"
    graph_path = catalog_dir / "graph.json"

    try:
        capabilities = load_json(capabilities_path)
        skills = load_json(skills_path)
        graph = load_json(graph_path)
    except Exception as e:
        print(f"STATS GENERATION FAILED: {e}")
        return 1

    if not isinstance(capabilities, list):
        print("STATS GENERATION FAILED: catalog/capabilities.json must contain a list")
        return 1

    if not isinstance(skills, list):
        print("STATS GENERATION FAILED: catalog/skills.json must contain a list")
        return 1

    if not isinstance(graph, dict):
        print("STATS GENERATION FAILED: catalog/graph.json must contain an object")
        return 1

    skill_graph = graph.get("skills", {})
    if not isinstance(skill_graph, dict):
        print("STATS GENERATION FAILED: graph.skills must be an object")
        return 1

    capability_ids: list[str] = []
    capability_domains: Counter[str] = Counter()
    capability_statuses: Counter[str] = Counter()
    skill_domains: Counter[str] = Counter()
    skill_channels: Counter[str] = Counter()
    capability_usage: Counter[str] = Counter()
    skill_tags: Counter[str] = Counter()
    capability_tags: Counter[str] = Counter()

    total_steps = 0
    skills_with_skill_dependencies = 0
    max_capabilities_per_skill = 0
    skill_to_capability_edges = 0
    skill_to_skill_edges = 0

    skills_with_nondefault_metadata = 0
    capabilities_with_nondefault_metadata = 0

    channels_seen: set[str] = set()
    domains_seen: set[str] = set()

    # Capabilities stats
    for capability in capabilities:
        if not isinstance(capability, dict):
            continue

        capability_id = capability.get("id")
        if isinstance(capability_id, str):
            capability_ids.append(capability_id)

        domain = capability_id.split(".")[0] if isinstance(capability_id, str) and "." in capability_id else None
        if isinstance(domain, str):
            capability_domains[domain] += 1
            domains_seen.add(domain)

        metadata = capability.get("metadata", {})
        if is_nondefault_metadata(metadata, DEFAULT_CAPABILITY_METADATA):
            capabilities_with_nondefault_metadata += 1

        cap_status = metadata.get("status", "unspecified") if isinstance(metadata, dict) else "unspecified"
        capability_statuses[cap_status] += 1

        if isinstance(metadata, dict):
            tags = metadata.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        capability_tags[tag] += 1

    # Skills stats
    for skill in skills:
        if not isinstance(skill, dict):
            continue

        domain = skill.get("domain")
        if isinstance(domain, str):
            skill_domains[domain] += 1
            domains_seen.add(domain)

        channel = skill.get("channel")
        if isinstance(channel, str):
            skill_channels[channel] += 1
            channels_seen.add(channel)

        steps = skill.get("steps", [])
        if isinstance(steps, list):
            total_steps += len(steps)

        metadata = skill.get("metadata", {})
        if is_nondefault_metadata(metadata, DEFAULT_SKILL_METADATA):
            skills_with_nondefault_metadata += 1

        if isinstance(metadata, dict):
            tags = metadata.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        skill_tags[tag] += 1

    # Dependency stats from graph
    for skill_id, deps in skill_graph.items():
        if not isinstance(deps, dict):
            continue

        cap_list = deps.get("capabilities", [])
        skill_list = deps.get("skills", [])

        if not isinstance(cap_list, list):
            cap_list = []
        if not isinstance(skill_list, list):
            skill_list = []

        skill_to_capability_edges += len(cap_list)
        skill_to_skill_edges += len(skill_list)

        if skill_list:
            skills_with_skill_dependencies += 1

        if len(cap_list) > max_capabilities_per_skill:
            max_capabilities_per_skill = len(cap_list)

        for capability_id in cap_list:
            if isinstance(capability_id, str):
                capability_usage[capability_id] += 1

    unused_capabilities = sorted(
        [cap_id for cap_id in capability_ids if capability_usage[cap_id] == 0]
    )

    average_steps = round((total_steps / len(skills)), 2) if skills else 0.0

    stats = {
        "summary": {
            "capability_count": len(capabilities),
            "skill_count": len(skills),
            "domain_count": len(domains_seen),
            "channel_count": len(channels_seen),
        },
        "skills": {
            "by_domain": sort_counter_desc(skill_domains),
            "by_channel": sort_counter_desc(skill_channels),
            "average_steps": average_steps,
            "with_skill_dependencies": skills_with_skill_dependencies,
        },
        "capabilities": {
            "by_domain": sort_counter_desc(capability_domains),
            "by_status": sort_counter_desc(capability_statuses),
            "most_used": counter_to_ranked_list(capability_usage),
            "unused": unused_capabilities,
        },
        "dependencies": {
            "skill_to_capability_edges": skill_to_capability_edges,
            "skill_to_skill_edges": skill_to_skill_edges,
            "max_capabilities_per_skill": max_capabilities_per_skill,
        },
        "metadata": {
            "skills_with_nondefault_metadata": skills_with_nondefault_metadata,
            "capabilities_with_nondefault_metadata": capabilities_with_nondefault_metadata,
            "top_skill_tags": counter_to_ranked_list(skill_tags),
            "top_capability_tags": counter_to_ranked_list(capability_tags),
        },
    }

    try:
        write_json(catalog_dir / "stats.json", stats)
    except Exception as e:
        print(f"STATS GENERATION FAILED: {e}")
        return 1

    print("STATS GENERATED")
    print("Written:")
    print("- catalog/stats.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())