"""Arbitrage detection and scoring from verified market matches."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


def _extract_yes_no_prices(market: dict[str, Any]) -> tuple[float, float]:
    """Return (yes_price, no_price) from normalized outcomes."""
    yes_price = 0.0
    no_price = 0.0
    for outcome in market.get("outcomes", []):
        name = str(outcome.get("name", "")).strip().lower()
        if name == "yes":
            yes_price = float(outcome.get("price", 0.0))
        elif name == "no":
            no_price = float(outcome.get("price", 0.0))
    return yes_price, no_price


def _extract_min_liquidity(market: dict[str, Any]) -> float:
    """Get minimum side liquidity for conservative sizing."""
    liquidities = [float(o.get("liquidity", 0.0)) for o in market.get("outcomes", [])]
    return min(liquidities) if liquidities else 0.0


def _direction_metrics(
    yes_price_buy: float,
    no_price_buy: float,
    fee_rate: float,
    slippage_rate: float,
    gas_cost_usd: float,
) -> dict[str, float]:
    """Compute arbitrage economics for one direction after frictions."""
    gross_cost = yes_price_buy + no_price_buy
    fee_cost = gross_cost * fee_rate
    slippage_cost = gross_cost * slippage_rate
    net_cost = gross_cost + fee_cost + slippage_cost + gas_cost_usd
    gross_profit = 1.0 - gross_cost
    net_profit = 1.0 - net_cost
    profit_pct = (net_profit / net_cost * 100.0) if net_profit > 0 and net_cost > 0 else 0.0

    return {
        "gross_cost": round(gross_cost, 6),
        "fee_cost": round(fee_cost, 6),
        "slippage_cost": round(slippage_cost, 6),
        "gas_cost_usd": round(gas_cost_usd, 6),
        "net_cost": round(net_cost, 6),
        "gross_profit": round(gross_profit, 6),
        "net_profit": round(net_profit, 6),
        "profit_pct": round(profit_pct, 6),
    }


def detect_opportunities(
    accepted_matches: list[dict[str, Any]],
    fee_rate: float = 0.01,
    slippage_rate: float = 0.005,
    gas_cost_usd: float = 0.004,
) -> list[dict[str, Any]]:
    """Detect and score arbitrage opportunities from verified matches."""
    opportunities: list[dict[str, Any]] = []

    for item in accepted_matches:
        verification = item.get("verification", {})
        if not verification.get("is_match", False):
            continue
        if not verification.get("arbitrage_safe", False):
            continue
        if str(verification.get("resolution_verdict", "CAUTION")).upper() != "SAFE":
            continue

        market_a = item["market_a"]
        market_b = item["market_b"]
        yes_a, no_a = _extract_yes_no_prices(market_a)
        yes_b, no_b = _extract_yes_no_prices(market_b)

        # Direction 1: Buy YES on A + NO on B
        d1 = _direction_metrics(
            yes_price_buy=yes_a,
            no_price_buy=no_b,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
            gas_cost_usd=gas_cost_usd,
        )
        # Direction 2: Buy YES on B + NO on A
        d2 = _direction_metrics(
            yes_price_buy=yes_b,
            no_price_buy=no_a,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
            gas_cost_usd=gas_cost_usd,
        )

        spread = abs(yes_a - yes_b)
        spread_pct = spread * 100.0
        min_liquidity = min(_extract_min_liquidity(market_a), _extract_min_liquidity(market_b))
        confidence = float(verification.get("confidence", 0.0))

        best_direction = "A_yes_B_no" if d1["net_profit"] >= d2["net_profit"] else "B_yes_A_no"
        best = d1 if best_direction == "A_yes_B_no" else d2

        if best["net_profit"] <= 0:
            continue

        score = best["profit_pct"] * confidence * (min_liquidity / 10000.0)
        time_decay_days = _time_decay_days(market_a, market_b)
        is_time_value_spread = time_decay_days is not None and time_decay_days > 7
        opportunities.append(
            {
                "event_summary": verification.get("event_summary", market_a.get("title", "")),
                "market_a": market_a,
                "market_b": market_b,
                "similarity_score": item.get("similarity_score", 0.0),
                "ai_confidence": confidence,
                "spread": round(spread, 6),
                "spread_pct": round(spread_pct, 6),
                "min_liquidity": round(min_liquidity, 2),
                "direction": best_direction,
                "economics": best,
                "score": round(score, 6),
                "recommended_action": (
                    f"Buy YES on {market_a['platform']} and NO on {market_b['platform']}"
                    if best_direction == "A_yes_B_no"
                    else f"Buy YES on {market_b['platform']} and NO on {market_a['platform']}"
                ),
                "verification": verification,
                "time_decay_days": time_decay_days,
                "is_time_value_spread": is_time_value_spread,
            }
        )

    opportunities.sort(key=lambda x: x["score"], reverse=True)
    return opportunities


def split_time_value_spreads(
    opportunities: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split opportunities into true safe arbs and time-value spreads."""
    safe: list[dict[str, Any]] = []
    time_value: list[dict[str, Any]] = []
    for row in opportunities:
        if bool(row.get("is_time_value_spread", False)):
            row = dict(row)
            row["time_value_explanation"] = (
                "Resolution dates differ by more than 7 days; spread may reflect time value, not pure arbitrage."
            )
            time_value.append(row)
        else:
            safe.append(row)
    return safe, time_value


def _time_decay_days(market_a: dict[str, Any], market_b: dict[str, Any]) -> int | None:
    """Return absolute date gap in days between market resolutions."""
    da = str(market_a.get("resolution_date", ""))
    db = str(market_b.get("resolution_date", ""))
    try:
        d1 = date.fromisoformat(da)
        d2 = date.fromisoformat(db)
    except ValueError:
        return None
    return abs((d1 - d2).days)


def select_top_opportunity(opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return top-1 opportunity to save gas and keep execution simple."""
    return opportunities[:1]


def save_opportunities(payload: dict[str, Any], output_path: Path) -> None:
    """Persist opportunities JSON for dashboard and agent execution."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
