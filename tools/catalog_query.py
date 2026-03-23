#!/usr/bin/env python3
"""
Semantic query tool over the capability catalog.

Exploits cognitive_hints, safety, and properties to answer questions like:
  - What capabilities produce Risk?
  - What consumes Option?
  - What roles are covered?
  - What slots are covered vs uncovered?
  - What capabilities are compatible (produces → consumes)?

Usage:
  python tools/catalog_query.py produces Risk
  python tools/catalog_query.py consumes Option
  python tools/catalog_query.py role analyze
  python tools/catalog_query.py compatible analysis.risk.extract
  python tools/catalog_query.py coverage
  python tools/catalog_query.py safety
  python tools/catalog_query.py chain Risk Decision
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _default_base() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_catalog(base: Path) -> list[dict[str, Any]]:
    path = base / "catalog" / "capabilities.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_cognitive_types(base: Path) -> dict[str, Any]:
    path = base / "vocabulary" / "cognitive_types.yaml"
    if not path.exists():
        return {}
    import yaml
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ── Index builders ──────────────────────────────────────────────


def _build_produces_index(caps: list[dict]) -> dict[str, list[str]]:
    """type_name → [capability_ids that produce it]"""
    index: dict[str, list[str]] = {}
    for c in caps:
        hints = c.get("cognitive_hints")
        if not hints:
            continue
        produces = hints.get("produces")
        if not isinstance(produces, dict):
            continue
        seen_types: set[str] = set()
        for field_spec in produces.values():
            if isinstance(field_spec, dict):
                t = field_spec.get("type")
                if isinstance(t, str) and t not in seen_types:
                    seen_types.add(t)
                    index.setdefault(t, []).append(c["id"])
    return index


def _build_consumes_index(caps: list[dict]) -> dict[str, list[str]]:
    """type_name → [capability_ids that consume it]"""
    index: dict[str, list[str]] = {}
    for c in caps:
        hints = c.get("cognitive_hints")
        if not hints:
            continue
        consumes = hints.get("consumes")
        if not isinstance(consumes, list):
            continue
        for t in consumes:
            if isinstance(t, str):
                index.setdefault(t, []).append(c["id"])
    return index


def _build_role_index(caps: list[dict]) -> dict[str, list[str]]:
    """role → [capability_ids]"""
    index: dict[str, list[str]] = {}
    for c in caps:
        hints = c.get("cognitive_hints")
        if not hints:
            continue
        role = hints.get("role")
        if isinstance(role, str):
            index.setdefault(role, []).append(c["id"])
        elif isinstance(role, list):
            for r in role:
                index.setdefault(r, []).append(c["id"])
    return index


# ── Query commands ──────────────────────────────────────────────


def cmd_produces(caps: list[dict], type_name: str) -> None:
    """Which capabilities produce a given cognitive type?"""
    idx = _build_produces_index(caps)
    matches = idx.get(type_name, [])
    if not matches:
        print(f"No capabilities produce '{type_name}'.")
        all_types = sorted(idx.keys())
        if all_types:
            print(f"Available types: {', '.join(all_types)}")
        return
    print(f"Capabilities that produce '{type_name}':")
    for cid in sorted(matches):
        print(f"  {cid}")


def cmd_consumes(caps: list[dict], type_name: str) -> None:
    """Which capabilities consume a given cognitive type?"""
    idx = _build_consumes_index(caps)
    matches = idx.get(type_name, [])
    if not matches:
        print(f"No capabilities consume '{type_name}'.")
        all_types = sorted(idx.keys())
        if all_types:
            print(f"Available types: {', '.join(all_types)}")
        return
    print(f"Capabilities that consume '{type_name}':")
    for cid in sorted(matches):
        print(f"  {cid}")


def cmd_role(caps: list[dict], role_name: str) -> None:
    """Which capabilities belong to a given cognitive role?"""
    idx = _build_role_index(caps)
    matches = idx.get(role_name, [])
    if not matches:
        print(f"No capabilities with role '{role_name}'.")
        all_roles = sorted(idx.keys())
        if all_roles:
            print(f"Available roles: {', '.join(all_roles)}")
        return
    print(f"Capabilities with role '{role_name}':")
    for cid in sorted(matches):
        print(f"  {cid}")


def cmd_compatible(caps: list[dict], capability_id: str) -> None:
    """What capabilities can consume what this one produces (downstream)?"""
    cap = next((c for c in caps if c["id"] == capability_id), None)
    if not cap:
        print(f"Capability '{capability_id}' not found.")
        return
    hints = cap.get("cognitive_hints")
    if not hints or not hints.get("produces"):
        print(f"Capability '{capability_id}' has no produces declaration.")
        return
    produced_types: set[str] = set()
    for field_spec in hints["produces"].values():
        if isinstance(field_spec, dict) and isinstance(field_spec.get("type"), str):
            produced_types.add(field_spec["type"])

    consumes_idx = _build_consumes_index(caps)
    print(f"'{capability_id}' produces: {', '.join(sorted(produced_types))}")
    print()
    found = False
    for t in sorted(produced_types):
        consumers = consumes_idx.get(t, [])
        consumers = [c for c in consumers if c != capability_id]
        if consumers:
            found = True
            print(f"  {t} → consumed by:")
            for cid in sorted(consumers):
                print(f"    {cid}")
    if not found:
        print("  No downstream consumers found.")


def cmd_coverage(caps: list[dict], cognitive_types: dict) -> None:
    """Which cognitive types and roles are covered vs uncovered?"""
    produces_idx = _build_produces_index(caps)
    consumes_idx = _build_consumes_index(caps)
    role_idx = _build_role_index(caps)

    all_types = sorted(set(
        list(cognitive_types.get("types", {}).keys())
    ))
    all_roles = sorted(cognitive_types.get("roles", []))

    total_caps = len(caps)
    annotated = sum(1 for c in caps if c.get("cognitive_hints"))

    print(f"Annotation coverage: {annotated}/{total_caps} capabilities")
    print()

    print("Type coverage (produced / consumed):")
    for t in all_types:
        p = len(produces_idx.get(t, []))
        c = len(consumes_idx.get(t, []))
        marker = "✓" if p > 0 else "✗"
        print(f"  {marker} {t:20s}  produced={p}  consumed={c}")

    uncovered = [t for t in all_types if t not in produces_idx and t not in consumes_idx]
    if uncovered:
        print(f"\n  Uncovered types: {', '.join(uncovered)}")

    print()
    print("Role coverage:")
    for r in all_roles:
        count = len(role_idx.get(r, []))
        marker = "✓" if count > 0 else "✗"
        print(f"  {marker} {r:15s}  capabilities={count}")

    empty_roles = [r for r in all_roles if r not in role_idx]
    if empty_roles:
        print(f"\n  Uncovered roles: {', '.join(empty_roles)}")


def cmd_safety(caps: list[dict]) -> None:
    """Which capabilities have safety blocks and what do they require?"""
    with_safety = [c for c in caps if c.get("safety")]
    side_effect_caps = [
        c for c in caps
        if isinstance(c.get("properties"), dict) and c["properties"].get("side_effects")
    ]
    missing_safety = [
        c for c in side_effect_caps if not c.get("safety")
    ]

    print(f"Safety coverage: {len(with_safety)} annotated / "
          f"{len(side_effect_caps)} side-effecting capabilities")
    if missing_safety:
        print(f"\n  ⚠ Missing safety (side_effects=true but no safety block):")
        for c in missing_safety:
            print(f"    {c['id']}")

    if with_safety:
        print()
        for c in with_safety:
            s = c["safety"]
            parts = [f"trust={s.get('trust_level', '?')}"]
            if s.get("requires_confirmation"):
                parts.append("confirm=yes")
            if s.get("reversible") is True:
                parts.append("reversible")
            if s.get("allowed_targets"):
                parts.append(f"targets={s['allowed_targets']}")
            pre = s.get("mandatory_pre_gates", [])
            post = s.get("mandatory_post_gates", [])
            if pre:
                parts.append(f"pre_gates={len(pre)}")
            if post:
                parts.append(f"post_gates={len(post)}")
            print(f"  {c['id']:40s}  {', '.join(parts)}")


def cmd_chain(caps: list[dict], source_type: str, target_type: str) -> None:
    """Find capability chains from source_type to target_type (1-2 hops)."""
    produces_idx = _build_produces_index(caps)
    consumes_idx = _build_consumes_index(caps)

    # Direct: capabilities that consume source_type AND produce target_type
    source_consumers = set(consumes_idx.get(source_type, []))
    target_producers = set(produces_idx.get(target_type, []))
    direct = sorted(source_consumers & target_producers)

    print(f"Chain: {source_type} → ... → {target_type}")
    print()

    if direct:
        print(f"  Direct (1-hop):")
        for cid in direct:
            print(f"    {cid}")

    # 2-hop: source_type → Cap A (produces X) → Cap B (consumes X, produces target_type)
    two_hop: list[tuple[str, str, str]] = []
    for cap_a_id in consumes_idx.get(source_type, []):
        cap_a = next((c for c in caps if c["id"] == cap_a_id), None)
        if not cap_a:
            continue
        a_hints = cap_a.get("cognitive_hints", {})
        a_produces = a_hints.get("produces", {})
        for field_spec in a_produces.values():
            if not isinstance(field_spec, dict):
                continue
            mid_type = field_spec.get("type")
            if not isinstance(mid_type, str):
                continue
            for cap_b_id in consumes_idx.get(mid_type, []):
                if cap_b_id == cap_a_id:
                    continue
                if cap_b_id in target_producers:
                    two_hop.append((cap_a_id, mid_type, cap_b_id))

    seen: set[tuple[str, str]] = set()
    unique_hops: list[tuple[str, str, str]] = []
    for a, mid, b in two_hop:
        key = (a, b)
        if key not in seen:
            seen.add(key)
            unique_hops.append((a, mid, b))

    if unique_hops:
        print(f"\n  2-hop paths:")
        for a, mid, b in sorted(unique_hops):
            print(f"    {a} →[{mid}]→ {b}")

    if not direct and not unique_hops:
        print("  No chains found.")


# ── Main ────────────────────────────────────────────────────────


USAGE = """\
Usage: python tools/catalog_query.py <command> [args...]

Commands:
  produces <Type>              Capabilities that produce a cognitive type
  consumes <Type>              Capabilities that consume a cognitive type
  role <role>                  Capabilities with a given cognitive role
  compatible <capability_id>   Downstream capabilities compatible with outputs
  coverage                     Type and role coverage report
  safety                       Safety block coverage and details
  chain <SourceType> <TargetType>  Find capability chains (1-2 hops)
"""


def main() -> None:
    base = _default_base()
    caps = _load_catalog(base)

    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(1)

    command = args[0]

    if command == "produces" and len(args) >= 2:
        cmd_produces(caps, args[1])
    elif command == "consumes" and len(args) >= 2:
        cmd_consumes(caps, args[1])
    elif command == "role" and len(args) >= 2:
        cmd_role(caps, args[1])
    elif command == "compatible" and len(args) >= 2:
        cmd_compatible(caps, args[1])
    elif command == "coverage":
        ct = _load_cognitive_types(base)
        cmd_coverage(caps, ct)
    elif command == "safety":
        cmd_safety(caps)
    elif command == "chain" and len(args) >= 3:
        cmd_chain(caps, args[1], args[2])
    else:
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
