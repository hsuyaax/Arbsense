"""Embedding generation and cosine-similarity candidate matching."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from src.config import Settings

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - dependency may be unavailable in setup
    OpenAI = None  # type: ignore[assignment]


def create_market_text(market: dict[str, Any]) -> str:
    """Create a rich market text for semantic embedding."""
    outcomes = market.get("outcomes", [])
    outcome_part = ", ".join(
        [f"{o.get('name', '')}:{o.get('price', '')}" for o in outcomes if isinstance(o, dict)]
    )
    return (
        f"Title: {market.get('title', '')}\n"
        f"Description: {market.get('description', '')}\n"
        f"Category: {market.get('category', '')}\n"
        f"Resolution: {market.get('resolution_date', '')}\n"
        f"Outcomes: {outcome_part}"
    )


def _normalize(vector: list[float]) -> list[float]:
    """Return L2-normalized vector."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def _deterministic_local_embedding(text: str, dims: int = 96) -> list[float]:
    """Deterministic local embedding fallback when APIs/dependencies are unavailable."""
    vec = [0.0] * dims
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    features = list(tokens)
    features.extend([f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)])

    for token in features:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "big") % dims
        weight = 0.25 + (digest[3] / 255.0)
        vec[idx] += weight
    return _normalize(vec)


def _embed_with_openai(
    settings: Settings, inputs: list[str], max_items: int
) -> tuple[list[list[float]], str]:
    """Call OpenAI embeddings API with simple per-run guardrails."""
    if OpenAI is None:
        raise RuntimeError("openai package is unavailable")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")
    if len(inputs) > max_items:
        raise RuntimeError(
            f"Embedding limit exceeded: {len(inputs)} > {max_items} for this run."
        )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.embedding_model, input=inputs)
    vectors = [list(item.embedding) for item in response.data]
    return vectors, "openai"


def embed_all_markets(
    markets: list[dict[str, Any]], settings: Settings
) -> tuple[list[dict[str, Any]], str]:
    """Embed all markets and return records containing vector + market metadata."""
    texts = [create_market_text(m) for m in markets]

    try:
        vectors, provider = _embed_with_openai(
            settings=settings,
            inputs=texts,
            max_items=settings.max_embedding_inputs_per_run,
        )
    except Exception:
        vectors = [_deterministic_local_embedding(text) for text in texts]
        provider = "local_fallback"

    records: list[dict[str, Any]] = []
    for market, text, vector in zip(markets, texts, vectors):
        records.append(
            {
                "platform": market.get("platform"),
                "market_id": market.get("market_id"),
                "title": market.get("title"),
                "resolution_date": market.get("resolution_date"),
                "category": market.get("category"),
                "text": text,
                "vector": vector,
                "market": market,
            }
        )
    return records, provider


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_candidate_pairs(
    embedded_records: list[dict[str, Any]], threshold: float = 0.70
) -> list[dict[str, Any]]:
    """Find candidate cross-platform pairs above cosine similarity threshold."""
    candidates: list[dict[str, Any]] = []
    total = len(embedded_records)
    for i in range(total):
        a = embedded_records[i]
        for j in range(i + 1, total):
            b = embedded_records[j]
            if a.get("platform") == b.get("platform"):
                continue
            score = cosine_similarity(a["vector"], b["vector"])
            if score >= threshold:
                candidates.append(
                    {
                        "similarity_score": round(score, 6),
                        "market_a": a["market"],
                        "market_b": b["market"],
                    }
                )
    candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
    return candidates


def save_json(payload: dict[str, Any], output_path: Path) -> None:
    """Write JSON payload to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
