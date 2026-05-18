from pathlib import Path

from .kg_builder import BASE_IRI


PREFIX = f"""
PREFIX bda: <{BASE_IRI}>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


QUERIES = {
    "high_tourism_pressure_neighborhoods": """
        SELECT ?neighborhood ?district ?listings ?huts ?assetScore
        WHERE {
          ?n a bda:Neighborhood ;
             rdfs:label ?neighborhood ;
             bda:inDistrict ?d ;
             bda:hasTourismPressure <https://example.org/bda/barcelona-tourism/pressure/high> ;
             bda:listingCount ?listings ;
             bda:hutCount ?huts ;
             bda:tourismAssetScore ?assetScore .
          ?d rdfs:label ?district .
        }
        ORDER BY DESC(?listings)
        LIMIT 15
    """,
    "many_hut_low_income_neighborhoods": """
        SELECT ?neighborhood ?district ?huts ?income
        WHERE {
          ?n a bda:Neighborhood ;
             rdfs:label ?neighborhood ;
             bda:inDistrict ?d ;
             bda:hutCount ?huts ;
             bda:incomeEur ?income .
          ?d rdfs:label ?district .
          FILTER(?huts >= 10 && ?income < 22000)
        }
        ORDER BY DESC(?huts)
        LIMIT 15
    """,
    "tourism_assets_and_airbnb_supply": """
        SELECT ?neighborhood ?district ?assetScore ?listings ?avgPrice
        WHERE {
          ?n a bda:Neighborhood ;
             rdfs:label ?neighborhood ;
             bda:inDistrict ?d ;
             bda:tourismAssetScore ?assetScore ;
             bda:listingCount ?listings ;
             bda:avgPrice ?avgPrice .
          ?d rdfs:label ?district .
        }
        ORDER BY DESC(?assetScore) DESC(?listings)
        LIMIT 15
    """,
}


def require_rdflib():
    try:
        from rdflib import Graph
    except ImportError as err:
        raise RuntimeError("Missing rdflib. Install with: pip install -r requirements.txt") from err
    return Graph


def rows_to_markdown(result) -> str:
    headers = [str(var) for var in result.vars]
    rows = list(result)
    if not rows:
        return "_No rows returned._\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def run_queries(kg_path: Path, out_path: Path) -> Path:
    Graph = require_rdflib()
    graph = Graph()
    graph.parse(str(kg_path), format="turtle")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sections = ["# SPARQL Analysis\n"]
    for name, query in QUERIES.items():
        rows = graph.query(PREFIX + query)
        sections.append(f"## {name}\n")
        sections.append(rows_to_markdown(rows))
    out_path.write_text("\n".join(sections), encoding="utf-8")
    return out_path
