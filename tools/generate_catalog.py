#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml


def _default_base() -> Path:
    # Resolve repo root from this script location to avoid cwd-dependent writes.
    return Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def discover_capability_files(base: Path) -> list[Path]:
    cap_dir = base / "capabilities"
    if not cap_dir.exists():
        return []
    return sorted(
        p.resolve()
        for p in cap_dir.glob("*.yaml")
        if p.name != "_index.yaml"
    )


def discover_skill_files(base: Path) -> list[Path]:
    skills_dir = base / "skills"
    if not skills_dir.exists():
        return []
    return sorted(p.resolve() for p in skills_dir.glob("*/*/*/skill.yaml"))


def relative_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def extract_skill_path_metadata(path: Path, base: Path) -> dict[str, str | None]:
    rel = path.relative_to(base)
    parts = rel.parts
    # skills/<channel>/<domain>/<skill-name>/skill.yaml
    if len(parts) == 5 and parts[0] == "skills" and parts[4] == "skill.yaml":
        return {
            "channel": parts[1],
            "domain": parts[2],
            "slug": parts[3],
        }
    return {
        "channel": None,
        "domain": None,
        "slug": None,
    }


def normalize_capability_metadata(raw_metadata: Any) -> dict[str, Any]:
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}

    return {
        "tags": metadata.get("tags", []) if isinstance(metadata.get("tags", []), list) else [],
        "category": metadata.get("category", None) if isinstance(metadata.get("category", None), str) or metadata.get("category", None) is None else None,
        "status": metadata.get("status", "unspecified") if isinstance(metadata.get("status", "unspecified"), str) else "unspecified",
        "examples": metadata.get("examples", []) if isinstance(metadata.get("examples", []), list) else [],
    }


def normalize_skill_metadata(raw_metadata: Any) -> dict[str, Any]:
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}

    result: dict[str, Any] = {
        "tags": metadata.get("tags", []) if isinstance(metadata.get("tags", []), list) else [],
        "category": metadata.get("category", None) if isinstance(metadata.get("category", None), str) or metadata.get("category", None) is None else None,
        "status": metadata.get("status", "unspecified") if isinstance(metadata.get("status", "unspecified"), str) else "unspecified",
        "use_cases": metadata.get("use_cases", []) if isinstance(metadata.get("use_cases", []), list) else [],
        "examples": metadata.get("examples", []) if isinstance(metadata.get("examples", []), list) else [],
    }

    raw_classification = metadata.get("classification")
    if isinstance(raw_classification, dict):
        classification: dict[str, Any] = {
            "role": raw_classification.get("role"),
            "invocation": raw_classification.get("invocation"),
            "effect_mode": raw_classification.get("effect_mode"),
        }
        attach_targets = raw_classification.get("attach_targets")
        if isinstance(attach_targets, list):
            classification["attach_targets"] = attach_targets
        result["classification"] = classification
    else:
        result["classification"] = None

    return result


def extract_capability_entry(path: Path, data: dict[str, Any], base: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": data.get("id"),
        "version": data.get("version"),
        "description": data.get("description"),
        "file": relative_posix(path, base),
        "inputs": data.get("inputs", {}),
        "outputs": data.get("outputs", {}),
        "metadata": normalize_capability_metadata(data.get("metadata")),
    }

    if "properties" in data:
        entry["properties"] = data.get("properties", {})
    if "requires" in data:
        entry["requires"] = data.get("requires", [])
    if "deprecated" in data:
        entry["deprecated"] = data.get("deprecated")
    if "replacement" in data:
        entry["replacement"] = data.get("replacement")
    if "aliases" in data:
        entry["aliases"] = data.get("aliases", [])
    if "examples" in data:
        entry["examples"] = data.get("examples", [])
    if "cognitive_hints" in data:
        entry["cognitive_hints"] = data["cognitive_hints"]
    if "safety" in data:
        entry["safety"] = data["safety"]

    return entry


def extract_skill_dependencies(steps: Any) -> tuple[list[str], list[str]]:
    uses_capabilities: list[str] = []
    uses_skills: list[str] = []

    if isinstance(steps, list):
        for step in steps:
            if not isinstance(step, dict):
                continue

            uses = step.get("uses")
            if not isinstance(uses, str):
                continue

            if uses.startswith("skill:"):
                uses_skills.append(uses.split("skill:", 1)[1])
            else:
                uses_capabilities.append(uses)

    uses_capabilities = sorted(dict.fromkeys(uses_capabilities))
    uses_skills = sorted(dict.fromkeys(uses_skills))
    return uses_capabilities, uses_skills


def extract_skill_entry(path: Path, data: dict[str, Any], base: Path) -> dict[str, Any]:
    path_meta = extract_skill_path_metadata(path, base)
    steps = data.get("steps", [])
    uses_capabilities, uses_skills = extract_skill_dependencies(steps)

    entry: dict[str, Any] = {
        "id": data.get("id"),
        "version": data.get("version"),
        "name": data.get("name"),
        "description": data.get("description"),
        "channel": path_meta["channel"],
        "domain": path_meta["domain"],
        "slug": path_meta["slug"],
        "file": relative_posix(path, base),
        "inputs": data.get("inputs", {}),
        "outputs": data.get("outputs", {}),
        "steps": steps,
        "uses_capabilities": uses_capabilities,
        "uses_skills": uses_skills,
        "metadata": normalize_skill_metadata(data.get("metadata")),
    }

    return entry


def build_graph(skills: list[dict[str, Any]]) -> dict[str, Any]:
    graph_skills: dict[str, Any] = {}

    for skill in skills:
        skill_id = skill.get("id")
        if not isinstance(skill_id, str):
            continue

        graph_skills[skill_id] = {
            "capabilities": skill.get("uses_capabilities", []),
            "skills": skill.get("uses_skills", []),
        }

    return {"skills": graph_skills}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def generate_catalog(base: Path) -> tuple[int, int]:
    capability_files = discover_capability_files(base)
    skill_files = discover_skill_files(base)

    capabilities: list[dict[str, Any]] = []
    skills: list[dict[str, Any]] = []

    for path in capability_files:
        data = load_yaml(path)
        if isinstance(data, dict):
            capabilities.append(extract_capability_entry(path, data, base))

    for path in skill_files:
        data = load_yaml(path)
        if isinstance(data, dict):
            skills.append(extract_skill_entry(path, data, base))

    capabilities.sort(key=lambda x: (str(x.get("id") or ""), str(x.get("version") or "")))
    skills.sort(key=lambda x: (str(x.get("id") or ""), str(x.get("version") or "")))

    graph = build_graph(skills)

    catalog_dir = base / "catalog"
    write_json(catalog_dir / "capabilities.json", capabilities)
    write_json(catalog_dir / "skills.json", skills)
    write_json(catalog_dir / "graph.json", graph)

    return len(capabilities), len(skills)


def main() -> int:
    base = _default_base()

    try:
        capability_count, skill_count = generate_catalog(base)
    except Exception as e:
        print(f"CATALOG GENERATION FAILED: {e}")
        return 1

    print("CATALOG GENERATED")
    print(f"Capabilities: {capability_count}")
    print(f"Skills: {skill_count}")
    print("Written:")
    print("- catalog/capabilities.json")
    print("- catalog/skills.json")
    print("- catalog/graph.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())