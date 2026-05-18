import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.semantic_ai.config import EMBEDDING_REPORT_PATH, KG_PATH
from src.semantic_ai.embedding_ml import cluster_embeddings


def main() -> None:
    parser = argparse.ArgumentParser(description="Cluster graph-derived neighborhood embeddings.")
    parser.add_argument("--kg", type=Path, default=KG_PATH)
    parser.add_argument("--out", type=Path, default=EMBEDDING_REPORT_PATH)
    parser.add_argument("--k", type=int, default=4)
    args = parser.parse_args()

    if not args.kg.exists():
        raise FileNotFoundError(f"KG file not found: {args.kg}. Run scripts/build_kg.py first.")

    out_path = cluster_embeddings(args.kg, args.out, k=args.k)
    print(f"Embedding/ML report written to {out_path}")


if __name__ == "__main__":
    main()
