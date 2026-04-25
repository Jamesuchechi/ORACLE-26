"""
◈ CONFLUX — Social Signal
==========================
Tracks public attention and cultural momentum via:
  - Google Trends (pytrends)
  - Reddit sentiment (PRAW)
  - Cultural moment tipping point detector (Vertical IV)
"""

import os
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    ALL_WC_TEAMS, TRACKED_CULTURAL_TOPICS, TIPPING_POINT_THRESHOLD
)

load_dotenv()
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


class SocialSignalEngine:
    """
    Builds social attention and sentiment signals across all four verticals.
    """

    def __init__(self):
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl="en-US", tz=360)
            self._trends_available = True
        except ImportError:
            self.pytrends = None
            self._trends_available = False

        try:
            import praw
            self.reddit = praw.Reddit(
                client_id     = os.getenv("REDDIT_CLIENT_ID", ""),
                client_secret = os.getenv("REDDIT_CLIENT_SECRET", ""),
                user_agent    = os.getenv("REDDIT_USER_AGENT", "conflux/1.0"),
            )
            self._reddit_available = bool(os.getenv("REDDIT_CLIENT_ID"))
        except:
            self.reddit = None
            self._reddit_available = False
            
        self.cache_path = RAW_DIR / "trends_cache.json"
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self._cache, f)
        except: pass


    # ──────────────────────────────────────────────
    # Google Trends
    # ──────────────────────────────────────────────

    def fetch_trends_batch(self, terms: list, timeframe: str = "today 3-m") -> dict:
        """Fetch Google Trends for up to 5 terms with caching and backoff."""
        now = time.time()
        results = {}
        missing = []

        # 1. Check Cache
        for t in terms:
            entry = self._cache.get(t)
            if entry and (now - entry.get("ts", 0)) < 86400:  # 24h TTL
                results[t] = entry["val"]
            else:
                missing.append(t)

        if not missing:
            return results

        if not self._trends_available or not self.pytrends:
            return {t: self._synthetic_trend(t) for t in terms}

        # 2. Fetch Missing with Exponential Backoff
        max_retries = 3
        delay = 30
        
        try:
            for attempt in range(max_retries):
                try:
                    self.pytrends.build_payload(missing[:5], timeframe=timeframe)
                    df = self.pytrends.interest_over_time()
                    
                    for term in missing[:5]:
                        val = float(df[term].mean()) if term in df.columns else self._synthetic_trend(term)
                        results[term] = val
                        # Update cache
                        self._cache[term] = {"val": val, "ts": now}
                    
                    self._save_cache()
                    return results
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        print(f"  [social] Rate limited (429). Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise e
        except Exception as e:
            print(f"  [social] Trends failed for {missing}: {e}")
            # Final fallback
            for t in missing:
                results[t] = self._synthetic_trend(t)
            return results


    def _synthetic_trend(self, term: str) -> float:
        """Deterministic synthetic trend based on term hash (for reproducibility)."""
        seed = sum(ord(c) for c in term) % 100
        return float(seed)

    def fetch_team_trends(self) -> pd.DataFrame:
        """Fetch search momentum for all 48 WC teams."""
        print("  [social] Fetching team search trends...")
        scores = {}

        for i in range(0, len(ALL_WC_TEAMS), 5):
            batch = ALL_WC_TEAMS[i:i + 5]
            result = self.fetch_trends_batch(
                [f"{t} football" for t in batch], timeframe="today 3-m"
            )
            for j, team in enumerate(batch):
                key = f"{team} football"
                scores[team] = result.get(key, self._synthetic_trend(team))
            time.sleep(2)   # Polite rate limiting

        # Normalize to [0, 1]
        vals = list(scores.values())
        mn, mx = min(vals), max(vals)

        rows = []
        for team, raw in scores.items():
            norm = (raw - mn) / (mx - mn) if mx > mn else 0.5
            rows.append({
                "team":          team,
                "trend_raw":     round(raw, 2),
                "social_signal": round(float(norm), 4),
            })

        df = pd.DataFrame(rows).sort_values("social_signal", ascending=False).reset_index(drop=True)
        df.to_csv(RAW_DIR / "social_signals_wc.csv", index=False)
        return df

    # ──────────────────────────────────────────────
    # Vertical IV — Cultural Moment Detector
    # ──────────────────────────────────────────────

    def detect_tipping_point(self, topic: str) -> dict:
        """
        Compute tipping point probability for a cultural topic.
        Combines trend momentum, acceleration, and market confirmation.
        """
        meta = TRACKED_CULTURAL_TOPICS.get(topic, {})

        # Trend data (6-month window)
        trend_data = self.fetch_trends_batch([topic], timeframe="today 6-m")
        raw_trend  = trend_data.get(topic, 50.0)
        trend_norm = float(np.clip(raw_trend / 100, 0, 1))

        # Momentum: 3-month vs 6-month (is it accelerating?)
        recent_data  = self.fetch_trends_batch([topic], timeframe="today 3-m")
        recent_trend = recent_data.get(topic, raw_trend)
        time.sleep(2)

        momentum = float(np.clip((recent_trend - raw_trend) / 50 + 0.5, 0, 1))

        # Reddit presence signal
        reddit_signal = self._fetch_reddit_signal(topic)

        # Combined tipping point score
        tp_score = trend_norm * 0.45 + momentum * 0.35 + reddit_signal * 0.20
        is_tipping = tp_score >= TIPPING_POINT_THRESHOLD

        return {
            "topic":              topic,
            "category":           meta.get("category", "general"),
            "market_proxy":       meta.get("market_proxy"),
            "trend_score":        round(trend_norm, 4),
            "momentum_score":     round(momentum, 4),
            "reddit_signal":      round(reddit_signal, 4),
            "tipping_score":      round(tp_score, 4),
            "is_tipping":         is_tipping,
            "social_signal":      round(tp_score, 4),
            "interpretation": (
                f"{'TIPPING POINT DETECTED' if is_tipping else 'Building momentum'}: "
                f"{topic} scores {tp_score:.0%} on the CONFLUX cultural moment detector."
            )
        }

    def _fetch_reddit_signal(self, topic: str) -> float:
        """Fetch Reddit presence signal for a topic."""
        if not self._reddit_available or not self.reddit:
            # Synthetic: based on topic category
            meta = TRACKED_CULTURAL_TOPICS.get(topic, {})
            category_base = {
                "technology": 0.70, "health": 0.55, "sports": 0.65,
                "food": 0.50, "automotive": 0.60,
            }
            return float(category_base.get(meta.get("category", "general"), 0.50))

        try:
            subreddit = self.reddit.subreddit("all")
            posts = list(subreddit.search(topic, limit=25, time_filter="month"))
            if not posts:
                return 0.3
            avg_score = np.mean([p.score for p in posts])
            # Normalize: 1000 upvotes = strong signal
            return float(np.clip(avg_score / 1000, 0, 1))
        except:
            return 0.4

    def build_cultural_moment_signals(self) -> pd.DataFrame:
        """Run cultural moment detection on all tracked topics."""
        print("  [social] Detecting cultural moments...")
        rows = [self.detect_tipping_point(t) for t in TRACKED_CULTURAL_TOPICS.keys()]
        df   = pd.DataFrame(rows).sort_values("tipping_score", ascending=False).reset_index(drop=True)
        df.to_csv(RAW_DIR / "cultural_moment_signals.csv", index=False)
        return df

    def run(self) -> dict:
        print("\n" + "=" * 50)
        print("◈ CONFLUX | Social Signal Collection")
        print("=" * 50)
        team_trends   = self.fetch_team_trends()
        cultural_data = self.build_cultural_moment_signals()
        return {"teams": team_trends, "cultural": cultural_data}


if __name__ == "__main__":
    engine = SocialSignalEngine()
    results = engine.run()

    print("\nTeam social signals (top 10):")
    print(results["teams"].head(10)[["team", "trend_raw", "social_signal"]].to_string(index=False))

    print("\nCultural moment signals:")
    print(results["cultural"][["topic", "tipping_score", "is_tipping"]].to_string(index=False))