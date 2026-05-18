import re
import unicodedata


def normalize_literal(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\ufeff", "").strip()
    return re.sub(r"\s+", " ", text)


def uri_safe(value: object) -> str:
    text = normalize_literal(value).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "unknown"


def canonical_neighborhood_name(value: object) -> str:
    text = normalize_literal(value)
    canonical_key = uri_safe(text)
    aliases = {
        "el-poble-sec": "el Poble Sec",
    }
    return aliases.get(canonical_key, text)


def classify_tourism_pressure(
    listing_count: float,
    hut_count: float,
    tourism_asset_score: float,
) -> str:
    score = float(listing_count) * 1.0 + float(hut_count) * 1.5 + float(tourism_asset_score) * 0.5
    if score >= 200:
        return "high"
    if score >= 40:
        return "medium"
    return "low"
