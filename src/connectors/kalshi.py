"""Kalshi API connector — fetches live prediction markets.

Kalshi's public API requires no authentication for reading market data.
We use the events endpoint to discover real single-event markets (not parlays).

Endpoints used:
  GET https://api.elections.kalshi.com/trade-api/v2/events   — event discovery
  GET https://api.elections.kalshi.com/trade-api/v2/markets   — markets by series
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"
_HEADERS = {"Accept": "application/json", "User-Agent": "ArbSense/1.0"}


def _safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _category_map(raw: str) -> str:
    """Map Kalshi category names to ArbSense categories."""
    low = raw.lower()
    if "politic" in low or "elect" in low or "congress" in low:
        return "politics"
    if "climate" in low or "weather" in low:
        return "science"
    if "econ" in low or "financ" in low or "fed" in low:
        return "macro"
    if "tech" in low or "science" in low or "ai" in low:
        return "technology"
    if "crypto" in low or "bitcoin" in low:
        return "crypto"
    if "sport" in low:
        return "sports"
    return "general"


def _normalize_market(m: dict[str, Any], event_title: str, event_category: str) -> dict[str, Any] | None:
    """Normalize a single Kalshi market to ArbSense schema."""
    ticker = m.get("ticker", "")

    # Skip parlay/combo markets
    if ticker.startswith("KXMVE"):
        return None

    # Kalshi prices are in cents (0-100)
    yes_bid = _safe_float(m.get("yes_bid", 0)) / 100.0
    yes_ask = _safe_float(m.get("yes_ask", 0)) / 100.0
    last_price = _safe_float(m.get("last_price", 0)) / 100.0

    yes_price = last_price if last_price > 0 else (yes_bid + yes_ask) / 2.0 if (yes_bid + yes_ask) > 0 else 0.0
    no_price = 1.0 - yes_price if yes_price > 0 else 0.0

    if yes_price <= 0 and no_price <= 0:
        return None

    volume = _safe_float(m.get("volume", 0))
    open_interest = _safe_float(m.get("open_interest", 0))
    liquidity_est = max(volume * 0.5, open_interest * 5, 3000)

    title = str(m.get("title", event_title))
    subtitle = str(m.get("subtitle", ""))
    if subtitle and subtitle != title:
        title = f"{title} — {subtitle}" if len(title) < 40 else title

    end_date = str(m.get("close_time", m.get("expiration_time", "")))
    if end_date and "T" in end_date:
        end_date = end_date.split("T")[0]

    if not title:
        return None

    return {
        "platform": "Kalshi",
        "market_id": f"kalshi-{ticker[:24]}",
        "title": title,
        "description": str(m.get("rules_primary", title))[:300],
        "outcomes": [
            {"name": "Yes", "price": round(yes_price, 4), "liquidity": round(liquidity_est / 2)},
            {"name": "No", "price": round(no_price, 4), "liquidity": round(liquidity_est / 2)},
        ],
        "resolution_date": end_date or "2026-12-31",
        "category": _category_map(event_category),
    }


def fetch_kalshi_markets(limit: int = 30) -> list[dict[str, Any]]:
    """Fetch active markets from Kalshi via the events discovery endpoint.

    Returns normalized ArbSense market dicts.
    """
    markets: list[dict[str, Any]] = []
    seen_tickers: set[str] = set()

    # Step 1: Fetch events (which contain series tickers)
    try:
        resp = requests.get(
            f"{KALSHI_API}/events",
            params={"limit": 100, "status": "open", "with_nested_markets": "true"},
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        events = resp.json().get("events", [])
    except Exception as exc:
        logger.warning("Kalshi events API failed: %s", exc)
        return []

    # Step 2: Collect nested markets from events
    for event in events:
        event_title = event.get("title", "")
        event_category = event.get("category", "")

        for raw_market in event.get("markets", []):
            ticker = raw_market.get("ticker", "")
            if ticker in seen_tickers:
                continue
            seen_tickers.add(ticker)

            normalized = _normalize_market(raw_market, event_title, event_category)
            if normalized:
                markets.append(normalized)

        if len(markets) >= limit:
            break

    # Step 3: Fetch more markets by series if we need more
    if len(markets) < limit:
        for event in events:
            series_ticker = event.get("series_ticker", "")
            if not series_ticker:
                continue
            try:
                resp2 = requests.get(
                    f"{KALSHI_API}/markets",
                    params={"limit": 10, "series_ticker": series_ticker, "status": "open"},
                    headers=_HEADERS,
                    timeout=10,
                )
                for raw_market in resp2.json().get("markets", []):
                    ticker = raw_market.get("ticker", "")
                    if ticker in seen_tickers:
                        continue
                    seen_tickers.add(ticker)

                    normalized = _normalize_market(raw_market, event.get("title", ""), event.get("category", ""))
                    if normalized:
                        markets.append(normalized)
            except Exception:
                continue

            if len(markets) >= limit:
                break

    markets = markets[:limit]
    logger.info("Kalshi: fetched %d markets", len(markets))
    return markets
