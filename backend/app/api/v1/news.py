"""
QuantVision - News Endpoints (RSS Feeds)
"""
from fastapi import APIRouter, Query
from typing import List, Optional
import feedparser
import httpx
from datetime import datetime

router = APIRouter(prefix="/news", tags=["news"])

RSS_FEEDS = {
    "yahoo": "https://finance.yahoo.com/news/rssindex",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
}

FEED_NAME = {
    "yahoo": "Yahoo Finance",
    "marketwatch": "MarketWatch",
}


@router.get("")
async def get_news(limit: int = Query(default=20, ge=1, le=100)):
    """Obtiene las últimas noticias financieras de los RSS feeds."""
    all_items = []

    for name, url in RSS_FEEDS.items():
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.text)
                    for entry in feed.entries[:limit]:
                        all_items.append({
                            "title": entry.get("title", ""),
                            "description": entry.get("summary", "")[:300],
                            "url": entry.get("link", ""),
                            "source": FEED_NAME.get(name, name),
                            "published": entry.get("published", ""),
                        })
        except Exception:
            pass

    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return {"news": all_items[:limit], "total": len(all_items)}


@router.get("/{symbol}")
async def get_news_for_symbol(symbol: str, limit: int = Query(default=10, ge=1, le=50)):
    """Obtiene noticias filtradas por símbolo (búsqueda básica)."""
    # Note: Real implementation would filter by symbol using a news API
    # For now, return general news (RSS feeds don't support symbol filtering)
    return await get_news(limit=limit)