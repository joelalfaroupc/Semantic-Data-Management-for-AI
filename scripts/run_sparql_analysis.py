import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.semantic_ai.config import KG_PATH, SPARQL_REPORT_PATH
from src.semantic_ai.sparql_analysis import run_queries


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SPARQL analysis over the RDF knowledge graph.")
    parser.add_argument("--kg", type=Path, default=KG_PATH)
    parser.add_argument("--out", type=Path, default=SPARQL_REPORT_PATH)
    args = parser.parse_args()

    if not args.kg.exists():
        raise FileNotFoundError(f"KG file not found: {args.kg}. Run scripts/build_kg.py first.")

    out_path = run_queries(args.kg, args.out)
    print(f"SPARQL report written to {out_path}")


if __name__ == "__main__":
    main()
