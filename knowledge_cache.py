# -*- coding: utf-8 -*-
"""Sistema de cache inteligente de conhecimento com web scraping responsável."""

import hashlib
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("knowledge_cache")
logger.setLevel(logging.DEBUG)

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
DB_PATH = CACHE_DIR / "knowledge.db"


class KnowledgeCache:
    """Cache inteligente com web scraping responsável e versionamento."""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for caching."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                timestamp REAL NOT NULL,
                ttl_hours INTEGER DEFAULT 24,
                hits INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                confidence REAL DEFAULT 0.8,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def get(self, key: str, force_refresh: bool = False) -> Optional[dict]:
        """Get cached value or return None if expired."""
        if force_refresh:
            self.delete(key)
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM cache WHERE key = ?", (key,))
        row = c.fetchone()

        if not row:
            conn.close()
            return None

        created = datetime.fromisoformat(row["created_at"])
        ttl = timedelta(hours=row["ttl_hours"])

        if datetime.now() - created > ttl:
            c.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()
            return None

        # Update hit count
        c.execute("UPDATE cache SET hits = hits + 1 WHERE key = ?", (key,))
        conn.commit()
        conn.close()

        logger.info(f"Cache hit for '{key}' (hits: {row['hits'] + 1})")
        return {
            "content": json.loads(row["content"]),
            "source": row["source"],
            "timestamp": row["timestamp"],
        }

    def set(self, key: str, content: Any, source: str = "local", ttl_hours: int = 24):
        """Store value in cache."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        content_json = json.dumps(content, ensure_ascii=False)
        timestamp = time.time()

        try:
            c.execute(
                """
                INSERT OR REPLACE INTO cache (key, content, source, timestamp, ttl_hours)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, content_json, source, timestamp, ttl_hours),
            )
            conn.commit()
            logger.info(f"Cached '{key}' from {source} (TTL: {ttl_hours}h)")
        finally:
            conn.close()

    def delete(self, key: str):
        """Delete cached value."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        logger.info(f"Deleted cache for '{key}'")

    def scrape_safely(
        self,
        url: str,
        selector: str = "body",
        cache_ttl: int = 24,
        timeout: int = 10,
    ) -> Optional[dict]:
        """Scrape web content responsibly with caching."""
        cache_key = f"web:{hashlib.md5(url.encode()).hexdigest()}"

        # Check cache first
        cached = self.get(cache_key)
        if cached:
            return cached

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (IA Futurista Knowledge Crawler)"
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            element = soup.select_one(selector)

            if not element:
                logger.warning(f"Selector '{selector}' not found in {url}")
                return None

            content = element.get_text(strip=True)[:5000]  # Limit to 5K chars

            result = {"url": url, "content": content, "timestamp": datetime.now().isoformat()}

            self.set(cache_key, result, source=url, ttl_hours=cache_ttl)
            logger.info(f"Scraped {url} ({len(content)} chars)")
            return result

        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            return None

    def search_knowledge(self, query: str, limit: int = 5) -> list:
        """Search cached knowledge base."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            """
            SELECT * FROM knowledge_base 
            WHERE topic LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (f"%{query}%", f"%{query}%", limit),
        )

        results = [dict(row) for row in c.fetchall()]
        conn.close()
        logger.info(f"Found {len(results)} knowledge entries for '{query}'")
        return results

    def add_knowledge(self, topic: str, content: str, sources: list = None):
        """Add structured knowledge to base."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        sources_json = json.dumps(sources or [])

        c.execute(
            """
            INSERT INTO knowledge_base (topic, content, sources)
            VALUES (?, ?, ?)
            """,
            (topic, content, sources_json),
        )
        conn.commit()
        conn.close()
        logger.info(f"Added knowledge: {topic}")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM cache")
        cache_count = c.fetchone()[0]

        c.execute("SELECT SUM(hits) FROM cache")
        total_hits = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = c.fetchone()[0]

        conn.close()

        return {
            "cache_entries": cache_count,
            "total_hits": total_hits,
            "knowledge_base_entries": kb_count,
            "cache_size_mb": os.path.getsize(self.db_path) / (1024 * 1024),
        }


# Singleton instance
cache = KnowledgeCache()
