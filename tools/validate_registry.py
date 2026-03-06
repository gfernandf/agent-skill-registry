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
    # json.load documented usage for reading from a file-like object
    # See Python stdlib docs: json.load(...) description. :contentReference[oaicite:0]{index=0}
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
    # expects exactly skills/<channel>/<domain>/<skill-name>/skill.yaml
    return sorted(p.resolve() for p in skills_dir.glob("*/*/*/skill.yaml"))


def relative_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


# ----------------------------------------------------------------------
# Vocabulary enforcement
# ----------------------------------------------------------------------


def load_vocabulary(base: Path) -> Dict[str, Any]:
    vocab_path = base / "vocabulary" / "vocabulary.json"
    if not vocab_path.exists():
        raise FileNotFoundError(
            f"Vocabulary file not found: {vocab_path}. "
            "Expected vocabulary/vocabulary.json"
        )
    return load_json(vocab_path)


def validate_capability_id_against_vocab(
    capability_id: str, vocab: Dict[str, Any], errors: List[str], path: Path
) -> None:
    """
    Validate domain, optional noun, and verb based on vocabulary rules.
    Allowed forms: domain.verb or domain.noun.verb
    """
    rules = vocab.get("rules", {})
    max_segments = rules.get("max_segments", 3)

    segments = capability_id.split(".")
    if not (2 <= len(segments) <= max_segments):
        errors.append(
            f"{path}: capability id '{capability_id}' has {len(segments)} segments; "
            f"allowed up to {max_segments}."
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

    # last segment is verb
    verb = segments[-1]
    if verb not in verbs:
        errors.append(
            f"{path}: unknown verb '{verb}' in capability id '{capability_id}'"
        )

    # if there is a noun (i.e., 3 segments), validate it
    if len(segments) == 3:
        noun = segments[1]
        if noun not in nouns:
            errors.append(
                f"{path}: unknown noun '{noun}' in capability id '{capability_id}'"
            )


# ----------------------------------------------------------------------
# Capability validation logic
# ----------------------------------------------------------------------


def validate_capability_structure(
    path: Path, data: Dict[str, Any], vocab: Dict[str, Any], errors: List[str]
) -> None:
    # Required fields
    required = ["id", "version", "description", "inputs", "outputs"]
    for r in required:
        if r not in data:
            errors.append(f"{path}: missing required field '{r}'")
            return  # further checks rely on these fields

    capability_id = data.get("id")
    if not isinstance(capability_id, str) or "." not in capability_id:
        errors.append(f"{path}: invalid capability id '{capability_id}'")
        return

    # Validate against vocabulary
    validate_capability_id_against_vocab(capability_id, vocab, errors, path)

    # Version could be semver; simple check: non-empty string
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{path}: invalid version '{version}'")

    # Inputs/outputs should be dicts
    if not isinstance(data.get("inputs"), dict):
        errors.append(f"{path}: 'inputs' must be a mapping")
    if not isinstance(data.get("outputs"), dict):
        errors.append(f"{path}: 'outputs' must be a mapping")


# ----------------------------------------------------------------------
# Skill validation logic
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

    skill_id = data.get("id")
    if not isinstance(skill_id, str) or "." not in skill_id:
        errors.append(f"{path}: invalid skill id '{skill_id}'")
        return

    # version check similar to capability
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{path}: invalid version '{version}'")

    if not isinstance(data.get("inputs"), dict):
        errors.append(f"{path}: 'inputs' must be a mapping")
    if not isinstance(data.get("outputs"), dict):
        errors.append(f"{path}: 'outputs' must be a mapping")

    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{path}: 'steps' must be a non-empty list")
        return

    # Basic structure of steps
    step_ids: set[str] = set()
    for step in steps:
        if not isinstance(step, dict):
            errors.append(f"{path}: step is not a mapping: {step}")
            continue

        sid = step.get("id")
        if not sid or not isinstance(sid, str):
            errors.append(f"{path}: step without valid 'id'")
            continue
        if sid in step_ids:
            errors.append(f"{path}: duplicate step id '{sid}'")
            continue
        step_ids.add(sid)

        uses = step.get("uses")
        if not uses or not isinstance(uses, str):
            errors.append(f"{path}: step '{sid}' missing or invalid 'uses'")

        # input/output presence validation will be more detailed later


# ----------------------------------------------------------------------
# Dataflow and reference validation
#    (placeholder simplified; real validator may do more)
# ----------------------------------------------------------------------


def validate_skill_references(
    path: Path,
    data: Dict[str, Any],
    capability_ids: set[str],
    skill_ids: set[str],
    errors: List[str],
) -> None:
    """
    Validate each step 'uses' refers to a known capability or skill.
    Recognizes:
      - capability id directly: text.summarize
      - skill composition prefix: skill:<id>
    """
    steps = data.get("steps", [])
    for step in steps:
        sid = step.get("id", "<unknown>")
        uses = step.get("uses")
        if not isinstance(uses, str):
            continue

        if uses.startswith("skill:"):
            ref = uses.split("skill:", 1)[1]
            if ref not in skill_ids:
                errors.append(
                    f"{path}: step '{sid}' references unknown skill '{ref}'"
                )
        else:
            # capability reference
            if uses not in capability_ids:
                errors.append(
                    f"{path}: step '{sid}' references unknown capability '{uses}'"
                )

        # Optionally more dataflow checks could be here
        # e.g., inputs.* vars.* outputs.* correctness, duplicates, etc.


# ----------------------------------------------------------------------
# Main registry validation loop
# ----------------------------------------------------------------------


def main() -> int:
    base = Path.cwd()
    errors: List[str] = []

    # Load vocabulary
    try:
        vocab = load_vocabulary(base)
    except Exception as e:
        print(f"VOCABULARY LOAD FAILED: {e}")
        return 1

    # Discover and validate capabilities
    capability_files = discover_capability_files(base)
    capability_ids: set[str] = set()

    for path in capability_files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML content")
            continue
        validate_capability_structure(path, data, vocab, errors)
        # collect id for reference checking if valid
        cid = data.get("id")
        if isinstance(cid, str):
            capability_ids.add(cid)

    # Discover and validate skills
    skill_files = discover_skill_files(base)
    skill_ids: set[str] = set()

    for path in skill_files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML content")
            continue
        validate_skill_structure(path, data, errors)
        sid = data.get("id")
        if isinstance(sid, str):
            skill_ids.add(sid)

    # Validate references in skills
    for path in skill_files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            continue
        validate_skill_references(path, data, capability_ids, skill_ids, errors)

    # Final reporting
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