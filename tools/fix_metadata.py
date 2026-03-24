#!/usr/bin/env python3
"""
One-shot maintenance script: add missing tags, examples, and status
to all 122 capability YAMLs.

Fixes:
1. 31 capabilities missing `metadata.tags`
2. 84 capabilities missing `metadata.examples`
3. 35 capabilities missing `metadata.status`

Run from agent-skill-registry root:
    python tools/fix_metadata.py
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPS_DIR = ROOT / "capabilities"

# ── Tags mapping (domain → default tags for capabilities without tags) ──

DOMAIN_TAGS: dict[str, list[str]] = {
    "agent":       ["agent", "orchestration"],
    "analysis":    ["analysis"],
    "audio":       ["audio", "speech"],
    "code":        ["code", "developer-tools"],
    "data":        ["data", "processing"],
    "decision":    ["decision", "reasoning"],
    "doc":         ["document", "processing"],
    "email":       ["email", "messaging"],
    "eval":        ["evaluation", "scoring"],
    "fs":          ["filesystem", "io"],
    "identity":    ["identity", "iam"],
    "image":       ["image", "vision"],
    "integration": ["integration", "connector"],
    "memory":      ["memory", "storage"],
    "message":     ["messaging", "notification"],
    "model":       ["model", "llm"],
    "ops":         ["operations", "monitoring"],
    "pdf":         ["pdf", "document"],
    "policy":      ["policy", "governance"],
    "provenance":  ["provenance", "citation"],
    "research":    ["research", "retrieval"],
    "security":    ["security"],
    "table":       ["table", "data"],
    "task":        ["task", "workflow"],
    "text":        ["text", "nlp"],
    "video":       ["video", "media"],
    "web":         ["web", "http"],
}

# Extra verb-specific tags
VERB_TAGS: dict[str, list[str]] = {
    "transcribe":  ["transcription", "speech-to-text"],
    "synthesize":  ["synthesis", "text-to-speech"],
    "extract":     ["extraction"],
    "classify":    ["classification"],
    "generate":    ["generation"],
    "embed":       ["embedding", "vector"],
    "summarize":   ["summarization"],
    "translate":   ["translation"],
    "detect":      ["detection"],
    "redact":      ["redaction", "privacy"],
    "filter":      ["filtering"],
    "sort":        ["sorting"],
    "aggregate":   ["aggregation"],
    "deduplicate": ["deduplication"],
    "validate":    ["validation"],
    "parse":       ["parsing"],
    "chunk":       ["chunking"],
    "execute":     ["execution", "sandbox"],
    "format":      ["formatting"],
    "search":      ["search"],
    "fetch":       ["fetch", "retrieval"],
    "read":        ["read", "input"],
    "write":       ["write", "output"],
    "list":        ["listing"],
    "send":        ["sending"],
    "store":       ["persistence"],
    "retrieve":    ["retrieval"],
    "route":       ["routing"],
    "delegate":    ["delegation"],
    "create":      ["creation"],
    "update":      ["mutation"],
    "delete":      ["deletion"],
    "close":       ["lifecycle"],
    "get":         ["lookup"],
    "assign":      ["assignment"],
    "approve":     ["approval"],
    "reject":      ["approval"],
    "verify":      ["verification"],
    "gate":        ["access-control"],
    "score":       ["scoring"],
    "monitor":     ["monitoring"],
    "acknowledge": ["event-handling"],
    "sync":        ["synchronization"],
    "reconcile":   ["reconciliation"],
    "compare":     ["comparison"],
    "upsert":      ["upsert"],
    "transform":   ["transformation"],
    "schedule":    ["scheduling"],
    "transition":  ["state-machine"],
    "justify":     ["explainability"],
    "merge":       ["merging"],
    "template":    ["templating"],
}


# ── Examples (one per capability, using the same data as TEST_DATA) ──

EXAMPLES: dict[str, dict[str, Any]] = {
    "audio.speech.transcribe": {
        "summary": "Transcribe a short speech clip",
        "inputs": {"audio": "(binary audio data)"},
        "outputs": {"text": "Hello, welcome to the meeting."},
    },
    "code.diff.extract": {
        "summary": "Extract diff between two code versions",
        "inputs": {"code_a": "x = 5", "code_b": "x = 10"},
        "outputs": {"changes": [{"type": "modified", "before": "x = 5", "after": "x = 10"}]},
    },
    "code.snippet.execute": {
        "summary": "Execute a Python expression",
        "inputs": {"code": "print(2 + 3)", "language": "python"},
        "outputs": {"stdout": "5\n", "exit_code": 0},
    },
    "code.source.format": {
        "summary": "Format Python code",
        "inputs": {"code": "def foo( x,y ):\n  return x+y", "language": "python"},
        "outputs": {"code": "def foo(x, y):\n    return x + y\n"},
    },
    "data.json.parse": {
        "summary": "Parse a JSON string",
        "inputs": {"text": "{\"name\": \"John\", \"age\": 30}"},
        "outputs": {"data": {"name": "John", "age": 30}},
    },
    "data.record.deduplicate": {
        "summary": "Remove duplicate records by key",
        "inputs": {"records": [{"id": 1, "name": "Alice"}, {"id": 1, "name": "Alice"}], "key_fields": ["id"]},
        "outputs": {"records": [{"id": 1, "name": "Alice"}]},
    },
    "data.schema.validate": {
        "summary": "Validate data against a JSON schema",
        "inputs": {"data": {"name": "John"}, "schema": {"type": "object", "required": ["name"]}},
        "outputs": {"valid": True},
    },
    "decision.option.justify": {
        "summary": "Justify a recommended option",
        "inputs": {"scored_options": [{"id": "a", "score": 0.9}], "goal": "Choose deployment strategy"},
        "outputs": {"justification": "Option A selected due to highest score.", "recommended": "a"},
    },
    "doc.content.chunk": {
        "summary": "Split a document into chunks",
        "inputs": {"text": "A long document...", "chunk_size": 500},
        "outputs": {"chunks": ["A long doc...", "ument continued..."]},
    },
    "email.inbox.read": {
        "summary": "Read messages from an inbox",
        "inputs": {"mailbox": "inbox"},
        "outputs": {"messages": [{"from": "alice@example.com", "subject": "Meeting notes"}]},
    },
    "email.message.send": {
        "summary": "Send an email message",
        "inputs": {"to": "bob@example.com", "subject": "Follow-up", "body": "Please review the proposal."},
        "outputs": {"sent": True, "message_id": "msg-001"},
    },
    "fs.file.read": {
        "summary": "Read a text file",
        "inputs": {"path": "data/report.txt", "mode": "text"},
        "outputs": {"content": "Report contents here...", "size": 1234},
    },
    "identity.assignee.identify": {
        "summary": "Find the best assignee for a task",
        "inputs": {"task": {"type": "code_review", "required_skills": ["python"]}},
        "outputs": {"assignee": {"id": "alice", "match_score": 0.7}},
    },
    "identity.decision.justify": {
        "summary": "Justify an identity-related decision",
        "inputs": {"decision": "granted", "subject": {"id": "alice"}, "policies": []},
        "outputs": {"justification": "Access granted based on role.", "confidence": 0.9},
    },
    "identity.permission.gate": {
        "summary": "Check whether a principal is allowed an action",
        "inputs": {"principal_id": "alice", "permission": "resource:read"},
        "outputs": {"allowed": True, "reason": "Permission granted via admin role."},
    },
    "identity.permission.get": {
        "summary": "Retrieve a specific permission definition",
        "inputs": {"permission_id": "resource:read"},
        "outputs": {"permission": {"id": "resource:read", "description": "Read resources"}, "found": True},
    },
    "identity.permission.list": {
        "summary": "List permissions for a principal",
        "inputs": {"principal_id": "alice"},
        "outputs": {"permissions": [{"id": "resource:read"}], "total": 1},
    },
    "identity.permission.verify": {
        "summary": "Verify a principal holds a permission",
        "inputs": {"principal_id": "alice", "permission": "resource:read"},
        "outputs": {"verified": True, "source": "role-inherited"},
    },
    "identity.risk.score": {
        "summary": "Score risk for an identity action",
        "inputs": {"principal_id": "alice", "signals": {"login_failures": 5}},
        "outputs": {"risk_score": 0.3, "factors": ["high_login_failures"], "safe": True},
    },
    "identity.role.assign": {
        "summary": "Assign a role to a principal",
        "inputs": {"principal_id": "alice", "role_id": "editor"},
        "outputs": {"assigned": True, "effective_permissions": ["resource:read", "resource:write"]},
    },
    "identity.role.get": {
        "summary": "Retrieve a role definition",
        "inputs": {"role_id": "admin"},
        "outputs": {"role": {"id": "admin", "name": "Administrator"}, "found": True},
    },
    "identity.role.list": {
        "summary": "List available roles",
        "inputs": {"scope": "all"},
        "outputs": {"roles": [{"id": "admin"}, {"id": "editor"}], "total": 2},
    },
    "image.caption.generate": {
        "summary": "Generate a caption for an image",
        "inputs": {"image": "(binary image data)"},
        "outputs": {"caption": "A sunset over the mountains."},
    },
    "image.content.classify": {
        "summary": "Classify image content by labels",
        "inputs": {"image": "(binary image data)", "labels": ["cat", "dog", "bird"]},
        "outputs": {"label": "cat", "confidence": 0.92},
    },
    "integration.connector.get": {
        "summary": "Retrieve connector metadata",
        "inputs": {"connector_id": "crm-rest"},
        "outputs": {"connector": {"id": "crm-rest", "type": "rest", "status": "active"}, "found": True},
    },
    "integration.connector.list": {
        "summary": "List available connectors",
        "inputs": {"status_filter": "active"},
        "outputs": {"connectors": [{"id": "crm-rest", "status": "active"}], "total": 1},
    },
    "integration.connector.sync": {
        "summary": "Trigger connector synchronization",
        "inputs": {"connector_id": "crm-rest"},
        "outputs": {"synced": True, "records_processed": 42},
    },
    "integration.event.acknowledge": {
        "summary": "Acknowledge an integration event",
        "inputs": {"event_id": "evt-001", "handler": "sync-worker"},
        "outputs": {"acknowledged": True},
    },
    "integration.mapping.transform": {
        "summary": "Apply field mapping to a record",
        "inputs": {"record": {"first_name": "Alice"}, "mapping": {"rename": {"first_name": "name"}}},
        "outputs": {"record": {"name": "Alice"}},
    },
    "integration.mapping.validate": {
        "summary": "Validate a field mapping definition",
        "inputs": {"mapping": {"rename": {"first_name": "name"}}, "source_schema": {"fields": ["first_name"]}},
        "outputs": {"valid": True, "warnings": []},
    },
    "integration.record.compare": {
        "summary": "Compare records across systems",
        "inputs": {"record_a": {"id": "1", "name": "Alice"}, "record_b": {"id": "1", "name": "Alicia"}, "key_fields": ["id"]},
        "outputs": {"match": True, "discrepancies": [{"field": "name", "a": "Alice", "b": "Alicia"}]},
    },
    "integration.record.create": {
        "summary": "Create a record in an external system",
        "inputs": {"connector_id": "crm-rest", "record": {"name": "New Contact"}},
        "outputs": {"record_id": "rec-001", "created": True},
    },
    "integration.record.delete": {
        "summary": "Delete a record in an external system",
        "inputs": {"connector_id": "crm-rest", "record_id": "rec-001"},
        "outputs": {"deleted": True},
    },
    "integration.record.reconcile": {
        "summary": "Reconcile records between two systems",
        "inputs": {"records_a": [{"id": "1"}], "records_b": [{"id": "2"}], "key_field": "id"},
        "outputs": {"matched": [], "only_a": [{"id": "1"}], "only_b": [{"id": "2"}]},
    },
    "integration.record.update": {
        "summary": "Update a record in an external system",
        "inputs": {"connector_id": "crm-rest", "record_id": "rec-001", "fields": {"email": "new@example.com"}},
        "outputs": {"updated": True},
    },
    "integration.record.upsert": {
        "summary": "Create-or-update a record in an external system",
        "inputs": {"connector_id": "crm-rest", "record": {"id": "rec-001", "name": "Updated"}, "key_fields": ["id"]},
        "outputs": {"upserted": True, "action": "updated"},
    },
    "memory.entry.retrieve": {
        "summary": "Retrieve a stored memory entry",
        "inputs": {"key": "user_preference"},
        "outputs": {"value": "dark_mode", "found": True},
    },
    "memory.entry.store": {
        "summary": "Store a key-value memory entry",
        "inputs": {"key": "user_preference", "value": "dark_mode"},
        "outputs": {"stored": True},
    },
    "memory.record.store": {
        "summary": "Store a structured record in a namespace",
        "inputs": {"namespace": "session", "record": {"id": "r1", "content": "Context data"}},
        "outputs": {"stored": True, "record_id": "r1"},
    },
    "memory.vector.search": {
        "summary": "Search memory by semantic similarity",
        "inputs": {"query": "deployment strategy", "top_k": 3},
        "outputs": {"results": [{"id": "r1", "score": 0.89, "content": "Use blue-green deployment."}]},
    },
    "message.notification.send": {
        "summary": "Send a notification message",
        "inputs": {"message": "Build succeeded", "recipient": "ops-channel"},
        "outputs": {"sent": True, "message_id": "notif-001"},
    },
    "message.priority.classify": {
        "summary": "Classify message priority",
        "inputs": {"message": "URGENT: production outage on API gateway"},
        "outputs": {"priority": "critical", "confidence": 0.95},
    },
    "ops.budget.estimate": {
        "summary": "Estimate cost for a plan",
        "inputs": {"plan": {"steps": [{"id": "s1"}, {"id": "s2"}]}, "limits": {"max_cost": 1.0}},
        "outputs": {"estimated_cost": 0.35, "within_budget": True},
    },
    "ops.event.acknowledge": {
        "summary": "Acknowledge an operational event",
        "inputs": {"event_id": "evt-001", "handler": "on-call-bot"},
        "outputs": {"acknowledged": True},
    },
    "ops.event.monitor": {
        "summary": "Monitor operational events against thresholds",
        "inputs": {"events": [{"type": "error", "severity": "critical"}], "thresholds": {"max_error_count": 0}},
        "outputs": {"status": "alert", "alerts": [{"rule": "max_error_count", "actual": 1}]},
    },
    "pdf.document.read": {
        "summary": "Read text from a PDF document",
        "inputs": {"path": "reports/q3.pdf"},
        "outputs": {"text": "Q3 revenue increased...", "metadata": {"pages": 5}},
    },
    "policy.constraint.validate": {
        "summary": "Validate payload against policy constraints",
        "inputs": {"payload": {"title": "Report"}, "constraint": {"required_keys": ["title"]}},
        "outputs": {"valid": True, "violations": []},
    },
    "policy.constraint.gate": {
        "summary": "Gate an action based on policy rules",
        "inputs": {"payload": {"title": "Report"}, "gate": {"rules": {"required_keys": ["title"]}, "action": "block"}},
        "outputs": {"allowed": True},
    },
    "policy.decision.justify": {
        "summary": "Justify a policy decision",
        "inputs": {"decision": "approved", "rules": [{"id": "R1", "outcome": "approved"}]},
        "outputs": {"justification": "Approved per rule R1.", "applicable_rules": ["R1"]},
    },
    "policy.risk.classify": {
        "summary": "Classify risk level of an action",
        "inputs": {"action": {"type": "deploy", "destructive": False, "external": True}},
        "outputs": {"risk_level": "medium", "factors": ["external"]},
    },
    "policy.risk.score": {
        "summary": "Compute a numeric risk score for an action",
        "inputs": {"action": {"type": "data_export", "involves_pii": True}},
        "outputs": {"risk_score": 0.7, "breakdown": {"pii": 0.3, "external": 0.2}},
    },
    "provenance.citation.generate": {
        "summary": "Generate a citation from a source",
        "inputs": {"source": {"url": "https://example.com/article", "title": "Example"}, "excerpt": "Key fact"},
        "outputs": {"citation": "Example. Retrieved from https://example.com/article"},
    },
    "provenance.claim.verify": {
        "summary": "Verify a claim against sources",
        "inputs": {"claim": "Revenue grew 15%", "sources": [{"text": "Revenue grew 15% in Q3."}]},
        "outputs": {"supported": True, "confidence": 0.95},
    },
    "research.source.retrieve": {
        "summary": "Retrieve full content from source references",
        "inputs": {"items": [{"content": "ML overview", "source_ref": {"url": "https://example.com/ml"}}]},
        "outputs": {"items": [{"content": "Machine learning is...", "resolved": True}]},
    },
    "table.row.filter": {
        "summary": "Filter table rows by condition",
        "inputs": {"table": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}], "condition": {"age": {"$gt": 26}}},
        "outputs": {"table": [{"name": "Bob", "age": 30}]},
    },
    "task.approval.approve": {
        "summary": "Approve an approval request",
        "inputs": {"approval_id": "apr-001", "approver": "manager-1"},
        "outputs": {"approved": True},
    },
    "task.approval.reject": {
        "summary": "Reject an approval request",
        "inputs": {"approval_id": "apr-002", "rejector": "manager-2", "reason": "Missing justification"},
        "outputs": {"rejected": True},
    },
    "task.assignee.assign": {
        "summary": "Assign a task to a user",
        "inputs": {"task_id": "CASE-1", "assignee_id": "alice"},
        "outputs": {"assigned": True},
    },
    "task.case.close": {
        "summary": "Close a case with a resolution",
        "inputs": {"case_id": "CASE-1", "resolution": "Fixed in v2.1"},
        "outputs": {"closed": True},
    },
    "task.case.create": {
        "summary": "Create a new case",
        "inputs": {"title": "Bug in login page", "priority": "high"},
        "outputs": {"case_id": "CASE-1", "created": True},
    },
    "task.case.get": {
        "summary": "Retrieve a specific case",
        "inputs": {"case_id": "CASE-1"},
        "outputs": {"case": {"id": "CASE-1", "title": "Bug in login page", "state": "open"}, "found": True},
    },
    "task.case.list": {
        "summary": "List cases filtered by status",
        "inputs": {"status_filter": "open"},
        "outputs": {"cases": [{"id": "CASE-1", "state": "open"}], "total": 1},
    },
    "task.case.search": {
        "summary": "Search cases by keyword",
        "inputs": {"query": "login"},
        "outputs": {"results": [{"id": "CASE-1", "title": "Bug in login page"}], "total": 1},
    },
    "task.case.update": {
        "summary": "Update a case's fields",
        "inputs": {"case_id": "CASE-1", "fields": {"priority": "critical"}},
        "outputs": {"updated": True},
    },
    "task.event.acknowledge": {
        "summary": "Acknowledge a task event",
        "inputs": {"event_id": "task-evt-001", "handler": "escalation-bot"},
        "outputs": {"acknowledged": True},
    },
    "task.incident.create": {
        "summary": "Create a new incident",
        "inputs": {"title": "API 503 errors", "severity": "high", "affected_system": "api-gateway"},
        "outputs": {"incident_id": "INC-1", "created": True},
    },
    "task.milestone.schedule": {
        "summary": "Schedule a project milestone",
        "inputs": {"milestone_name": "Beta Release", "target_date": "2026-03-15", "deliverables": ["feature-x"]},
        "outputs": {"milestone_id": "MS-1", "scheduled": True},
    },
    "task.priority.classify": {
        "summary": "Classify priority of a task",
        "inputs": {"task": {"title": "DB running out of disk", "type": "incident"}, "context": {"environment": "production"}},
        "outputs": {"priority": "critical", "confidence": 0.9},
    },
    "task.sla.monitor": {
        "summary": "Monitor SLA compliance",
        "inputs": {"tasks": [{"id": "CASE-1", "priority": "high", "state": "open"}], "sla_rules": [{"priority": "high", "max_resolution_hours": 4}]},
        "outputs": {"compliant": [], "breached": ["CASE-1"], "at_risk": []},
    },
    "task.state.transition": {
        "summary": "Transition a task to a new state",
        "inputs": {"task_id": "CASE-1", "target_state": "in_progress"},
        "outputs": {"transitioned": True, "previous_state": "open", "current_state": "in_progress"},
    },
    "text.content.classify": {
        "summary": "Classify text into categories",
        "inputs": {"text": "I love this product!", "labels": ["positive", "negative", "neutral"]},
        "outputs": {"label": "positive", "confidence": 0.95},
    },
    "text.content.embed": {
        "summary": "Generate a vector embedding for text",
        "inputs": {"text": "This is a test sentence."},
        "outputs": {"vector": [0.01, -0.03, 0.12]},
    },
    "text.content.extract": {
        "summary": "Extract clean text from HTML",
        "inputs": {"text": "<html><body><h1>Title</h1><p>Content.</p></body></html>"},
        "outputs": {"text": "Title\nContent."},
    },
    "text.content.generate": {
        "summary": "Generate text from an instruction",
        "inputs": {"instruction": "Write a one-sentence description of Python."},
        "outputs": {"text": "Python is a versatile, high-level programming language."},
    },
    "text.content.merge": {
        "summary": "Merge text items into a single block",
        "inputs": {"items": ["Hello", "World"]},
        "outputs": {"text": "Hello\n\nWorld"},
    },
    "text.content.summarize": {
        "summary": "Summarize a passage of text",
        "inputs": {"text": "Machine learning is a subset of AI that enables systems to learn from data..."},
        "outputs": {"summary": "ML lets systems learn from data without explicit programming."},
    },
    "text.content.template": {
        "summary": "Render a template with variables",
        "inputs": {"template": "Hello {{name}}, welcome to {{place}}!", "variables": {"name": "Alice", "place": "HQ"}},
        "outputs": {"text": "Hello Alice, welcome to HQ!"},
    },
    "text.content.transform": {
        "summary": "Transform text style or tone",
        "inputs": {"text": "The system is operational.", "goal": "simplify for non-technical audience"},
        "outputs": {"text": "Everything is working normally."},
    },
    "text.content.translate": {
        "summary": "Translate text to another language",
        "inputs": {"text": "Hello world", "target_language": "es"},
        "outputs": {"text": "Hola mundo"},
    },
    "text.entity.extract": {
        "summary": "Extract named entities from text",
        "inputs": {"text": "John Smith works at Google in Mountain View."},
        "outputs": {"entities": [{"text": "John Smith", "type": "PERSON"}, {"text": "Google", "type": "ORG"}]},
    },
    "text.keyword.extract": {
        "summary": "Extract keywords from text",
        "inputs": {"text": "Python is great for machine learning and data science."},
        "outputs": {"keywords": ["Python", "machine learning", "data science"]},
    },
    "text.language.detect": {
        "summary": "Detect the language of a text",
        "inputs": {"text": "Bonjour le monde"},
        "outputs": {"language": "fr", "confidence": 0.98},
    },
    "text.response.extract": {
        "summary": "Extract an answer from context",
        "inputs": {"question": "What is Python?", "context": "Python is a high-level programming language."},
        "outputs": {"text": "A high-level programming language."},
    },
    "video.frame.extract": {
        "summary": "Extract frames from a video",
        "inputs": {"video": "(binary video data)"},
        "outputs": {"frames": ["(frame 1 data)", "(frame 2 data)"]},
    },
}


def _get_tags(cap_id: str) -> list[str]:
    """Derive tags from capability id (domain + verb)."""
    parts = cap_id.split(".")
    domain = parts[0]
    verb = parts[-1]

    tags = list(DOMAIN_TAGS.get(domain, [domain]))
    if verb in VERB_TAGS:
        for vt in VERB_TAGS[verb]:
            if vt not in tags:
                tags.append(vt)
    return tags


def _add_yaml_block(text: str, cap_id: str, need_tags: bool, need_examples: bool, need_status: bool) -> str:
    """
    Append missing metadata fields to YAML text.
    Strategy: find the metadata: block and insert fields at the end of it.
    """
    lines = text.split("\n")
    result_lines = list(lines)

    # Find metadata block
    meta_line_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^metadata:\s*$", line):
            meta_line_idx = i
            break

    if meta_line_idx is None:
        # No metadata block — append one at end
        result_lines.append("")
        result_lines.append("metadata:")
        meta_line_idx = len(result_lines) - 1
        if need_status:
            result_lines.append("  status: experimental")
        if need_tags:
            tags = _get_tags(cap_id)
            result_lines.append(f"  tags: [{', '.join(tags)}]")
        if need_examples and cap_id in EXAMPLES:
            result_lines.extend(_format_examples(cap_id))
        return "\n".join(result_lines)

    # Find end of metadata block (next zero-indent line or end of file)
    meta_end = len(lines)
    for i in range(meta_line_idx + 1, len(lines)):
        stripped = lines[i]
        if stripped and not stripped[0].isspace() and not stripped.startswith("#"):
            meta_end = i
            break

    # Insert new fields before meta_end
    insert_lines = []
    if need_status:
        insert_lines.append("  status: experimental")
    if need_tags:
        tags = _get_tags(cap_id)
        insert_lines.append(f"  tags: [{', '.join(tags)}]")
    if need_examples and cap_id in EXAMPLES:
        insert_lines.extend(_format_examples(cap_id))

    for offset, line in enumerate(insert_lines):
        result_lines.insert(meta_end + offset, line)

    return "\n".join(result_lines)


def _format_examples(cap_id: str) -> list[str]:
    """Format an example block as indented YAML lines."""
    ex = EXAMPLES[cap_id]
    lines = ["  examples:"]
    lines.append(f"    - summary: \"{ex['summary']}\"")
    lines.append("      inputs:")
    for k, v in ex["inputs"].items():
        lines.append(f"        {k}: {_yaml_inline(v)}")
    lines.append("      outputs:")
    for k, v in ex["outputs"].items():
        lines.append(f"        {k}: {_yaml_inline(v)}")
    return lines


def _yaml_inline(val: Any) -> str:
    """Convert a value to inline YAML representation."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        # Quote strings that could be ambiguous
        if any(c in val for c in ":{}\n[]#&*!|>'\","):
            escaped = val.replace('"', '\\"')
            return f'"{escaped}"'
        return f'"{val}"'
    if isinstance(val, list):
        items = ", ".join(_yaml_inline(v) for v in val)
        return f"[{items}]"
    if isinstance(val, dict):
        items = ", ".join(f"{k}: {_yaml_inline(v)}" for k, v in val.items())
        return "{" + items + "}"
    return str(val)


def main() -> None:
    caps = sorted(CAPS_DIR.glob("*.yaml"))
    fixed_tags = 0
    fixed_examples = 0
    fixed_status = 0

    for path in caps:
        if path.name == "_index.yaml":
            continue

        with open(path, encoding="utf-8") as f:
            raw = f.read()

        data = yaml.safe_load(raw)
        if not data:
            continue

        cap_id = data.get("id", path.stem)
        meta = data.get("metadata") or {}

        need_tags = not meta.get("tags")
        need_examples = not meta.get("examples")
        need_status = not meta.get("status")

        if not need_tags and not need_examples and not need_status:
            continue

        updated = _add_yaml_block(raw, cap_id, need_tags, need_examples, need_status)

        if updated != raw:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)

            changes = []
            if need_tags:
                changes.append("tags")
                fixed_tags += 1
            if need_examples:
                changes.append("examples")
                fixed_examples += 1
            if need_status:
                changes.append("status")
                fixed_status += 1

            print(f"  {cap_id}: +{', +'.join(changes)}")

    print(f"\nDone. Fixed: {fixed_tags} tags, {fixed_examples} examples, {fixed_status} status")


if __name__ == "__main__":
    main()
