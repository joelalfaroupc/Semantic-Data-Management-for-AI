import unittest

from src.semantic_ai.semantic_utils import (
    canonical_neighborhood_name,
    classify_tourism_pressure,
    normalize_literal,
    uri_safe,
)


class SemanticUtilsTest(unittest.TestCase):
    def test_uri_safe_normalizes_accents_spaces_and_symbols(self):
        self.assertEqual(uri_safe("la Dreta de l'Eixample"), "la-dreta-de-l-eixample")
        self.assertEqual(uri_safe("Sant Martí / Provençals"), "sant-marti-provencals")

    def test_normalize_literal_strips_bom_and_collapses_spaces(self):
        self.assertEqual(normalize_literal("\ufeff  Sant   Martí  "), "Sant Martí")

    def test_canonical_neighborhood_name_merges_poble_sec_variants(self):
        self.assertEqual(canonical_neighborhood_name("el Poble Sec"), "el Poble Sec")
        self.assertEqual(canonical_neighborhood_name("el Poble-sec"), "el Poble Sec")

    def test_tourism_pressure_uses_listing_hut_and_asset_density(self):
        high = classify_tourism_pressure(
            listing_count=120,
            hut_count=40,
            tourism_asset_score=85.0,
        )
        medium = classify_tourism_pressure(
            listing_count=40,
            hut_count=8,
            tourism_asset_score=25.0,
        )
        low = classify_tourism_pressure(
            listing_count=5,
            hut_count=0,
            tourism_asset_score=3.0,
        )

        self.assertEqual(high, "high")
        self.assertEqual(medium, "medium")
        self.assertEqual(low, "low")


if __name__ == "__main__":
    unittest.main()
