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

The semantic exploitation zone is the generated RDF graph stored in
`exploitation_zone/barcelona_tourism_kg.ttl`. This file is the analysis-ready
version of the integrated data: downstream analysis does not need to join the
original DuckDB tables directly, but can consume entities, relations and
attributes through a common graph vocabulary.

## RDF/RDFS Model

The KG uses RDF/Turtle with lightweight RDFS classes and properties:

- `District`
- `Neighborhood`
- `AirbnbZone`
- `TourismPressureLevel`
- `inDistrict`
- `hasTourismPressure`
- `hasAirbnbZone`
- `describesNeighborhood`
- numeric attributes such as `listingCount`, `hutCount`, `incomeEur` and `avgPrice`

This keeps the model explainable and easy to query with SPARQL while leaving room
to extend it with listings, hotels and points of interest as individual nodes.
Core properties also declare `rdfs:domain` and `rdfs:range`, so consumers can
infer the intended subject and value types instead of relying only on naming
conventions.

Airbnb supply is represented as an `AirbnbZone` node linked from each
`Neighborhood` with `hasAirbnbZone`. Listing count, average price and average
rating belong to that zone node, while socioeconomic and HUT license metrics stay
on the neighborhood. This keeps the administrative area separate from the
short-term rental measurement unit.

### Entity Normalization

Neighborhood names are canonicalized before URI creation. This avoids creating
two graph identities for the same real-world neighborhood when source tables use
minor spelling variants. For example, `el Poble Sec` and `el Poble-sec` are
merged into the canonical label `el Poble Sec` and URI
`bda:neighborhood/el-poble-sec`.

When several rows map to the same canonical neighborhood, numeric metrics are
merged by taking the maximum non-null value. This conservative rule preserves
available signal when one source row contains zeros or missing values and another
source row contains the populated tourism metric.

### Tourism Pressure Heuristic

Tourism pressure is encoded as a lightweight semantic category (`low`, `medium`
or `high`) so it can be queried directly from SPARQL and reused as an ordinal ML
feature. The category is computed from the three most interpretable neighborhood
signals available in the integrated data:

```text
pressure_score = listings + 1.5 * HUT licenses + 0.5 * tourism asset score
```

The cutoffs are intentionally simple: scores below 40 are `low`, scores from 40
to 199 are `medium`, and scores of 200 or more are `high`. This makes the rule
easy to explain in the report and keeps the classification stable for a small
dataset. HUT licenses receive a higher weight because they represent regulated
tourist accommodation capacity, while tourism assets receive a lower weight
because they are contextual attractors rather than direct accommodation supply.

## Analysis Pipelines

Two analysis paths are implemented:

1. SPARQL pattern matching over the RDF graph.
2. ML clustering over graph-derived neighborhood embeddings.

The embedding pipeline uses graph-derived semantic embeddings rather than a
black-box graph neural method. Each neighborhood vector combines direct RDF
attributes with features derived from graph concepts and relations:

- numeric literals: Airbnb listings, average price, rating, tourism asset score,
  income, HUT licenses and licensed beds;
- semantic pressure features: ordinal pressure level and high-pressure flag;
- ratio features: HUT licenses per listing and licensed beds per HUT license;
- district-relative features: listing share within the district, income relative
  to district average and tourism assets relative to district average;
- missingness features: `incomeMissing` marks neighborhoods where income was
  absent before controlled median imputation;
- combined policy signal: low-income and high-tourism-pressure flag.

This hybrid representation is easier to inspect and justify than node2vec for a
small neighborhood-level graph, while still exploiting the KG structure. The ML
pipeline imputes missing income with the district median, then the global median
as fallback, so absent numeric values are not silently treated as real zeros. It
then applies two clustering strategies to the standardized embedding matrix:

- `KMeans` as a centroid-based baseline.
- `AgglomerativeClustering` with Ward linkage as a hierarchical alternative that
  is well suited to a small set of neighborhoods.

The report also computes silhouette scores for both methods and stores a 2D PCA
projection of the standardized embeddings. PCA is not used as the clustering
model; it is included to visually inspect whether the generated groups are
separated in a low-dimensional view.

An additional static dashboard is generated from the embedding CSV at
`analysis_zone/kg_embedding_dashboard.html`. It keeps the same analytical
content as the Markdown and CSV outputs, but makes the PCA projection easier to
inspect: each neighborhood is a selectable point, the color can switch between
KMeans and agglomerative clusters, and the side panel exposes the underlying
values used to interpret the result. The dashboard is dependency-free so it can
be opened directly in a browser or attached as a visual artifact for reporting.

Node2Vec or other random-walk embeddings are left as future work. They would be
more complex and less interpretable for this dataset size, so the current design
prioritizes reproducibility and explainability.
