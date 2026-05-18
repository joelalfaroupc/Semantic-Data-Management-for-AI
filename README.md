# Semantic Data Management for AI

Project 2 extends the previous BDA data pipeline with a Knowledge Graph based
exploitation zone and two KG-based analysis pipelines.

The previous project remains the source of cleaned and integrated data:

```text
../BDA_DataPipeline/exploitation_zone/exploitation_zone.duckdb
```

## Structure

```text
scripts/
  build_kg.py               Build the RDF/RDFS knowledge graph
  run_sparql_analysis.py    Run SPARQL pattern-matching analysis
  run_embedding_ml.py       Build graph-derived embeddings and cluster neighborhoods
  build_embedding_dashboard.py
                            Build an interactive HTML dashboard from the ML CSV
src/semantic_ai/
  kg_builder.py             DuckDB -> RDF transformation
  sparql_analysis.py        SPARQL queries and Markdown reporting
  embedding_ml.py           KG feature embeddings and ML clustering
  embedding_dashboard.py    Static HTML dashboard generation
  semantic_utils.py         Shared normalization and labeling helpers
exploitation_zone/
  barcelona_tourism_kg.ttl  Generated RDF graph
analysis_zone/
  sparql_analysis.md        Generated SPARQL report
  kg_embedding_clusters.md  Generated embedding/ML report
  kg_embedding_clusters.csv Generated embedding/ML table
  kg_embedding_dashboard.html
                            Interactive visual dashboard for the ML results
```

## Setup

```bash
pip install -r requirements.txt
```

## Execution

Run from this repository root:

```bash
python scripts/build_kg.py
python scripts/run_sparql_analysis.py
python scripts/run_embedding_ml.py
python scripts/build_embedding_dashboard.py
```

If the previous project is stored elsewhere:

```bash
python scripts/build_kg.py --p1-root "C:/path/to/BDA_DataPipeline"
```

## Analytical Goal

The graph models Barcelona tourism entities such as districts, neighborhoods,
Airbnb supply, HUT licenses, income and tourism assets. The SPARQL pipeline
answers semantic questions such as high tourism pressure or many HUT licenses in
lower-income neighborhoods. The embedding pipeline represents each neighborhood
as a graph-derived semantic feature vector, including direct RDF attributes,
tourism pressure levels, ratios and district-relative indicators. It compares a
KMeans baseline with hierarchical agglomerative clustering, reports silhouette
scores, and exports PCA coordinates for visual inspection of the neighborhood
groups. The HTML dashboard at `analysis_zone/kg_embedding_dashboard.html` uses
the exported CSV to show the PCA scatter plot, switch between KMeans and
Agglomerative clusters, inspect each neighborhood, and summarize cluster totals.
