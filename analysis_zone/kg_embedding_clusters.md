# KG Embedding Clusters

Each neighborhood is represented by a graph-derived semantic embedding extracted from RDF triples.

Rows clustered: 73

## Method Comparison

| method        |   clusters |   silhouette | interpretation                                               |
|:--------------|-----------:|-------------:|:-------------------------------------------------------------|
| KMeans        |          4 |        0.175 | Centroid baseline over standardized semantic features        |
| Agglomerative |          4 |        0.165 | Hierarchical grouping useful for small neighborhood datasets |

## KMeans Cluster Centroids

|   kmeansCluster |   listingCount |   avgPrice |   avgRating |   tourismAssetScore |   incomeEur |   hutCount |   licensedBeds |   pressureOrdinal |   isHighPressure |   hutListingRatio |   bedsPerHut |   incomeMissing |   listingDistrictShare |   incomeVsDistrictAvg |   tourismVsDistrictAvg |   lowIncomeHighTourism |
|----------------:|---------------:|-----------:|------------:|--------------------:|------------:|-----------:|---------------:|------------------:|-----------------:|------------------:|-------------:|----------------:|-----------------------:|----------------------:|-----------------------:|-----------------------:|
|               0 |        439.148 |    192.371 |       4.59  |              41.222 |     24321.2 |    306.889 |       1707.15  |             3     |                1 |             0.817 |        5.531 |           0.037 |                  0.232 |                 1.025 |                  1.262 |                  0.333 |
|               1 |         45.87  |    144.698 |       4.617 |              14.87  |     24541.4 |     22.261 |        124.087 |             1.783 |                0 |             0.504 |        5.93  |           0     |                  0.109 |                 1.085 |                  1.043 |                  0     |
|               2 |         19.182 |     89.805 |       4.657 |               3.318 |     16318.1 |      5.636 |         47     |             1.227 |                0 |             0.216 |        3.035 |           0.045 |                  0.04  |                 0.873 |                  0.521 |                  0     |
|               3 |       1942     |    252.835 |       4.648 |             242     |     29815.3 |   1802     |      12472     |             3     |                1 |             0.928 |        6.921 |           0     |                  0.356 |                 1.15  |                  3.465 |                  0     |

## Agglomerative Cluster Centroids

|   hierarchicalCluster |   listingCount |   avgPrice |   avgRating |   tourismAssetScore |   incomeEur |   hutCount |   licensedBeds |   pressureOrdinal |   isHighPressure |   hutListingRatio |   bedsPerHut |   incomeMissing |   listingDistrictShare |   incomeVsDistrictAvg |   tourismVsDistrictAvg |   lowIncomeHighTourism |
|----------------------:|---------------:|-----------:|------------:|--------------------:|------------:|-----------:|---------------:|------------------:|-----------------:|------------------:|-------------:|----------------:|-----------------------:|----------------------:|-----------------------:|-----------------------:|
|                     0 |        434.481 |    188.53  |       4.583 |              41.037 |     23916   |    303.074 |       1680.7   |             2.926 |            0.963 |             0.802 |        5.401 |           0.074 |                  0.229 |                 1.009 |                  1.247 |                  0.333 |
|                     1 |         44.914 |    127.755 |       4.612 |              11.314 |     22334.7 |     21     |        120.457 |             1.714 |            0.029 |             0.464 |        5.762 |           0     |                  0.095 |                 1.026 |                  0.885 |                  0     |
|                     2 |       1942     |    252.835 |       4.648 |             242     |     29815.3 |   1802     |      12472     |             3     |            1     |             0.928 |        6.921 |           0     |                  0.356 |                 1.15  |                  3.465 |                  0     |
|                     3 |          3.1   |     94.555 |       4.764 |               2.4   |     15267.8 |      0.4   |          5     |             1     |            0     |             0.052 |        0.5   |           0     |                  0.014 |                 0.87  |                  0.491 |                  0     |

## PCA Projection

The PCA coordinates are generated from the standardized embedding matrix and are meant for visual inspection of the cluster structure.

| label                                        | district            | pressureLevel   |   kmeansCluster |   hierarchicalCluster |   pca1 |   pca2 |
|:---------------------------------------------|:--------------------|:----------------|----------------:|----------------------:|-------:|-------:|
| la Barceloneta                               | Ciutat Vella        | high            |               0 |                     0 |  0.482 | -1.374 |
| el Parc i la Llacuna del Poblenou            | Sant Martí          | high            |               0 |                     0 |  1.149 |  0.576 |
| Sants - Badal                                | Sants-Montjuïc      | high            |               0 |                     0 |  1.172 |  0.519 |
| el Baix Guinardó                             | Horta-Guinardó      | high            |               0 |                     0 |  1.25  |  0.972 |
| el Camp d'en Grassot i Gràcia Nova           | Gràcia              | high            |               0 |                     0 |  1.279 |  1.046 |
| el Putxet i el Farró                         | Sarrià-Sant Gervasi | high            |               0 |                     0 |  1.411 |  0.846 |
| la Font de la Guatlla                        | Sants-Montjuïc      | high            |               0 |                     0 |  1.478 |  1.351 |
| Sants                                        | Sants-Montjuïc      | high            |               0 |                     0 |  1.518 |  0.733 |
| la Vila Olímpica del Poblenou                | Sant Martí          | high            |               0 |                     1 |  1.552 |  3.134 |
| Sant Gervasi - la Bonanova                   | Sarrià-Sant Gervasi | high            |               0 |                     0 |  1.573 |  2.238 |
| Hostafrancs                                  | Sants-Montjuïc      | high            |               0 |                     0 |  1.583 |  0.421 |
| el Fort Pienc                                | Eixample            | high            |               0 |                     0 |  1.692 |  0.532 |
| el Guinardó                                  | Horta-Guinardó      | high            |               0 |                     0 |  1.696 |  0.406 |
| el Camp de l'Arpa del Clot                   | Sant Martí          | high            |               0 |                     0 |  1.712 |  1.07  |
| Diagonal Mar i el Front Marítim del Poblenou | Sant Martí          | high            |               0 |                     0 |  1.91  |  1.959 |

Full embeddings saved to `kg_embedding_clusters.csv`.
