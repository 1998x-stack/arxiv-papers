"""Fetch recent arXiv papers."""
from __future__ import annotations

import feedparser

from .config import Config
from .models import Article

BASE_URL = "http://export.arxiv.org/api/query?"


def build_url(cfg: Config) -> str:
    return (
        f"{BASE_URL}search_query={cfg.query}"
        f"&sortBy=lastUpdatedDate&max_results={cfg.max_results}"
    )


def parse_entries(entries) -> list[Article]:
    papers = []
    for entry in entries:
        papers.append(
            Article(
                id=entry.id,
                title=entry.title,
                summary=entry.summary,
                authors=[a.name for a in entry.authors],
                published=entry.published,
                link=entry.link,
            )
        )
    return papers


def fetch(cfg: Config) -> list[Article]:
    feed = feedparser.parse(build_url(cfg))
    return parse_entries(feed.entries)