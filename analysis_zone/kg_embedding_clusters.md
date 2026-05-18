# KG Embedding Clusters

Each neighborhood is represented by a graph-derived semantic embedding extracted from RDF triples.

Rows clustered: 73

## Method Comparison

| method        |   clusters |   silhouette | interpretation                                               |
|:--------------|-----------:|-------------:|:-------------------------------------------------------------|
| KMeans        |          4 |        0.222 | Centroid baseline over standardized semantic features        |
| Agglomerative |          4 |        0.329 | Hierarchical grouping useful for small neighborhood datasets |

## KMeans Cluster Centroids

|   kmeansCluster |   listingCount |   avgPrice |   avgRating |   tourismAssetScore |   incomeEur |   hutCount |   licensedBeds |   pressureOrdinal |   isHighPressure |   hutListingRatio |   bedsPerHut |   listingDistrictShare |   incomeVsDistrictAvg |   tourismVsDistrictAvg |   lowIncomeHighTourism |
|----------------:|---------------:|-----------:|------------:|--------------------:|------------:|-----------:|---------------:|------------------:|-----------------:|------------------:|-------------:|-----------------------:|----------------------:|-----------------------:|-----------------------:|
|               0 |          5.231 |     74.956 |       3.942 |                3    |     13996.1 |      1     |          3.077 |             1     |                0 |             0.136 |        1.133 |                  0.023 |                 0.802 |                  0.608 |                   0    |
|               1 |       1193.33  |    211.257 |       4.613 |              137    |     18193.9 |   1059     |       6484     |             3     |                1 |             0.867 |        5.668 |                  0.506 |                 0.714 |                  3.558 |                   0    |
|               2 |         44.031 |    129.679 |       4.628 |               11.75 |     22511.1 |     19.469 |        108.5   |             1.719 |                0 |             0.455 |        5.888 |                  0.096 |                 1.043 |                  0.861 |                   0    |
|               3 |        408.76  |    192.523 |       4.59  |               37.76 |     24430.4 |    276.44  |       1564.52  |             3     |                1 |             0.815 |        5.57  |                  0.205 |                 1.083 |                  1.075 |                   0.32 |

## Agglomerative Cluster Centroids

|   hierarchicalCluster |   listingCount |   avgPrice |   avgRating |   tourismAssetScore |   incomeEur |   hutCount |   licensedBeds |   pressureOrdinal |   isHighPressure |   hutListingRatio |   bedsPerHut |   listingDistrictShare |   incomeVsDistrictAvg |   tourismVsDistrictAvg |   lowIncomeHighTourism |
|----------------------:|---------------:|-----------:|------------:|--------------------:|------------:|-----------:|---------------:|------------------:|-----------------:|------------------:|-------------:|-----------------------:|----------------------:|-----------------------:|-----------------------:|
|                     0 |        439.148 |    192.371 |       4.59  |              41.222 |     23538.1 |    306.889 |       1707.15  |             3     |                1 |             0.817 |        5.531 |                  0.232 |                 1.039 |                  1.262 |                  0.296 |
|                     1 |         34.349 |    119.167 |       4.636 |               9.605 |     20353.6 |     14.791 |         81.674 |             1.535 |                0 |             0.38  |        4.725 |                  0.078 |                 0.982 |                  0.814 |                  0     |
|                     2 |       1942     |    252.835 |       4.648 |             242     |     29815.3 |   1802     |      12472     |             3     |                1 |             0.928 |        6.921 |                  0.356 |                 1.15  |                  3.465 |                  0     |
|                     3 |          0     |      0     |       0     |               1     |     13549.2 |      0     |          0     |             1     |                0 |             0     |        0     |                  0     |                 0.792 |                  0.237 |                  0     |

## PCA Projection

The PCA coordinates are generated from the standardized embedding matrix and are meant for visual inspection of the cluster structure.

| label                      | district       | pressureLevel   |   kmeansCluster |   hierarchicalCluster |   pca1 |   pca2 |
|:---------------------------|:---------------|:----------------|----------------:|----------------------:|-------:|-------:|
| Baró de Viver              | Sant Andreu    | low             |               0 |                     3 | -3.912 | -3.367 |
| Vallbona                   | Nou Barris     | low             |               0 |                     3 | -3.818 | -3.261 |
| Ciutat Meridiana           | Nou Barris     | low             |               0 |                     1 | -3.04  | -2.023 |
| Can Peguera                | Nou Barris     | low             |               0 |                     1 | -3.022 | -1.462 |
| la Marina del Prat Vermell | Sants-Montjuïc | low             |               0 |                     1 | -2.953 | -3.028 |
| la Trinitat Nova           | Nou Barris     | low             |               0 |                     1 | -2.904 | -1.582 |
| Torre Baró                 | Nou Barris     | low             |               0 |                     1 | -2.819 | -1.515 |
| les Roquetes               | Nou Barris     | low             |               0 |                     1 | -2.609 | -0.848 |
| Montbau                    | Horta-Guinardó | low             |               0 |                     1 | -2.561 | -0.979 |
| la Trinitat Vella          | Sant Andreu    | low             |               0 |                     1 | -2.355 | -0.885 |
| el Bon Pastor              | Sant Andreu    | low             |               0 |                     1 | -2.309 | -0.596 |
| la Clota                   | Horta-Guinardó | low             |               0 |                     1 | -2.245 | -0.363 |
| el Turó de la Peira        | Nou Barris     | low             |               0 |                     1 | -2.086 | -1.378 |
| el Poble Sec               | Sants-Montjuïc | high            |               1 |                     0 |  3.289 | -4.583 |
| la Vila de Gràcia          | Gràcia         | high            |               1 |                     0 |  5.392 | -1.988 |

Full embeddings saved to `kg_embedding_clusters.csv`.
