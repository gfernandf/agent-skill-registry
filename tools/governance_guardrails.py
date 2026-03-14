#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
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


def _as_str_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _parse_channels(raw: str | None) -> set[str]:
    if not raw:
        return set()
    allowed = {"experimental", "community", "official"}
    parsed = {
        item.strip().lower()
        for item in raw.split(",")
        if item.strip()
    }
    invalid = sorted(parsed - allowed)
    if invalid:
        raise ValueError(
            "invalid channel(s): "
            + ", ".join(invalid)
            + ". Allowed: experimental, community, official"
        )
    return parsed


def _get_skill_meta_issues(skill: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    metadata = skill.get("metadata")

    if not isinstance(metadata, dict):
        return ["missing_metadata"]

    use_cases = metadata.get("use_cases")
    examples = metadata.get("examples")
    tags = metadata.get("tags")

    if not isinstance(use_cases, list) or len(use_cases) == 0:
        issues.append("missing_use_cases")
    if not isinstance(examples, list) or len(examples) == 0:
        issues.append("missing_examples")
    if not isinstance(tags, list) or len(tags) == 0:
        issues.append("missing_tags")

    return issues


def build_guardrails_report(
    *,
    base: Path,
    overlap_threshold: float,
    min_shared_capabilities: int,
) -> dict[str, Any]:
    skills_path = base / "catalog" / "skills.json"
    capabilities_path = base / "catalog" / "capabilities.json"

    if not skills_path.exists() or not capabilities_path.exists():
        raise FileNotFoundError(
            "Missing catalog files. Run tools/generate_catalog.py first."
        )

    skills_raw = _load_json(skills_path)
    capabilities_raw = _load_json(capabilities_path)

    if not isinstance(skills_raw, list):
        raise ValueError("catalog/skills.json must contain a list.")
    if not isinstance(capabilities_raw, list):
        raise ValueError("catalog/capabilities.json must contain a list.")

    skills = [s for s in skills_raw if isinstance(s, dict) and isinstance(s.get("id"), str)]
    capability_ids = {
        c.get("id")
        for c in capabilities_raw
        if isinstance(c, dict) and isinstance(c.get("id"), str)
    }

    overlaps: list[dict[str, Any]] = []
    skills_with_issues: list[dict[str, Any]] = []

    for skill in skills:
        issues = _get_skill_meta_issues(skill)
        if issues:
            skills_with_issues.append(
                {
                    "skill_id": skill["id"],
                    "channel": skill.get("channel"),
                    "issues": issues,
                }
            )

    for i in range(len(skills)):
        left = skills[i]
        left_caps = _as_str_set(left.get("uses_capabilities"))
        left_outputs = set(left.get("outputs", {}).keys()) if isinstance(left.get("outputs"), dict) else set()

        for j in range(i + 1, len(skills)):
            right = skills[j]
            right_caps = _as_str_set(right.get("uses_capabilities"))
            right_outputs = set(right.get("outputs", {}).keys()) if isinstance(right.get("outputs"), dict) else set()

            shared_caps = left_caps & right_caps
            if len(shared_caps) < min_shared_capabilities:
                continue

            cap_overlap = _jaccard(left_caps, right_caps)
            output_overlap = _jaccard(left_outputs, right_outputs)
            combined = (0.75 * cap_overlap) + (0.25 * output_overlap)

            if combined < overlap_threshold:
                continue

            overlaps.append(
                {
                    "left_skill_id": left["id"],
                    "right_skill_id": right["id"],
                    "left_channel": left.get("channel"),
                    "right_channel": right.get("channel"),
                    "shared_capabilities": sorted(shared_caps),
                    "capability_jaccard": round(cap_overlap, 4),
                    "output_jaccard": round(output_overlap, 4),
                    "combined_score": round(combined, 4),
                    "risk": "high" if combined >= 0.9 else "medium",
                    "recommendation": "consider-merge-or-profile-variants",
                }
            )

    overlaps.sort(key=lambda x: (-x["combined_score"], x["left_skill_id"], x["right_skill_id"]))
    skills_with_issues.sort(key=lambda x: x["skill_id"])

    unknown_cap_refs: dict[str, list[str]] = {}
    for skill in skills:
        skill_id = skill["id"]
        cap_refs = _as_str_set(skill.get("uses_capabilities"))
        missing = sorted([cap for cap in cap_refs if cap not in capability_ids])
        if missing:
            unknown_cap_refs[skill_id] = missing

    report = {
        "summary": {
            "skills_total": len(skills),
            "skills_with_metadata_issues": len(skills_with_issues),
            "overlap_alerts": len(overlaps),
            "unknown_capability_references": len(unknown_cap_refs),
            "overlap_threshold": overlap_threshold,
            "min_shared_capabilities": min_shared_capabilities,
        },
        "skills_with_metadata_issues": skills_with_issues,
        "overlap_alerts": overlaps,
        "unknown_capability_references": unknown_cap_refs,
        "policy_hints": {
            "canonical_first": "Prefer one canonical skill per job-to-be-done; model variants with inputs/profiles.",
            "new_skill_gate": "Require explicit differentiation from existing skills with similar capability graph.",
            "sunset": "If overlap remains unresolved and usage is low, deprecate duplicate skill IDs.",
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(prog="governance_guardrails")
    parser.add_argument(
        "--base",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current working directory).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Output report file (default: catalog/governance_guardrails.json).",
    )
    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=0.8,
        help="Combined overlap threshold [0..1] to flag skill pairs.",
    )
    parser.add_argument(
        "--min-shared-capabilities",
        type=int,
        default=2,
        help="Minimum shared capabilities to consider a pair for overlap analysis.",
    )
    parser.add_argument(
        "--fail-on-overlap",
        action="store_true",
        help="Exit with code 1 when overlap alerts exist.",
    )
    parser.add_argument(
        "--fail-on-metadata-channels",
        default="",
        help=(
            "Comma-separated channels that should fail when metadata issues are detected. "
            "Example: community,official"
        ),
    )
    parser.add_argument(
        "--fail-on-high-risk-overlap-channels",
        default="",
        help=(
            "Comma-separated channels that should fail when high-risk overlaps are detected. "
            "Example: community,official"
        ),
    )
    args = parser.parse_args()

    base = args.base.resolve()
    report_path = args.report.resolve() if args.report is not None else (base / "catalog" / "governance_guardrails.json")

    if args.overlap_threshold < 0.0 or args.overlap_threshold > 1.0:
        print("GUARDRAILS FAILED: --overlap-threshold must be between 0 and 1.")
        return 1

    if args.min_shared_capabilities < 1:
        print("GUARDRAILS FAILED: --min-shared-capabilities must be >= 1.")
        return 1

    try:
        fail_metadata_channels = _parse_channels(args.fail_on_metadata_channels)
        fail_overlap_channels = _parse_channels(args.fail_on_high_risk_overlap_channels)
    except ValueError as e:
        print(f"GUARDRAILS FAILED: {e}")
        return 1

    try:
        report = build_guardrails_report(
            base=base,
            overlap_threshold=args.overlap_threshold,
            min_shared_capabilities=args.min_shared_capabilities,
        )
    except Exception as e:
        print(f"GUARDRAILS FAILED: {e}")
        return 1

    _write_json(report_path, report)

    summary = report.get("summary", {})
    overlaps = int(summary.get("overlap_alerts", 0) or 0)
    metadata_issues = int(summary.get("skills_with_metadata_issues", 0) or 0)

    print("GOVERNANCE GUARDRAILS GENERATED")
    print(f"Skills analyzed: {summary.get('skills_total', 0)}")
    print(f"Metadata issues: {metadata_issues}")
    print(f"Overlap alerts: {overlaps}")
    print(f"Written: {report_path.as_posix()}")

    if args.fail_on_overlap and overlaps > 0:
        print("GUARDRAILS FAILED: overlap alerts detected.")
        return 1

    if fail_metadata_channels:
        metadata_blockers = [
            item
            for item in report.get("skills_with_metadata_issues", [])
            if isinstance(item, dict) and item.get("channel") in fail_metadata_channels
        ]
        if metadata_blockers:
            print(
                "GUARDRAILS FAILED: metadata issues found in blocked channels "
                + ", ".join(sorted(fail_metadata_channels))
            )
            print(f"Blocked metadata issue count: {len(metadata_blockers)}")
            return 1

    if fail_overlap_channels:
        overlap_blockers = [
            item
            for item in report.get("overlap_alerts", [])
            if isinstance(item, dict)
            and item.get("risk") == "high"
            and (
                item.get("left_channel") in fail_overlap_channels
                or item.get("right_channel") in fail_overlap_channels
            )
        ]
        if overlap_blockers:
            print(
                "GUARDRAILS FAILED: high-risk overlap alerts found in blocked channels "
                + ", ".join(sorted(fail_overlap_channels))
            )
            print(f"Blocked overlap issue count: {len(overlap_blockers)}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())