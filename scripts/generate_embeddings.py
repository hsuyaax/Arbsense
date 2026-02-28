"""CLI entrypoint for embedding and candidate pair generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_settings
from src.embeddings import embed_all_markets, find_candidate_pairs, save_json


def parse_args() -> argparse.Namespace:
    """Parse CLI args for embedding pipeline."""
    parser = argparse.ArgumentParser(description="Generate embeddings and candidate market pairs.")
    parser.add_argument("--input", type=str, default="data/markets.json", help="Input markets JSON path.")
    parser.add_argument(
        "--embeddings-output",
        type=str,
        default="data/embeddings.json",
        help="Output embeddings JSON path.",
    )
    parser.add_argument(
        "--pairs-output",
        type=str,
        default="data/candidate_pairs.json",
        help="Output candidate pairs JSON path.",
    )
    parser.add_argument("--threshold", type=float, default=0.70, help="Cosine threshold.")
    return parser.parse_args()


def main() -> None:
    """Execute embedding + candidate pair pipeline."""
    args = parse_args()
    settings = load_settings()

    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    markets = payload.get("markets", [])

    embedded_records, provider = embed_all_markets(markets=markets, settings=settings)
    candidates = find_candidate_pairs(embedded_records=embedded_records, threshold=args.threshold)

    embeddings_payload = {
        "provider": provider,
        "model": settings.embedding_model if provider == "openai" else "local_deterministic_hash",
        "count": len(embedded_records),
        "records": embedded_records,
    }
    pairs_payload = {"threshold": args.threshold, "count": len(candidates), "pairs": candidates}

    save_json(embeddings_payload, Path(args.embeddings_output))
    save_json(pairs_payload, Path(args.pairs_output))

    print(f"Embeddings provider: {provider}")
    print(f"Embedded markets: {len(embedded_records)}")
    print(f"Candidate pairs: {len(candidates)}")
    if candidates:
        print("Top candidates:")
        for row in candidates[:10]:
            a = row["market_a"]["title"]
            b = row["market_b"]["title"]
            print(f"- {row['similarity_score']:.4f} | {a} <> {b}")


if __name__ == "__main__":
    main()
