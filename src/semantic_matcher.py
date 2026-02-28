"""LLM-backed semantic verification for candidate market pairs."""

from __future__ import annotations

import json
import re
from typing import Any

from src.config import Settings

try:
    from anthropic import Anthropic
except ModuleNotFoundError:  # pragma: no cover
    Anthropic = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


def _verification_prompt(
    market_a: dict[str, Any], market_b: dict[str, Any], similarity_score: float
) -> str:
    """Build a strict JSON-only prompt for semantic verification."""
    return f"""
You are a strict prediction-market arbitrage verifier.
Prioritize precision over recall. Reject uncertain matches.

Compare these markets:

Market A:
{json.dumps(market_a, indent=2)}

Market B:
{json.dumps(market_b, indent=2)}

Embedding similarity score: {similarity_score:.6f}

Rules:
1) Return JSON only, no markdown.
2) is_match=true only if BOTH markets refer to the same underlying event AND compatible resolution rules.
3) If resolution source/timing/criteria differ materially, set is_match=false.
4) confidence must be 0.0-1.0.
5) arbitrage_safe=true only when outcome mapping is clear and no major resolution divergence risk.
6) reasoning must be concise but concrete.

JSON schema:
{{
  "is_match": true or false,
  "confidence": 0.0,
  "reasoning": "short explanation",
  "event_summary": "one sentence",
  "outcome_mapping": [{{"a_outcome": "Yes", "b_outcome": "Yes", "relation": "equivalent"}}],
  "key_differences": ["..."],
  "risk_factors": ["..."],
  "arbitrage_safe": true or false,
  "resolution_conflict_score": 0,
  "resolution_verdict": "SAFE | CAUTION | DANGER",
  "resolution_analysis": "specific resolution-trap analysis"
}}
""".strip()


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON object from model output safely."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")
    return json.loads(match.group(0))


def _validate_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate verifier result shape."""
    result = {
        "is_match": bool(raw.get("is_match", False)),
        "confidence": float(raw.get("confidence", 0.0)),
        "reasoning": str(raw.get("reasoning", "")),
        "event_summary": str(raw.get("event_summary", "")),
        "outcome_mapping": raw.get("outcome_mapping", []),
        "key_differences": raw.get("key_differences", []),
        "risk_factors": raw.get("risk_factors", []),
        "arbitrage_safe": bool(raw.get("arbitrage_safe", False)),
        "resolution_conflict_score": int(raw.get("resolution_conflict_score", 50)),
        "resolution_verdict": str(raw.get("resolution_verdict", "CAUTION")).upper(),
        "resolution_analysis": str(raw.get("resolution_analysis", "")),
    }
    result["confidence"] = max(0.0, min(1.0, result["confidence"]))
    result["resolution_conflict_score"] = max(0, min(100, result["resolution_conflict_score"]))
    if result["resolution_verdict"] not in {"SAFE", "CAUTION", "DANGER"}:
        result["resolution_verdict"] = "CAUTION"
    return result


def _local_precision_fallback(
    market_a: dict[str, Any], market_b: dict[str, Any], similarity_score: float
) -> dict[str, Any]:
    """Deterministic precision-first fallback verifier for offline mode."""
    title_a = str(market_a.get("title", "")).lower()
    title_b = str(market_b.get("title", "")).lower()
    desc_a = str(market_a.get("description", "")).lower()
    desc_b = str(market_b.get("description", "")).lower()
    text_a = f"{title_a} {desc_a}"
    text_b = f"{title_b} {desc_b}"

    date_a = str(market_a.get("resolution_date", ""))
    date_b = str(market_b.get("resolution_date", ""))
    cat_a = str(market_a.get("category", "")).lower()
    cat_b = str(market_b.get("category", "")).lower()

    def score_overlap(lhs: str, rhs: str) -> float:
        lhs_tokens = set(re.findall(r"[a-z0-9]+", lhs))
        rhs_tokens = set(re.findall(r"[a-z0-9]+", rhs))
        if not lhs_tokens or not rhs_tokens:
            return 0.0
        inter = len(lhs_tokens.intersection(rhs_tokens))
        union = len(lhs_tokens.union(rhs_tokens))
        return inter / union

    overlap = score_overlap(text_a, text_b)
    common_tokens = set(re.findall(r"[a-z0-9]+", text_a)).intersection(
        set(re.findall(r"[a-z0-9]+", text_b))
    )
    strong_token_hit = any(
        token in common_tokens
        for token in {"bitcoin", "india", "world", "cup", "mars", "usdc", "ethereum", "gold", "recession", "solana", "etf", "gdp"}
    )
    same_date = date_a == date_b and bool(date_a)
    same_category = cat_a == cat_b and bool(cat_a)
    precision_gate = (
        similarity_score >= 0.71
        and overlap >= 0.24
        and same_category
        and same_date
        and strong_token_hit
    )
    confidence = min(
        0.97,
        max(
            0.05,
            (similarity_score * 0.5)
            + (overlap * 0.3)
            + (0.1 if same_date else 0.0)
            + (0.1 if same_category else 0.0)
            + (0.08 if strong_token_hit else 0.0),
        ),
    )

    is_match = bool(precision_gate)
    if not is_match:
        risk_score = 75
    elif same_date and same_category and overlap >= 0.35:
        risk_score = 18
    elif same_date:
        risk_score = 42
    else:
        risk_score = 64
    risk_score = max(0, min(100, int(risk_score)))
    resolution_verdict = "SAFE" if risk_score < 30 else ("DANGER" if risk_score > 70 else "CAUTION")
    arbitrage_safe = bool(is_match and confidence >= 0.78 and resolution_verdict == "SAFE")

    return {
        "is_match": is_match,
        "confidence": round(confidence, 4),
        "reasoning": (
            "High lexical/semantic overlap with aligned category and resolution date."
            if is_match
            else "Insufficient strict overlap under precision-first policy."
        ),
        "event_summary": market_a.get("title", ""),
        "outcome_mapping": [
            {"a_outcome": "Yes", "b_outcome": "Yes", "relation": "equivalent"},
            {"a_outcome": "No", "b_outcome": "No", "relation": "equivalent"},
        ],
        "key_differences": [] if is_match else ["Potential mismatch in event framing or semantics."],
        "risk_factors": [] if arbitrage_safe else ["Resolution criteria may diverge across platforms."],
        "arbitrage_safe": arbitrage_safe,
        "resolution_conflict_score": risk_score,
        "resolution_verdict": resolution_verdict,
        "resolution_analysis": (
            "Low conflict: aligned category, deadline, and event phrasing."
            if resolution_verdict == "SAFE"
            else (
                "Medium conflict: probable wording ambiguity or criteria differences."
                if resolution_verdict == "CAUTION"
                else "High conflict: likely divergent resolution criteria."
            )
        ),
    }


def _verify_with_anthropic(
    settings: Settings, market_a: dict[str, Any], market_b: dict[str, Any], similarity_score: float
) -> dict[str, Any]:
    """Verify using Anthropic API."""
    if Anthropic is None:
        raise RuntimeError("anthropic package unavailable")
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")

    client = Anthropic(api_key=settings.anthropic_api_key)
    prompt = _verification_prompt(market_a, market_b, similarity_score)
    response = client.messages.create(
        model=settings.verifier_model,
        max_tokens=900,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    content = ""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            content += block.text
    return _validate_result(_extract_json(content))


def _verify_with_openai(
    settings: Settings, market_a: dict[str, Any], market_b: dict[str, Any], similarity_score: float
) -> dict[str, Any]:
    """Fallback verification using OpenAI chat model."""
    if OpenAI is None:
        raise RuntimeError("openai package unavailable")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = _verification_prompt(market_a, market_b, similarity_score)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content or "{}"
    return _validate_result(_extract_json(content))


def verify_pair(
    market_a: dict[str, Any], market_b: dict[str, Any], similarity_score: float, settings: Settings
) -> tuple[dict[str, Any], str]:
    """Verify one candidate pair using Anthropic, then OpenAI, then local fallback."""
    try:
        return _verify_with_anthropic(settings, market_a, market_b, similarity_score), "anthropic"
    except Exception:
        try:
            return _verify_with_openai(settings, market_a, market_b, similarity_score), "openai"
        except Exception:
            return _local_precision_fallback(market_a, market_b, similarity_score), "local_fallback"


def verify_candidate_pairs(
    candidate_pairs: list[dict[str, Any]], settings: Settings
) -> tuple[list[dict[str, Any]], str]:
    """Verify candidate pairs with per-run call guardrails."""
    limit = settings.max_verification_calls_per_run
    selected = candidate_pairs[:limit]

    verified: list[dict[str, Any]] = []
    provider_used = "local_fallback"
    for pair in selected:
        result, provider = verify_pair(
            market_a=pair["market_a"],
            market_b=pair["market_b"],
            similarity_score=float(pair["similarity_score"]),
            settings=settings,
        )
        provider_used = provider
        verified.append(
            {
                "similarity_score": pair["similarity_score"],
                "market_a": pair["market_a"],
                "market_b": pair["market_b"],
                "verification": result,
                "time_decay_days": _resolution_day_gap(pair["market_a"], pair["market_b"]),
            }
        )

    verified.sort(key=lambda x: x["verification"]["confidence"], reverse=True)
    return verified, provider_used


def _resolution_day_gap(market_a: dict[str, Any], market_b: dict[str, Any]) -> int | None:
    """Return absolute resolution-date gap in days, when parseable."""
    from datetime import date

    da = str(market_a.get("resolution_date", ""))
    db = str(market_b.get("resolution_date", ""))
    try:
        d1 = date.fromisoformat(da)
        d2 = date.fromisoformat(db)
    except ValueError:
        return None
    return abs((d1 - d2).days)
