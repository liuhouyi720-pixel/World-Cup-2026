"""Build the dashboard's offline 2026 schedule/results cache.

The running application never calls these sources. This script is only for
rebuilding local data after checkout or conflict resolution.
"""
from __future__ import annotations
import csv
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "world_cup_2026"
RESULTS_URL = "https://www.thestatszone.com/fwc26/matches/results"
FIXTURES_URL = "https://www.thestatsapi.com/world-cup/data/fixtures.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
ALIASES = {
    "Korea Republic": "South Korea",
    "USA": "United States",
    "Turkiye": "Turkey",
    "Türkiye": "Turkey",
    "Czech Republic": "Czechia",
}

def download(url: str) -> str:
    return urlopen(Request(url, headers=HEADERS), timeout=45).read().decode("utf-8", "replace")

def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<.*?>", "", value))).strip()

def canonical(team: str) -> str:
    return ALIASES.get(team.strip(), team.strip())

def parse_results() -> list[dict]:
    page = download(RESULTS_URL)
    encoded = re.search(r'data-hx-vals="([^\"]*sprig:config[^\"]*)"', page)
    if not encoded:
        raise RuntimeError("The result page no longer exposes its pagination configuration.")
    config = json.loads(unescape(encoded.group(1)))["sprig:config"]
    endpoint = "https://www.thestatszone.com/index.php?p=actions/sprig-core/components/render&" + urlencode(
        {"sprig:config": config, "activeTab": "results", "visibleLimit": "104"}
    )
    fragment = download(endpoint)
    cards = re.findall(r'<div data-local-match-item data-local-kickoff="([^"]+)">(.*?)</a>', fragment, re.S)
    if len(cards) != 104:
        raise RuntimeError(f"Expected 104 result cards; found {len(cards)}.")
    stage_names = {
        "Round of 32": "Round of 32", "Round of 16": "Round of 16",
        "Quarter-finals": "Quarter-finals", "Semi-finals": "Semi-finals",
        "3rd Place Final": "Third place", "Final": "Final",
    }
    results = []
    for kickoff, card in cards:
        source_url = re.search(r'<a href="([^"]+)"', card).group(1)
        status = clean(re.search(r'<div class="text-slate-500[^>]*>\s*(.*?)\s*</div>', card, re.S).group(1))
        source_stage = clean(re.search(r'<div>([^<]+)</div>\s*</div>\s*\n\s*<div class="grid', card).group(1))
        teams = re.findall(r'<div class="font-slab font-bold text-lg truncate">\s*([^<]+)\s*</div>\s*<div[^>]*>\s*(\d+)\s*</div>', card)
        if len(teams) != 2:
            raise RuntimeError(f"Could not parse teams from {source_url}")
        note_match = re.search(r'<div class="mt-2[^>]*>\s*(.*?)\s*</div>', card, re.S)
        note = clean(note_match.group(1)) if note_match else ""
        home, home_score = teams[0]
        away, away_score = teams[1]
        if source_stage.startswith("Group "):
            stage, group = "Group", source_stage.split()[-1]
        else:
            stage, group = stage_names[source_stage], ""
        winner_match = re.search(r"· (.*?) won after", note)
        if winner_match:
            winner = canonical(winner_match.group(1))
        elif int(home_score) > int(away_score):
            winner = canonical(home)
        elif int(away_score) > int(home_score):
            winner = canonical(away)
        else:
            winner = ""
        results.append({
            "match_id": "tsz_" + source_url.rstrip("/").split("/")[-1],
            "kickoff": kickoff, "stage": stage, "group": group,
            "home_team": canonical(home), "away_team": canonical(away),
            "home_score": home_score, "away_score": away_score,
            "winner": winner, "status": status, "venue": "",
            "source_url": source_url, "result_note": note,
        })
    return sorted(results, key=lambda result: (result["kickoff"], result["match_id"]))

def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    results = parse_results()
    write_csv(DATA / "matches.csv", results)
    (DATA / "fixtures_source.csv").write_text(download(FIXTURES_URL), encoding="utf-8")
    teams = sorted({row["home_team"] for row in results} | {row["away_team"] for row in results})
    mappings = [
        {"canonical_team_name": team, "source_name": team, "source_file": "matches.csv", "country_code": "", "notes": "Cached result source"}
        for team in teams
    ] + [
        {"canonical_team_name": canonical(alias), "source_name": alias, "source_file": "fixtures_source.csv", "country_code": "", "notes": "Schedule source alias"}
        for alias in ALIASES
    ]
    write_csv(DATA / "team_name_mapping.csv", mappings)
    priors = [
        {"team": team, "strength_score": 0.0, "source": "global_neutral_fallback", "data_date": "", "manually_configured": False, "notes": "Historical xT proxy may replace this fallback."}
        for team in teams
    ]
    write_csv(DATA / "team_strength_priors.csv", priors)
    print(f"Cached {len(results)} matches and {len(teams)} teams.")

if __name__ == "__main__":
    main()

