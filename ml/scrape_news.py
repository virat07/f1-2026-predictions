import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
from pathlib import Path

def fetch_and_analyze_news():
    """
    Fetches the latest F1 news via RSS and performs sentiment analysis 
    on the coverage for each constructor to determine their 'Hype' or 'Momentum' score.
    """
    rss_url = "https://news.google.com/rss/search?q=F1&hl=en-US&gl=US&ceid=US:en"
    print(f"Fetching F1 news from {rss_url}")
    feed = feedparser.parse(rss_url)
    
    analyzer = SentimentIntensityAnalyzer()
    
    # Map of team keywords to identify which team an article is about
    teams = {
        "Mercedes": ["mercedes", "russell", "antonelli", "toto"],
        "Ferrari": ["ferrari", "leclerc", "hamilton", "vasseur"],
        "Red Bull Racing": ["red bull", "verstappen", "hadjar", "horner"],
        "McLaren": ["mclaren", "norris", "piastri", "brown"],
        "Aston Martin": ["aston martin", "alonso", "stroll"],
        "Alpine": ["alpine", "gasly", "colapinto"],
        "Williams": ["williams", "albon", "sainz"],
        "Racing Bulls": ["rb", "racing bulls", "lawson", "lindblad"],
        "Haas F1 Team": ["haas", "bearman", "ocon", "komatsu"],
        "Audi": ["audi", "sauber", "hulkenberg", "bortoleto"],
        "Cadillac": ["cadillac", "andretti", "bottas", "perez", "gm"]
    }
    
    team_sentiments = {team: [] for team in teams.keys()}
    
    # Process the latest 50 news articles
    for entry in feed.entries[:50]:
        # Combine headline and summary for analysis
        text = entry.title + " " + entry.get('description', '')
        # Analyze sentiment (compound score between -1.0 and 1.0)
        score = analyzer.polarity_scores(text)['compound']
        
        text_lower = text.lower()
        for team, keywords in teams.items():
            if any(kw in text_lower for kw in keywords):
                team_sentiments[team].append(score)
                
    # Calculate the average sentiment score for each team
    final_scores = {}
    for team, scores in team_sentiments.items():
        if scores:
            final_scores[team] = sum(scores) / len(scores)
        else:
            final_scores[team] = 0.0 # Neutral if no recent news
            
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "team_sentiment.json"
    
    out_path.write_text(json.dumps(final_scores, indent=2))
    print(f"Scraped {len(feed.entries[:50])} articles. Analyzed sentiment and saved to {out_path}")

if __name__ == "__main__":
    fetch_and_analyze_news()
