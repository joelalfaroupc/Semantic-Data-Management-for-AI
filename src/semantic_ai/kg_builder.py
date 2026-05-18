from pathlib import Path

from .semantic_utils import canonical_neighborhood_name, classify_tourism_pressure, normalize_literal, uri_safe


BASE_IRI = "https://example.org/bda/barcelona-tourism/"


def require_dependencies():
    try:
        import duckdb
        from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD
    except ImportError as err:
        raise RuntimeError(
            "Missing dependency. Install project requirements with: pip install -r requirements.txt"
        ) from err
    return duckdb, Graph, Literal, Namespace, RDF, RDFS, XSD


def read_table(db_path: Path, table_name: str) -> list[dict[str, object]]:
    duckdb, *_ = require_dependencies()
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        cursor = conn.execute(f'SELECT * FROM "{table_name}"')
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def add_literal(graph, subject, predicate, value, datatype=None):
    if value in (None, ""):
        return
    _, _, Literal, *_ = require_dependencies()
    graph.add((subject, predicate, Literal(value, datatype=datatype)))


def numeric_or_zero(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def merge_numeric_max(existing: dict[str, object], incoming: dict[str, object], columns: list[str]) -> None:
    for column in columns:
        if column in incoming:
            existing[column] = max(numeric_or_zero(existing.get(column)), numeric_or_zero(incoming.get(column)))


def index_rows_by_neighborhood(rows: list[dict[str, object]], numeric_columns: list[str]) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    for row in rows:
        name = canonical_neighborhood_name(row["neighborhood_name"])
        if name not in indexed:
            indexed[name] = {**row, "neighborhood_name": name}
            continue
        merge_numeric_max(indexed[name], row, numeric_columns)
    return indexed


def create_graph(db_path: Path):
    _, Graph, Literal, Namespace, RDF, RDFS, XSD = require_dependencies()

    graph = Graph()
    BDA = Namespace(BASE_IRI)
    graph.bind("bda", BDA)
    graph.bind("rdfs", RDFS)

    for class_name in ["District", "Neighborhood", "AirbnbZone", "TourismPressureLevel"]:
        graph.add((BDA[class_name], RDF.type, RDFS.Class))

    properties = [
        "inDistrict",
        "hasTourismPressure",
        "listingCount",
        "avgPrice",
        "avgRating",
        "tourismAssetScore",
        "incomeEur",
        "hutCount",
        "licensedBeds",
    ]
    for prop in properties:
        graph.add((BDA[prop], RDF.type, RDF.Property))

    district_rows = read_table(db_path, "district_profile")
    neighborhood_rows = read_table(db_path, "neighborhood_profile")
    income_rows = read_table(db_path, "neighborhood_income_profile")
    hut_rows = read_table(db_path, "neighborhood_hut_profile")
    zone_rows = read_table(db_path, "airbnb_zone_features")

    neighborhood_by_name = index_rows_by_neighborhood(neighborhood_rows, ["tourism_asset_score"])
    income_by_neighborhood = index_rows_by_neighborhood(income_rows, ["avg_income_eur"])
    hut_by_neighborhood = index_rows_by_neighborhood(hut_rows, ["hut_license_count", "total_hut_beds"])
    zone_by_neighborhood = index_rows_by_neighborhood(zone_rows, ["listing_count", "avg_price", "avg_rating"])

    for row in district_rows:
        district_name = normalize_literal(row["district_name"])
        district = BDA[f"district/{uri_safe(district_name)}"]
        graph.add((district, RDF.type, BDA.District))
        graph.add((district, RDFS.label, Literal(district_name)))
        add_literal(graph, district, BDA.tourismAssetScore, row.get("tourism_asset_score"), XSD.double)

    for neighborhood_name, row in sorted(neighborhood_by_name.items()):
        district_name = normalize_literal(row["district_name"])
        neighborhood = BDA[f"neighborhood/{uri_safe(neighborhood_name)}"]
        district = BDA[f"district/{uri_safe(district_name)}"]
        income = income_by_neighborhood.get(neighborhood_name, {})
        hut = hut_by_neighborhood.get(neighborhood_name, {})
        zone = zone_by_neighborhood.get(neighborhood_name, {})

        listing_count = float(zone.get("listing_count") or 0)
        hut_count = float(hut.get("hut_license_count") or 0)
        asset_score = float(row.get("tourism_asset_score") or 0)
        pressure = classify_tourism_pressure(listing_count, hut_count, asset_score)

        graph.add((neighborhood, RDF.type, BDA.Neighborhood))
        graph.add((neighborhood, RDFS.label, Literal(neighborhood_name)))
        graph.add((neighborhood, BDA.inDistrict, district))
        graph.add((neighborhood, BDA.hasTourismPressure, BDA[f"pressure/{pressure}"]))
        graph.add((BDA[f"pressure/{pressure}"], RDF.type, BDA.TourismPressureLevel))
        graph.add((BDA[f"pressure/{pressure}"], RDFS.label, Literal(pressure)))
        add_literal(graph, neighborhood, BDA.tourismAssetScore, asset_score, XSD.double)
        add_literal(graph, neighborhood, BDA.incomeEur, income.get("avg_income_eur"), XSD.double)
        add_literal(graph, neighborhood, BDA.hutCount, hut_count, XSD.integer)
        add_literal(graph, neighborhood, BDA.licensedBeds, hut.get("total_hut_beds"), XSD.integer)
        add_literal(graph, neighborhood, BDA.listingCount, listing_count, XSD.integer)
        add_literal(graph, neighborhood, BDA.avgPrice, zone.get("avg_price"), XSD.double)
        add_literal(graph, neighborhood, BDA.avgRating, zone.get("avg_rating"), XSD.double)

    return graph


def build_kg(db_path: Path, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    graph = create_graph(db_path)
    graph.serialize(destination=str(out_path), format="turtle")
    return out_path
