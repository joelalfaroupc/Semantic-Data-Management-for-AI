# Design Choices

## Reuse of Project 1

Project 2 does not modify the previous `BDA_DataPipeline` repository. It reads
the already integrated DuckDB database from Project 1 and builds a new semantic
exploitation layer in this repository.

## Knowledge Graph Scope

The first RDF graph focuses on neighborhood-level tourism pressure because the
previous project already provides reliable integrated tables at this granularity.
The graph includes districts, neighborhoods, income, HUT licenses, Airbnb supply
and tourism asset indicators.

## RDF/RDFS Model

The KG uses RDF/Turtle with lightweight RDFS classes and properties:

- `District`
- `Neighborhood`
- `TourismPressureLevel`
- `inDistrict`
- `hasTourismPressure`
- numeric attributes such as `listingCount`, `hutCount`, `incomeEur` and `avgPrice`

This keeps the model explainable and easy to query with SPARQL while leaving room
to extend it with listings, hotels and points of interest as individual nodes.

## Analysis Pipelines

Two analysis paths are implemented:

1. SPARQL pattern matching over the RDF graph.
2. ML clustering over graph-derived neighborhood embeddings.

The embedding pipeline is intentionally lightweight: it extracts a numeric vector
from RDF triples for each neighborhood and applies KMeans. This provides a clear
baseline before adding heavier graph embedding methods such as node2vec.
