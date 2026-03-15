"""
ml/scrape_news.py
Fetches recent F1 news headlines and scores basic sentiment per constructor.
Output: ml/processed/news_sentiment.json

Used as optional features in export_predictions.py.
Run standalone: python -m ml.scrape_news
"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from config import PROCESSED_DIR, CONSTRUCTORS_2026

CONSTRUCTORS = CONSTRUCTORS_2026

# Simple keyword sentiment lists
_POSITIVE = {"win", "wins", "won", "victory", "podium", "fastest", "pole",
             "dominant", "strong", "upgrade", "ahead", "lead", "leading"}
_NEGATIVE = {"crash", "penalty", "retire", "retired", "dnf", "issue",
             "problem", "slow", "struggle", "behind", "loss", "lost", "ban"}

OUTPUT_FILE = PROCESSED_DIR / "news_sentiment.json"


def _fetch_headlines(query: str, max_results: int = 10) -> list[str]:
    """Fetch headlines from RSS via Google News (no API key needed)."""
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}+F1+Formula1&hl=en-US&gl=US&ceid=US:en"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        # Extract <title> tags (skip first — it's the feed title)
        titles = []
        for part in content.split("<title>")[2:]:  # [0]=feed title, skip
            title = part.split("</title>")[0].strip()
            if title:
                titles.append(title)
            if len(titles) >= max_results:
                break
        return titles
    except Exception as exc:
        print(f"  Warning: could not fetch news for '{query}': {exc}")
        return []


def _score_sentiment(headlines: list[str]) -> float:
    """
    Return a sentiment score in [-1, 1] based on keyword counts.
    Positive keywords → +1, negative → -1, averaged over all words found.
    """
    pos, neg = 0, 0
    for h in headlines:
        words = set(h.lower().split())
        pos += len(words & _POSITIVE)
        neg += len(words & _NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 4)


def scrape_news() -> dict:
    """
    Scrape recent F1 news for each constructor and return sentiment scores.
    """
    print("Scraping F1 news sentiment …")
    results = {}
    for constructor in CONSTRUCTORS:
        # Use a short search-friendly alias
        alias = constructor.replace(" F1 Team", "").replace(" Racing", "")
        headlines = _fetch_headlines(alias)
        score = _score_sentiment(headlines)
        results[constructor] = {
            "sentiment_score": score,
            "headline_count": len(headlines),
            "sample_headlines": headlines[:3],
        }
        print(f"  {constructor:<25} sentiment={score:+.3f}  ({len(headlines)} headlines)")

    output = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "constructors": results,
    }
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    print(f"Saved → {OUTPUT_FILE}")
    return output


if __name__ == "__main__":
    scrape_news()