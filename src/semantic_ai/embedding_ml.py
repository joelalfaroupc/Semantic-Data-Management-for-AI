import os
from pathlib import Path

from .kg_builder import BASE_IRI


FEATURES = [
    "listingCount",
    "avgPrice",
    "avgRating",
    "tourismAssetScore",
    "incomeEur",
    "hutCount",
    "licensedBeds",
    "pressureOrdinal",
    "isHighPressure",
    "hutListingRatio",
    "bedsPerHut",
    "incomeMissing",
    "listingDistrictShare",
    "incomeVsDistrictAvg",
    "tourismVsDistrictAvg",
    "lowIncomeHighTourism",
]


def require_dependencies():
    try:
        os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))
        import pandas as pd
        from rdflib import Graph, Namespace, RDF, RDFS
        from sklearn.cluster import AgglomerativeClustering, KMeans
        from sklearn.decomposition import PCA
        from sklearn.metrics import silhouette_score
        from sklearn.preprocessing import StandardScaler
    except ImportError as err:
        raise RuntimeError(
            "Missing ML dependencies. Install with: pip install -r requirements.txt"
        ) from err
    return pd, Graph, Namespace, RDF, RDFS, AgglomerativeClustering, KMeans, PCA, silhouette_score, StandardScaler


def numeric_value(graph, subject, predicate) -> float:
    if subject is None:
        return float("nan")
    value = graph.value(subject, predicate)
    return float(value) if value is not None else float("nan")


def first_numeric_value(graph, subjects, predicate) -> float:
    for subject in subjects:
        value = numeric_value(graph, subject, predicate)
        if value == value:
            return value
    return float("nan")


def pressure_value(uri: object) -> str:
    if uri is None:
        return "unknown"
    return str(uri).rstrip("/").split("/")[-1]


def extract_neighborhood_embeddings(kg_path: Path):
    pd, Graph, Namespace, RDF, RDFS, *_ = require_dependencies()
    graph = Graph()
    graph.parse(str(kg_path), format="turtle")
    BDA = Namespace(BASE_IRI)

    rows = []
    pressure_ordinals = {"low": 1.0, "medium": 2.0, "high": 3.0}
    for neighborhood in graph.subjects(RDF.type, BDA.Neighborhood):
        district = graph.value(neighborhood, BDA.inDistrict)
        district_label = str(graph.value(district, RDFS.label)) if district is not None else ""
        pressure = pressure_value(graph.value(neighborhood, BDA.hasTourismPressure))
        row = {
            "uri": str(neighborhood),
            "label": str(graph.value(neighborhood, RDFS.label)),
            "district": district_label,
            "pressureLevel": pressure,
        }
        airbnb_zone = graph.value(neighborhood, BDA.hasAirbnbZone)
        for feature in ["listingCount", "avgPrice", "avgRating"]:
            row[feature] = first_numeric_value(graph, [airbnb_zone, neighborhood], BDA[feature])
        for feature in ["tourismAssetScore", "incomeEur", "hutCount", "licensedBeds"]:
            row[feature] = numeric_value(graph, neighborhood, BDA[feature])
        row["pressureOrdinal"] = pressure_ordinals.get(pressure, 0.0)
        row["isHighPressure"] = 1.0 if pressure == "high" else 0.0
        row["hutListingRatio"] = (
            row["hutCount"] / row["listingCount"]
            if pd.notna(row["hutCount"]) and pd.notna(row["listingCount"]) and row["listingCount"]
            else 0.0
        )
        row["bedsPerHut"] = (
            row["licensedBeds"] / row["hutCount"]
            if pd.notna(row["licensedBeds"]) and pd.notna(row["hutCount"]) and row["hutCount"]
            else 0.0
        )
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("label").reset_index(drop=True)
    if df.empty:
        return df

    df["incomeMissing"] = df["incomeEur"].isna().astype(float)
    district_income_median = df.groupby("district")["incomeEur"].transform("median")
    global_income_median = df["incomeEur"].median()
    if pd.isna(global_income_median):
        global_income_median = 0.0
    df["incomeEur"] = df["incomeEur"].fillna(district_income_median).fillna(global_income_median)
    df["lowIncomeHighTourism"] = (
        (df["incomeEur"] < 22000) & (df["pressureLevel"] == "high")
    ).astype(float)
    district_listing_total = df.groupby("district")["listingCount"].transform("sum").replace(0, 1)
    district_income_avg = df.groupby("district")["incomeEur"].transform("mean").replace(0, 1)
    district_tourism_avg = df.groupby("district")["tourismAssetScore"].transform("mean").replace(0, 1)
    df["listingDistrictShare"] = df["listingCount"] / district_listing_total
    df["incomeVsDistrictAvg"] = df["incomeEur"] / district_income_avg
    df["tourismVsDistrictAvg"] = df["tourismAssetScore"] / district_tourism_avg
    return df


def cluster_quality(scaled, labels, silhouette_score) -> float | None:
    if len(set(labels)) < 2 or len(set(labels)) >= len(labels):
        return None
    return float(silhouette_score(scaled, labels))


def method_comparison_table(pd, rows: list[dict[str, object]]) -> str:
    display_rows = []
    for row in rows:
        display_rows.append(
            {
                "method": row["method"],
                "clusters": row["clusters"],
                "silhouette": None if row["silhouette"] is None else round(row["silhouette"], 3),
                "interpretation": row["interpretation"],
            }
        )
    return pd.DataFrame(display_rows).to_markdown(index=False)


def pca_projection_table(df, limit: int = 15) -> str:
    columns = ["label", "district", "pressureLevel", "kmeansCluster", "hierarchicalCluster", "pca1", "pca2"]
    return (
        df[columns]
        .sort_values(["kmeansCluster", "pca1", "label"])
        .head(limit)
        .round({"pca1": 3, "pca2": 3})
        .to_markdown(index=False)
    )


def cluster_embeddings(kg_path: Path, out_path: Path, k: int = 4) -> Path:
    pd, _, _, _, _, AgglomerativeClustering, KMeans, PCA, silhouette_score, StandardScaler = require_dependencies()
    df = extract_neighborhood_embeddings(kg_path)
    if df.empty:
        raise RuntimeError("No neighborhood embeddings found in KG.")

    feature_df = df[FEATURES]
    matrix = feature_df.fillna(feature_df.median(numeric_only=True)).fillna(0.0)
    scaled = StandardScaler().fit_transform(matrix)
    k = max(1, min(k, len(df)))
    kmeans_labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
    hierarchical_labels = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(scaled)
    pca_components = PCA(n_components=2, random_state=42).fit_transform(scaled)
    df["kmeansCluster"] = kmeans_labels
    df["hierarchicalCluster"] = hierarchical_labels
    df["cluster"] = kmeans_labels
    df["pca1"] = pca_components[:, 0]
    df["pca2"] = pca_components[:, 1]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False)

    kmeans_summary = (
        df.groupby("kmeansCluster")[FEATURES]
        .mean(numeric_only=True)
        .round(3)
        .reset_index()
        .to_markdown(index=False)
    )
    hierarchical_summary = (
        df.groupby("hierarchicalCluster")[FEATURES]
        .mean(numeric_only=True)
        .round(3)
        .reset_index()
        .to_markdown(index=False)
    )
    comparison = method_comparison_table(
        pd,
        [
            {
                "method": "KMeans",
                "clusters": k,
                "silhouette": cluster_quality(scaled, kmeans_labels, silhouette_score),
                "interpretation": "Centroid baseline over standardized semantic features",
            },
            {
                "method": "Agglomerative",
                "clusters": k,
                "silhouette": cluster_quality(scaled, hierarchical_labels, silhouette_score),
                "interpretation": "Hierarchical grouping useful for small neighborhood datasets",
            },
        ],
    )
    pca_preview = pca_projection_table(df)
    out_path.write_text(
        "# KG Embedding Clusters\n\n"
        "Each neighborhood is represented by a graph-derived semantic embedding extracted from RDF triples.\n\n"
        f"Rows clustered: {len(df)}\n\n"
        "## Method Comparison\n\n"
        f"{comparison}\n\n"
        "## KMeans Cluster Centroids\n\n"
        f"{kmeans_summary}\n\n"
        "## Agglomerative Cluster Centroids\n\n"
        f"{hierarchical_summary}\n\n"
        "## PCA Projection\n\n"
        "The PCA coordinates are generated from the standardized embedding matrix and are meant for visual inspection of the cluster structure.\n\n"
        f"{pca_preview}\n\n"
        f"Full embeddings saved to `{csv_path.name}`.\n",
        encoding="utf-8",
    )
    return out_path
