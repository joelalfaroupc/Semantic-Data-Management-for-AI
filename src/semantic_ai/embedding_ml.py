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
]


def require_dependencies():
    try:
        import pandas as pd
        from rdflib import Graph, Namespace, RDFS
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError as err:
        raise RuntimeError(
            "Missing ML dependencies. Install with: pip install -r requirements.txt"
        ) from err
    return pd, Graph, Namespace, RDFS, KMeans, StandardScaler


def extract_neighborhood_embeddings(kg_path: Path):
    pd, Graph, Namespace, RDFS, _, _ = require_dependencies()
    graph = Graph()
    graph.parse(str(kg_path), format="turtle")
    BDA = Namespace(BASE_IRI)

    rows = []
    for neighborhood in graph.subjects(predicate=RDFS.label):
        if not str(neighborhood).startswith(BASE_IRI + "neighborhood/"):
            continue
        row = {"uri": str(neighborhood), "label": str(graph.value(neighborhood, RDFS.label))}
        for feature in FEATURES:
            value = graph.value(neighborhood, BDA[feature])
            row[feature] = float(value) if value is not None else 0.0
        rows.append(row)
    return pd.DataFrame(rows).sort_values("label")


def cluster_embeddings(kg_path: Path, out_path: Path, k: int = 4) -> Path:
    pd, _, _, _, KMeans, StandardScaler = require_dependencies()
    df = extract_neighborhood_embeddings(kg_path)
    if df.empty:
        raise RuntimeError("No neighborhood embeddings found in KG.")

    matrix = df[FEATURES].fillna(0.0)
    scaled = StandardScaler().fit_transform(matrix)
    k = max(1, min(k, len(df)))
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
    df["cluster"] = labels

    out_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False)

    summary = (
        df.groupby("cluster")[FEATURES]
        .mean(numeric_only=True)
        .round(3)
        .reset_index()
        .to_markdown(index=False)
    )
    out_path.write_text(
        "# KG Embedding Clusters\n\n"
        "Each neighborhood is represented by a graph-derived feature embedding extracted from RDF triples.\n\n"
        f"Rows clustered: {len(df)}\n\n"
        "## Cluster Centroids\n\n"
        f"{summary}\n\n"
        f"Full embeddings saved to `{csv_path.name}`.\n",
        encoding="utf-8",
    )
    return out_path
