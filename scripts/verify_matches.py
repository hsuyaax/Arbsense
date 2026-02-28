"""CLI entrypoint for semantic verification of candidate pairs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_settings
from src.embeddings import save_json
from src.semantic_matcher import verify_candidate_pairs


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Verify candidate pairs with LLM.")
    parser.add_argument(
        "--input",
        type=str,
        default="data/candidate_pairs.json",
        help="Input candidate pairs JSON path.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/verified_matches.json",
        help="Output verified matches path.",
    )
    parser.add_argument(
        "--match-threshold",
        type=float,
        default=0.78,
        help="Minimum verifier confidence to retain a positive match.",
    )
    return parser.parse_args()


def main() -> None:
    """Run semantic verification and persist both full and accepted results."""
    args = parse_args()
    settings = load_settings()

    pairs_payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    pairs = pairs_payload.get("pairs", [])

    verified, provider = verify_candidate_pairs(pairs, settings=settings)

    accepted = [
        row
        for row in verified
        if row["verification"]["is_match"]
        and row["verification"]["confidence"] >= args.match_threshold
    ]

    payload = {
        "provider": provider,
        "input_candidates": len(pairs),
        "verified_count": len(verified),
        "accepted_count": len(accepted),
        "match_threshold": args.match_threshold,
        "accepted_matches": accepted,
        "all_verifications": verified,
    }
    save_json(payload, Path(args.output))

    print(f"Verifier provider: {provider}")
    print(f"Input candidates: {len(pairs)}")
    print(f"Accepted high-precision matches: {len(accepted)}")
    for item in accepted[:10]:
        print(
            "- "
            f"{item['verification']['confidence']:.3f} | "
            f"{item['market_a']['title']} <> {item['market_b']['title']}"
        )


if __name__ == "__main__":
    main()
