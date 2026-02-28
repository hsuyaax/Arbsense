"""FastAPI backend for ArbSense dashboard with live data + SSE streaming."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api.schemas import (
    ChainInfoResponse,
    ChainNetworkInfo,
    HealthResponse,
    LogEntryResponse,
    MarketResponse,
    MatchResponse,
    OpportunityResponse,
    StatsResponse,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ENV_PATH = PROJECT_ROOT / ".env"


def _load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    """Load JSON data with resilient fallback."""
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _read_env() -> dict[str, str]:
    """Parse .env values for non-secret display fields."""
    if not ENV_PATH.exists():
        return {}
    values: dict[str, str] = {}
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _yes_no_liquidity(market: dict[str, Any]) -> tuple[float, float, float]:
    """Return yes/no prices and minimum liquidity from normalized outcomes."""
    yes_price = 0.0
    no_price = 0.0
    liqs: list[float] = []
    for o in market.get("outcomes", []):
        name = str(o.get("name", "")).lower()
        if name == "yes":
            yes_price = float(o.get("price", 0.0))
        if name == "no":
            no_price = float(o.get("price", 0.0))
        liqs.append(float(o.get("liquidity", 0.0)))
    return yes_price, no_price, (min(liqs) if liqs else 0.0)


def _normalize_opportunity(row: dict[str, Any]) -> OpportunityResponse:
    """Convert internal opportunities format to documented API shape."""
    market_a = row.get("market_a", {})
    market_b = row.get("market_b", {})
    ver = row.get("verification", {})
    econ = row.get("economics", {})

    yes_a, no_a, liq_a = _yes_no_liquidity(market_a)
    yes_b, no_b, liq_b = _yes_no_liquidity(market_b)

    return OpportunityResponse(
        market_a={
            "platform": market_a.get("platform", ""),
            "title": market_a.get("title", ""),
            "yes_price": yes_a,
            "no_price": no_a,
            "liquidity": liq_a,
        },
        market_b={
            "platform": market_b.get("platform", ""),
            "title": market_b.get("title", ""),
            "yes_price": yes_b,
            "no_price": no_b,
            "liquidity": liq_b,
        },
        spread_pct=float(row.get("spread_pct", 0.0)),
        profit_pct=float(econ.get("profit_pct", 0.0)),
        action=str(row.get("recommended_action", "")),
        safety_badge=str(ver.get("resolution_verdict", "CAUTION")),
        resolution_conflict_score=int(ver.get("resolution_conflict_score", 50)),
        ai_confidence=float(row.get("ai_confidence", 0.0)),
        score=float(row.get("score", 0.0)),
        reasoning=str(ver.get("reasoning", "")),
        resolution_risks=[str(x) for x in (ver.get("risk_factors", []) or [])],
        outcome_mapping=ver.get("outcome_mapping", {}),
        time_decay_flag=bool(row.get("is_time_value_spread", False)),
        event_summary=str(row.get("event_summary", "")),
    )


def _normalize_match(row: dict[str, Any]) -> MatchResponse:
    """Convert internal verification format to documented API shape."""
    market_a = row.get("market_a", {})
    market_b = row.get("market_b", {})
    ver = row.get("verification", {})

    return MatchResponse(
        is_match=bool(ver.get("is_match", False)),
        confidence=float(ver.get("confidence", 0.0)),
        reasoning=str(ver.get("reasoning", "")),
        market_a=market_a,
        market_b=market_b,
        platform_a=str(market_a.get("platform", "")),
        platform_b=str(market_b.get("platform", "")),
        embedding_similarity=float(row.get("similarity_score", 0.0)),
        resolution_conflict_score=int(ver.get("resolution_conflict_score", 50)),
        safety_badge=str(ver.get("resolution_verdict", "CAUTION")),
        resolution_risks=[str(x) for x in (ver.get("risk_factors", []) or [])],
        resolution_criteria_a=str(market_a.get("description", "")),
        resolution_criteria_b=str(market_b.get("description", "")),
        edge_cases=[str(x) for x in (ver.get("key_differences", []) or [])],
        outcome_mapping=ver.get("outcome_mapping", {}),
        event_summary=str(ver.get("event_summary", "")),
    )


def _format_balance(rpc_url: str, wallet_address: str) -> str:
    """Read wallet native-token balance from RPC when web3 is available."""
    if not rpc_url or not wallet_address:
        return "N/A"
    try:
        from web3 import Web3  # type: ignore

        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return "N/A"
        balance = w3.eth.get_balance(Web3.to_checksum_address(wallet_address))
        return f"{w3.from_wei(balance, 'ether'):.4f} tBNB"
    except Exception:
        return "N/A"


def _onchain_opportunity_count(rpc_url: str, contract_address: str) -> int:
    """Read getOpportunityCount() from deployed contract when possible."""
    if not rpc_url or not contract_address:
        return 0
    artifact_path = PROJECT_ROOT / "contracts" / "ArbSenseRegistry.artifact.json"
    if not artifact_path.exists():
        return 0
    try:
        from web3 import Web3  # type: ignore

        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        abi = artifact.get("abi", [])
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return 0
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        return int(contract.functions.getOpportunityCount().call())
    except Exception:
        return 0


app = FastAPI(title="ArbSense API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Healthcheck endpoint."""
    return HealthResponse(status="ok")


@app.get("/markets", response_model=list[MarketResponse])
def markets() -> list[MarketResponse]:
    """Return all market data as a list."""
    payload = _load_json(DATA_DIR / "markets.json", {"markets": []})
    return [MarketResponse(**m) for m in payload.get("markets", [])]


@app.get("/opportunities", response_model=list[OpportunityResponse])
def opportunities() -> list[OpportunityResponse]:
    """Return scored opportunities list."""
    payload = _load_json(DATA_DIR / "opportunities.json", {"all_opportunities": [], "time_value_spreads": []})
    rows = payload.get("all_opportunities", []) + payload.get("time_value_spreads", [])
    return [_normalize_opportunity(row) for row in rows]


@app.get("/matches", response_model=list[MatchResponse])
def matches() -> list[MatchResponse]:
    """Return semantic verification list (matches and non-matches)."""
    payload = _load_json(DATA_DIR / "verified_matches.json", {"all_verifications": []})
    return [_normalize_match(row) for row in payload.get("all_verifications", [])]


@app.get("/logs", response_model=list[LogEntryResponse])
def logs() -> list[LogEntryResponse]:
    """Return latest 100 logs, newest first."""
    payload = _load_json(DATA_DIR / "agent_logs.json", {"logs": []})
    rows = list(reversed(payload.get("logs", [])[-100:]))
    out: list[LogEntryResponse] = []
    for i, row in enumerate(rows, start=1):
        out.append(
            LogEntryResponse(
                timestamp=str(row.get("timestamp", "")),
                type=str(row.get("type", "system")),
                message=str(row.get("message", "")),
                cycle=i,
            )
        )
    return out


@app.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    """Return dashboard metrics in the documented shape."""
    market_payload = _load_json(DATA_DIR / "markets.json", {"markets": []})
    verified_payload = _load_json(DATA_DIR / "verified_matches.json", {"all_verifications": []})
    opportunities_payload = _load_json(DATA_DIR / "opportunities.json", {"all_opportunities": [], "time_value_spreads": []})

    markets = market_payload.get("markets", [])
    platforms = sorted({str(m.get("platform", "unknown")) for m in markets if isinstance(m, dict)})

    matches_rows = [_normalize_match(row) for row in verified_payload.get("all_verifications", [])]
    matched = [m for m in matches_rows if m.is_match]

    opp_rows = [_normalize_opportunity(row) for row in opportunities_payload.get("all_opportunities", [])]
    all_rows = opp_rows + [_normalize_opportunity(row) for row in opportunities_payload.get("time_value_spreads", [])]

    safe_count = len([o for o in all_rows if o.safety_badge == "SAFE"])
    caution_count = len([o for o in all_rows if o.safety_badge == "CAUTION"])
    danger_count = len([o for o in all_rows if o.safety_badge == "DANGER"])

    spreads = [o.spread_pct for o in all_rows]
    confidences = [m.confidence for m in matched]
    quality_scores = [int(m.get("quality_score", 0)) for m in markets if isinstance(m, dict)]

    return StatsResponse(
        markets_scanned=len(markets),
        platforms_count=len(platforms),
        platform_names=platforms,
        matched_pairs=len(matched),
        total_opportunities=len(all_rows),
        safe_opportunities=safe_count,
        caution_opportunities=caution_count,
        danger_opportunities=danger_count,
        avg_spread_pct=round(sum(spreads) / len(spreads), 4) if spreads else 0.0,
        best_spread_pct=round(max(spreads), 4) if spreads else 0.0,
        avg_confidence=round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
        avg_quality_score=round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0.0,
    )


# ── SSE streaming + live refresh ──────────────────────────────────

_last_refresh: float = 0.0
_refresh_lock = asyncio.Lock()


def _run_live_pipeline() -> dict[str, Any]:
    """Run the ArbSense agent pipeline with live data from Polymarket + Kalshi."""
    from src.agent import AgentConfig, ArbSenseAgent
    from src.config import load_settings

    config = AgentConfig(use_live_data=True, target_market_count=60)
    agent = ArbSenseAgent(settings=load_settings(), config=config)
    return agent.run_single_cycle()


@app.post("/refresh")
async def refresh(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Trigger a live data refresh from Polymarket + Kalshi.

    Debounced to at most once per 30 seconds.
    """
    global _last_refresh
    now = time.time()
    if now - _last_refresh < 30:
        return {"status": "debounced", "message": "Refresh already ran recently. Wait 30s."}

    async with _refresh_lock:
        _last_refresh = time.time()

    background_tasks.add_task(_run_live_pipeline)
    return {"status": "started", "message": "Live pipeline refresh started in background."}


async def _sse_generator():
    """Server-Sent Events generator that pushes fresh stats every 5s."""
    while True:
        try:
            payload = _load_json(DATA_DIR / "markets.json", {"markets": []})
            market_count = len(payload.get("markets", []))

            opp_payload = _load_json(DATA_DIR / "opportunities.json", {"all_opportunities": []})
            opps = opp_payload.get("all_opportunities", [])

            spreads = []
            for row in opps:
                s = float(row.get("spread_pct", 0))
                if s > 0:
                    spreads.append(s)

            stats_data = {
                "markets_scanned": market_count,
                "opportunities": len(opps),
                "avg_spread": round(sum(spreads) / len(spreads), 4) if spreads else 0,
                "timestamp": time.time(),
            }
            yield f"data: {json.dumps(stats_data)}\n\n"
        except Exception:
            yield f"data: {json.dumps({'error': 'read_failed'})}\n\n"

        await asyncio.sleep(5)


@app.get("/stream")
async def stream():
    """SSE endpoint — pushes live dashboard metrics to the frontend."""
    return StreamingResponse(
        _sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/chain-info", response_model=ChainInfoResponse)
def chain_info() -> ChainInfoResponse:
    """Return chain metadata in documented shape."""
    env = _read_env()
    wallet = env.get("WALLET_ADDRESS", "")

    bsc_addr = env.get("BSC_CONTRACT_ADDRESS", "")
    opbnb_addr = env.get("OPBNB_CONTRACT_ADDRESS", "")

    bsc_info = ChainNetworkInfo(
        contract_address=bsc_addr,
        explorer_url=(f"https://testnet.bscscan.com/address/{bsc_addr}" if bsc_addr else ""),
        verified=bool(bsc_addr),
        opportunity_count=_onchain_opportunity_count(env.get("BSC_TESTNET_RPC", ""), bsc_addr),
        network="BSC Testnet (Chain ID: 97)",
    )
    opbnb_info = ChainNetworkInfo(
        contract_address=opbnb_addr,
        explorer_url=(f"https://opbnb-testnet.bscscan.com/address/{opbnb_addr}" if opbnb_addr else ""),
        verified=bool(opbnb_addr),
        opportunity_count=_onchain_opportunity_count(env.get("OPBNB_TESTNET_RPC", ""), opbnb_addr),
        network="opBNB Testnet",
    )

    return ChainInfoResponse(
        bsc=bsc_info,
        opbnb=opbnb_info,
        wallet_address=wallet,
        wallet_balance_bsc=_format_balance(env.get("BSC_TESTNET_RPC", ""), wallet),
        wallet_balance_opbnb=_format_balance(env.get("OPBNB_TESTNET_RPC", ""), wallet),
    )
