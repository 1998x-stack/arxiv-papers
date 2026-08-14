"""Core data model for a single arXiv paper."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Article:
    id: str
    title: str
    summary: str
    authors: list[str]
    published: str
    link: str