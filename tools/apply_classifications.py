#!/usr/bin/env python3
"""
One-time migration tool: adds canonical classification blocks to skill YAMLs.

Run from the registry root after reviewing the classification table:

    python tools/apply_classifications.py [--dry-run]

The script appends a `metadata.classification` block to each skill YAML that
does not already have one.  If a skill already has a `metadata:` block (e.g.
agent.trace), the classification block is inserted under it.  Files that
already contain `classification:` are skipped.

Remove this script once all skills have been classified.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical classification table
# ---------------------------------------------------------------------------
# Schema per metadata.classification in SKILL_FORMAT.md:
#   role:           procedure | utility | sidecar
#   invocation:     direct | attach | both
#   attach_targets: list[task|run|output|transcript|artifact]  (if invocation != direct)
#   effect_mode:    read_only | enrich | control_signal

CLASSIFICATIONS: dict[str, dict] = {
    "agent.plan-and-route": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "agent.plan-from-objective": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "agent.trace": {
        "role": "sidecar",
        "invocation": "attach",
        "attach_targets": ["run", "output", "transcript"],
        "effect_mode": "control_signal",
    },
    "audio.transcribe-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "code.diff-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "data.parse-and-validate": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "doc.chunk-and-embed": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "doc.chunk-text": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "email.read-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "image.caption-and-classify": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "memory.retrieve-summary": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "memory.store-embedding": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "memory.store-summary": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "pdf.chunk-and-embed": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "pdf.read-keyword-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "pdf.read-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "table.filter-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "text.classify-input": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "text.detect-language-and-classify": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "text.entity-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "text.extract-entities": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "text.extract-keywords": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "read_only",
    },
    "text.hello-world": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "text.keyword-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "text.language-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "text.simple-summarize": {
        "role": "utility",
        "invocation": "both",
        "attach_targets": ["output", "transcript"],
        "effect_mode": "enrich",
    },
    "text.translate-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "web.fetch-classify": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "web.fetch-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "web.page-chunk-and-embed": {
        "role": "utility",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
    "web.page-summary": {
        "role": "utility",
        "invocation": "attach",
        "attach_targets": ["output"],
        "effect_mode": "enrich",
    },
    "web.search-summary": {
        "role": "procedure",
        "invocation": "direct",
        "effect_mode": "enrich",
    },
}


# ---------------------------------------------------------------------------
# YAML block generator
# ---------------------------------------------------------------------------

def _build_classification_block(c: dict) -> str:
    """Build the indented YAML text for a classification block under metadata."""
    lines = ["  classification:"]
    lines.append(f"    role: {c['role']}")
    lines.append(f"    invocation: {c['invocation']}")
    if "attach_targets" in c:
        lines.append("    attach_targets:")
        for target in c["attach_targets"]:
            lines.append(f"      - {target}")
    lines.append(f"    effect_mode: {c['effect_mode']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------

def _extract_skill_id(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("id:"):
            return stripped.split(":", 1)[1].strip()
    return None


def apply(dry_run: bool) -> int:
    base = Path(__file__).resolve().parent.parent
    skills_dir = base / "skills"

    if not skills_dir.exists():
        print(f"ERROR: skills directory not found at {skills_dir}", file=sys.stderr)
        return 1

    updated = 0
    skipped_no_entry = 0
    skipped_already = 0
    errors = 0

    for skill_file in sorted(skills_dir.glob("*/*/*/skill.yaml")):
        rel = skill_file.relative_to(base)
        text = skill_file.read_text(encoding="utf-8")

        skill_id = _extract_skill_id(text)
        if skill_id is None:
            print(f"ERROR (no id found): {rel}", file=sys.stderr)
            errors += 1
            continue

        if skill_id not in CLASSIFICATIONS:
            print(f"SKIP  (no entry in table): {rel}")
            skipped_no_entry += 1
            continue

        if "classification:" in text:
            print(f"SKIP  (already classified): {rel}")
            skipped_already += 1
            continue

        c = CLASSIFICATIONS[skill_id]
        classification_block = _build_classification_block(c)
        stripped = text.rstrip()

        if "metadata:" in text:
            # Extend existing metadata block by appending classification as a child key.
            new_text = stripped + "\n" + classification_block + "\n"
        else:
            # No metadata block yet — add a full metadata section.
            new_text = stripped + "\nmetadata:\n" + classification_block + "\n"

        if dry_run:
            print(f"DRY   {rel}")
        else:
            skill_file.write_text(new_text, encoding="utf-8")
            print(f"WROTE {rel}")
        updated += 1

    action = "Would update" if dry_run else "Updated"
    print(
        f"\n{action} {updated} skill(s). "
        f"Skipped: {skipped_already} already classified, "
        f"{skipped_no_entry} without table entry."
    )
    if errors:
        print(f"Errors: {errors}", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply canonical classification blocks to all skill YAMLs."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be changed without writing any files.",
    )
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
