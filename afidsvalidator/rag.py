"""RAG (Retrieval-Augmented Generation) for the AFIDs guided learning mode.

Knowledge chunks (landmark definitions, protocol passages, etc.) are stored in
PostgreSQL alongside their embeddings. At query time the most semantically
relevant chunks are retrieved and injected into the LLM context window,
replacing the large static landmark block with targeted, query-specific context.

Quick start
-----------
1. Apply migrations to create the knowledge_chunks table:
       flask db upgrade

2. Ingest the 32 AFIDs landmark definitions (takes ~30 s with OpenAI embeddings):
       flask ingest-knowledge

3. (Optional) Ingest additional text documents such as the AFIDs protocol paper:
       flask ingest-knowledge --file afids_paper.txt --source afids_paper

Embedding model configuration
------------------------------
Uses the same LLM_API_KEY / LLM_BASE_URL environment variables as llm.py.

  EMBED_MODEL  — Embedding model name.
                 Defaults to  text-embedding-3-small  when LLM_API_KEY is set,
                 or  nomic-embed-text  when running against local Ollama.
                 Examples: text-embedding-3-small, nomic-embed-text,
                           mxbai-embed-large, text-embedding-ada-002

Embeddings are stored as JSON-encoded float lists in a standard Text column, so
no Postgres extensions are required. Cosine similarity is computed in NumPy.
For production deployments with larger knowledge bases the column can be
migrated to pgvector's native vector type and an HNSW index added — the retrieval
interface in this module stays unchanged.
"""

from __future__ import annotations

import json
import os

import numpy as np
from sqlalchemy import Column, Integer, String, Text

from afidsvalidator.landmark_info import LANDMARK_INFO
from afidsvalidator.model import db

# ── SQLAlchemy model ──────────────────────────────────────────────────────────


class KnowledgeChunk(db.Model):
    """One chunk of domain knowledge and its embedding vector."""

    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True)
    # Where the text came from: "landmark_info", "afids_paper", …
    source = Column(String(256), nullable=False)
    # AFIDs abbreviation this chunk is primarily about ("AC", "PC", …), or
    # None for general / cross-landmark text.
    landmark_tag = Column(String(32), nullable=True)
    chunk_text = Column(Text, nullable=False)
    # JSON-encoded list[float] — the embedding produced by embed_text()
    embedding_json = Column(Text, nullable=True)


# ── Embedding helpers ─────────────────────────────────────────────────────────

_OLLAMA_DEFAULT_URL = "http://localhost:11434/v1"
_OPENAI_DEFAULT_URL = "https://api.openai.com/v1"


def _embed_base_url() -> str:
    if os.environ.get("LLM_API_KEY"):
        return os.environ.get("LLM_BASE_URL", _OPENAI_DEFAULT_URL)
    return os.environ.get("LLM_BASE_URL", _OLLAMA_DEFAULT_URL)


def _embed_model() -> str:
    if "EMBED_MODEL" in os.environ:
        return os.environ["EMBED_MODEL"]
    return (
        "text-embedding-3-small"
        if os.environ.get("LLM_API_KEY")
        else "nomic-embed-text"
    )


def embed_text(text: str) -> list[float]:
    """Return a raw embedding vector for *text* from the configured model."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required. Install it with: poetry add openai"
        ) from exc

    api_key = os.environ.get("LLM_API_KEY", "ollama")
    client = OpenAI(api_key=api_key, base_url=_embed_base_url())
    resp = client.embeddings.create(model=_embed_model(), input=text)
    return resp.data[0].embedding


# ── Similarity ────────────────────────────────────────────────────────────────


def _cosine(a: list[float], b: list[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    return float(np.dot(va, vb) / denom) if denom > 0 else 0.0


# ── Retrieval ─────────────────────────────────────────────────────────────────


def retrieve(
    query: str,
    landmark_hint: str | None = None,
    top_k: int = 4,
) -> list[str]:
    """Return the *top_k* most relevant chunk texts for *query*.

    Falls back to the hard-coded landmark dictionary when the knowledge_chunks
    table is empty or an error occurs, so the tutoring mode degrades gracefully
    before ``flask ingest-knowledge`` has been run.

    Parameters
    ----------
    query:
        Free-text query — landmark name, anatomy question, error description, …
    landmark_hint:
        AFIDs abbreviation of the landmark the user is currently working on.
        Chunks tagged with this landmark receive a +0.25 cosine-similarity boost
        so they rank higher than equally-relevant general passages.
    top_k:
        Maximum number of chunks to return (default 4).
    """
    try:
        return _db_retrieve(query, landmark_hint, top_k)
    except Exception:  # noqa: BLE001 — graceful degradation
        return _fallback_retrieve(landmark_hint)


def _db_retrieve(
    query: str,
    landmark_hint: str | None,
    top_k: int,
) -> list[str]:
    rows = (
        db.session.query(KnowledgeChunk)
        .filter(KnowledgeChunk.embedding_json.isnot(None))
        .all()
    )
    if not rows:
        return _fallback_retrieve(landmark_hint)

    q_vec = embed_text(query)
    scored: list[tuple[float, str]] = []
    for row in rows:
        vec = json.loads(row.embedding_json)
        sim = _cosine(q_vec, vec)
        if row.landmark_tag == landmark_hint:
            sim += 0.25
        scored.append((sim, row.chunk_text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]


def _fallback_retrieve(landmark_hint: str | None) -> list[str]:
    """Return hard-coded landmark info when the DB is unavailable or empty."""
    if landmark_hint and landmark_hint in LANDMARK_INFO:
        info = LANDMARK_INFO[landmark_hint]
        return [
            f"{landmark_hint} — {info['full_name']}\n"
            f"Description: {info['description']}\n"
            f"Key features on MRI: {info['key_features']}\n"
            f"Common mistakes: {info['common_mistakes']}"
        ]
    return []


# ── Ingestion ─────────────────────────────────────────────────────────────────


def ingest_landmarks() -> int:
    """Embed and store all 32 AFIDs landmark definitions.

    Existing ``landmark_info`` rows are replaced on each run (idempotent).
    Returns the number of chunks written.
    """
    count = 0
    for abbrev, info in LANDMARK_INFO.items():
        text = (
            f"{abbrev} — {info['full_name']}\n"
            f"Description: {info['description']}\n"
            f"Key features on MRI: {info['key_features']}\n"
            f"Common mistakes: {info['common_mistakes']}"
        )
        db.session.query(KnowledgeChunk).filter_by(
            source="landmark_info", landmark_tag=abbrev
        ).delete()
        db.session.add(
            KnowledgeChunk(
                source="landmark_info",
                landmark_tag=abbrev,
                chunk_text=text,
                embedding_json=json.dumps(embed_text(text)),
            )
        )
        count += 1

    db.session.commit()
    return count


def ingest_text_file(path: str, source: str) -> int:
    """Chunk and ingest a plain-text document (e.g. the AFIDs protocol paper).

    Splits on blank lines (paragraph boundaries), filters fragments shorter
    than 80 characters, and stores each chunk with its embedding.
    Existing rows for *source* are replaced on each run.
    Returns the number of chunks written.
    """
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()

    paragraphs = [p.strip() for p in raw.split("\n\n") if len(p.strip()) >= 80]

    db.session.query(KnowledgeChunk).filter_by(source=source).delete()

    count = 0
    for para in paragraphs:
        db.session.add(
            KnowledgeChunk(
                source=source,
                landmark_tag=None,
                chunk_text=para,
                embedding_json=json.dumps(embed_text(para)),
            )
        )
        count += 1

    db.session.commit()
    return count
