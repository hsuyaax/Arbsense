"""Market data collection and normalization for ArbSense.

This module intentionally supports a reliable sample-data mode first, while keeping
live connectors as explicit extension points for hackathon iteration.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from src.config import Settings
from src.quality_scorer import enrich_with_quality_scores

YES_NO_OUTCOMES = ("Yes", "No")


def _market(
    platform: str,
    market_id: str,
    title: str,
    description: str,
    yes_price: float,
    no_price: float,
    liquidity_yes: float,
    liquidity_no: float,
    resolution_date: str,
    category: str,
) -> dict[str, Any]:
    """Build a normalized market dictionary with common schema."""
    return {
        "platform": platform,
        "market_id": market_id,
        "title": title,
        "description": description,
        "outcomes": [
            {"name": YES_NO_OUTCOMES[0], "price": round(yes_price, 4), "liquidity": liquidity_yes},
            {"name": YES_NO_OUTCOMES[1], "price": round(no_price, 4), "liquidity": liquidity_no},
        ],
        "resolution_date": resolution_date,
        "category": category,
    }


def build_sample_markets() -> list[dict[str, Any]]:
    """Create realistic cross-platform sample markets with semantic overlap."""
    return [
        _market(
            "predict.fun",
            "pf-ct25-india",
            "Will India win ICC Champions Trophy 2025?",
            "Resolves YES if India is the official winner of ICC Champions Trophy 2025.",
            0.62,
            0.38,
            18000,
            16000,
            "2025-03-20",
            "sports",
        ),
        _market(
            "probable",
            "pr-icc-ct25-india",
            "ICC CT25 Winner - India",
            "YES resolves if India lifts the ICC Champions Trophy 2025 title.",
            0.54,
            0.46,
            14000,
            13000,
            "2025-03-20",
            "sports",
        ),
        _market(
            "XO Market",
            "xo-btc-150k-q3",
            "BTC above 150k before Q3 2025?",
            "YES resolves if BTC spot price exceeds 150,000 USD prior to July 1, 2025 UTC.",
            0.47,
            0.53,
            22000,
            20000,
            "2025-07-01",
            "crypto",
        ),
        _market(
            "Opinion",
            "op-bitcoin-150k-july",
            "Will Bitcoin cross $150,000 by July 2025?",
            "Resolves to YES when Bitcoin trades above $150,000 before July 2025 cutoff.",
            0.40,
            0.60,
            15500,
            15000,
            "2025-07-01",
            "crypto",
        ),
        _market(
            "Bento",
            "be-eth-7k-2025",
            "ETH to hit $7,000 in 2025?",
            "YES resolves if ETH/USD reaches 7000 any time before Dec 31, 2025.",
            0.33,
            0.67,
            12000,
            12500,
            "2025-12-31",
            "crypto",
        ),
        _market(
            "predict.fun",
            "pf-eth-7000-2025",
            "Ethereum above 7k by end of 2025?",
            "YES if Ether spot price prints above $7,000 before 2026.",
            0.39,
            0.61,
            15000,
            14500,
            "2025-12-31",
            "crypto",
        ),
        _market(
            "probable",
            "pr-sol-etf-2025",
            "Will a US SOL ETF be approved in 2025?",
            "Resolves YES if a spot Solana ETF is approved by a US regulator by Dec 31, 2025.",
            0.29,
            0.71,
            6000,
            7000,
            "2025-12-31",
            "regulation",
        ),
        _market(
            "XO Market",
            "xo-solana-etf-2025",
            "Spot Solana ETF approval by end-2025?",
            "YES if US authorities approve a spot SOL ETF before 2026.",
            0.36,
            0.64,
            9200,
            9100,
            "2025-12-31",
            "regulation",
        ),
        _market(
            "Opinion",
            "op-fed-cut-sep",
            "Fed rate cut by September 2025?",
            "YES if FOMC delivers at least one cut by Sep 30, 2025.",
            0.58,
            0.42,
            11000,
            10800,
            "2025-09-30",
            "macro",
        ),
        _market(
            "Bento",
            "be-us-rates-cut-q3",
            "US policy rate lower by Q3 2025?",
            "YES resolves if benchmark US policy rate is lower by end of Q3 2025 than Jan 1 level.",
            0.51,
            0.49,
            9000,
            9200,
            "2025-09-30",
            "macro",
        ),
        _market(
            "predict.fun",
            "pf-gold-3000-2025",
            "Gold above $3,000 in 2025?",
            "YES if XAU/USD touches or exceeds 3000 before year end.",
            0.45,
            0.55,
            8400,
            8300,
            "2025-12-31",
            "commodities",
        ),
        _market(
            "probable",
            "pr-xau-3k-2025",
            "Will XAUUSD break 3000 this year?",
            "YES resolves when spot gold prints 3000+ in 2025.",
            0.49,
            0.51,
            8600,
            8500,
            "2025-12-31",
            "commodities",
        ),
        _market(
            "XO Market",
            "xo-ai-act-passed",
            "EU AI Act fully effective by 2025?",
            "YES if core AI Act obligations are enforceable before Dec 31, 2025.",
            0.43,
            0.57,
            4500,
            4700,
            "2025-12-31",
            "policy",
        ),
        _market(
            "Opinion",
            "op-eu-ai-law-active",
            "Will EU AI law become enforceable in 2025?",
            "YES if EU AI regulation enforcement begins within 2025.",
            0.38,
            0.62,
            5100,
            5000,
            "2025-12-31",
            "policy",
        ),
        _market(
            "Bento",
            "be-nvidia-2t-q2",
            "NVIDIA market cap > $2T by Q2 2025?",
            "YES if NVDA reaches a market capitalization above 2 trillion USD by Jun 30, 2025.",
            0.57,
            0.43,
            9700,
            9600,
            "2025-06-30",
            "equities",
        ),
        _market(
            "predict.fun",
            "pf-nvda-2trn-june",
            "Will NVDA exceed $2 trillion by June 2025?",
            "YES if NVIDIA valuation passes 2T before July 2025.",
            0.61,
            0.39,
            10200,
            10100,
            "2025-06-30",
            "equities",
        ),
        _market(
            "probable",
            "pr-mars-landing-2030",
            "Human on Mars before 2030?",
            "YES if first crewed Mars landing occurs before Jan 1, 2030.",
            0.18,
            0.82,
            4300,
            4200,
            "2030-01-01",
            "science",
        ),
        _market(
            "XO Market",
            "xo-crewed-mars-before-2030",
            "Crewed Mars mission lands before 2030?",
            "YES if humans land on Mars before 2030.",
            0.16,
            0.84,
            4100,
            4050,
            "2030-01-01",
            "science",
        ),
        _market(
            "Opinion",
            "op-us-election-turnout-70",
            "US 2028 election turnout above 70%?",
            "YES if official eligible voter turnout exceeds 70%.",
            0.23,
            0.77,
            3300,
            3250,
            "2028-11-08",
            "politics",
        ),
        _market(
            "Bento",
            "be-voter-participation-2028",
            "Will 2028 US voter participation exceed 70%?",
            "YES if national turnout is above 70% in 2028 US election.",
            0.27,
            0.73,
            3100,
            3000,
            "2028-11-08",
            "politics",
        ),
        _market(
            "predict.fun",
            "pf-ai-gdp-10-2030",
            "AI contributes 10% to global GDP by 2030?",
            "YES if mainstream estimates indicate >=10% GDP contribution by 2030.",
            0.31,
            0.69,
            2600,
            2500,
            "2030-12-31",
            "economy",
        ),
        _market(
            "probable",
            "pr-ai-global-gdp-share",
            "Global GDP share from AI above 10% by 2030?",
            "YES if AI-attributed GDP share reaches 10 percent or more before 2031.",
            0.36,
            0.64,
            2900,
            2950,
            "2030-12-31",
            "economy",
        ),
        _market(
            "XO Market",
            "xo-world-cup-2030-spain",
            "Will Spain win FIFA World Cup 2030?",
            "YES if Spain wins FIFA World Cup 2030 final.",
            0.14,
            0.86,
            5600,
            5500,
            "2030-07-31",
            "sports",
        ),
        _market(
            "Opinion",
            "op-fifa-2030-spain-title",
            "Spain to lift 2030 World Cup trophy?",
            "YES if Spain is declared winner of 2030 FIFA World Cup.",
            0.19,
            0.81,
            5900,
            5750,
            "2030-07-31",
            "sports",
        ),
        _market(
            "Bento",
            "be-us-recession-2026",
            "US recession starts in 2026?",
            "YES if NBER dates recession start in calendar year 2026.",
            0.34,
            0.66,
            7800,
            7600,
            "2026-12-31",
            "macro",
        ),
        _market(
            "predict.fun",
            "pf-nber-recession-2026",
            "NBER to call a 2026 recession?",
            "YES if NBER identifies recession beginning during 2026.",
            0.28,
            0.72,
            8200,
            8000,
            "2026-12-31",
            "macro",
        ),
        _market(
            "probable",
            "pr-apple-5t-before-2030",
            "Apple market cap to hit $5T before 2030?",
            "YES if AAPL reaches 5 trillion USD market cap before Jan 1, 2030.",
            0.26,
            0.74,
            7200,
            7100,
            "2030-01-01",
            "equities",
        ),
        _market(
            "XO Market",
            "xo-aapl-5trn-2030",
            "AAPL above 5 trillion valuation before 2030?",
            "YES if Apple valuation crosses 5T by end of 2029.",
            0.22,
            0.78,
            6900,
            6800,
            "2030-01-01",
            "equities",
        ),
        _market(
            "Opinion",
            "op-usdc-depeg-2026",
            "USDC depegs below $0.95 in 2026?",
            "YES if USDC spot price falls below 0.95 USD at any point in 2026.",
            0.21,
            0.79,
            10800,
            10400,
            "2026-12-31",
            "crypto",
        ),
        _market(
            "Bento",
            "be-usdc-below-95c-2026",
            "Will USDC trade under $0.95 during 2026?",
            "YES if USDC market price is under $0.95 at least once in 2026.",
            0.25,
            0.75,
            11200,
            10900,
            "2026-12-31",
            "crypto",
        ),
    ]


def filter_by_min_liquidity(
    markets: list[dict[str, Any]], min_liquidity_usd: float
) -> list[dict[str, Any]]:
    """Drop markets where either side has very low liquidity."""
    filtered: list[dict[str, Any]] = []
    for market in markets:
        outcomes = market.get("outcomes", [])
        if len(outcomes) < 2:
            continue
        min_outcome_liq = min(float(outcomes[0]["liquidity"]), float(outcomes[1]["liquidity"]))
        if min_outcome_liq >= min_liquidity_usd:
            filtered.append(market)
    return filtered


def maybe_collect_live_markets() -> list[dict[str, Any]]:
    """Placeholder for live connectors; returns empty until adapters are implemented."""
    return []


def collect_markets(
    settings: Settings, use_live: bool = False, target_count: int = 30
) -> list[dict[str, Any]]:
    """Collect markets from live sources when available, otherwise use curated samples."""
    markets = maybe_collect_live_markets() if use_live else []
    if len(markets) < target_count:
        markets = build_sample_markets()

    markets = filter_by_min_liquidity(markets, settings.min_liquidity_usd)
    markets = markets[: max(1, min(target_count, len(markets)))]
    return enrich_with_quality_scores(markets)


def save_markets(markets: list[dict[str, Any]], output_path: Path) -> None:
    """Persist normalized markets JSON for downstream embedding pipeline."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": date.today().isoformat(),
        "count": len(markets),
        "markets": markets,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
