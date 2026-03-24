#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def _default_base() -> Path:
    # Resolve repo root from this script location to avoid cwd-dependent writes.
    return Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
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
        raise FileNotFoundError(f"Vocabulary file not found: {vocab_path}")
    return load_json(vocab_path)


def load_cognitive_types(base: Path) -> Dict[str, Any]:
    ct_path = base / "vocabulary" / "cognitive_types.yaml"
    if not ct_path.exists():
        return {}
    return load_yaml(ct_path) or {}


def load_safety_vocabulary(base: Path) -> Dict[str, Any]:
    sv_path = base / "vocabulary" / "safety_vocabulary.yaml"
    if not sv_path.exists():
        return {}
    return load_yaml(sv_path) or {}


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


ALLOWED_STATUS = {"stable", "experimental", "draft", "deprecated", "unspecified"}

ALLOWED_ROLES = {"procedure", "utility", "sidecar"}
ALLOWED_INVOCATIONS = {"direct", "attach", "both"}
ALLOWED_ATTACH_TARGETS = {"task", "run", "output", "transcript", "artifact"}
ALLOWED_EFFECT_MODES = {"read_only", "enrich", "control_signal"}


def validate_classification_block(
    classification: Any,
    path: Path,
    errors: List[str],
) -> None:
    """Validate the metadata.classification sub-block of a skill YAML."""
    if not isinstance(classification, dict):
        errors.append(f"{path}: metadata.classification must be a mapping")
        return

    role = classification.get("role")
    if role is None:
        errors.append(f"{path}: metadata.classification.role is required")
    elif role not in ALLOWED_ROLES:
        errors.append(
            f"{path}: metadata.classification.role must be one of "
            f"{sorted(ALLOWED_ROLES)}, got '{role}'"
        )

    invocation = classification.get("invocation")
    if invocation is None:
        errors.append(f"{path}: metadata.classification.invocation is required")
    elif invocation not in ALLOWED_INVOCATIONS:
        errors.append(
            f"{path}: metadata.classification.invocation must be one of "
            f"{sorted(ALLOWED_INVOCATIONS)}, got '{invocation}'"
        )

    attach_targets = classification.get("attach_targets")
    if invocation in {"attach", "both"}:
        if not attach_targets:
            errors.append(
                f"{path}: metadata.classification.attach_targets is required "
                f"when invocation is '{invocation}'"
            )
        elif not isinstance(attach_targets, list):
            errors.append(
                f"{path}: metadata.classification.attach_targets must be a list"
            )
        else:
            for t in attach_targets:
                if t not in ALLOWED_ATTACH_TARGETS:
                    errors.append(
                        f"{path}: metadata.classification.attach_targets entry "
                        f"'{t}' must be one of {sorted(ALLOWED_ATTACH_TARGETS)}"
                    )
    elif invocation == "direct" and attach_targets is not None:
        errors.append(
            f"{path}: metadata.classification.attach_targets must not be set "
            "when invocation is 'direct'"
        )

    effect_mode = classification.get("effect_mode")
    if effect_mode is None:
        errors.append(f"{path}: metadata.classification.effect_mode is required")
    elif effect_mode not in ALLOWED_EFFECT_MODES:
        errors.append(
            f"{path}: metadata.classification.effect_mode must be one of "
            f"{sorted(ALLOWED_EFFECT_MODES)}, got '{effect_mode}'"
        )

    # Cross-field rule: sidecar must not be invoked directly
    if role == "sidecar" and invocation == "direct":
        errors.append(
            f"{path}: metadata.classification — a sidecar skill must not have "
            "invocation='direct'; use 'attach' or 'both'"
        )


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
    if tags is not None:
        if not isinstance(tags, list):
            errors.append(f"{path}: metadata.tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str):
                    errors.append(f"{path}: metadata.tags entries must be strings")

    category = metadata.get("category")
    if category is not None and not isinstance(category, str):
        errors.append(f"{path}: metadata.category must be string or null")

    status = metadata.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        errors.append(f"{path}: metadata.status must be one of {sorted(ALLOWED_STATUS)}")

    examples = metadata.get("examples")
    if examples is not None and not isinstance(examples, list):
        errors.append(f"{path}: metadata.examples must be a list")

    if skill_mode:
        use_cases = metadata.get("use_cases")
        if use_cases is not None:
            if not isinstance(use_cases, list):
                errors.append(f"{path}: metadata.use_cases must be a list")
            else:
                for use_case in use_cases:
                    if not isinstance(use_case, str):
                        errors.append(f"{path}: metadata.use_cases entries must be strings")

        classification = metadata.get("classification")
        # official/ and community/ channels require a classification block.
        # experimental/ and local/ validate the block if present but do not require it.
        is_required_channel = any(
            part in {"official", "community"} for part in path.parts
        )
        if classification is None:
            if is_required_channel:
                errors.append(
                    f"{path}: metadata.classification is required for "
                    "official and community skills"
                )
        else:
            validate_classification_block(classification, path, errors)


# ----------------------------------------------------------------------
# Cognitive hints validation
# ----------------------------------------------------------------------


def validate_cognitive_hints_block(
    hints: Any,
    data: Dict[str, Any],
    cognitive_types: Dict[str, Any],
    path: Path,
    errors: List[str],
) -> None:
    """Validate the optional cognitive_hints block of a capability YAML."""
    if hints is None:
        return

    if not isinstance(hints, dict):
        errors.append(f"{path}: cognitive_hints must be a mapping")
        return

    known_types = set(cognitive_types.get("types", {}).keys())
    known_roles = set(cognitive_types.get("roles", []))

    # --- role (required when hints present) ---
    role = hints.get("role")
    if role is None:
        errors.append(f"{path}: cognitive_hints.role is required when cognitive_hints is present")
    elif isinstance(role, str):
        if known_roles and role not in known_roles:
            errors.append(
                f"{path}: cognitive_hints.role '{role}' not in vocabulary roles {sorted(known_roles)}"
            )
    elif isinstance(role, list):
        for r in role:
            if not isinstance(r, str):
                errors.append(f"{path}: cognitive_hints.role entries must be strings")
            elif known_roles and r not in known_roles:
                errors.append(
                    f"{path}: cognitive_hints.role entry '{r}' not in vocabulary roles {sorted(known_roles)}"
                )
    else:
        errors.append(f"{path}: cognitive_hints.role must be a string or list of strings")

    # --- produces (required when hints present) ---
    produces = hints.get("produces")
    output_fields = set(data.get("outputs", {}).keys()) if isinstance(data.get("outputs"), dict) else set()
    if produces is None:
        errors.append(f"{path}: cognitive_hints.produces is required when cognitive_hints is present")
    elif not isinstance(produces, dict):
        errors.append(f"{path}: cognitive_hints.produces must be a mapping")
    else:
        for field_name, field_spec in produces.items():
            if not isinstance(field_name, str):
                errors.append(f"{path}: cognitive_hints.produces keys must be strings")
                continue
            if field_name not in output_fields:
                errors.append(
                    f"{path}: cognitive_hints.produces field '{field_name}' "
                    f"does not match any declared output field"
                )
            if not isinstance(field_spec, dict):
                errors.append(
                    f"{path}: cognitive_hints.produces.{field_name} must be a mapping"
                )
                continue
            ptype = field_spec.get("type")
            if not isinstance(ptype, str) or not ptype:
                errors.append(
                    f"{path}: cognitive_hints.produces.{field_name}.type is required"
                )
            elif known_types and ptype not in known_types:
                errors.append(
                    f"{path}: cognitive_hints.produces.{field_name}.type '{ptype}' "
                    f"not in vocabulary types {sorted(known_types)}"
                )
            merge = field_spec.get("merge")
            if merge is not None and merge not in {"append", "replace", "deep_merge", "overwrite"}:
                errors.append(
                    f"{path}: cognitive_hints.produces.{field_name}.merge '{merge}' "
                    f"must be one of append, replace, deep_merge, overwrite"
                )
            target = field_spec.get("target")
            if target is not None and not isinstance(target, str):
                errors.append(
                    f"{path}: cognitive_hints.produces.{field_name}.target must be a string"
                )

    # --- consumes (optional) ---
    consumes = hints.get("consumes")
    if consumes is not None:
        if not isinstance(consumes, list):
            errors.append(f"{path}: cognitive_hints.consumes must be a list")
        else:
            for item in consumes:
                if not isinstance(item, str):
                    errors.append(f"{path}: cognitive_hints.consumes entries must be strings")
                elif known_types and item not in known_types:
                    errors.append(
                        f"{path}: cognitive_hints.consumes entry '{item}' "
                        f"not in vocabulary types {sorted(known_types)}"
                    )


# ----------------------------------------------------------------------
# Safety block validation
# ----------------------------------------------------------------------


def validate_safety_block(
    safety: Any,
    data: Dict[str, Any],
    safety_vocab: Dict[str, Any],
    path: Path,
    errors: List[str],
) -> None:
    """Validate the optional safety block of a capability YAML."""
    if safety is None:
        return

    if not isinstance(safety, dict):
        errors.append(f"{path}: safety must be a mapping")
        return

    known_trust = set(safety_vocab.get("trust_levels", {}).keys())
    known_data_class = set(safety_vocab.get("data_classifications", {}).keys())
    known_failure = set(safety_vocab.get("failure_policies", []))
    known_targets = set(safety_vocab.get("allowed_targets", {}).keys())
    known_constraints = set(safety_vocab.get("scope_constraints", {}).keys())

    # --- trust_level (required when safety present) ---
    trust = safety.get("trust_level")
    if trust is None:
        errors.append(f"{path}: safety.trust_level is required when safety is present")
    elif not isinstance(trust, str) or (known_trust and trust not in known_trust):
        errors.append(
            f"{path}: safety.trust_level '{trust}' must be one of {sorted(known_trust)}"
        )

    # --- data_classification (optional) ---
    dc = safety.get("data_classification")
    if dc is not None:
        if not isinstance(dc, str) or (known_data_class and dc not in known_data_class):
            errors.append(
                f"{path}: safety.data_classification '{dc}' must be one of {sorted(known_data_class)}"
            )

    # --- reversible (optional, boolean) ---
    rev = safety.get("reversible")
    if rev is not None and not isinstance(rev, bool):
        errors.append(f"{path}: safety.reversible must be a boolean")

    # --- requires_confirmation (optional, boolean) ---
    rc = safety.get("requires_confirmation")
    if rc is not None and not isinstance(rc, bool):
        errors.append(f"{path}: safety.requires_confirmation must be a boolean")

    # --- allowed_targets (optional, list) ---
    at = safety.get("allowed_targets")
    if at is not None:
        if not isinstance(at, list):
            errors.append(f"{path}: safety.allowed_targets must be a list")
        else:
            for item in at:
                if not isinstance(item, str):
                    errors.append(f"{path}: safety.allowed_targets entries must be strings")
                elif known_targets and item not in known_targets:
                    errors.append(
                        f"{path}: safety.allowed_targets entry '{item}' "
                        f"not in vocabulary {sorted(known_targets)}"
                    )

    # --- mandatory_pre_gates / mandatory_post_gates ---
    for gate_key in ("mandatory_pre_gates", "mandatory_post_gates"):
        gates = safety.get(gate_key)
        if gates is None:
            continue
        if not isinstance(gates, list):
            errors.append(f"{path}: safety.{gate_key} must be a list")
            continue
        for idx, gate in enumerate(gates):
            if isinstance(gate, str):
                continue  # short form: capability id only, on_fail defaults to block
            if isinstance(gate, dict):
                gcap = gate.get("capability")
                if not isinstance(gcap, str) or not gcap:
                    errors.append(
                        f"{path}: safety.{gate_key}[{idx}].capability is required"
                    )
                on_fail = gate.get("on_fail", "block")
                if known_failure and on_fail not in known_failure:
                    errors.append(
                        f"{path}: safety.{gate_key}[{idx}].on_fail '{on_fail}' "
                        f"must be one of {sorted(known_failure)}"
                    )
            else:
                errors.append(
                    f"{path}: safety.{gate_key}[{idx}] must be a string or mapping"
                )

    # --- scope_constraints (optional, list) ---
    sc = safety.get("scope_constraints")
    if sc is not None:
        if not isinstance(sc, list):
            errors.append(f"{path}: safety.scope_constraints must be a list")
        else:
            for item in sc:
                if not isinstance(item, str):
                    errors.append(f"{path}: safety.scope_constraints entries must be strings")
                elif known_constraints and item not in known_constraints:
                    errors.append(
                        f"{path}: safety.scope_constraints entry '{item}' "
                        f"not in vocabulary {sorted(known_constraints)}"
                    )


def enforce_safety_for_side_effects(
    data: Dict[str, Any],
    path: Path,
    errors: List[str],
) -> None:
    """v2 enforcement: capabilities with side_effects: true MUST have a safety block."""
    props = data.get("properties")
    if not isinstance(props, dict):
        return
    if props.get("side_effects") is not True:
        return
    if data.get("safety") is None:
        errors.append(
            f"{path}: capability with properties.side_effects=true "
            f"must define a 'safety' block"
        )


# ----------------------------------------------------------------------
# Capability validation
# ----------------------------------------------------------------------


def validate_capability_structure(
    path: Path, data: Dict[str, Any], vocab: Dict[str, Any], errors: List[str],
    cognitive_types: Dict[str, Any] | None = None,
    safety_vocab: Dict[str, Any] | None = None,
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

    if not isinstance(data.get("version"), str) or not data.get("version"):
        errors.append(f"{path}: version must be a non-empty string")

    if not isinstance(data.get("description"), str) or not data.get("description"):
        errors.append(f"{path}: description must be a non-empty string")

    if not isinstance(data.get("inputs"), dict):
        errors.append(f"{path}: 'inputs' must be mapping")

    if not isinstance(data.get("outputs"), dict):
        errors.append(f"{path}: 'outputs' must be mapping")

    validate_metadata_block(data.get("metadata"), path, errors)

    validate_cognitive_hints_block(
        data.get("cognitive_hints"),
        data,
        cognitive_types or {},
        path,
        errors,
    )

    validate_safety_block(
        data.get("safety"),
        data,
        safety_vocab or {},
        path,
        errors,
    )

    enforce_safety_for_side_effects(data, path, errors)


def validate_capability_semantics(
    path: Path,
    data: Dict[str, Any],
    capability_ids: Set[str],
    errors: List[str],
) -> None:
    metadata = data.get("metadata", {})
    status = None
    if isinstance(metadata, dict):
        status = metadata.get("status")

    replacement = data.get("replacement")

    if status == "deprecated":
        if not isinstance(replacement, str) or not replacement:
            errors.append(
                f"{path}: deprecated capability must define a non-empty 'replacement'"
            )
        elif replacement not in capability_ids:
            errors.append(
                f"{path}: replacement '{replacement}' does not reference an existing capability"
            )

    if replacement is not None and not isinstance(replacement, str):
        errors.append(f"{path}: replacement must be a string when present")


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

    if not isinstance(data.get("id"), str) or not data.get("id"):
        errors.append(f"{path}: id must be a non-empty string")

    if not isinstance(data.get("version"), str) or not data.get("version"):
        errors.append(f"{path}: version must be a non-empty string")

    if not isinstance(data.get("name"), str) or not data.get("name"):
        errors.append(f"{path}: name must be a non-empty string")

    if not isinstance(data.get("description"), str) or not data.get("description"):
        errors.append(f"{path}: description must be a non-empty string")

    if not isinstance(data.get("inputs"), dict):
        errors.append(f"{path}: inputs must be a mapping")

    if not isinstance(data.get("outputs"), dict):
        errors.append(f"{path}: outputs must be a mapping")

    steps = data.get("steps")
    if not isinstance(steps, list):
        errors.append(f"{path}: steps must be a list")
    else:
        step_ids: Set[str] = set()
        for step in steps:
            if not isinstance(step, dict):
                errors.append(f"{path}: each step must be a mapping")
                continue

            step_id = step.get("id")
            if not isinstance(step_id, str) or not step_id:
                errors.append(f"{path}: each step must have a non-empty string 'id'")
            else:
                if step_id in step_ids:
                    errors.append(f"{path}: duplicate step id '{step_id}'")
                step_ids.add(step_id)

            uses = step.get("uses")
            if not isinstance(uses, str) or not uses:
                errors.append(
                    f"{path}: step '{step_id if isinstance(step_id, str) else '<unknown>'}' must define a non-empty string 'uses'"
                )

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
    capability_ids: Set[str],
    skill_ids: Set[str],
    errors: List[str],
) -> None:
    steps = data.get("steps", [])

    for step in steps:
        if not isinstance(step, dict):
            continue

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


def build_skill_dependency_graph(skill_docs: Dict[str, Dict[str, Any]]) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {}

    for skill_id, data in skill_docs.items():
        deps: Set[str] = set()
        steps = data.get("steps", [])
        if isinstance(steps, list):
            for step in steps:
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses")
                if isinstance(uses, str) and uses.startswith("skill:"):
                    deps.add(uses.split("skill:", 1)[1])
        graph[skill_id] = deps

    return graph


def detect_skill_cycles(graph: Dict[str, Set[str]], errors: List[str]) -> None:
    visited: Set[str] = set()
    visiting: Set[str] = set()
    stack: List[str] = []

    def dfs(node: str) -> None:
        if node in visiting:
            try:
                start_idx = stack.index(node)
                cycle = stack[start_idx:] + [node]
            except ValueError:
                cycle = stack + [node]
            errors.append(
                "skill dependency cycle detected: " + " -> ".join(cycle)
            )
            return

        if node in visited:
            return

        visiting.add(node)
        stack.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor in graph:
                dfs(neighbor)

        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        if node not in visited:
            dfs(node)


# ----------------------------------------------------------------------
# Main validation loop
# ----------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(prog="validate_registry")
    parser.add_argument(
        "--base",
        type=Path,
        default=_default_base(),
        help="Repository root (default: script-relative repo root).",
    )
    args = parser.parse_args()

    base = args.base.resolve()
    errors: List[str] = []

    vocab = load_vocabulary(base)
    cognitive_types = load_cognitive_types(base)
    safety_vocab = load_safety_vocabulary(base)

    capability_files = discover_capability_files(base)
    skill_files = discover_skill_files(base)

    capability_ids: Set[str] = set()
    skill_ids: Set[str] = set()

    capability_docs: Dict[str, Dict[str, Any]] = {}
    skill_docs: Dict[str, Dict[str, Any]] = {}

    for path in capability_files:
        data = load_yaml(path)

        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML")
            continue

        validate_capability_structure(path, data, vocab, errors, cognitive_types, safety_vocab)

        cid = data.get("id")
        if isinstance(cid, str):
            capability_ids.add(cid)
            capability_docs[cid] = data

    for path in skill_files:
        data = load_yaml(path)

        if not isinstance(data, dict):
            errors.append(f"{path}: invalid YAML")
            continue

        validate_skill_structure(path, data, errors)

        sid = data.get("id")
        if isinstance(sid, str):
            skill_ids.add(sid)
            skill_docs[sid] = data

    for path in capability_files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            continue
        validate_capability_semantics(path, data, capability_ids, errors)

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

    skill_graph = build_skill_dependency_graph(skill_docs)
    detect_skill_cycles(skill_graph, errors)

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