from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_P1_ROOT = PROJECT_ROOT.parent / "BDA_DataPipeline"

SEMANTIC_EXPLOITATION_ZONE = PROJECT_ROOT / "exploitation_zone"
ANALYSIS_ZONE = PROJECT_ROOT / "analysis_zone"

KG_PATH = SEMANTIC_EXPLOITATION_ZONE / "barcelona_tourism_kg.ttl"
SPARQL_REPORT_PATH = ANALYSIS_ZONE / "sparql_analysis.md"
EMBEDDING_REPORT_PATH = ANALYSIS_ZONE / "kg_embedding_clusters.md"


def p1_exploitation_db(p1_root: Path = DEFAULT_P1_ROOT) -> Path:
    return p1_root / "exploitation_zone" / "exploitation_zone.duckdb"
