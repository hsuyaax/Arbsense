"""Market quality scoring for ArbSense."""

from __future__ import annotations

import re
from typing import Any


def quality_grade(score: int) -> str:
    """Convert numeric quality score to letter grade."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def score_market_quality(market: dict[str, Any]) -> tuple[int, str, str]:
    """Return deterministic quality score, grade, and concise reasoning."""
    score = 50
    reasons: list[str] = []

    title = str(market.get("title", ""))
    description = str(market.get("description", ""))
    date_text = str(market.get("resolution_date", ""))
    outcomes = market.get("outcomes", [])

    if len(title.split()) >= 5:
        score += 8
        reasons.append("clear title")
    if len(description.split()) >= 10:
        score += 12
        reasons.append("detailed criteria")
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_text):
        score += 10
        reasons.append("explicit deadline")
    if isinstance(outcomes, list) and len(outcomes) == 2:
        names = {str(o.get("name", "")).strip().lower() for o in outcomes if isinstance(o, dict)}
        if names == {"yes", "no"}:
            score += 10
            reasons.append("binary outcomes")

    ambiguous_terms = {"soon", "maybe", "could", "someday", "eventually"}
    text = f"{title} {description}".lower()
    if any(term in text for term in ambiguous_terms):
        score -= 15
        reasons.append("ambiguous phrasing")

    spam_terms = {"world end", "guaranteed moon", "1000x"}
    if any(term in text for term in spam_terms):
        score -= 20
        reasons.append("speculative/spam signals")

    score = max(0, min(100, score))
    grade = quality_grade(score)
    reasoning = ", ".join(reasons) if reasons else "baseline clarity"
    return score, grade, reasoning


def enrich_with_quality_scores(markets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add quality score metadata to each market."""
    enriched: list[dict[str, Any]] = []
    for market in markets:
        score, grade, reasoning = score_market_quality(market)
        market_with_quality = dict(market)
        market_with_quality["quality_score"] = score
        market_with_quality["quality_grade"] = grade
        market_with_quality["quality_reasoning"] = reasoning
        enriched.append(market_with_quality)
    return enriched
