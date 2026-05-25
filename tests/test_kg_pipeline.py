import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from rdflib import Namespace, RDF, RDFS, XSD

from src.semantic_ai.embedding_ml import cluster_embeddings, extract_neighborhood_embeddings
from src.semantic_ai.embedding_dashboard import build_dashboard_html
from src.semantic_ai.kg_builder import BASE_IRI, create_graph


class KnowledgeGraphPipelineTest(unittest.TestCase):
    def test_create_graph_merges_poble_sec_name_variants(self):
        tables = {
            "district_profile": [{"district_name": "Sants-Montjuic", "tourism_asset_score": 10}],
            "neighborhood_profile": [
                {"neighborhood_name": "el Poble Sec", "district_name": "Sants-Montjuic", "tourism_asset_score": 0},
                {"neighborhood_name": "el Poble-sec", "district_name": "Sants-Montjuic", "tourism_asset_score": 73},
            ],
            "neighborhood_income_profile": [
                {"neighborhood_name": "el Poble-sec", "avg_income_eur": 18000},
            ],
            "neighborhood_hut_profile": [
                {"neighborhood_name": "el Poble Sec", "hut_license_count": 571, "total_hut_beds": 2762},
            ],
            "airbnb_zone_features": [
                {"neighborhood_name": "el Poble-sec", "listing_count": 697, "avg_price": 205.69, "avg_rating": 4.58},
            ],
        }

        with patch("src.semantic_ai.kg_builder.read_table", side_effect=lambda _db, name: tables[name]):
            graph = create_graph(Path("unused.duckdb"))

        BDA = Namespace(BASE_IRI)
        neighborhoods = list(graph.subjects(RDF.type, BDA.Neighborhood))
        labels = [str(graph.value(node, RDFS.label)) for node in neighborhoods]
        poble_sec = BDA["neighborhood/el-poble-sec"]

        self.assertEqual(neighborhoods, [poble_sec])
        self.assertEqual(labels, ["el Poble Sec"])
        self.assertEqual(float(graph.value(poble_sec, BDA.tourismAssetScore)), 73.0)
        self.assertEqual(float(graph.value(poble_sec, BDA.hutCount)), 571.0)

        airbnb_zone = BDA["airbnb-zone/el-poble-sec"]
        self.assertEqual(list(graph.subjects(RDF.type, BDA.AirbnbZone)), [airbnb_zone])
        self.assertEqual(graph.value(poble_sec, BDA.hasAirbnbZone), airbnb_zone)
        self.assertEqual(graph.value(airbnb_zone, BDA.describesNeighborhood), poble_sec)
        self.assertEqual(float(graph.value(airbnb_zone, BDA.listingCount)), 697.0)
        self.assertEqual(float(graph.value(airbnb_zone, BDA.avgPrice)), 205.69)

    def test_create_graph_declares_rdfs_domains_and_ranges(self):
        tables = {
            "district_profile": [{"district_name": "Sants-Montjuic", "tourism_asset_score": 10}],
            "neighborhood_profile": [
                {"neighborhood_name": "el Poble Sec", "district_name": "Sants-Montjuic", "tourism_asset_score": 73},
            ],
            "neighborhood_income_profile": [
                {"neighborhood_name": "el Poble Sec", "avg_income_eur": 18000},
            ],
            "neighborhood_hut_profile": [
                {"neighborhood_name": "el Poble Sec", "hut_license_count": 571, "total_hut_beds": 2762},
            ],
            "airbnb_zone_features": [
                {"neighborhood_name": "el Poble Sec", "listing_count": 697, "avg_price": 205.69, "avg_rating": 4.58},
            ],
        }

        with patch("src.semantic_ai.kg_builder.read_table", side_effect=lambda _db, name: tables[name]):
            graph = create_graph(Path("unused.duckdb"))

        BDA = Namespace(BASE_IRI)
        self.assertIn((BDA.inDistrict, RDFS.domain, BDA.Neighborhood), graph)
        self.assertIn((BDA.inDistrict, RDFS.range, BDA.District), graph)
        self.assertIn((BDA.hasAirbnbZone, RDFS.domain, BDA.Neighborhood), graph)
        self.assertIn((BDA.hasAirbnbZone, RDFS.range, BDA.AirbnbZone), graph)
        self.assertIn((BDA.describesNeighborhood, RDFS.domain, BDA.AirbnbZone), graph)
        self.assertIn((BDA.describesNeighborhood, RDFS.range, BDA.Neighborhood), graph)
        self.assertIn((BDA.listingCount, RDFS.domain, BDA.AirbnbZone), graph)
        self.assertIn((BDA.listingCount, RDFS.range, XSD.integer), graph)
        self.assertIn((BDA.incomeEur, RDFS.domain, BDA.Neighborhood), graph)
        self.assertIn((BDA.incomeEur, RDFS.range, XSD.double), graph)

    def test_extract_neighborhood_embeddings_adds_semantic_features_without_duplicate_labels(self):
        kg_path = Path("tests/fixtures/embedding_test.ttl")
        df = extract_neighborhood_embeddings(kg_path)

        self.assertEqual(len(df), 2)
        self.assertEqual(int(df["label"].duplicated().sum()), 0)
        self.assertIn("pressureOrdinal", df.columns)
        self.assertIn("hutListingRatio", df.columns)
        self.assertIn("bedsPerHut", df.columns)
        self.assertIn("listingDistrictShare", df.columns)
        self.assertIn("incomeMissing", df.columns)
        poble_sec = df.set_index("label").loc["el Poble Sec"]
        self.assertEqual(poble_sec["pressureOrdinal"], 3.0)
        self.assertAlmostEqual(poble_sec["hutListingRatio"], 0.25)
        self.assertAlmostEqual(poble_sec["bedsPerHut"], 5.0)
        hostafrancs = df.set_index("label").loc["Hostafrancs"]
        self.assertEqual(hostafrancs["incomeMissing"], 1.0)
        self.assertEqual(hostafrancs["incomeEur"], 18000.0)

    def test_cluster_embeddings_exports_kmeans_hierarchical_and_pca_outputs(self):
        kg_path = Path("tests/fixtures/embedding_test.ttl")

        with TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "cluster-report.md"

            cluster_embeddings(kg_path, out_path, k=2)

            report = out_path.read_text(encoding="utf-8")
            csv_path = out_path.with_suffix(".csv")
            self.assertTrue(csv_path.exists())
            self.assertIn("## Method Comparison", report)
            self.assertIn("KMeans", report)
            self.assertIn("Agglomerative", report)
            self.assertIn("## PCA Projection", report)

            import pandas as pd

            df = pd.read_csv(csv_path)
            self.assertIn("kmeansCluster", df.columns)
            self.assertIn("hierarchicalCluster", df.columns)
            self.assertIn("pca1", df.columns)
            self.assertIn("pca2", df.columns)
            self.assertEqual(len(df), 2)

    def test_cluster_embeddings_rejects_single_neighborhood_kg_with_clear_error(self):
        with TemporaryDirectory() as tmp_dir:
            kg_path = Path(tmp_dir) / "single.ttl"
            kg_path.write_text(
                """
                @prefix bda: <https://example.org/bda/barcelona-tourism/> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                <https://example.org/bda/barcelona-tourism/district/test> a bda:District ;
                  rdfs:label "Test District" .
                <https://example.org/bda/barcelona-tourism/neighborhood/test> a bda:Neighborhood ;
                  rdfs:label "Test <b>Neighborhood</b>" ;
                  bda:inDistrict <https://example.org/bda/barcelona-tourism/district/test> ;
                  bda:hasTourismPressure <https://example.org/bda/barcelona-tourism/pressure/low> ;
                  bda:hasAirbnbZone <https://example.org/bda/barcelona-tourism/airbnb-zone/test> ;
                  bda:tourismAssetScore "1"^^xsd:double ;
                  bda:incomeEur "10000"^^xsd:double ;
                  bda:hutCount "0"^^xsd:integer ;
                  bda:licensedBeds "0"^^xsd:integer .
                <https://example.org/bda/barcelona-tourism/airbnb-zone/test> a bda:AirbnbZone ;
                  bda:listingCount "1"^^xsd:integer ;
                  bda:avgPrice "100"^^xsd:double ;
                  bda:avgRating "4.5"^^xsd:double .
                """,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "At least 2 neighborhoods"):
                cluster_embeddings(kg_path, Path(tmp_dir) / "report.md", k=2)

    def test_build_dashboard_html_contains_interactive_visual_sections(self):
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "label": "el Poble Sec",
                    "district": "Sants-Montjuic",
                    "pressureLevel": "high",
                    "listingCount": 697,
                    "hutCount": 571,
                    "incomeEur": 18000,
                    "tourismAssetScore": 73,
                    "hutListingRatio": 0.82,
                    "bedsPerHut": 4.84,
                    "kmeansCluster": 1,
                    "hierarchicalCluster": 0,
                    "pca1": 1.2,
                    "pca2": -0.5,
                },
                {
                    "label": "Hostafrancs",
                    "district": "Sants-Montjuic",
                    "pressureLevel": "medium",
                    "listingCount": 120,
                    "hutCount": 35,
                    "incomeEur": 21000,
                    "tourismAssetScore": 40,
                    "hutListingRatio": 0.29,
                    "bedsPerHut": 3.5,
                    "kmeansCluster": 0,
                    "hierarchicalCluster": 1,
                    "pca1": -0.6,
                    "pca2": 0.8,
                },
            ]
        )

        html = build_dashboard_html(df)

        self.assertIn("<svg", html)
        self.assertIn('id="cluster-method"', html)
        self.assertIn('id="cluster-summary"', html)
        self.assertIn("KMeans", html)
        self.assertIn("Agglomerative", html)
        self.assertIn("el Poble Sec", html)
        self.assertIn("PCA", html)

    def test_build_dashboard_html_escapes_text_values_from_records(self):
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "label": "<img src=x onerror=alert(1)>",
                    "district": "District <script>alert(1)</script>",
                    "pressureLevel": "high",
                    "listingCount": 1,
                    "hutCount": 0,
                    "incomeEur": 10000,
                    "tourismAssetScore": 1,
                    "hutListingRatio": 0,
                    "bedsPerHut": 0,
                    "kmeansCluster": 0,
                    "hierarchicalCluster": 0,
                    "pca1": 0,
                    "pca2": 0,
                }
            ]
        )

        html = build_dashboard_html(df)

        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)


if __name__ == "__main__":
    unittest.main()
