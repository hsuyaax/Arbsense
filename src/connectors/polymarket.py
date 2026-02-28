"""Polymarket CLOB API connector — fetches live prediction markets.

Polymarket's CLOB (Central Limit Order Book) API is public and requires
no authentication for reading market data.

Endpoints used:
  GET https://clob.polymarket.com/markets       — paginated market list
  GET https://gamma-api.polymarket.com/markets   — gamma API (richer metadata)
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# We fetch active, binary markets with reasonable volume
_GAMMA_PARAMS: dict[str, Any] = {
    "active": True,
    "closed": False,
    "limit": 100,
    "order": "volume24hr",
    "ascending": False,
}

# Tags / categories likely to overlap with Kalshi
_PRIORITY_KEYWORDS = [
    "iran", "fed", "interest rate", "trump", "pope", "mars",
    "bitcoin", "btc", "ethereum", "recession", "gdp", "election",
    "ai", "tariff", "china", "ukraine", "russia", "nato",
    "tesla", "nvidia", "apple", "google", "spacex", "tiktok",
    "supreme court", "congress", "senate", "climate", "temperature",
]


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def fetch_polymarket_markets(limit: int = 30) -> list[dict[str, Any]]:
    """Fetch active binary markets from Polymarket Gamma API.

    Returns normalized ArbSense market dicts.
    """
    markets: list[dict[str, Any]] = []

    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={**_GAMMA_PARAMS, "limit": min(limit * 2, 100)},
            timeout=15,
        )
        resp.raise_for_status()
        raw_markets = resp.json()
    except Exception as exc:
        logger.warning("Polymarket Gamma API fetch failed: %s", exc)
        # Fallback to CLOB API
        try:
            resp = requests.get(
                f"{CLOB_API}/markets",
                params={"next_cursor": "MA=="},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            raw_markets = data.get("data", data) if isinstance(data, dict) else data
        except Exception as exc2:
            logger.error("Polymarket CLOB API also failed: %s", exc2)
            return []

    if not isinstance(raw_markets, list):
        raw_markets = raw_markets.get("data", []) if isinstance(raw_markets, dict) else []

    for item in raw_markets:
        if not isinstance(item, dict):
            continue

        # Skip non-binary or inactive markets
        outcomes = item.get("outcomes", [])
        if isinstance(outcomes, str):
            # Gamma API returns outcomes as JSON string sometimes
            import json
            try:
                outcomes = json.loads(outcomes)
            except Exception:
                outcomes = ["Yes", "No"]

        if len(outcomes) != 2:
            continue

        # Extract prices from tokens or outcome_prices
        tokens = item.get("tokens", [])
        outcome_prices = item.get("outcomePrices", item.get("outcome_prices", []))
        if isinstance(outcome_prices, str):
            import json
            try:
                outcome_prices = json.loads(outcome_prices)
            except Exception:
                outcome_prices = []

        yes_price = 0.5
        no_price = 0.5

        if tokens and len(tokens) >= 2:
            yes_price = _safe_float(tokens[0].get("price", 0.5), 0.5)
            no_price = _safe_float(tokens[1].get("price", 0.5), 0.5)
        elif outcome_prices and len(outcome_prices) >= 2:
            yes_price = _safe_float(outcome_prices[0], 0.5)
            no_price = _safe_float(outcome_prices[1], 0.5)

        # Skip markets with no real price data
        if yes_price == 0 and no_price == 0:
            continue

        volume = _safe_float(item.get("volume", item.get("volume24hr", 0)))
        liquidity = _safe_float(item.get("liquidity", volume / 2 if volume else 5000))

        title = str(item.get("question", item.get("title", "")))
        description = str(item.get("description", title))
        end_date = str(item.get("end_date_iso", item.get("endDate", item.get("resolution_date", ""))))

        # Normalize date to YYYY-MM-DD
        if end_date and "T" in end_date:
            end_date = end_date.split("T")[0]

        category = str(item.get("category", item.get("groupItemTitle", "general"))).lower()
        market_id = str(item.get("condition_id", item.get("id", item.get("slug", ""))))

        if not title:
            continue

        markets.append({
            "platform": "Polymarket",
            "market_id": f"poly-{market_id[:20]}",
            "title": title,
            "description": description[:300],
            "outcomes": [
                {"name": "Yes", "price": round(yes_price, 4), "liquidity": round(liquidity / 2)},
                {"name": "No", "price": round(no_price, 4), "liquidity": round(liquidity / 2)},
            ],
            "resolution_date": end_date or "2025-12-31",
            "category": category if category else "general",
        })

        if len(markets) >= limit * 2:
            break

    # Sort: priority keywords first, then by price variance from 0.5 (more interesting)
    def _priority(m: dict[str, Any]) -> tuple[int, float]:
        title_lower = m["title"].lower()
        is_priority = any(kw in title_lower for kw in _PRIORITY_KEYWORDS)
        yes_p = m["outcomes"][0]["price"]
        variance = abs(yes_p - 0.5)  # closer to 0.5 = more uncertain = more interesting
        return (0 if is_priority else 1, variance)

    markets.sort(key=_priority)
    markets = markets[:limit]

    logger.info("Polymarket: fetched %d markets", len(markets))
    return markets
