# Barcelona Tourism Knowledge Graph

**RDF modelling, semantic queries and neighborhood clustering from integrated urban data.**

This university team project extends the [Barcelona Tourism Data Pipeline](https://github.com/joelalfaroupc/BDA_DataPipeline) with a knowledge graph and two analytical workflows: SPARQL pattern matching and clustering of graph-derived neighborhood features.

## What the project delivers

- An RDF/RDFS graph connecting Barcelona districts, neighborhoods, accommodation supply, tourist licenses, income and tourism assets.
- SPARQL analyses that expose relationships between tourism pressure and neighborhood characteristics.
- A reusable 16-feature representation of each neighborhood.
- KMeans and Ward clustering, evaluation summaries and an interactive HTML dashboard.

## Architecture

```text
Integrated DuckDB database
          ↓
      RDF/RDFS graph
          ├── SPARQL queries → analytical report
          └── Semantic features → scaling → clustering → PCA dashboard
```

| Component | Implementation | Output |
| --- | --- | --- |
| Graph construction | [kg_builder.py](src/semantic_ai/kg_builder.py) | [RDF graph](exploitation_zone/barcelona_tourism_kg.ttl) |
| Semantic analysis | [sparql_analysis.py](src/semantic_ai/sparql_analysis.py) | [SPARQL report](analysis_zone/sparql_analysis.md) |
| Feature generation and clustering | [embedding_ml.py](src/semantic_ai/embedding_ml.py) | [cluster report](analysis_zone/kg_embedding_clusters.md), [CSV](analysis_zone/kg_embedding_clusters.csv) |
| Visualization | [embedding_dashboard.py](src/semantic_ai/embedding_dashboard.py) | [HTML dashboard](analysis_zone/kg_embedding_dashboard.html) |

The feature vectors encode graph attributes, ratios, tourism-pressure indicators and district-relative information. They are engineered semantic features, rather than learned neural graph embeddings. Missing income values use district/global median imputation with a missing-value flag.

Features are standardized before KMeans and Ward agglomerative clustering. PCA projects them into two dimensions for visual inspection; it does not establish cluster validity.

## Results and use

The [recorded cluster report](analysis_zone/kg_embedding_clusters.md) covers **73 neighborhoods** and compares **four clusters**. Reported silhouette scores are **0.175 for KMeans** and **0.165 for Ward**.

The separation is modest. These groups support exploratory comparison of neighborhood profiles, not a validated classification of tourism impacts or a causal explanation.

Download or clone the repository and open `analysis_zone/kg_embedding_dashboard.html` in a browser. It provides a PCA view, switches between clustering methods, and displays neighborhood details and cluster totals. GitHub's file preview does not run the dashboard.

## Setup and execution

The pipeline needs the integrated database from the preceding project:

```text
workspace/
├── BDA_DataPipeline/exploitation_zone/exploitation_zone.duckdb
└── Semantic-Data-Management-for-AI/
```

From this repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_all.py --p1-root ../BDA_DataPipeline
```

On Windows, activate with `.venv\Scripts\activate`. If the data pipeline is elsewhere, pass its repository directory to `--p1-root`. Dependencies are not pinned.

The runner builds the graph, executes SPARQL analysis, performs clustering and writes the dashboard. Individual stages can also be run:

```bash
python scripts/build_kg.py
python scripts/run_sparql_analysis.py
python scripts/run_embedding_ml.py
python scripts/build_embedding_dashboard.py
```

Those default commands expect the sibling directory shown above.

## Tests and design notes

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

See [tests](tests/) for graph, normalization and runner checks, and [design choices](docs/design_choices.md) for modelling decisions. The figures above come from versioned reports; this documentation update does not claim a fresh pipeline or test execution.

## Project context

This repository preserves the university team's implementation and commit history from [Albertroca9/Semantic-Data-Management-for-AI](https://github.com/Albertroca9/Semantic-Data-Management-for-AI). This portfolio edition improves the explanation of the methods, results and execution requirements.
