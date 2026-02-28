"""ArbSense autonomous agent orchestration."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.arbitrage_detector import (
    detect_opportunities,
    save_opportunities,
    select_top_opportunity,
    split_time_value_spreads,
)
from src.blockchain import ArbSenseChainClient, load_contract_artifact
from src.config import Settings, load_settings
from src.data_collector import collect_markets, save_markets
from src.embeddings import embed_all_markets, find_candidate_pairs, save_json
from src.semantic_matcher import verify_candidate_pairs


@dataclass
class AgentConfig:
    """Behavior toggles for agent execution."""

    use_live_data: bool = False
    target_market_count: int = 30
    embedding_threshold: float = 0.70
    match_threshold: float = 0.78
    fee_rate: float = 0.01
    slippage_rate: float = 0.005
    gas_cost_usd: float = 0.004
    report_on_chain: bool = False
    network: str = "bsc"
    loop_interval_seconds: int = 300


class ArbSenseAgent:
    """End-to-end pipeline runner with structured logging."""

    def __init__(self, settings: Settings | None = None, config: AgentConfig | None = None):
        self.settings = settings or load_settings()
        self.config = config or AgentConfig()
        self.data_dir = self.settings.data_dir
        self.logs_path = self.data_dir / "agent_logs.json"

    def _utc_now(self) -> str:
        """Return current UTC timestamp in ISO-8601."""
        return datetime.now(timezone.utc).isoformat()

    def _load_logs(self) -> list[dict[str, Any]]:
        """Load existing logs file."""
        if not self.logs_path.exists():
            return []
        try:
            payload = json.loads(self.logs_path.read_text(encoding="utf-8"))
            logs = payload.get("logs", [])
            return logs if isinstance(logs, list) else []
        except Exception:
            return []

    def log(self, ltype: str, message: str, extra: dict[str, Any] | None = None) -> None:
        """Write log entry to console and persistent JSON file."""
        entry = {
            "timestamp": self._utc_now(),
            "type": ltype,
            "message": message,
        }
        if extra:
            entry["extra"] = extra

        print(f"[{entry['timestamp']}] [{ltype}] {message}")

        logs = self._load_logs()
        logs.append(entry)
        payload = {"count": len(logs), "logs": logs[-500:]}
        self.logs_path.parent.mkdir(parents=True, exist_ok=True)
        self.logs_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def run_single_cycle(self) -> dict[str, Any]:
        """Run one full agent cycle and return summary output."""
        self.log("system", "Starting agent cycle.")

        markets = collect_markets(
            settings=self.settings,
            use_live=self.config.use_live_data,
            target_count=self.config.target_market_count,
        )
        markets_path = self.data_dir / "markets.json"
        save_markets(markets, markets_path)
        self.log("scan", f"Collected {len(markets)} markets.", {"path": str(markets_path)})

        embedded_records, embedding_provider = embed_all_markets(markets=markets, settings=self.settings)
        pairs = find_candidate_pairs(
            embedded_records=embedded_records,
            threshold=self.config.embedding_threshold,
        )
        embeddings_path = self.data_dir / "embeddings.json"
        pairs_path = self.data_dir / "candidate_pairs.json"
        save_json(
            {
                "provider": embedding_provider,
                "model": self.settings.embedding_model
                if embedding_provider == "openai"
                else "local_deterministic_hash",
                "count": len(embedded_records),
                "records": embedded_records,
            },
            embeddings_path,
        )
        save_json(
            {"threshold": self.config.embedding_threshold, "count": len(pairs), "pairs": pairs},
            pairs_path,
        )
        self.log(
            "match",
            f"Generated {len(pairs)} cross-platform candidate pairs.",
            {"provider": embedding_provider},
        )

        verified_rows, verify_provider = verify_candidate_pairs(pairs, settings=self.settings)
        accepted = [
            row
            for row in verified_rows
            if row["verification"]["is_match"]
            and float(row["verification"]["confidence"]) >= self.config.match_threshold
        ]
        verified_path = self.data_dir / "verified_matches.json"
        save_json(
            {
                "provider": verify_provider,
                "input_candidates": len(pairs),
                "verified_count": len(verified_rows),
                "accepted_count": len(accepted),
                "match_threshold": self.config.match_threshold,
                "accepted_matches": accepted,
                "all_verifications": verified_rows,
            },
            verified_path,
        )
        self.log(
            "match",
            f"Verified pairs: {len(verified_rows)} | accepted high-precision matches: {len(accepted)}.",
            {"provider": verify_provider},
        )

        opportunities = detect_opportunities(
            accepted_matches=accepted,
            fee_rate=self.config.fee_rate,
            slippage_rate=self.config.slippage_rate,
            gas_cost_usd=self.config.gas_cost_usd,
        )
        safe_opps, time_value_spreads = split_time_value_spreads(opportunities)
        selected = select_top_opportunity(safe_opps)
        opportunities_path = self.data_dir / "opportunities.json"
        save_opportunities(
            {
                "input_matches": len(accepted),
                "opportunity_count_before_top1": len(opportunities),
                "safe_opportunity_count": len(safe_opps),
                "time_value_spread_count": len(time_value_spreads),
                "selected_count": len(selected),
                "top_opportunity": selected[0] if selected else None,
                "all_opportunities": safe_opps,
                "time_value_spreads": time_value_spreads,
            },
            opportunities_path,
        )
        self.log(
            "opportunity",
            (
                f"Detected {len(opportunities)} opportunities "
                f"({len(safe_opps)} safe, {len(time_value_spreads)} time-value); "
                f"selected {len(selected)} top candidate."
            ),
            {"path": str(opportunities_path)},
        )

        tx_hash = None
        if self.config.report_on_chain and selected:
            top = selected[0]
            try:
                artifact_path = Path("contracts/ArbSenseRegistry.artifact.json")
                if not artifact_path.exists():
                    raise RuntimeError(
                        "Contract artifact missing. Run scripts/deploy_contract.py first."
                    )
                abi = load_contract_artifact(artifact_path)["abi"]
                client = ArbSenseChainClient(
                    settings=self.settings,
                    network=self.config.network,
                    abi=abi,
                )

                spread_bps = int(round(float(top["spread_pct"]) * 100))
                confidence_bps = int(round(float(top["ai_confidence"]) * 10000))
                tx_hash = client.report_opportunity(
                    market_a=str(top["market_a"]["market_id"]),
                    market_b=str(top["market_b"]["market_id"]),
                    spread_bps=spread_bps,
                    confidence_bps=confidence_bps,
                )
                self.log(
                    "execute",
                    "Reported top opportunity on-chain.",
                    {"network": self.config.network, "tx_hash": tx_hash},
                )
            except Exception as exc:
                self.log("execute", f"On-chain reporting skipped/failed: {exc}")

        summary = {
            "markets": len(markets),
            "pairs": len(pairs),
            "accepted_matches": len(accepted),
            "opportunities": len(safe_opps),
            "time_value_spreads": len(time_value_spreads),
            "selected": len(selected),
            "on_chain_tx_hash": tx_hash,
        }
        self.log("system", "Agent cycle completed.", summary)
        return summary

    def run_continuous(self) -> None:
        """Run the agent in a continuous loop."""
        self.log(
            "system",
            f"Starting continuous loop, interval={self.config.loop_interval_seconds}s.",
        )
        while True:
            try:
                self.run_single_cycle()
            except Exception as exc:
                self.log("system", f"Cycle failed: {exc}")
            time.sleep(self.config.loop_interval_seconds)
