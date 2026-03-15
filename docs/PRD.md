# PRD: Scuba v0.1 — Universal File Intelligence

**Version:** 0.1
**Date:** 2026-03-15
**Branch:** `prd/agentic-spotlight`
**License:** Open Source (TBD)

---

## 1. Vision

Scuba is a cross-platform, Spotlight-like file intelligence tool that finds any file by what it **means**, not what it's named. It combines instant keyword search with local semantic understanding (embeddings, vision models, OCR) and optional cloud AI for deeper reasoning — with full transparency on what data leaves the machine.

---

## 2. Project Structure

```
scuba/
├── apps/
│   ├── backend/
│   │   └── python/
│   │       ├── core/                    # EXISTING — file traversal & metadata
│   │       │   ├── __init__.py
│   │       │   ├── traverser.py         # recursive directory walker
│   │       │   ├── extractor.py         # file metadata extraction
│   │       │   ├── indexer.py           # orchestrates traverser + extractor
│   │       │   └── storage.py           # JSON persistence (to be replaced by SQLite)
│   │       │
│   │       ├── db/                      # NEW — database layer
│   │       │   ├── __init__.py
│   │       │   ├── schema.sql           # raw CREATE TABLE statements
│   │       │   ├── connection.py        # SQLite connection pool + sqlite-vec init
│   │       │   ├── models.py            # dataclasses for DB rows
│   │       │   └── queries.py           # parameterized query functions
│   │       │
│   │       ├── search/                  # NEW — search engines
│   │       │   ├── __init__.py
│   │       │   ├── keyword.py           # SQLite FTS5 full-text search
│   │       │   ├── semantic.py          # embedding-based vector search
│   │       │   ├── hybrid.py            # fuses keyword + semantic + activity
│   │       │   └── ranking.py           # scoring weights and result fusion
│   │       │
│   │       ├── extractors/              # NEW — content extraction pipelines
│   │       │   ├── __init__.py
│   │       │   ├── document.py          # PDF, Word, Excel, PPT text extraction
│   │       │   ├── vision.py            # CLIP/SigLIP image tagging
│   │       │   ├── ocr.py              # Tesseract OCR for screenshots/receipts
│   │       │   ├── code.py             # tree-sitter AST parsing
│   │       │   ├── media.py            # EXIF, ffprobe, ID3 metadata
│   │       │   └── registry.py         # maps file extensions → extractors
│   │       │
│   │       ├── agent/                   # NEW — AI agent layer
│   │       │   ├── __init__.py
│   │       │   ├── engine.py            # orchestrates LLM calls + tool dispatch
│   │       │   ├── privacy_proxy.py     # PII detection (Presidio) + payload logging
│   │       │   ├── tools.py             # tool definitions for LLM function calling
│   │       │   └── memory.py            # persistent agent memory store
│   │       │
│   │       ├── intelligence/            # NEW — background intelligence
│   │       │   ├── __init__.py
│   │       │   ├── relationships.py     # version chains, topic clusters, temporal bundles
│   │       │   ├── activity.py          # ActivityWatch integration
│   │       │   ├── proactive.py         # duplicate detection, stale file alerts
│   │       │   └── app_registry.py      # installed app detection + category mapping
│   │       │
│   │       ├── watcher/                 # NEW — file system monitoring
│   │       │   ├── __init__.py
│   │       │   └── fs_watcher.py        # watchdog-based file system events
│   │       │
│   │       ├── main.py                  # ENHANCED — FastAPI app with new endpoints
│   │       ├── config.py                # NEW — centralized configuration
│   │       └── pyproject.toml           # ENHANCED — new dependencies
│   │
│   └── frontend/
│       ├── app/
│       │   ├── components/
│       │   │   ├── SpotlightBar/        # NEW — Cmd+K overlay
│       │   │   │   ├── SpotlightBar.tsx
│       │   │   │   ├── SpotlightBar.module.css
│       │   │   │   └── useSpotlight.ts  # keyboard shortcut hook
│       │   │   ├── ResultList/          # NEW — flat ranked results
│       │   │   │   ├── ResultList.tsx
│       │   │   │   ├── ResultItem.tsx
│       │   │   │   └── ResultList.module.css
│       │   │   ├── ExpandablePanel/     # NEW — file Q&A panel
│       │   │   │   ├── ExpandablePanel.tsx
│       │   │   │   └── ExpandablePanel.module.css
│       │   │   ├── AuditLog/            # NEW — audit log viewer
│       │   │   │   ├── AuditLog.tsx
│       │   │   │   └── AuditLog.module.css
│       │   │   ├── GlassCard.tsx        # EXISTING
│       │   │   ├── GlassButton.tsx      # EXISTING
│       │   │   ├── GlassInput.tsx       # EXISTING
│       │   │   └── BackendStatus.tsx    # EXISTING
│       │   ├── hooks/
│       │   │   ├── useSearch.ts         # NEW — search API hook with progressive loading
│       │   │   └── useWebSocket.ts      # NEW — real-time result streaming
│       │   ├── lib/
│       │   │   └── api.ts              # NEW — typed API client
│       │   └── page.tsx                # ENHANCED
│       └── package.json
│
├── docs/
│   ├── PRD.md
│   └── scuba-agent-explainer.html
├── scripts/
│   └── status.py
├── Makefile                             # ENHANCED — new commands
├── turbo.json
└── package.json
```

---

## 3. Database Schema (SQLite)

Replace JSON storage with SQLite. All tables in a single `scuba.db` file.

```sql
-- Core file index
CREATE TABLE files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    path            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    extension       TEXT,
    size_bytes       INTEGER NOT NULL,
    mime_type       TEXT,
    created_at      TEXT NOT NULL,           -- ISO 8601
    modified_at     TEXT NOT NULL,           -- ISO 8601
    indexed_at      TEXT NOT NULL DEFAULT (datetime('now')),
    content_hash    TEXT,                    -- SHA-256 of file content
    extracted_text  TEXT,                    -- full text for FTS, NULL for binary files
    is_deleted      INTEGER NOT NULL DEFAULT 0
);

-- FTS5 virtual table for keyword search
CREATE VIRTUAL TABLE files_fts USING fts5(
    name,
    path,
    extracted_text,
    content='files',
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER files_ai AFTER INSERT ON files BEGIN
    INSERT INTO files_fts(rowid, name, path, extracted_text)
    VALUES (new.id, new.name, new.path, new.extracted_text);
END;

CREATE TRIGGER files_ad AFTER DELETE ON files BEGIN
    INSERT INTO files_fts(files_fts, rowid, name, path, extracted_text)
    VALUES ('delete', old.id, old.name, old.path, old.extracted_text);
END;

CREATE TRIGGER files_au AFTER UPDATE ON files BEGIN
    INSERT INTO files_fts(files_fts, rowid, name, path, extracted_text)
    VALUES ('delete', old.id, old.name, old.path, old.extracted_text);
    INSERT INTO files_fts(rowid, name, path, extracted_text)
    VALUES (new.id, new.name, new.path, new.extracted_text);
END;

-- Vector embeddings (sqlite-vec)
-- sqlite-vec uses virtual tables for vector storage
CREATE VIRTUAL TABLE embeddings USING vec0(
    file_id     INTEGER,
    embedding   float[384],                 -- dimension depends on model
    +source     TEXT,                       -- 'text', 'ocr', 'clip'
    +model      TEXT                        -- 'nomic-embed-text', 'clip-vit-b32'
);

-- Image tags from CLIP/SigLIP
CREATE TABLE image_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id     INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    tag         TEXT NOT NULL,
    confidence  REAL NOT NULL,              -- 0.0 to 1.0
    model       TEXT NOT NULL DEFAULT 'clip-vit-b32',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_image_tags_file ON image_tags(file_id);
CREATE INDEX idx_image_tags_tag ON image_tags(tag);

-- Code dependency graph (for code files only)
CREATE TABLE code_graph (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_id  INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    target_file_id  INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    relationship    TEXT NOT NULL,           -- 'imports', 'calls', 'references', 'inherits'
    symbol_name     TEXT,                    -- e.g., function or class name
    line_number     INTEGER
);
CREATE INDEX idx_code_graph_source ON code_graph(source_file_id);
CREATE INDEX idx_code_graph_target ON code_graph(target_file_id);

-- File relationships (non-code: version chains, topic clusters, temporal bundles)
CREATE TABLE file_relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id_a       INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    file_id_b       INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    relationship    TEXT NOT NULL,           -- 'version_chain', 'topic_cluster', 'temporal_bundle', 'source_tracking'
    confidence      REAL NOT NULL DEFAULT 1.0,
    metadata        TEXT,                    -- JSON blob for extra data
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_file_rel_a ON file_relationships(file_id_a);
CREATE INDEX idx_file_rel_b ON file_relationships(file_id_b);

-- Audit log (append-only)
CREATE TABLE audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL DEFAULT (datetime('now')),
    action          TEXT NOT NULL,           -- 'search', 'open', 'llm_request', 'workflow_step'
    target_path     TEXT,
    query           TEXT,
    payload_sent    TEXT,                    -- exact JSON sent to cloud LLM (NULL if local-only)
    payload_size    INTEGER,                 -- bytes sent to cloud
    pii_redacted    TEXT,                    -- JSON list of PII types found and redacted
    response        TEXT,                    -- summary of LLM response
    duration_ms     INTEGER
);

-- Agent memory (persistent across sessions)
CREATE TABLE agent_memory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT NOT NULL UNIQUE,
    value       TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'learned',  -- 'user_taught' or 'learned'
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    access_count INTEGER NOT NULL DEFAULT 0
);

-- Activity signals (from ActivityWatch)
CREATE TABLE activity_signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path       TEXT NOT NULL,
    access_count    INTEGER NOT NULL DEFAULT 1,
    last_accessed   TEXT NOT NULL,
    total_duration_s INTEGER NOT NULL DEFAULT 0,
    co_accessed     TEXT,                    -- JSON array of file paths frequently opened together
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX idx_activity_path ON activity_signals(file_path);

-- App registry
CREATE TABLE app_registry (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    path        TEXT NOT NULL UNIQUE,
    categories  TEXT NOT NULL,              -- JSON array: ["photo_editing", "image_viewer"]
    icon_path   TEXT,
    detected_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- User settings
CREATE TABLE settings (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);

-- Default settings
INSERT INTO settings (key, value) VALUES
    ('blocked_paths', '["~/.ssh", "~/.aws", "~/.gnupg", "~/.env"]'),
    ('llm_provider', 'claude'),
    ('llm_model', 'claude-sonnet-4-6'),
    ('embedding_model', 'nomic-embed-text'),
    ('vision_model', 'clip-vit-base-patch32'),
    ('index_on_startup', 'true'),
    ('max_file_size_mb', '100');
```

---

## 4. API Endpoints

### 4.1 Search (Phase 1)

```
GET /api/v1/search?q={query}&limit={20}&offset={0}

Response (streamed via WebSocket for progressive results):
{
    "results": [
        {
            "id": 1234,
            "path": "/Users/john/Documents/invoice_dentist.pdf",
            "name": "invoice_dentist.pdf",
            "extension": ".pdf",
            "size_bytes": 245000,
            "mime_type": "application/pdf",
            "modified_at": "2026-02-14T10:30:00Z",
            "snippet": "...dental cleaning copay $25...",
            "score": 0.92,
            "match_type": "semantic",          // "keyword", "semantic", or "hybrid"
            "image_tags": null,
            "related_files": [1235, 1236]
        }
    ],
    "total": 47,
    "timing": {
        "keyword_ms": 12,
        "semantic_ms": 280,
        "total_ms": 310
    }
}
```

### 4.2 Progressive Search via WebSocket (Phase 1)

```
WS /api/v1/search/stream

Client sends:
{ "query": "dentist receipt", "limit": 20 }

Server sends progressively:
{ "phase": "keyword", "results": [...], "timing_ms": 12 }
{ "phase": "semantic", "results": [...], "timing_ms": 280 }
{ "phase": "activity", "results": [...], "timing_ms": 450 }
{ "phase": "done", "total": 47 }
```

### 4.3 File Q&A (Phase 2)

```
POST /api/v1/ask
{
    "file_id": 1234,
    "question": "summarize this document",
    "conversation_id": "conv_abc123"    // for multi-turn
}

Response:
{
    "answer": "This is a dental invoice from February 2026...",
    "sources": ["page 1, paragraph 2"],
    "cloud_used": true,
    "payload_size_bytes": 1240,
    "pii_redacted": ["email", "phone"],
    "conversation_id": "conv_abc123"
}
```

### 4.4 Index Management

```
POST   /api/v1/index/rebuild              # full re-index
POST   /api/v1/index/update               # incremental update (changed files only)
GET    /api/v1/index/status               # indexing progress
DELETE /api/v1/index/file/{file_id}       # remove file from index

GET    /api/v1/stats                      # total files, index size, last updated
GET    /api/v1/audit                      # audit log entries (paginated)
GET    /api/v1/health                     # health check (existing, enhanced)
```

### 4.5 Agent (Phase 4)

```
POST /api/v1/agent/execute
{
    "query": "find screenshots older than 30 days and move to archive",
    "dry_run": true                        // show plan without executing
}

Response:
{
    "plan": [
        {"step": 1, "action": "search", "params": {"type": "image", "tag": "screenshot", "older_than": "30d"}, "result_count": 47},
        {"step": 2, "action": "create_folder", "params": {"path": "~/Archive/Screenshots"}},
        {"step": 3, "action": "batch_move", "params": {"count": 47, "destination": "~/Archive/Screenshots"}}
    ],
    "requires_approval": true,
    "destructive_steps": [3]
}

POST /api/v1/agent/approve
{ "plan_id": "plan_abc123", "approved_steps": [1, 2, 3] }
```

---

## 5. Backend Implementation Details

### 5.1 Dependencies (pyproject.toml additions)

```toml
[tool.poetry.dependencies]
python = "^3.10"

# Web framework (existing)
fastapi = "^0.115.0"
uvicorn = "^0.34.0"
websockets = "^14.0"

# Database
aiosqlite = "^0.20.0"                     # async SQLite
sqlite-vec = "^0.1.6"                     # vector search extension

# Embeddings (local)
sentence-transformers = "^3.4.0"          # for nomic-embed-text
onnxruntime = "^1.20.0"                   # CPU inference

# Document extraction
pymupdf = "^1.25.0"                       # PDF text extraction
python-docx = "^1.1.0"                    # Word documents
openpyxl = "^3.1.0"                       # Excel spreadsheets
python-pptx = "^1.0.0"                    # PowerPoint

# Vision
open-clip-torch = "^2.29.0"              # CLIP/SigLIP image tagging
pillow = "^11.0.0"                        # image processing
pytesseract = "^0.3.13"                   # OCR wrapper

# Code parsing
tree-sitter = "^0.24.0"
tree-sitter-python = "^0.23.0"
tree-sitter-javascript = "^0.23.0"
tree-sitter-typescript = "^0.23.0"

# Privacy
presidio-analyzer = "^2.2.0"             # PII detection
presidio-anonymizer = "^2.2.0"           # PII redaction

# File system
watchdog = "^6.0.0"                       # file system events

# LLM
anthropic = "^0.42.0"                     # Claude API

# Media metadata
mutagen = "^1.47.0"                       # audio metadata (ID3)
exifread = "^3.0.0"                       # EXIF from images

# Activity tracking
httpx = "^0.28.0"                         # async HTTP for ActivityWatch API
```

### 5.2 Configuration (config.py)

```python
from dataclasses import dataclass, field
from pathlib import Path
import platform

@dataclass
class ScubaConfig:
    # Database
    db_path: Path = Path.home() / ".scuba" / "scuba.db"

    # Indexing
    index_paths: list[str] = field(default_factory=lambda: [str(Path.home())])
    blocked_paths: list[str] = field(default_factory=lambda: [
        "~/.ssh", "~/.aws", "~/.gnupg", "~/.env",
        "~/.Trash", "~/Library", "~/.cache",
        "node_modules", ".git", "__pycache__", ".venv",
        "/System", "/Library", "C:\\Windows", "C:\\Program Files",
    ])
    max_file_size_mb: int = 100
    watch_enabled: bool = True

    # Embedding model
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    # Vision
    clip_model: str = "ViT-B-32"
    clip_pretrained: str = "openai"
    ocr_languages: list[str] = field(default_factory=lambda: ["eng"])
    vision_enabled: bool = True

    # LLM
    llm_provider: str = "claude"
    llm_model: str = "claude-sonnet-4-6"

    # Search
    keyword_weight: float = 0.3
    semantic_weight: float = 0.5
    activity_weight: float = 0.2

    # ActivityWatch
    activitywatch_url: str = "http://localhost:5600"
    activitywatch_enabled: bool = False      # opt-in

    # Privacy
    pii_detection_enabled: bool = True
    audit_log_enabled: bool = True
```

### 5.3 Keyword Search (search/keyword.py)

```python
import aiosqlite

async def keyword_search(db: aiosqlite.Connection, query: str, limit: int = 20) -> list[dict]:
    """
    Uses SQLite FTS5 for instant full-text search.
    Returns results ranked by BM25 relevance.
    Target: <50ms for 1M+ files.
    """
    sql = """
        SELECT f.id, f.path, f.name, f.extension, f.size_bytes, f.mime_type,
               f.modified_at, snippet(files_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
               rank
        FROM files_fts
        JOIN files f ON f.id = files_fts.rowid
        WHERE files_fts MATCH ?
          AND f.is_deleted = 0
        ORDER BY rank
        LIMIT ?
    """
    # FTS5 query syntax: prefix matching with *
    fts_query = " OR ".join(f'"{word}"*' for word in query.split())
    async with db.execute(sql, (fts_query, limit)) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
```

### 5.4 Semantic Search (search/semantic.py)

```python
from sentence_transformers import SentenceTransformer
import sqlite_vec

class SemanticSearch:
    def __init__(self, config):
        self.model = SentenceTransformer(config.embedding_model)
        self.dimension = config.embedding_dimension

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query. ~15ms on CPU."""
        return self.model.encode(query, normalize_embeddings=True).tolist()

    async def search(self, db, query: str, limit: int = 20) -> list[dict]:
        """
        Vector similarity search using sqlite-vec.
        Target: <300ms for 1M+ vectors.
        """
        query_vec = self.embed_query(query)
        sql = """
            SELECT f.id, f.path, f.name, f.extension, f.size_bytes,
                   f.mime_type, f.modified_at, e.distance
            FROM embeddings e
            JOIN files f ON f.id = e.file_id
            WHERE e.embedding MATCH ?
              AND k = ?
              AND f.is_deleted = 0
            ORDER BY e.distance
        """
        async with db.execute(sql, (serialize_float32(query_vec), limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def embed_and_store(self, db, file_id: int, text: str, source: str):
        """Embed text and store vector. Called during indexing."""
        vec = self.model.encode(text, normalize_embeddings=True).tolist()
        await db.execute(
            "INSERT INTO embeddings (file_id, embedding, source, model) VALUES (?, ?, ?, ?)",
            (file_id, serialize_float32(vec), source, self.model.get_model_name())
        )
```

### 5.5 Hybrid Ranker (search/hybrid.py)

```python
async def hybrid_search(db, query: str, config, limit: int = 20) -> dict:
    """
    Fuses keyword, semantic, and activity signals.
    Returns progressively via WebSocket.

    Scoring formula:
        score = (semantic_score * 0.5) + (keyword_score * 0.3) + (activity_score * 0.2)
    """
    import asyncio
    from .keyword import keyword_search
    from .semantic import SemanticSearch
    from .ranking import fuse_results

    semantic = SemanticSearch(config)

    # Run keyword and semantic in parallel
    keyword_task = asyncio.create_task(keyword_search(db, query, limit * 2))
    semantic_task = asyncio.create_task(semantic.search(db, query, limit * 2))

    keyword_results = await keyword_task       # <50ms
    semantic_results = await semantic_task      # <300ms

    # Activity signals (sync lookup, fast)
    activity_scores = await get_activity_scores(db, [r["path"] for r in keyword_results + semantic_results])

    # Fuse and rank
    fused = fuse_results(
        keyword_results, semantic_results, activity_scores,
        weights=(config.keyword_weight, config.semantic_weight, config.activity_weight)
    )

    return {
        "results": fused[:limit],
        "total": len(fused),
        "timing": {
            "keyword_ms": keyword_task.result_time_ms,
            "semantic_ms": semantic_task.result_time_ms,
        }
    }
```

### 5.6 Document Extraction (extractors/document.py)

```python
import pymupdf
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from pathlib import Path

class DocumentExtractor:
    """Extract text from documents. All processing is local."""

    SUPPORTED = {
        ".pdf": "extract_pdf",
        ".docx": "extract_docx",
        ".doc": "extract_docx",
        ".xlsx": "extract_xlsx",
        ".xls": "extract_xlsx",
        ".pptx": "extract_pptx",
        ".txt": "extract_text",
        ".md": "extract_text",
        ".csv": "extract_text",
        ".json": "extract_text",
        ".xml": "extract_text",
        ".html": "extract_text",
    }

    def extract(self, path: Path) -> str | None:
        ext = path.suffix.lower()
        method = self.SUPPORTED.get(ext)
        if not method:
            return None
        return getattr(self, method)(path)

    def extract_pdf(self, path: Path) -> str:
        doc = pymupdf.open(str(path))
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()

    def extract_docx(self, path: Path) -> str:
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def extract_xlsx(self, path: Path) -> str:
        wb = load_workbook(str(path), read_only=True, data_only=True)
        text = []
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            for row in ws.iter_rows(values_only=True):
                row_text = " ".join(str(c) for c in row if c is not None)
                if row_text.strip():
                    text.append(row_text)
        wb.close()
        return "\n".join(text)

    def extract_pptx(self, path: Path) -> str:
        prs = Presentation(str(path))
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text.append(shape.text_frame.text)
        return "\n".join(text)

    def extract_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
```

### 5.7 Vision Pipeline (extractors/vision.py)

```python
import open_clip
import torch
from PIL import Image
from pathlib import Path

class VisionPipeline:
    """
    CLIP/SigLIP image tagging. Runs on CPU (~500MB RAM).
    Tags every image with descriptive labels.
    """

    # Default tag vocabulary — expanded at runtime
    DEFAULT_TAGS = [
        "photo", "screenshot", "document", "receipt", "invoice",
        "diagram", "chart", "graph", "map", "logo", "icon",
        "person", "people", "group", "selfie", "portrait",
        "landscape", "building", "city", "nature", "beach", "mountain",
        "sunset", "sunrise", "night", "snow", "rain",
        "food", "animal", "dog", "cat", "car", "airplane",
        "text", "handwriting", "whiteboard", "presentation",
        "code", "terminal", "error message", "UI design", "mockup",
        "certificate", "ID card", "passport", "ticket", "boarding pass",
        "meme", "comic", "art", "painting", "drawing",
    ]

    SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".heic"}

    def __init__(self, model_name="ViT-B-32", pretrained="openai"):
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.model.eval()

        # Pre-encode tag vocabulary
        text_tokens = self.tokenizer(self.DEFAULT_TAGS)
        with torch.no_grad():
            self.text_features = self.model.encode_text(text_tokens)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def tag_image(self, path: Path, top_k: int = 5, threshold: float = 0.15) -> list[dict]:
        """
        Returns top-k tags with confidence scores.
        Example: [{"tag": "receipt", "confidence": 0.82}, {"tag": "text", "confidence": 0.71}]
        """
        image = self.preprocess(Image.open(path).convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            similarity = (image_features @ self.text_features.T).squeeze(0)

        scores = similarity.cpu().numpy()
        top_indices = scores.argsort()[-top_k:][::-1]

        return [
            {"tag": self.DEFAULT_TAGS[i], "confidence": round(float(scores[i]), 3)}
            for i in top_indices
            if scores[i] >= threshold
        ]

    def embed_image(self, path: Path) -> list[float]:
        """Returns CLIP embedding for vector similarity search."""
        image = self.preprocess(Image.open(path).convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            features = self.model.encode_image(image)
            features /= features.norm(dim=-1, keepdim=True)
        return features.squeeze(0).cpu().numpy().tolist()
```

### 5.8 Privacy Proxy (agent/privacy_proxy.py)

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import json
from datetime import datetime

class PrivacyProxy:
    """
    Sits between the agent and the cloud LLM.
    1. Detects PII using Microsoft Presidio
    2. Redacts sensitive data
    3. Logs exact payload to audit trail
    """

    PII_ENTITIES = [
        "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
        "CREDIT_CARD", "US_SSN", "IP_ADDRESS",
        "IBAN_CODE", "US_BANK_NUMBER", "US_PASSPORT",
        "CRYPTO", "NRP", "MEDICAL_LICENSE",
    ]

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def sanitize(self, text: str) -> dict:
        """
        Returns:
            {
                "sanitized_text": "... <PERSON> visited <EMAIL_ADDRESS> ...",
                "pii_found": [{"type": "EMAIL_ADDRESS", "start": 42, "end": 65}],
                "original_length": 1500,
                "sanitized_length": 1480
            }
        """
        results = self.analyzer.analyze(text=text, language="en", entities=self.PII_ENTITIES)
        anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)

        return {
            "sanitized_text": anonymized.text,
            "pii_found": [
                {"type": r.entity_type, "start": r.start, "end": r.end, "score": r.score}
                for r in results
            ],
            "original_length": len(text),
            "sanitized_length": len(anonymized.text),
        }

    async def send_to_llm(self, db, client, text: str, system_prompt: str, query: str) -> dict:
        """Sanitize, log, send, and return response."""
        sanitized = self.sanitize(text)

        payload = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [{"role": "user", "content": f"{query}\n\nContext:\n{sanitized['sanitized_text']}"}]
        }

        # Log to audit trail BEFORE sending
        await db.execute(
            """INSERT INTO audit_log (action, query, payload_sent, payload_size, pii_redacted)
               VALUES (?, ?, ?, ?, ?)""",
            ("llm_request", query, json.dumps(payload), len(json.dumps(payload)),
             json.dumps([p["type"] for p in sanitized["pii_found"]]))
        )
        await db.commit()

        # Send to LLM
        response = await client.messages.create(**payload)
        return {
            "answer": response.content[0].text,
            "cloud_used": True,
            "payload_size_bytes": len(json.dumps(payload)),
            "pii_redacted": [p["type"] for p in sanitized["pii_found"]],
        }
```

### 5.9 File System Watcher (watcher/fs_watcher.py)

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

class ScubaWatcher(FileSystemEventHandler):
    """
    Watches file system for changes and triggers incremental re-indexing.
    Uses watchdog for cross-platform file events.
    """

    def __init__(self, index_queue: asyncio.Queue, blocked_paths: list[str]):
        self.queue = index_queue
        self.blocked = [Path(p).expanduser() for p in blocked_paths]

    def _is_blocked(self, path: str) -> bool:
        p = Path(path)
        return any(p.is_relative_to(b) for b in self.blocked)

    def on_created(self, event):
        if not event.is_directory and not self._is_blocked(event.src_path):
            self.queue.put_nowait(("created", event.src_path))

    def on_modified(self, event):
        if not event.is_directory and not self._is_blocked(event.src_path):
            self.queue.put_nowait(("modified", event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            self.queue.put_nowait(("deleted", event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.queue.put_nowait(("moved", (event.src_path, event.dest_path)))
```

### 5.10 App Registry (intelligence/app_registry.py)

```python
import platform
import subprocess
import json
from pathlib import Path

# Category → search terms mapping
APP_CATEGORIES = {
    "photo_editing": ["photoshop", "gimp", "snapseed", "lightroom", "affinity photo", "pixelmator", "darktable"],
    "video_editing": ["premiere", "davinci", "final cut", "imovie", "kdenlive", "shotcut", "capcut"],
    "text_editor": ["notepad", "sublime", "textmate", "bbedit", "kate", "gedit"],
    "code_editor": ["visual studio code", "vscode", "intellij", "pycharm", "webstorm", "sublime", "vim", "neovim", "cursor"],
    "document_writing": ["word", "pages", "libreoffice writer", "google docs", "notion", "obsidian"],
    "spreadsheet": ["excel", "numbers", "libreoffice calc", "google sheets"],
    "presentation": ["powerpoint", "keynote", "libreoffice impress", "google slides"],
    "music_player": ["spotify", "apple music", "vlc", "foobar", "winamp", "audacity"],
    "web_browser": ["chrome", "firefox", "safari", "edge", "brave", "arc", "vivaldi"],
    "file_manager": ["finder", "explorer", "nautilus", "dolphin", "nemo"],
    "pdf_viewer": ["adobe", "preview", "foxit", "sumatra", "okular", "evince"],
    "image_viewer": ["preview", "photos", "irfanview", "xnview", "nomacs"],
}

def detect_installed_apps() -> list[dict]:
    """Detect installed applications and categorize them."""
    system = platform.system()
    if system == "Darwin":
        return _detect_macos_apps()
    elif system == "Windows":
        return _detect_windows_apps()
    else:
        return _detect_linux_apps()

def _detect_macos_apps() -> list[dict]:
    result = subprocess.run(
        ["mdfind", "kMDItemKind == 'Application'"],
        capture_output=True, text=True
    )
    apps = []
    for line in result.stdout.strip().split("\n"):
        if line:
            name = Path(line).stem
            categories = _categorize_app(name)
            apps.append({"name": name, "path": line, "categories": categories})
    return apps

def _detect_windows_apps() -> list[dict]:
    # Read from Start Menu + registry
    apps = []
    start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
    for lnk in start_menu.rglob("*.lnk"):
        name = lnk.stem
        categories = _categorize_app(name)
        apps.append({"name": name, "path": str(lnk), "categories": categories})
    return apps

def _categorize_app(name: str) -> list[str]:
    name_lower = name.lower()
    return [cat for cat, terms in APP_CATEGORIES.items() if any(t in name_lower for t in terms)]
```

---

## 6. Frontend Implementation Details

### 6.1 SpotlightBar Component

```typescript
// apps/frontend/app/components/SpotlightBar/SpotlightBar.tsx

interface SpotlightState {
  isOpen: boolean;
  query: string;
  results: SearchResult[];
  selectedIndex: number;
  isExpanded: boolean;           // file Q&A panel open
  phase: 'idle' | 'keyword' | 'semantic' | 'done';
}

// Keyboard shortcuts:
// Cmd+K / Ctrl+K  → open/close
// Escape          → close (or collapse panel first)
// ArrowUp/Down    → navigate results
// Enter           → open selected file
// Cmd+Enter       → ask about selected file (opens expandable panel)
// Tab             → autocomplete suggestion
```

### 6.2 Progressive Search Hook

```typescript
// apps/frontend/app/hooks/useSearch.ts

function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [phase, setPhase] = useState<'idle' | 'keyword' | 'semantic' | 'done'>('idle');
  const wsRef = useRef<WebSocket | null>(null);

  const search = useCallback((query: string) => {
    if (!query.trim()) { setResults([]); setPhase('idle'); return; }

    const ws = new WebSocket(`ws://localhost:8000/api/v1/search/stream`);
    wsRef.current = ws;

    ws.onopen = () => ws.send(JSON.stringify({ query, limit: 20 }));

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPhase(data.phase);

      if (data.phase === 'keyword') {
        setResults(data.results);                    // show immediately
      } else if (data.phase === 'semantic') {
        setResults(prev => mergeAndRerank(prev, data.results));  // blend in
      } else if (data.phase === 'activity') {
        setResults(prev => mergeAndRerank(prev, data.results));  // final rerank
      }
    };
  }, []);

  return { results, phase, search };
}
```

### 6.3 New Frontend Dependencies

```json
{
  "dependencies": {
    "next": "^16.1.6",
    "react": "^19.2.3",
    "react-dom": "^19.2.3",
    "swr": "^2.3.0",
    "lucide-react": "^0.470.0",
    "fuse.js": "^7.0.0",
    "react-hotkeys-hook": "^4.6.0",
    "react-markdown": "^9.0.0",
    "highlight.js": "^11.11.0"
  }
}
```

---

## 7. Embedding Model Comparison

| Model | Params | RAM | Latency/1K tokens | MTEB Score | Best For |
|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 22M | ~200MB | ~15ms | Low (outdated) | Prototyping only |
| **nomic-embed-text-v1.5** | 137M | ~500MB | ~42ms | High | **Default choice** — good quality, reasonable size |
| EmbeddingGemma | 308M | <200MB (quantized) | <15ms | Highest under 500M | Best quality if quantized model available |
| BGE-base-en-v1.5 | 110M | ~500MB | ~23ms | High | Alternative to nomic |
| E5-base-v2 | 110M | ~500MB | ~20ms | Very High | Best accuracy/speed balance |

**Recommendation for v0.1:** Start with `nomic-embed-text-v1.5` via `sentence-transformers`. Dimension: 384. Good quality, well-supported, runs on any CPU.

---

## 8. Phased Rollout — Detailed Checklists

### Phase 1: Hybrid Search + Spotlight UI

**Backend:**
- [ ] Create `db/schema.sql` with all CREATE TABLE statements
- [ ] Implement `db/connection.py` — SQLite connection with sqlite-vec loaded
- [ ] Migrate from JSON storage to SQLite — port existing traverser/extractor to write to SQLite
- [ ] Implement `search/keyword.py` — FTS5 search with BM25 ranking
- [ ] Implement `search/semantic.py` — embedding + sqlite-vec vector search
- [ ] Implement `search/hybrid.py` — fuse keyword + semantic results
- [ ] Implement `extractors/document.py` — PDF, Word, Excel, PPT, plain text
- [ ] Implement `extractors/registry.py` — extension → extractor mapping
- [ ] Implement `watcher/fs_watcher.py` — watchdog file system monitoring
- [ ] Implement `agent/privacy_proxy.py` — Presidio PII detection + payload logging
- [ ] Add WebSocket endpoint for progressive search streaming
- [ ] Add `/api/v1/search` REST endpoint
- [ ] Add `/api/v1/index/rebuild` and `/api/v1/index/status` endpoints
- [ ] Add `/api/v1/audit` endpoint for audit log access
- [ ] Implement `config.py` with all settings
- [ ] Background indexing task on startup (full machine scan)
- [ ] Incremental re-indexing via file watcher events

**Frontend:**
- [ ] Create `SpotlightBar` component — Cmd+K overlay, clean blank empty state
- [ ] Create `useSpotlight` hook — keyboard shortcut registration
- [ ] Create `ResultList` component — flat ranked list with file icon + name + snippet
- [ ] Create `ResultItem` component — individual result row
- [ ] Create `useSearch` hook — WebSocket progressive search
- [ ] Create `api.ts` — typed API client for all endpoints
- [ ] Wire SpotlightBar to search hook with debounced input (150ms)
- [ ] Show phase indicator: keyword results first, semantic blending in
- [ ] Keyboard navigation: ArrowUp/Down, Enter to open, Escape to close

**Testing:**
- [ ] Unit tests for keyword search (FTS5 queries)
- [ ] Unit tests for document extraction (PDF, Word, Excel)
- [ ] Unit tests for privacy proxy (PII detection)
- [ ] Integration test: index test_data → search → verify results
- [ ] Performance test: keyword search <50ms on 10K files
- [ ] Performance test: semantic search <500ms on 10K embeddings

### Phase 2: Vision + Content Intelligence + File Q&A

**Backend:**
- [ ] Implement `extractors/vision.py` — CLIP/SigLIP image tagging
- [ ] Implement `extractors/ocr.py` — Tesseract OCR wrapper
- [ ] Implement `extractors/media.py` — EXIF, ffprobe, ID3 metadata
- [ ] Add image tags to indexing pipeline (tag on index, store in `image_tags`)
- [ ] Add OCR text to `extracted_text` for screenshots/scanned docs
- [ ] Add CLIP image embeddings to `embeddings` table
- [ ] Implement `/api/v1/ask` endpoint — file Q&A with cloud LLM
- [ ] Implement conversation context for multi-turn Q&A
- [ ] Implement `intelligence/app_registry.py` — detect installed apps
- [ ] Add `/api/v1/apps/search?action={action}` endpoint
- [ ] Implement near-duplicate detection via content fingerprinting (SHA-256 + locality-sensitive hashing)

**Frontend:**
- [ ] Create `ExpandablePanel` component — expands below Spotlight for Q&A
- [ ] Add "Sending to cloud..." indicator with Presidio summary
- [ ] Add multi-turn conversation UI in expandable panel
- [ ] Render image thumbnails in search results
- [ ] Show CLIP tags as badges on image results
- [ ] Show OCR text snippets for screenshot results
- [ ] Add app launcher results (type "edit photos" → installed apps)

**Testing:**
- [ ] Unit tests for CLIP tagging (verify top-5 accuracy >85% on test images)
- [ ] Unit tests for OCR (verify >95% accuracy on screenshot samples)
- [ ] Unit tests for document extraction (all formats)
- [ ] Integration test: index images → search "sunset" → verify CLIP results
- [ ] Integration test: file Q&A → verify PII redaction in audit log

### Phase 3: Background Intelligence

**Backend:**
- [ ] Implement `intelligence/relationships.py`:
  - Version chain detection: Levenshtein distance on filenames + content hash similarity
  - Topic clustering: k-means on embedding vectors, auto-label clusters
  - Temporal bundling: group files modified within configurable time window (default: 1 hour)
  - Source tracking: parse download metadata (Chrome, Firefox download history DBs)
- [ ] Implement `intelligence/activity.py`:
  - ActivityWatch API client (GET `/api/0/buckets/{bucket_id}/events`)
  - Poll interval: every 60 seconds
  - Extract: file paths, access timestamps, duration
  - Calculate co-access scores (files opened within 5 minutes of each other)
- [ ] Implement `intelligence/proactive.py`:
  - Duplicate scanner: group by content_hash, alert on 2+ matches
  - Stale file detector: files not accessed in >90 days (configurable)
  - Large unused file detector: >50MB files not accessed in >30 days
  - Dead code detector: integrate Knip (JS/TS) and Vulture (Python) as subprocesses
- [ ] Implement `extractors/code.py` — tree-sitter AST parsing:
  - Parse imports, function definitions, class definitions
  - Build edges in `code_graph` table
  - Support: Python, JavaScript, TypeScript (add more grammars later)
- [ ] Add "related files" to search results using relationship graph
- [ ] Background job scheduler for periodic intelligence tasks (every 6 hours)

**Frontend:**
- [ ] Show "related files" as secondary suggestions below search results
- [ ] Proactive alerts panel (accessible from settings or system tray)
- [ ] Notification for duplicate/stale file detection

**Testing:**
- [ ] Unit tests for version chain detection
- [ ] Unit tests for temporal bundling
- [ ] Unit tests for tree-sitter code graph (Python imports)
- [ ] Integration test: ActivityWatch mock → verify ranking boost

### Phase 4: Agent + MCP Plugins

**Backend:**
- [ ] Implement `agent/engine.py` — orchestration:
  - Parse user intent via LLM tool-use
  - Generate execution plan as list of tool calls
  - Execute plan step-by-step with approval gates
  - Track progress and report to frontend
- [ ] Implement `agent/tools.py` — tool definitions:
  - `search_files`: search the index
  - `open_file`: open file in default app
  - `move_file`: move with undo metadata
  - `copy_file`: copy to destination
  - `rename_file`: rename with undo
  - `delete_file`: soft-delete with undo window
  - `create_folder`: create directory
  - `batch_operation`: chain multiple operations
- [ ] Implement `agent/memory.py` — persistent memory:
  - Auto-learn: track user preferences (e.g., "always opens .psd with Photoshop")
  - User-taught: explicit "remember: my tax folder is D:/Finance"
  - Memory retrieval during search for context
- [ ] Implement MCP client host:
  - JSON-RPC 2.0 over stdio transport
  - Dynamic tool discovery from MCP servers
  - Configuration via `~/.scuba/mcp.json`
- [ ] Add `/api/v1/agent/execute` and `/api/v1/agent/approve` endpoints

**Frontend:**
- [ ] Create `WorkflowProgress` component — step-by-step execution view
- [ ] Approval modal for destructive operations
- [ ] Memory management UI (view, edit, delete learned preferences)

**Testing:**
- [ ] Unit tests for plan generation
- [ ] Unit tests for tool execution (mock file system)
- [ ] Integration test: "move old screenshots to archive" → verify plan + execution
- [ ] Test approval gate blocks destructive actions without consent

### Phase 5: Tauri Desktop Shell

- [ ] Initialize Tauri project wrapping the Next.js frontend
- [ ] Global hotkey registration (configurable, default: `Ctrl+Space`)
- [ ] System tray icon with status indicator (indexing/idle/error)
- [ ] Background indexing daemon (runs on login)
- [ ] Auto-update mechanism
- [ ] Platform-specific installers:
  - macOS: `.dmg`
  - Windows: `.msi` via WiX
  - Linux: `.AppImage` + `.deb`
- [ ] Target binary size: <50MB

---

## 9. Competitive Advantages

| Feature | Apple Spotlight | Raycast ($16-18/mo) | Scuba v0.1 (Free, OSS) |
|---|---|---|---|
| Semantic search | No | No | Local embeddings |
| Image understanding | Basic (macOS Tahoe) | No | CLIP + OCR |
| File Q&A | No | Cloud AI (no file context) | Expandable panel with context |
| Privacy transparency | Opaque | "We don't log" | Payload receipt in audit log |
| PII protection | On-device ML | None | Microsoft Presidio |
| File relationships | No | No | Background graph |
| Activity-aware ranking | Basic recency | Frecency | ActivityWatch integration |
| Extensibility | None | Custom TS (unsandboxed) | MCP standard (5,800+ servers) |
| Persistent memory | No | No | Cross-session learning |
| Platform | macOS only | macOS + Windows beta | Cross-platform day 1 |
| Code | Closed | Closed | Open source |

---

## 10. Non-Goals

- Cloud file storage / sync
- Multi-user / authentication
- Full file manager (Finder/Explorer replacement)
- Arbitrary code execution
- Model training / fine-tuning
- Mobile app

---

## 11. Success Metrics

| Metric | Target |
|---|---|
| Keyword search latency | <50ms on 100K files |
| Semantic search latency | <500ms on 100K embeddings |
| CLIP tag accuracy | >85% top-5 on common objects |
| OCR accuracy | >95% on screenshots |
| PII detection rate | >90% on English text |
| Zero content leakage | Every cloud payload auditable |
| Full-machine index time | <1 hour on first run (500K files) |
| RAM at idle | <200MB (without vision model loaded) |
| Tauri binary size | <50MB |
