#!/usr/bin/env python3
"""One-shot script to add missing metadata (use_cases, examples, tags, classification) to skill YAMLs."""
from __future__ import annotations
import pathlib, yaml

SKILLS_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills"

# ── Tags by domain ──────────────────────────────────────────────────────────
DOMAIN_TAGS: dict[str, list[str]] = {
    "agent":       ["agent", "orchestration", "planning"],
    "analysis":    ["analysis", "reasoning", "evaluation"],
    "audio":       ["audio", "speech", "transcription"],
    "code":        ["code", "development", "engineering"],
    "data":        ["data", "parsing", "validation"],
    "decision":    ["decision", "evaluation", "strategy"],
    "doc":         ["document", "chunking", "processing"],
    "email":       ["email", "communication", "messaging"],
    "eval":        ["evaluation", "quality", "scoring"],
    "image":       ["image", "vision", "media"],
    "memory":      ["memory", "storage", "retrieval"],
    "pdf":         ["pdf", "document", "extraction"],
    "research":    ["research", "synthesis", "analysis"],
    "table":       ["table", "data", "filtering"],
    "task":        ["task", "planning", "workflow"],
    "text":        ["text", "nlp", "language"],
    "web":         ["web", "fetch", "scraping"],
}

# ── Verb-based extra tags ───────────────────────────────────────────────────
VERB_TAGS: dict[str, list[str]] = {
    "summary":     ["summarization"],
    "classify":    ["classification"],
    "embed":       ["embedding", "vector"],
    "chunk":       ["chunking", "segmentation"],
    "translate":   ["translation"],
    "extract":     ["extraction"],
    "compare":     ["comparison"],
    "validate":    ["validation"],
    "assess":      ["assessment"],
    "normalize":   ["normalization"],
    "synthesize":  ["synthesis"],
    "trace":       ["observability", "tracing"],
    "frame":       ["framing", "problem-definition"],
    "route":       ["routing", "delegation"],
    "fetch":       ["fetching", "http"],
    "search":      ["search", "discovery"],
}

# ── Classification defaults ─────────────────────────────────────────────────
DEFAULT_CLASSIFICATIONS: dict[str, dict] = {
    "analysis.compare":    {"role": "procedure", "invocation": "direct", "effect_mode": "enrich"},
    "analysis.risk-assess": {"role": "procedure", "invocation": "direct", "effect_mode": "enrich"},
    "eval.validate":       {"role": "procedure", "invocation": "direct", "effect_mode": "enrich"},
}

# ── Use-cases per skill ─────────────────────────────────────────────────────
USE_CASES: dict[str, list[str]] = {
    "agent.plan-and-route": [
        "Route an incoming user request to the appropriate capability",
        "Generate a multi-step plan from a complex goal",
        "Decompose an ambiguous request into actionable sub-tasks",
    ],
    "agent.trace": [
        "Analyze agent execution to produce structured trace state",
        "Monitor decision quality and risk signals during a run",
        "Generate decision graph views for debugging agent behavior",
    ],
    "audio.transcribe-summary": [
        "Transcribe an audio file and produce a text summary",
        "Extract key points from a recorded meeting",
        "Convert speech recordings into searchable text summaries",
    ],
    "code.diff-summary": [
        "Summarize code changes in a diff for review",
        "Extract key modifications from a pull request diff",
        "Generate human-readable summaries of code patches",
    ],
    "data.parse-and-validate": [
        "Parse raw JSON data and validate against a schema",
        "Ensure incoming data conforms to expected structure",
        "Validate API payloads before processing",
    ],
    "doc.chunk-and-embed": [
        "Split a document into chunks and generate embeddings",
        "Prepare documents for vector search indexing",
        "Create semantic embeddings for document retrieval",
    ],
    "email.read-summary": [
        "Read emails from inbox and generate summaries",
        "Extract action items from email threads",
        "Summarize unread emails for quick triage",
    ],
    "image.caption-and-classify": [
        "Generate captions for images and classify their content",
        "Categorize uploaded images by visual content",
        "Add descriptive metadata to image assets",
    ],
    "memory.retrieve-summary": [
        "Retrieve stored memories and generate a summary",
        "Find relevant past context for a given query",
        "Synthesize stored knowledge entries into a brief",
    ],
    "memory.store-embedding": [
        "Store text content with its vector embedding",
        "Index new information for future semantic retrieval",
        "Persist agent knowledge as embeddings for recall",
    ],
    "memory.store-summary": [
        "Store a summary of content in memory",
        "Persist key findings for later retrieval",
        "Save distilled context from agent interactions",
    ],
    "pdf.chunk-and-embed": [
        "Extract text from a PDF, chunk it, and generate embeddings",
        "Prepare PDF documents for vector search",
        "Index PDF content for semantic retrieval",
    ],
    "pdf.read-keyword-summary": [
        "Read a PDF and produce a keyword-focused summary",
        "Extract key terms and their context from PDF documents",
        "Generate keyword-weighted summaries of PDF content",
    ],
    "pdf.read-summary": [
        "Read a PDF and generate a comprehensive summary",
        "Extract key points from PDF documents",
        "Summarize multi-page PDFs for quick consumption",
    ],
    "table.filter-summary": [
        "Filter tabular data and summarize the results",
        "Apply criteria to a dataset and produce a focused summary",
        "Extract insights from filtered table records",
    ],
    "text.detect-language-and-classify": [
        "Detect the language of text and classify its content",
        "Route multilingual inputs by language and category",
        "Tag text documents with language and topic labels",
    ],
    "text.entity-summary": [
        "Extract named entities and produce a summary",
        "Identify key people, places, and organizations in text",
        "Generate entity-centric summaries from documents",
    ],
    "text.keyword-summary": [
        "Extract keywords and generate a keyword-focused summary",
        "Identify the most relevant terms in a text corpus",
        "Produce concise summaries highlighting key terminology",
    ],
    "text.language-summary": [
        "Detect the language of text and produce a summary",
        "Summarize content in its detected source language",
        "Process multilingual text with language-aware summarization",
    ],
    "text.translate-summary": [
        "Translate text and produce a summary of the translation",
        "Cross-lingual summarization for multilingual content",
        "Translate documents and distill key points",
    ],
    "web.fetch-classify": [
        "Fetch a web page and classify its content",
        "Categorize URLs by topic after fetching",
        "Tag web resources with content classifications",
    ],
    "web.fetch-summary": [
        "Fetch a web page and generate a summary",
        "Extract key content from URLs for quick review",
        "Summarize web articles for research consumption",
    ],
    "web.page-chunk-and-embed": [
        "Fetch a web page, chunk its content, and generate embeddings",
        "Index web pages for semantic search",
        "Prepare web content for vector-based retrieval",
    ],
    "web.page-summary": [
        "Fetch a web page and produce a comprehensive summary",
        "Extract and summarize content from a URL",
        "Generate structured summaries of web content",
    ],
    "web.search-summary": [
        "Perform a web search and summarize the results",
        "Find and synthesize information from search results",
        "Generate research summaries from web search queries",
    ],
}

# ── Examples per skill ──────────────────────────────────────────────────────
EXAMPLES: dict[str, list[dict]] = {
    "agent.plan-and-route": [{
        "description": "Route a user question to the right capability",
        "input": {"goal": "Summarize this PDF for me", "context": {"file": "report.pdf"}},
        "output": {"plan": [{"step": 1, "capability": "pdf.document.read"}, {"step": 2, "capability": "text.content.summarize"}]},
    }],
    "agent.trace": [{
        "description": "Analyze execution trace with risk monitoring",
        "input": {"goal": "Process customer feedback", "events": [{"type": "step_start", "timestamp": "2026-01-01T10:00:00Z", "step_id": "s1"}]},
        "output": {"trace_session_id": "ts-001", "control_status": "ok", "confidence": 0.85},
    }],
    "analysis.compare": [{
        "description": "Compare two strategic options",
        "input": {"items": [{"id": "opt-a", "content": "Expand to Europe"}, {"id": "opt-b", "content": "Focus on domestic market"}], "criteria": ["cost", "risk", "growth"]},
        "output": {"comparison_matrix": [{"criterion": "cost", "opt-a": "high", "opt-b": "low"}], "recommendation": "opt-b"},
    }],
    "analysis.decompose": [{
        "description": "Decompose a complex problem into sub-problems",
        "input": {"problem": "Reduce customer churn by 20%", "context": "SaaS platform with 10K users"},
        "output": {"sub_problems": ["Identify churn drivers", "Segment at-risk users", "Design retention interventions", "Measure intervention effectiveness"]},
    }],
    "analysis.risk-assess": [{
        "description": "Assess risk of a project proposal",
        "input": {"proposal": "Migrate to new cloud provider", "factors": ["cost", "downtime", "vendor lock-in"]},
        "output": {"risk_score": 0.65, "risk_factors": [{"factor": "downtime", "severity": "high", "mitigation": "Blue-green deployment"}]},
    }],
    "audio.transcribe-summary": [{
        "description": "Transcribe and summarize a meeting recording",
        "input": {"audio_path": "/recordings/standup.mp3", "language": "en"},
        "output": {"transcript_snippet": "Team discussed Q2 priorities...", "summary": "Standup covered sprint progress, blocker on API integration, and Q2 roadmap alignment."},
    }],
    "code.diff-summary": [{
        "description": "Summarize a code diff",
        "input": {"diff": "--- a/main.py\n+++ b/main.py\n@@ -10,3 +10,5 @@\n+import logging\n+logger = logging.getLogger(__name__)"},
        "output": {"summary": "Added logging import and logger initialization to main.py", "files_changed": ["main.py"], "change_type": "enhancement"},
    }],
    "data.parse-and-validate": [{
        "description": "Parse and validate a JSON payload",
        "input": {"raw_data": "{\"name\": \"Alice\", \"age\": 30}", "schema": {"type": "object", "required": ["name", "age"]}},
        "output": {"parsed": {"name": "Alice", "age": 30}, "valid": True, "errors": []},
    }],
    "doc.chunk-and-embed": [{
        "description": "Chunk a document and create embeddings",
        "input": {"document": "Long document text about market analysis...", "chunk_size": 512},
        "output": {"chunks": [{"id": "c1", "text": "Market analysis section...", "embedding_dim": 768}], "total_chunks": 5},
    }],
    "email.read-summary": [{
        "description": "Read and summarize inbox emails",
        "input": {"mailbox": "inbox", "max_messages": 10, "unread_only": True},
        "output": {"summary": "3 unread emails: 1 meeting invite for Friday, 1 project update from team lead, 1 vendor proposal.", "count": 3},
    }],
    "eval.validate": [{
        "description": "Validate model output quality",
        "input": {"output": "The capital of France is Paris.", "criteria": ["factual_accuracy", "completeness"]},
        "output": {"valid": True, "scores": {"factual_accuracy": 1.0, "completeness": 0.8}, "overall": 0.9},
    }],
    "image.caption-and-classify": [{
        "description": "Caption and classify an image",
        "input": {"image_path": "/images/product_photo.jpg"},
        "output": {"caption": "A laptop on a wooden desk with a coffee cup", "categories": ["technology", "workspace"], "confidence": 0.92},
    }],
    "memory.retrieve-summary": [{
        "description": "Retrieve and summarize stored memories",
        "input": {"query": "What do we know about client X preferences?", "max_results": 5},
        "output": {"summary": "Client X prefers email communication, has budget constraints, and prioritizes delivery speed.", "sources": 3},
    }],
    "memory.store-embedding": [{
        "description": "Store text with embedding",
        "input": {"content": "Q2 revenue grew 12% YoY", "namespace": "financial", "metadata": {"source": "quarterly_report"}},
        "output": {"stored": True, "embedding_id": "emb-a1b2", "dimensions": 768},
    }],
    "memory.store-summary": [{
        "description": "Store a summary in memory",
        "input": {"content": "Meeting concluded with agreement to proceed with option B", "key": "meeting-2026-03-20", "namespace": "meetings"},
        "output": {"stored": True, "key": "meeting-2026-03-20"},
    }],
    "pdf.chunk-and-embed": [{
        "description": "Extract, chunk, and embed PDF content",
        "input": {"pdf_path": "/docs/report.pdf", "chunk_size": 512},
        "output": {"total_chunks": 12, "chunks": [{"id": "c1", "text": "Executive summary...", "page": 1}]},
    }],
    "pdf.read-keyword-summary": [{
        "description": "Keyword-focused PDF summary",
        "input": {"pdf_path": "/docs/contract.pdf", "keywords": ["penalty", "termination", "liability"]},
        "output": {"summary": "Contract includes a 5% penalty clause for late delivery, 30-day termination notice, and capped liability at contract value.", "keyword_hits": {"penalty": 3, "termination": 2, "liability": 4}},
    }],
    "pdf.read-summary": [{
        "description": "Summarize a PDF document",
        "input": {"pdf_path": "/docs/whitepaper.pdf", "max_pages": 20},
        "output": {"summary": "Whitepaper proposes a new framework for distributed agent coordination with emphasis on fault tolerance and state management.", "pages_processed": 15},
    }],
    "research.normalize-corpus": [{
        "description": "Normalize a research corpus for analysis",
        "input": {"items": [{"id": "d1", "content": "Raw text with inconsistent formatting..."}, {"id": "d2", "content": "Another document..."}]},
        "output": {"normalized_items": [{"id": "d1", "content": "Clean normalized text..."}], "total": 2, "issues_fixed": 3},
    }],
    "research.quality-assess": [{
        "description": "Assess quality of research sources",
        "input": {"items": [{"id": "s1", "content": "Peer-reviewed study on AI safety", "type": "article"}]},
        "output": {"quality_scores": [{"id": "s1", "score": 0.88, "factors": {"recency": 0.9, "credibility": 0.95, "relevance": 0.8}}]},
    }],
    "table.filter-summary": [{
        "description": "Filter and summarize tabular data",
        "input": {"table": [{"name": "Alice", "score": 92}, {"name": "Bob", "score": 78}], "filter": {"score": {">": 80}}},
        "output": {"filtered": [{"name": "Alice", "score": 92}], "summary": "1 of 2 records match: Alice (score 92).", "count": 1},
    }],
    "task.frame": [{
        "description": "Frame a task for structured execution",
        "input": {"goal": "Evaluate market entry for Southeast Asia", "constraints": ["budget < 500K", "timeline < 6 months"]},
        "output": {"framed_task": {"objective": "Market entry evaluation", "scope": "Southeast Asia", "constraints": ["budget < 500K", "timeline < 6 months"], "success_criteria": ["Viable market identified", "Risk assessment complete"]}},
    }],
    "text.detect-language-and-classify": [{
        "description": "Detect language and classify text",
        "input": {"text": "La inteligencia artificial está transformando la industria."},
        "output": {"language": "es", "confidence": 0.97, "categories": ["technology", "industry"]},
    }],
    "text.entity-summary": [{
        "description": "Extract entities and summarize",
        "input": {"text": "Apple CEO Tim Cook announced a new partnership with Samsung in Seoul."},
        "output": {"entities": [{"text": "Tim Cook", "type": "PERSON"}, {"text": "Apple", "type": "ORG"}, {"text": "Samsung", "type": "ORG"}, {"text": "Seoul", "type": "LOC"}], "summary": "Apple CEO Tim Cook announced a Samsung partnership in Seoul."},
    }],
    "text.keyword-summary": [{
        "description": "Extract keywords and summarize",
        "input": {"text": "Machine learning models require large datasets for training. Transfer learning can reduce data requirements significantly."},
        "output": {"keywords": ["machine learning", "datasets", "training", "transfer learning"], "summary": "ML models need large datasets but transfer learning reduces data requirements."},
    }],
    "text.language-summary": [{
        "description": "Detect language and summarize",
        "input": {"text": "Le marché européen montre des signes de reprise après la crise."},
        "output": {"language": "fr", "summary": "Le marché européen se reprend après la crise.", "confidence": 0.95},
    }],
    "text.translate-summary": [{
        "description": "Translate and summarize text",
        "input": {"text": "Die Energiewende erfordert massive Investitionen in erneuerbare Energien.", "target_language": "en"},
        "output": {"translation": "The energy transition requires massive investments in renewable energy.", "summary": "Germany's energy transition demands significant renewable energy investment.", "source_language": "de"},
    }],
    "web.fetch-classify": [{
        "description": "Fetch a URL and classify content",
        "input": {"url": "https://example.com/blog/ai-trends-2026"},
        "output": {"title": "AI Trends 2026", "categories": ["technology", "artificial-intelligence", "trends"], "content_type": "blog_post"},
    }],
    "web.fetch-summary": [{
        "description": "Fetch and summarize a web page",
        "input": {"url": "https://example.com/article/market-report"},
        "output": {"summary": "Market report shows 15% growth in SaaS sector with emerging opportunities in AI-powered automation.", "word_count": 2400},
    }],
    "web.page-chunk-and-embed": [{
        "description": "Fetch, chunk, and embed web page content",
        "input": {"url": "https://example.com/docs/guide", "chunk_size": 512},
        "output": {"total_chunks": 8, "chunks": [{"id": "c1", "text": "Getting started section...", "embedding_dim": 768}]},
    }],
    "web.page-summary": [{
        "description": "Generate a comprehensive web page summary",
        "input": {"url": "https://example.com/whitepaper/cloud-native"},
        "output": {"summary": "Whitepaper advocates cloud-native architecture with microservices, containerization, and GitOps practices for enterprise adoption.", "sections": 5},
    }],
    "web.search-summary": [{
        "description": "Search the web and summarize results",
        "input": {"query": "latest advances in quantum computing 2026", "max_results": 5},
        "output": {"summary": "Recent advances include error-corrected qubits, hybrid quantum-classical algorithms, and first commercial quantum advantage demonstrations.", "sources": 5},
    }],
}


def _build_tags(skill_id: str) -> list[str]:
    domain = skill_id.split(".")[0]
    name = skill_id.split(".", 1)[1] if "." in skill_id else ""
    tags = list(DOMAIN_TAGS.get(domain, [domain]))
    for verb, extras in VERB_TAGS.items():
        if verb in name:
            for t in extras:
                if t not in tags:
                    tags.append(t)
    return tags


def fix_skill(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return []
    skill_id = data.get("id", "")
    if not skill_id:
        return []

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
        data["metadata"] = metadata

    fixes: list[str] = []

    # tags
    if not isinstance(metadata.get("tags"), list) or len(metadata.get("tags", [])) == 0:
        tags = _build_tags(skill_id)
        if tags:
            metadata["tags"] = tags
            fixes.append("tags")

    # use_cases
    if not isinstance(metadata.get("use_cases"), list) or len(metadata.get("use_cases", [])) == 0:
        uc = USE_CASES.get(skill_id)
        if uc:
            metadata["use_cases"] = uc
            fixes.append("use_cases")

    # examples
    if not isinstance(metadata.get("examples"), list) or len(metadata.get("examples", [])) == 0:
        ex = EXAMPLES.get(skill_id)
        if ex:
            metadata["examples"] = ex
            fixes.append("examples")

    # classification
    if not isinstance(metadata.get("classification"), dict) or not metadata.get("classification", {}).get("role"):
        cls = DEFAULT_CLASSIFICATIONS.get(skill_id)
        if cls:
            metadata["classification"] = cls
            fixes.append("classification")

    if not fixes:
        return []

    # Write back preserving order
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return fixes


def main() -> None:
    total = {"tags": 0, "use_cases": 0, "examples": 0, "classification": 0}
    for p in sorted(SKILLS_DIR.rglob("skill.yaml")):
        if "TEMPLATE" in str(p):
            continue
        fixes = fix_skill(p)
        if fixes:
            print(f"  {p.relative_to(SKILLS_DIR)}: {', '.join(fixes)}")
            for f in fixes:
                total[f] += 1
    print(f"\nFixed: {total['tags']} tags, {total['use_cases']} use_cases, "
          f"{total['examples']} examples, {total['classification']} classification")


if __name__ == "__main__":
    main()
