# Domain: web.*

> Web resource retrieval, extraction, search, verification, and normalization.

---

## Capabilities (6)

| ID | Status | Description | Binding | cognitive_hints |
|---|---|---|---|---|
| `web.page.fetch` | experimental | Fetch content from a web URL | python + MCP + OpenAPI mock | perceive → Artifact |
| `web.page.extract` | experimental | Extract main textual content from HTML | python | perceive → Artifact |
| `web.source.search` | experimental | Search the web for sources matching a query | python | perceive → Evidence |
| `web.source.verify` | experimental | Verify trust and integrity signals for a URL | python | evaluate → Evidence |
| `web.source.normalize` | experimental | Normalize search results into corpus items | python | analyze → Evidence |
| `web.request.send` | experimental | Generic HTTP request with safety blocks | python | interact → Artifact |

---

## Pipeline

```
web.source.search ──→ web.source.normalize ──→ (corpus items)
                                                    │
                                               [source_ref]
                                                    │
                                              web.page.fetch ──→ web.page.extract
                                                    │
                                              web.source.verify (sidecar)
```

Typical flows:

1. **Search → Normalize → Fetch → Extract**: full web research pipeline.
2. **Fetch → Extract**: direct page content retrieval.
3. **Verify**: standalone trust check on any URL.

---

## Service: `web_baseline` (`official_services/web_baseline.py`)

| Function | Capability | Notes |
|---|---|---|
| `fetch_webpage(url)` | web.page.fetch | SSRF guard, 10s timeout, 2MB limit, charset detection, mojibake repair, rejects binary types |
| `extract_webpage(content)` | web.page.extract | HTML → text via `HTMLParser`, title from `<title>`, 5000 char limit |
| `search_web(query, limit)` | web.source.search | DuckDuckGo HTML scraping (no API key), fallback to synthetic results, limit 5–20 |
| `verify_source(url)` | web.source.verify | Checks SSRF patterns (localhost, 127.x, 0.0.0.0), returns trusted + reason + normalized_source |
| `normalize_search_results(results, mode)` | web.source.normalize | `quick` mode: snippet as content; `deep` mode: empty content + source_ref for lazy resolution |

### SSRF Protection (`fetch_webpage`)

- Only `http`/`https` schemes allowed.
- Private/link-local IPs and cloud metadata endpoints blocked.
- URL validated after resolution, not just at configuration time.

### Observability events

- `service.web.page.fetch.start` — url, scheme, host.
- `service.web.page.fetch` — status, http_status, duration_ms.
- `web.source.search.live` — provider, result_count, duration_ms.
- `web.source.search.fallback` — reason, duration_ms (synthetic fallback).

---

## Bindings

### web.page.fetch (3 protocols)

| Binding ID | Protocol | Service | Status |
|---|---|---|---|
| `python_web_fetch` | pythoncall | web_baseline | stable |
| `mcp_web_fetch_inprocess` | mcp | web_mcp_inprocess | experimental |
| `openapi_web_fetch_mock` | openapi | web_fetch_openapi_mock | experimental |

### web.page.extract (1 protocol)

| Binding ID | Protocol | Service | Status |
|---|---|---|---|
| `python_web_page_extract` | pythoncall | web_baseline | stable |

### web.source.search (1 protocol)

| Binding ID | Protocol | Service | Status |
|---|---|---|---|
| `python_web_source_search` | pythoncall | web_baseline | stable |

### web.source.verify (1 protocol)

| Binding ID | Protocol | Service | Status |
|---|---|---|---|
| `python_web_source_verify` | pythoncall | web_baseline | stable |

### web.source.normalize (1 protocol)

| Binding ID | Protocol | Service | Status |
|---|---|---|---|
| `python_web_source_normalize` | pythoncall | web_baseline | stable |

---

## Skills (5)

| Skill ID | Channel | Steps | Capabilities used |
|---|---|---|---|
| `web.fetch-summary` | official | 3 | web.page.fetch → text.content.extract → text.content.summarize |
| `web.fetch-classify` | official | 3 | web.page.fetch → web.page.extract → text.content.classify |
| `web.page-summary` | official | 2 | web.page.extract → text.content.summarize |
| `web.search-summary` | official | 2 | web.source.search → text.content.summarize |
| `web.page-chunk-and-embed` | experimental | 4 | web.page.fetch → web.page.extract → doc.content.chunk → text.content.embed |

---

## MCP Coverage

Only `web.page.fetch` has an MCP binding (proof of concept via in-process
MCP server at `official_mcp_servers/web_tools.py`). Other capabilities use
pythoncall baselines. MCP expansion is planned capability-by-capability as
external MCP servers become available.

---

## Decisions & Rationale

- **No `web.page.screenshot`**: `screenshot` is not in the vocabulary; requires
  headless browser dependencies (Playwright/Selenium). Out of scope for v0.1.0.
- **No `web.content.scrape`**: `scrape` is not in the vocabulary; site-specific
  CSS/XPath extraction is too fragile for a generic capability. `web.page.extract`
  covers the general text extraction case.
- **No `web.page.parse`**: `parse` is in the vocabulary but would overlap with
  `web.page.extract`. Could be added later for structured extraction (JSON-LD,
  microdata, link graphs) if needed.
- **`extract_webpage` accepts HTML content**, not URL: aligns with the capability
  contract (`inputs.content`). Fetching is `web.page.fetch`'s responsibility.
  Skills compose fetch → extract when both steps are needed.
- **DuckDuckGo for search**: no API key required, synthetic fallback ensures
  degraded operation when live search is unavailable.
