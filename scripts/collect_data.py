"""CLI entrypoint for market data collection."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_settings
from src.data_collector import collect_markets, save_markets


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Collect and normalize ArbSense market data.")
    parser.add_argument(
        "--use-live",
        action="store_true",
        help="Attempt live collection first (falls back to sample markets).",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=30,
        help="Target number of markets to output.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/markets.json",
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> None:
    """Run market collection and write normalized JSON output."""
    args = parse_args()
    settings = load_settings()
    markets = collect_markets(
        settings=settings, use_live=args.use_live, target_count=args.target_count
    )
    save_markets(markets, Path(args.output))
    print(f"Saved {len(markets)} markets to {args.output}")


if __name__ == "__main__":
    main()
