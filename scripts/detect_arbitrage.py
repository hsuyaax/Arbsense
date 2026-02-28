"""CLI entrypoint for arbitrage detection from verified matches."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.arbitrage_detector import (
    detect_opportunities,
    save_opportunities,
    select_top_opportunity,
    split_time_value_spreads,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Detect arbitrage opportunities.")
    parser.add_argument(
        "--input",
        type=str,
        default="data/verified_matches.json",
        help="Input verified matches JSON path.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/opportunities.json",
        help="Output opportunities JSON path.",
    )
    parser.add_argument("--fee-rate", type=float, default=0.01, help="Fee rate as decimal.")
    parser.add_argument("--slippage-rate", type=float, default=0.005, help="Slippage rate as decimal.")
    parser.add_argument("--gas-cost-usd", type=float, default=0.004, help="Estimated gas cost in USD.")
    return parser.parse_args()


def main() -> None:
    """Run arbitrage detection and save top-1 opportunity."""
    args = parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    accepted = payload.get("accepted_matches", [])

    all_opps = detect_opportunities(
        accepted_matches=accepted,
        fee_rate=args.fee_rate,
        slippage_rate=args.slippage_rate,
        gas_cost_usd=args.gas_cost_usd,
    )
    safe_opps, time_value_spreads = split_time_value_spreads(all_opps)
    top_opps = select_top_opportunity(safe_opps)

    output_payload = {
        "input_matches": len(accepted),
        "opportunity_count_before_top1": len(all_opps),
        "safe_opportunity_count": len(safe_opps),
        "time_value_spread_count": len(time_value_spreads),
        "selected_count": len(top_opps),
        "top_opportunity": top_opps[0] if top_opps else None,
        "all_opportunities": safe_opps,
        "time_value_spreads": time_value_spreads,
    }
    save_opportunities(output_payload, Path(args.output))

    print(f"Accepted matches: {len(accepted)}")
    print(f"Detected opportunities: {len(all_opps)}")
    print(f"Safe opportunities: {len(safe_opps)}")
    print(f"Time-value spreads: {len(time_value_spreads)}")
    print(f"Selected for reporting (Top-1): {len(top_opps)}")
    if top_opps:
        opp = top_opps[0]
        print(
            "Top score: "
            f"{opp['score']:.4f} | spread={opp['spread_pct']:.2f}% | "
            f"net_profit={opp['economics']['net_profit']:.4f} | {opp['recommended_action']}"
        )


if __name__ == "__main__":
    main()
