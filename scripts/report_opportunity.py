"""Send top opportunity to on-chain ArbSenseRegistry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.blockchain import ArbSenseChainClient, load_contract_artifact
from src.config import load_settings


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Report top opportunity on-chain.")
    parser.add_argument("--network", choices=["bsc", "opbnb"], default="bsc")
    parser.add_argument(
        "--opportunities",
        type=str,
        default="data/opportunities.json",
        help="Path to opportunities file.",
    )
    parser.add_argument(
        "--artifact",
        type=str,
        default="contracts/ArbSenseRegistry.artifact.json",
        help="Path to compiled contract artifact with ABI.",
    )
    return parser.parse_args()


def main() -> None:
    """Load top opportunity and call reportOpportunity on-chain."""
    args = parse_args()
    payload = json.loads(Path(args.opportunities).read_text(encoding="utf-8"))
    top = payload.get("top_opportunity")
    if not top:
        print("No top opportunity found, skipping on-chain report.")
        return

    artifact = load_contract_artifact(Path(args.artifact))
    abi = artifact["abi"]
    settings = load_settings()
    client = ArbSenseChainClient(settings=settings, network=args.network, abi=abi)

    market_a = str(top["market_a"]["market_id"])
    market_b = str(top["market_b"]["market_id"])
    spread_bps = int(round(float(top["spread_pct"]) * 100))
    confidence_bps = int(round(float(top["ai_confidence"]) * 10000))

    tx_hash = client.report_opportunity(
        market_a=market_a,
        market_b=market_b,
        spread_bps=spread_bps,
        confidence_bps=confidence_bps,
    )
    count = client.get_opportunity_count()
    print(f"Network: {args.network}")
    print(f"Tx hash: {tx_hash}")
    print(f"On-chain opportunity count: {count}")


if __name__ == "__main__":
    main()
