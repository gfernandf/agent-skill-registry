#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Iterator

import yaml


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
CAPABILITY_ID_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9-]*){1,2}$")
SKILL_ID_RE = re.compile(r"^[a-z][a-z0-9]*\.[a-z][a-z0-9-]*$")
REF_RE = re.compile(r"^(inputs|vars|outputs)\.[A-Za-z_][A-Za-z0-9_]*$")


def is_semver(value: Any) -> bool:
    return isinstance(value, str) and bool(SEMVER_RE.fullmatch(value))


def is_capability_id(value: Any) -> bool:
    return isinstance(value, str) and bool(CAPABILITY_ID_RE.fullmatch(value))


def is_skill_id(value: Any) -> bool:
    return isinstance(value, str) and bool(SKILL_ID_RE.fullmatch(value))


def is_reference(value: Any) -> bool:
    return isinstance(value, str) and bool(REF_RE.fullmatch(value))


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iter_leaf_strings(obj: Any) -> Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from iter_leaf_strings(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_leaf_strings(item)


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


def resolve_targets(base: Path, raw_targets: list[Path]) -> tuple[list[Path], list[Path]]:
    if not raw_targets:
        return discover_capability_files(base), discover_skill_files(base)

    capability_files: list[Path] = []
    skill_files: list[Path] = []

    for raw in raw_targets:
        path = (base / raw).resolve() if not raw.is_absolute() else raw.resolve()

        if not path.exists():
            continue

        if path.is_file():
            if path.parent.name == "capabilities" and path.suffix == ".yaml" and path.name != "_index.yaml":
                capability_files.append(path)
            elif path.name == "skill.yaml":
                skill_files.append(path)

        elif path.is_dir():
            capability_files.extend(
                p.resolve()
                for p in path.rglob("*.yaml")
                if p.parent.name == "capabilities" and p.name != "_index.yaml"
            )
            skill_files.extend(p.resolve() for p in path.rglob("skill.yaml"))

    capability_files = list(dict.fromkeys(sorted(capability_files)))
    skill_files = list(dict.fromkeys(sorted(skill_files)))
    return capability_files, skill_files


def expected_capability_filename(capability_id: str) -> str:
    return f"{capability_id}.yaml"


def expected_skill_id_from_path(path: Path, base: Path) -> str | None:
    try:
        rel = path.relative_to(base)
    except ValueError:
        return None

    parts = rel.parts
    # skills/<channel>/<domain>/<skill-name>/skill.yaml
    if len(parts) == 5 and parts[0] == "skills" and parts[4] == "skill.yaml":
        return f"{parts[2]}.{parts[3]}"
    return None


def validate_schema_fields(
    path: Path,
    section_name: str,
    schema: Any,
    errors: list[str],
) -> None:
    if not isinstance(schema, dict):
        errors.append(f"{path}: '{section_name}' must be an object")
        return

    for field_name, field_def in schema.items():
        if not isinstance(field_def, dict):
            errors.append(f"{path}: '{section_name}.{field_name}' must be an object")
            continue

        if "type" not in field_def:
            errors.append(f"{path}: '{section_name}.{field_name}.type' is required")

        if "required" in field_def and not isinstance(field_def["required"], bool):
            errors.append(f"{path}: '{section_name}.{field_name}.required' must be boolean")

        if "description" in field_def and not isinstance(field_def["description"], str):
            errors.append(f"{path}: '{section_name}.{field_name}.description' must be a string")


def validate_capability_structure(
    path: Path,
    data: Any,
    errors: list[str],
) -> str | None:
    if not isinstance(data, dict):
        errors.append(f"{path}: root must be an object")
        return None

    required_fields = ["id", "version", "description", "inputs", "outputs"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")

    capability_id = data.get("id")
    version = data.get("version")
    description = data.get("description")
    inputs = data.get("inputs")
    outputs = data.get("outputs")

    if capability_id is not None and not is_capability_id(capability_id):
        errors.append(f"{path}: invalid capability id '{capability_id}'")

    if version is not None and not is_semver(version):
        errors.append(f"{path}: invalid semver version '{version}'")

    if description is not None and not isinstance(description, str):
        errors.append(f"{path}: 'description' must be a string")

    if inputs is not None:
        validate_schema_fields(path, "inputs", inputs, errors)

    if outputs is not None:
        validate_schema_fields(path, "outputs", outputs, errors)

    if "requires" in data and not isinstance(data["requires"], list):
        errors.append(f"{path}: 'requires' must be a list")

    if "properties" in data:
        properties = data["properties"]
        if not isinstance(properties, dict):
            errors.append(f"{path}: 'properties' must be an object")
        else:
            allowed = {"deterministic", "side_effects", "idempotent"}
            for key, value in properties.items():
                if key not in allowed:
                    errors.append(f"{path}: unknown property '{key}'")
                elif not isinstance(value, bool):
                    errors.append(f"{path}: property '{key}' must be boolean")

    if "deprecated" in data and not isinstance(data["deprecated"], bool):
        errors.append(f"{path}: 'deprecated' must be boolean")

    if "replacement" in data and not isinstance(data["replacement"], str):
        errors.append(f"{path}: 'replacement' must be a string")

    if "aliases" in data:
        aliases = data["aliases"]
        if not isinstance(aliases, list):
            errors.append(f"{path}: 'aliases' must be a list")
        else:
            for alias in aliases:
                if not isinstance(alias, str):
                    errors.append(f"{path}: all 'aliases' entries must be strings")

    if "examples" in data and not isinstance(data["examples"], list):
        errors.append(f"{path}: 'examples' must be a list")

    if capability_id:
        expected = expected_capability_filename(capability_id)
        if path.name != expected:
            errors.append(f"{path}: filename should be '{expected}'")

    return capability_id if isinstance(capability_id, str) else None


def validate_skill_structure(
    path: Path,
    data: Any,
    base: Path,
    errors: list[str],
) -> str | None:
    if not isinstance(data, dict):
        errors.append(f"{path}: root must be an object")
        return None

    required_fields = ["id", "version", "name", "description", "inputs", "outputs", "steps"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")

    skill_id = data.get("id")
    version = data.get("version")
    name = data.get("name")
    description = data.get("description")
    inputs = data.get("inputs")
    outputs = data.get("outputs")
    steps = data.get("steps")

    if skill_id is not None and not is_skill_id(skill_id):
        errors.append(f"{path}: invalid skill id '{skill_id}'")

    if version is not None and not is_semver(version):
        errors.append(f"{path}: invalid semver version '{version}'")

    if name is not None and not isinstance(name, str):
        errors.append(f"{path}: 'name' must be a string")

    if description is not None and not isinstance(description, str):
        errors.append(f"{path}: 'description' must be a string")

    if inputs is not None:
        validate_schema_fields(path, "inputs", inputs, errors)

    if outputs is not None:
        validate_schema_fields(path, "outputs", outputs, errors)

    if not isinstance(steps, list) or not steps:
        errors.append(f"{path}: 'steps' must be a non-empty list")
    else:
        seen_step_ids: set[str] = set()
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"{path}: step #{i + 1} must be an object")
                continue

            for field in ["id", "uses"]:
                if field not in step:
                    errors.append(f"{path}: step #{i + 1} missing required field '{field}'")

            step_id = step.get("id")
            uses = step.get("uses")
            step_input = step.get("input")
            step_output = step.get("output")

            if step_id is not None:
                if not isinstance(step_id, str):
                    errors.append(f"{path}: step #{i + 1} field 'id' must be a string")
                elif step_id in seen_step_ids:
                    errors.append(f"{path}: duplicate step id '{step_id}'")
                else:
                    seen_step_ids.add(step_id)

            if uses is not None and not isinstance(uses, str):
                errors.append(f"{path}: step '{step_id}' field 'uses' must be a string")

            if step_input is not None and not isinstance(step_input, dict):
                errors.append(f"{path}: step '{step_id}' field 'input' must be an object")

            if step_output is not None and not isinstance(step_output, dict):
                errors.append(f"{path}: step '{step_id}' field 'output' must be an object")

    expected_id = expected_skill_id_from_path(path, base)
    if expected_id and skill_id and skill_id != expected_id:
        errors.append(f"{path}: skill id should be '{expected_id}'")

    return skill_id if isinstance(skill_id, str) else None


def validate_capability_semantics(
    path: Path,
    data: dict[str, Any],
    known_capabilities: set[str],
    errors: list[str],
) -> None:
    requires = data.get("requires")
    if isinstance(requires, list):
        for req in requires:
            if not isinstance(req, str):
                errors.append(f"{path}: 'requires' entries must be strings")
            elif req not in known_capabilities:
                errors.append(f"{path}: required capability '{req}' does not exist")

    replacement = data.get("replacement")
    if isinstance(replacement, str) and replacement not in known_capabilities:
        errors.append(f"{path}: replacement capability '{replacement}' does not exist")

    aliases = data.get("aliases")
    if isinstance(aliases, list):
        for alias in aliases:
            if isinstance(alias, str) and not is_capability_id(alias):
                errors.append(f"{path}: alias '{alias}' is not a valid capability id")


def validate_skill_semantics(
    path: Path,
    data: dict[str, Any],
    known_capabilities: set[str],
    known_skills: set[str],
    errors: list[str],
) -> None:
    inputs = data.get("inputs", {})
    outputs = data.get("outputs", {})
    steps = data.get("steps", [])

    declared_inputs = set(inputs.keys()) if isinstance(inputs, dict) else set()
    declared_outputs = set(outputs.keys()) if isinstance(outputs, dict) else set()

    produced_vars: set[str] = set()
    produced_outputs: set[str] = set()
    written_targets: set[str] = set()

    if not isinstance(steps, list):
        return

    for step in steps:
        if not isinstance(step, dict):
            continue

        step_id = step.get("id", "<unknown>")
        uses = step.get("uses")
        step_input = step.get("input", {})
        step_output = step.get("output", {})

        if isinstance(uses, str):
            if uses.startswith("skill:"):
                nested_skill_id = uses.split("skill:", 1)[1]
                if nested_skill_id not in known_skills:
                    errors.append(f"{path}: step '{step_id}' references unknown skill '{nested_skill_id}'")
            else:
                if uses not in known_capabilities:
                    errors.append(f"{path}: step '{step_id}' references unknown capability '{uses}'")

        if isinstance(step_input, dict):
            for value in iter_leaf_strings(step_input):
                if is_reference(value):
                    namespace, field = value.split(".", 1)
                    if namespace == "inputs":
                        if field not in declared_inputs:
                            errors.append(f"{path}: step '{step_id}' references undeclared input '{value}'")
                    elif namespace == "vars":
                        if field not in produced_vars:
                            errors.append(f"{path}: step '{step_id}' references undefined var '{value}'")
                    elif namespace == "outputs":
                        if field not in declared_outputs:
                            errors.append(f"{path}: step '{step_id}' references undeclared output '{value}'")

        if isinstance(step_output, dict):
            for _, target in step_output.items():
                if not isinstance(target, str):
                    errors.append(f"{path}: step '{step_id}' output target must be a string")
                    continue

                if not is_reference(target):
                    errors.append(f"{path}: step '{step_id}' has invalid output target '{target}'")
                    continue

                namespace, field = target.split(".", 1)

                if namespace == "inputs":
                    errors.append(f"{path}: step '{step_id}' cannot write to '{target}'")
                    continue

                if namespace == "outputs" and field not in declared_outputs:
                    errors.append(f"{path}: step '{step_id}' writes to undeclared output '{target}'")
                    continue

                if target in written_targets:
                    errors.append(f"{path}: target '{target}' is written more than once")
                    continue

                written_targets.add(target)

                if namespace == "vars":
                    produced_vars.add(field)
                elif namespace == "outputs":
                    produced_outputs.add(field)

    missing_outputs = declared_outputs - produced_outputs
    for output_name in sorted(missing_outputs):
        errors.append(f"{path}: declared output 'outputs.{output_name}' is never produced by any step")


def main() -> int:
    base = Path.cwd()
    raw_args = [Path(arg) for arg in sys.argv[1:]]

    capability_files, skill_files = resolve_targets(base, raw_args)

    errors: list[str] = []
    capability_docs: dict[str, tuple[Path, dict[str, Any]]] = {}
    skill_docs: dict[str, tuple[Path, dict[str, Any]]] = {}

    for path in capability_files:
        try:
            data = load_yaml(path)
        except Exception as e:
            errors.append(f"{path}: failed to parse YAML ({e})")
            continue

        capability_id = validate_capability_structure(path, data, errors)
        if capability_id:
            if capability_id in capability_docs:
                errors.append(f"{path}: duplicate capability id '{capability_id}'")
            elif isinstance(data, dict):
                capability_docs[capability_id] = (path, data)

    for path in skill_files:
        try:
            data = load_yaml(path)
        except Exception as e:
            errors.append(f"{path}: failed to parse YAML ({e})")
            continue

        skill_id = validate_skill_structure(path, data, base, errors)
        if skill_id:
            if skill_id in skill_docs:
                errors.append(f"{path}: duplicate skill id '{skill_id}'")
            elif isinstance(data, dict):
                skill_docs[skill_id] = (path, data)

    known_capabilities = set(capability_docs.keys())
    known_skills = set(skill_docs.keys())

    for _, (path, data) in capability_docs.items():
        validate_capability_semantics(path, data, known_capabilities, errors)

    for _, (path, data) in skill_docs.items():
        validate_skill_semantics(path, data, known_capabilities, known_skills, errors)

    if errors:
        print("VALIDATION FAILED\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("VALIDATION PASSED")
    print(f"Capabilities: {len(capability_docs)}")
    print(f"Skills: {len(skill_docs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())