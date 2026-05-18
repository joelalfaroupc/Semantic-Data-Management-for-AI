import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.semantic_ai.config import DEFAULT_P1_ROOT, KG_PATH, p1_exploitation_db
from src.semantic_ai.kg_builder import build_kg


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Barcelona tourism RDF knowledge graph.")
    parser.add_argument("--p1-root", type=Path, default=DEFAULT_P1_ROOT)
    parser.add_argument("--out", type=Path, default=KG_PATH)
    args = parser.parse_args()

    db_path = p1_exploitation_db(args.p1_root)
    if not db_path.exists():
        raise FileNotFoundError(f"P1 exploitation DuckDB not found: {db_path}")

    out_path = build_kg(db_path, args.out)
    print(f"KG written to {out_path}")


if __name__ == "__main__":
    main()
