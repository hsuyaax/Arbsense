"""CLI runner for ArbSenseAgent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import AgentConfig, ArbSenseAgent


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for agent execution."""
    parser = argparse.ArgumentParser(description="Run ArbSense agent.")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous loop mode.")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=300,
        help="Loop interval for continuous mode.",
    )
    parser.add_argument("--use-live", action="store_true", help="Attempt live market collection.")
    parser.add_argument("--target-count", type=int, default=30, help="Target markets per cycle.")
    parser.add_argument("--embedding-threshold", type=float, default=0.70)
    parser.add_argument("--match-threshold", type=float, default=0.78)
    parser.add_argument("--report-on-chain", action="store_true", help="Send top match on-chain.")
    parser.add_argument("--network", choices=["bsc", "opbnb"], default="bsc")
    parser.add_argument("--fee-rate", type=float, default=0.01)
    parser.add_argument("--slippage-rate", type=float, default=0.005)
    parser.add_argument("--gas-cost-usd", type=float, default=0.004)
    return parser.parse_args()


def main() -> None:
    """Run one or continuous ArbSense agent cycles."""
    args = parse_args()
    config = AgentConfig(
        use_live_data=args.use_live,
        target_market_count=args.target_count,
        embedding_threshold=args.embedding_threshold,
        match_threshold=args.match_threshold,
        fee_rate=args.fee_rate,
        slippage_rate=args.slippage_rate,
        gas_cost_usd=args.gas_cost_usd,
        report_on_chain=args.report_on_chain,
        network=args.network,
        loop_interval_seconds=args.interval_seconds,
    )
    agent = ArbSenseAgent(config=config)

    if args.continuous:
        agent.run_continuous()
    else:
        summary = agent.run_single_cycle()
        print(f"Cycle summary: {summary}")


if __name__ == "__main__":
    main()
