#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


# ----------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_capability_files(base: Path) -> List[Path]:
    cap_dir = base / "capabilities"
    if not cap_dir.exists():
        return []
    return sorted(
        p.resolve()
        for p in cap_dir.glob("*.yaml")
        if p.name != "_index.yaml"
    )


def discover_skill_files(base: Path) -> List[Path]:
    skills_dir = base / "skills"
    if not skills_dir.exists():
        return []
    return sorted(p.resolve() for p in skills_dir.glob("*/*/*/skill.yaml"))


# ----------------------------------------------------------------------
# Vocabulary enforcement
# ----------------------------------------------------------------------


def load_vocabulary(base: Path) -> Dict[str, Any]:
    vocab_path = base / "vocabulary" / "vocabulary.json"
    if not vocab_path.exists():
        raise FileNotFoundError(
            f"Vocabulary file not found: {vocab_path}"
        )
    return load_json(vocab_path)


def validate_capability_id_against_vocab(
    capability_id: str, vocab: Dict[str, Any], errors: List[str], path: Path
) -> None:

    rules = vocab.get("rules", {})
    max_segments = rules.get("max_segments", 3)

    segments = capability_id.split(".")
    if not (2 <= len(segments) <= max_segments):
        errors.append(
            f"{path}: capability id '{capability_id}' has {len(segments)} segments"
        )
        return

    domains = vocab.get("domains", {})
    nouns = vocab.get("nouns", {})
    verbs = vocab.get("verbs", {})

    domain = segments[0]
    if domain not in domains:
        errors.append(
            f"{path}: unknown domain '{domain}' in capability id '{capability_id}'"
        )

    verb = segments[-1]
    if verb not in verbs:
        errors.append(
            f"{path}: unknown verb '{verb}' in capability id '{capability_id}'"
        )

    if len(segments) == 3:
        noun = segments[1]
        if noun not in nouns:
            errors.append(
                f"{path}: unknown noun '{noun}' in capability id '{capability_id}'"
            )


# ----------------------------------------------------------------------
# Metadata validation
# ----------------------------------------------------------------------


ALLOWED_STATUS = {"stable", "experimental", "deprecated", "unspecified"}


def validate_metadata_block(
    metadata: Any,
    path: Path,
    errors: List[str],
    skill_mode: bool = False,
) -> None:

    if metadata is None:
        return

    if not isinstance(metadata, dict):
        errors.append(f"{path}: metadata must be a mapping")
        return

    tags = metadata.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append(f"{path}: metadata.tags must be a list")

    category = metadata.get("category")
    if category is not None and not isinstance(category, str):
        errors.append(f"{path}: metadata.category must be string or null")

    status = metadata.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        errors.append(
            f"{path}: metadata.status must be one of {ALLOWED_STATUS}"
        )

    examples = metadata.get("examples")
    if examples is not None and not isinstance(examples, list):
        errors.append(f"{path}: metadata.examples must be a list")

    if skill_mode:
        use_cases = metadata.get("use_cases")
        if use_cases is not None and not isinstance(use_cases, list):
            errors.append(f"{path}: metadata.use_cases must be a list")


# ----------------------------------------------------------------------
# Capability validation
# ----------------------------------------------------------------------


def validate_capability_structure(
    path: Path, data: Dict[str, Any], vocab: Dict[str, Any], errors: List[str]
) -> None:

    required = ["id", "version", "description", "inputs", "outputs"]
    for r in required:
        if r not in data:
            errors.append(f"{path}: missing required field '{r}'")
            return

    capability_id = data.get("id")

    if not isinstance(capability_id, str):
        errors.append(f"{path}: invalid capability id")
        return

    validate_capability_id_against_vocab(capability_id, vocab, errors, path)

    if not isinstance(data.get("inputs"), dict):
        errors.append(f"{path}: 'inputs' must be mapping")

    if not isinstance(data.get("outputs"), dict):
        errors.append(f"{path}: 'outputs' must be mapping")

    validate_metadata_block(data.get("metadata"), path, errors)


# ----------------------------------------------------------------------
# Skill validation
# ----------------------------------------------------------------------


def validate_skill_structure(path: Path, data: Dict[str, Any], errors: List[str]) -> None:

    required = [
        "id",
        "version",
        "name",
        "description",
        "inputs",
        "outputs",
        "steps",
    ]

    for r in required:
        if r not in data:
            errors.append(f"{path}: missing required field '{r}'")
            return

    if not isinstance(data.get("steps"), list):
        errors.append(f"{path}: steps must be a list")

    validate_metadata_block(
        data.get("metadata"),
        path,
        errors,
        skill_mode=True,
    )


# ----------------------------------------------------------------------
# Skill reference validation
# ----------------------------------------------------------------------


def validate_skill_references(
    path: Path,
    data: Dict[str, Any],
    capability_ids: set[str],
    skill_ids: set[str],
    errors: List[str],
) -> None:

    steps = data.get("steps", [])

    for step in steps:

        uses = step.get("uses")
        sid = step.get("id", "<unknown>")

        if not isinstance(uses, str):
            continue

        if uses.startswith("skill:"):
            ref = uses.split("skill:", 1)[1]

            if ref not in skill_ids:
                errors.append(
                    f"{path}: step '{sid}' references unknown skill '{ref}'"
                )

        else:
            if uses not in capability_ids:
                errors.append(
                    f"{path}: step '{sid}' references unknown capability '{uses}'"
                )


# ----------------------------------------------------------------------
# Main validation loop
# ----------------------------------------------------------------------


def main() -> int:

    base = Path.cwd()
    errors: List[str] = []

    vocab = load_vocabulary(base)

    capability_files = discover_capability_files(base)
    skill_files = discover_skill_files(base)

    capability_ids: set[str] = set()
    skill_ids: set[str] = set()

    for path in capability_files:

        data = load_yaml(path)

        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML")
            continue

        validate_capability_structure(path, data, vocab, errors)

        cid = data.get("id")
        if isinstance(cid, str):
            capability_ids.add(cid)

    for path in skill_files:

        data = load_yaml(path)

        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML")
            continue

        validate_skill_structure(path, data, errors)

        sid = data.get("id")
        if isinstance(sid, str):
            skill_ids.add(sid)

    for path in skill_files:

        data = load_yaml(path)

        if not isinstance(data, dict):
            continue

        validate_skill_references(
            path,
            data,
            capability_ids,
            skill_ids,
            errors,
        )

    if errors:
        print("VALIDATION FAILED\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("VALIDATION PASSED")
    print(f"Capabilities: {len(capability_files)}")
    print(f"Skills: {len(skill_files)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())