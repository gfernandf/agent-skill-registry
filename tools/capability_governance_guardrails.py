#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.lower().strip().split())


def _parse_capability_id(capability_id: str) -> tuple[str, str | None, str]:
    parts = capability_id.split(".")
    if len(parts) == 2:
        return parts[0], None, parts[1]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return parts[0], None, parts[-1]


def build_report(base: Path) -> dict[str, Any]:
    capabilities_path = base / "catalog" / "capabilities.json"
    vocab_path = base / "vocabulary" / "vocabulary.json"

    if not capabilities_path.exists():
        raise FileNotFoundError("Missing catalog/capabilities.json. Run tools/generate_catalog.py first.")
    if not vocab_path.exists():
        raise FileNotFoundError("Missing vocabulary/vocabulary.json.")

    raw_caps = _load_json(capabilities_path)
    vocab = _load_json(vocab_path)

    if not isinstance(raw_caps, list):
        raise ValueError("catalog/capabilities.json must contain a list.")
    if not isinstance(vocab, dict):
        raise ValueError("vocabulary/vocabulary.json must contain an object.")

    caps = [item for item in raw_caps if isinstance(item, dict) and isinstance(item.get("id"), str)]
    known_domains = set((vocab.get("domains", {}) or {}).keys())

    used_domains: set[str] = set()
    family_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
    description_index: dict[str, list[str]] = {}
    metadata_issues: list[dict[str, Any]] = []

    for cap in caps:
        capability_id = cap["id"]
        domain, noun, verb = _parse_capability_id(capability_id)
        used_domains.add(domain)

        family_map.setdefault((domain, verb), []).append(
            {
                "id": capability_id,
                "noun": noun,
                "metadata": cap.get("metadata"),
            }
        )

        norm_desc = _normalize_text(cap.get("description"))
        if norm_desc:
            description_index.setdefault(norm_desc, []).append(capability_id)

        metadata = cap.get("metadata")
        issues: list[str] = []
        if not isinstance(metadata, dict):
            issues.append("missing_metadata")
        else:
            if not isinstance(metadata.get("tags"), list) or len(metadata.get("tags") or []) == 0:
                issues.append("missing_tags")
            if not isinstance(metadata.get("examples"), list) or len(metadata.get("examples") or []) == 0:
                issues.append("missing_examples")
        if issues:
            metadata_issues.append({"capability_id": capability_id, "issues": issues})

    family_alerts: list[dict[str, Any]] = []
    for (domain, verb), members in sorted(family_map.items()):
        if len(members) <= 1:
            continue
        ids = sorted(member["id"] for member in members)
        nouns = sorted({member["noun"] for member in members if member["noun"] is not None})
        family_alerts.append(
            {
                "domain": domain,
                "verb": verb,
                "capability_ids": ids,
                "noun_variants": nouns,
                "recommendation": "review-for-canonical-operation",
            }
        )

    duplicate_descriptions: list[dict[str, Any]] = []
    for desc, ids in sorted(description_index.items(), key=lambda x: (len(x[1]) * -1, x[0])):
        if len(ids) <= 1:
            continue
        duplicate_descriptions.append(
            {
                "description": desc,
                "capability_ids": sorted(ids),
                "recommendation": "review-description-and-semantic-uniqueness",
            }
        )

    uncovered_domains = sorted(known_domains - used_domains)

    return {
        "summary": {
            "capabilities_total": len(caps),
            "covered_domains": len(used_domains),
            "uncovered_domains": len(uncovered_domains),
            "semantic_family_alerts": len(family_alerts),
            "duplicate_description_alerts": len(duplicate_descriptions),
            "metadata_issues": len(metadata_issues),
        },
        "uncovered_domains": uncovered_domains,
        "semantic_family_alerts": family_alerts,
        "duplicate_description_alerts": duplicate_descriptions,
        "metadata_issues": metadata_issues,
        "policy_hints": {
            "admission": "New capability IDs require differentiation from existing domain/verb families.",
            "compatibility": "Prefer additive evolution; avoid breaking contract changes in place.",
            "sunset": "Deprecated capabilities must include replacement and lifecycle dates.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="capability_governance_guardrails")
    parser.add_argument("--base", type=Path, default=Path.cwd())
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Output report path (default: catalog/capability_governance_guardrails.json).",
    )
    args = parser.parse_args()

    base = args.base.resolve()
    report_path = args.report.resolve() if args.report else (base / "catalog" / "capability_governance_guardrails.json")

    try:
        report = build_report(base)
    except Exception as e:
        print(f"CAPABILITY GUARDRAILS FAILED: {e}")
        return 1

    _write_json(report_path, report)

    summary = report.get("summary", {})
    print("CAPABILITY GOVERNANCE GUARDRAILS GENERATED")
    print(f"Capabilities analyzed: {summary.get('capabilities_total', 0)}")
    print(f"Uncovered domains: {summary.get('uncovered_domains', 0)}")
    print(f"Family alerts: {summary.get('semantic_family_alerts', 0)}")
    print(f"Metadata issues: {summary.get('metadata_issues', 0)}")
    print(f"Written: {report_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
