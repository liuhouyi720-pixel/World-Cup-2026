from functools import lru_cache
import pandas as pd
from .config import DATA

ALIASES = {
    "USA": "United States",
    "United States of America": "United States",
    "Korea Republic": "South Korea",
    "Czech Republic": "Czechia",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "DR Congo": "Democratic Republic of the Congo",
    "Côte d’Ivoire": "Ivory Coast",
}

@lru_cache(maxsize=1)
def mapping() -> dict[str, str]:
    result = dict(ALIASES)
    path = DATA / "team_name_mapping.csv"
    if path.exists():
        for row in pd.read_csv(path).itertuples(index=False):
            result[str(row.source_name).strip()] = str(row.canonical_team_name).strip()
    return result

load_mapping = mapping

def normalize_team_name(value, custom_mapping: dict[str, str] | None = None):
    if value is None or pd.isna(value):
        return None
    clean = str(value).strip()
    return (custom_mapping if custom_mapping is not None else mapping()).get(clean, clean)

