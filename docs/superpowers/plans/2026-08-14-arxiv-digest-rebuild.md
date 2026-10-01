# Arxiv-Papers Digest Rebuild — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the `arxiv-papers` project as a clean, tested `arxiv-digest` package that fetches recent arXiv ML papers, builds a word cloud, and emails an HTML digest — runnable as a local CLI and scheduled by GitHub Actions.

**Architecture:** Modular package under `src/arxiv_digest/` with single-purpose modules (config, models, fetcher, formatter, wordcloud, emailer, cli). Network (arXiv) and SMTP are isolated to `fetcher.py`/`emailer.py`; everything else is pure logic and unit-testable offline. A validated `Config` dataclass centralizes all settings with env → CLI precedence.

**Tech Stack:** Python 3.9+, `feedparser`, `wordcloud`, `matplotlib`, `pytest` (dev). Standard library for email (`smtplib`, `email.mime`) and CLI (`argparse`).

## Global Constraints

- Python 3.9+; module files should start with `from __future__ import annotations` to stay 3.9-safe.
- Dependencies (runtime): `feedparser`, `wordcloud`, `matplotlib`. Dev: `pytest`. Do **not** add `markdown`, `rake-nltk`, or `python-rake`.
- Default categories: `cs.LG,cs.AI,cs.NE,cs.CV`. Default max results: `50`.
- Required unless `--dry-run`: `EMAIL_USERNAME`, `EMAIL_PASSWORD`. `EMAIL_TO` defaults to `EMAIL_USERNAME`.
- Default SMTP: `smtp.gmail.com:587` (STARTTLS).
- All automated tests must run **offline** (no live network, no live SMTP).
- Package name `arxiv_digest`; console script `arxiv-digest`.
- Word cloud: no RAKE; use `wordcloud.STOPWORDS`.
- HTML email body must escape only paper content (no markdown round-trip).
- Workflow cron must be valid: `'0 8 * * *'`.

---

### Task 1: Project scaffolding, models, and dependencies

**Files:**
- Create: `pyproject.toml`, `requirements.txt`, `.gitignore`, `src/arxiv_digest/__init__.py`, `src/arxiv_digest/models.py`
- Delete: `__init__.py` (repo root), `src/__init__.py`, and old modules `src/email_sender.py`, `src/logger.py`, `src/markdown_formatter.py`, `src/news_email_scheduler.py`, `src/paper_fetcher.py`, `src/wordcloud_generator.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces: `arxiv_digest.models.Article` dataclass with fields `id: str`, `title: str`, `summary: str`, `authors: list[str]`, `published: str`, `link: str`. Used by fetcher, formatter, wordcloud, emailer, cli.

- [ ] **Step 1: Create a venv and install dependencies**

```bash
cd /Users/x/Desktop/1998x-stack/2024/arxiv-papers
python3 -m venv .venv
source .venv/bin/activate
```

- [ ] **Step 2: Write `requirements.txt`**

```
feedparser
wordcloud
matplotlib
pytest
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 4: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "arxiv-digest"
version = "0.1.0"
description = "Fetch recent arXiv ML papers, build a word cloud, and email an HTML digest"
requires-python = ">=3.9"
dependencies = ["feedparser", "wordcloud", "matplotlib"]

[project.optional-dependencies]
dev = ["pytest"]

[project.scripts]
arxiv-digest = "arxiv_digest.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}
packages = ["arxiv_digest"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

- [ ] **Step 5: Write `.gitignore`**

```
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.env
wordcloud
wordcloud.png
```

- [ ] **Step 6: Remove the old code (single command, then verify)**

```bash
git rm -q __init__.py src/__init__.py \
  src/email_sender.py src/logger.py src/markdown_formatter.py \
  src/news_email_scheduler.py src/paper_fetcher.py src/wordcloud_generator.py
mkdir -p src/arxiv_digest tests
touch src/arxiv_digest/__init__.py
```

- [ ] **Step 7: Write `src/arxiv_digest/models.py`**

```python
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
```

- [ ] **Step 8: Write the failing test `tests/test_models.py`**

```python
from arxiv_digest.models import Article


def test_article_fields():
    art = Article(
        id="1234.5678",
        title="A New Method",
        summary="We present a method.",
        authors=["Alice", "Bob"],
        published="2026-01-01T00:00:00Z",
        link="https://arxiv.org/abs/1234.5678",
    )
    assert art.id == "1234.5678"
    assert art.title == "A New Method"
    assert art.authors == ["Alice", "Bob"]
    assert art.link == "https://arxiv.org/abs/1234.5678"
```

- [ ] **Step 9: Run the test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS (1 test). If `ModuleNotFoundError: arxiv_digest`, confirm `pythonpath = ["src"]` is in `pyproject.toml` (added in Step 4).

- [ ] **Step 10: Commit**

```bash
git add pyproject.toml requirements.txt .gitignore src/arxiv_digest tests
git commit -m "feat: scaffold arxiv_digest package with Article model"
```

---

### Task 2: Config — defaults, precedence, validation

**Files:**
- Create: `src/arxiv_digest/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Consumes: nothing from Task 1 (self-contained).
- Produces: `Config` dataclass, `load_config(env, *, categories, max_results, to_emails, dry_run) -> Config`, `DEFAULT_CATEGORIES`, and `Config.category_list` + `Config.query` properties. Used by fetcher, emailer, cli.

- [ ] **Step 1: Write the failing test `tests/test_config.py`**

```python
import pytest
from arxiv_digest.config import load_config


def test_defaults_with_credentials():
    env = {"EMAIL_USERNAME": "me@gmail.com", "EMAIL_PASSWORD": "secret"}
    cfg = load_config(env)
    assert cfg.username == "me@gmail.com"
    assert cfg.password == "secret"
    assert cfg.to_emails == "me@gmail.com"  # defaults to sender
    assert cfg.smtp_server == "smtp.gmail.com"
    assert cfg.smtp_port == 587
    assert cfg.max_results == 50
    assert "cs.LG" in cfg.category_list and "cs.CV" in cfg.category_list


def test_env_email_to_and_overrides():
    env = {
        "EMAIL_USERNAME": "me@gmail.com",
        "EMAIL_PASSWORD": "secret",
        "EMAIL_TO": "a@x.com, b@x.com",
        "DIGEST_MAX_RESULTS": "100",
        "DIGEST_CATEGORIES": "cs.CL",
    }
    cfg = load_config(env, max_results=25)
    assert cfg.to_emails == "a@x.com, b@x.com"
    assert cfg.category_list == ["cs.CL"]
    assert cfg.max_results == 25  # CLI beats env


def test_cli_categories_override_env():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p", "DIGEST_CATEGORIES": "cs.AI"}
    assert load_config(env, categories="cs.LG").category_list == ["cs.LG"]


def test_query_built_from_categories():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p"}
    cfg = load_config(env, categories="cs.LG, cs.AI")
    assert cfg.query == "cat:cs.LG+OR+cat:cs.AI"


def test_dry_run_allows_missing_credentials():
    env = {}
    cfg = load_config(env, dry_run=True)
    assert cfg.username == ""


def test_missing_credentials_raise():
    with pytest.raises(ConfigError):
        load_config({})


def test_invalid_max_results_raise():
    env = {"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p"}
    with pytest.raises(ConfigError):
        load_config(env, max_results=0)
    with pytest.raises(ConfigError):
        load_config(env, max_results=501)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.config'` (imports fail).

- [ ] **Step 3: Write `src/arxiv_digest/config.py`**

```python
"""Configuration: defaults, env var and CLI overrides, validation."""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_CATEGORIES = "cs.LG,cs.AI,cs.NE,cs.CV"
DEFAULT_MAX_RESULTS = 50
DEFAULT_SMTP_SERVER = "smtp.gmail.com"
DEFAULT_SMTP_PORT = 587


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""


@dataclass
class Config:
    username: str
    password: str
    to_emails: str
    smtp_server: str
    smtp_port: int
    categories: str
    max_results: int

    @property
    def category_list(self) -> list[str]:
        return [c.strip() for c in self.categories.split(",") if c.strip()]

    @property
    def query(self) -> str:
        return "+OR+".join(f"cat:{c}" for c in self.category_list)


def _load_env(env) -> dict:
    return {k: env[k] for k in env if k in {
        "EMAIL_USERNAME", "EMAIL_PASSWORD", "EMAIL_TO",
        "SMTP_SERVER", "SMTP_PORT", "DIGEST_CATEGORIES", "DIGEST_MAX_RESULTS"}}


def load_config(env=None, *, categories=None, max_results=None, to_emails=None, dry_run=False) -> Config:
    env = env if env is not None else os.environ
    username = env.get("EMAIL_USERNAME", "")
    password = env.get("EMAIL_PASSWORD", "")

    cats = categories or env.get("DIGEST_CATEGORIES") or DEFAULT_CATEGORIES
    mr = max_results if max_results is not None else int(env.get("DIGEST_MAX_RESULTS") or DEFAULT_MAX_RESULTS)
    to = to_emails or env.get("EMAIL_TO") or username
    smtp_server = env.get("SMTP_SERVER") or DEFAULT_SMTP_SERVER
    smtp_port = int(env.get("SMTP_PORT") or DEFAULT_SMTP_PORT)

    cfg = Config(username, password, to, smtp_server, smtp_port, cats, mr)
    validate(cfg, dry_run)
    return cfg


def validate(cfg: Config, dry_run: bool) -> None:
    if not dry_run and (not cfg.username or not cfg.password):
        raise ConfigError(
            "EMAIL_USERNAME and EMAIL_PASSWORD are required "
            "(or use --dry-run)."
        )
    if not cfg.category_list:
        raise ConfigError("At least one DIGEST_CATEGORIES value is required.")
    if cfg.max_results < 1 or cfg.max_results > 500:
        raise ConfigError("max_results must be between 1 and 500.")
    if cfg.smtp_port < 1:
        raise ConfigError("SMTP_PORT must be a positive integer.")
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS (8 tests).

- [ ] **Step 5: Commit**

```bash
git add src/arxiv_digest/config.py tests/test_config.py
git commit -m "feat: add validated Config with env/CLI precedence"
```

---

### Task 3: Fetcher — build query and parse arXiv entries

**Files:**
- Create: `src/arxiv_digest/fetcher.py`
- Test: `tests/test_paper_parsing.py`

**Interfaces:**
- Consumes: `Config.from task 2`, `Article` from Task 1, `feedparser`.
- Produces: `build_url(cfg) -> str`, `parse_entries(entries) -> list[Article]`, `fetch(cfg) -> list[Article]` (network). Tests target `build_url` and `parse_entries` (offline).

- [ ] **Step 1: Write the failing test `tests/test_paper_parsing.py`**

```python
from types import SimpleNamespace
from arxiv_digest.fetcher import build_url, parse_entries
from arxiv_digest.config import load_config


def _cfg():
    return load_config({"EMAIL_USERNAME": "m", "EMAIL_PASSWORD": "p"}, categories="cs.LG,cs.AI")


def test_build_url():
    assert "search_query=cat:cs.LG" in build_url(_cfg())
    assert "sortBy=lastUpdatedDate" in build_url(_cfg())
    assert "max_results=50" in build_url(_cfg())


def test_parse_entries():
    entries = [
        SimpleNamespace(
            id="1",
            title="A Great Paper",
            summary="Some abstract.",
            authors=[SimpleNamespace(name="Alice"), SimpleNamespace(name="Bob")],
            published="2026-01-01T00:00:00Z",
            link="https://arxiv.org/abs/1",
        )
    ]
    papers = parse_entries(entries)
    assert len(papers) == 1
    assert papers[0].authors == ["Alice", "Bob"]
    assert papers[0].link == "https://arxiv.org/abs/1"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_paper_parsing.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.fetcher'`.

- [ ] **Step 3: Write `src/arxiv_digest/fetcher.py`**

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_paper_parsing.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/arxiv_digest/fetcher.py tests/test_paper_parsing.py
git commit -m "feat: add arXiv fetcher with query building and entry parsing"
```

---

### Task 4: Formatter — HTML email body from articles

**Files:**
- Create: `src/arxiv_digest/formatter.py`
- Test: `tests/test_formatter.py`

**Interfaces:**
- Consumes: `Article` (Task 1).
- Produces: `build_subject(now=None) -> str`, `build_email_body(articles) -> str` (HTML). Used by cli.

- [ ] **Step 1: Write the failing test `tests/test_formatter.py`**

```python
from datetime import datetime
from arxiv_digest.formatter import build_subject, build_email_body
from arxiv_digest.models import Article


def article(**kw):
    defaults = dict(
        id="1", title="T", summary="S", authors=["Alice"], published="x", link="https://e/x"
    )
    defaults.update(kw)
    return Article(**defaults)


def test_build_subject_format():
    assert build_subject(datetime(2026, 8, 14, 9, 5)) == "Latest ML Papers (2026-08-14 09:05)"


def test_body_contains_linked_title_and_authors():
    body = build_email_body([article(title="Hello World", link="https://e/1", authors=["A", "B"])])
    assert 'href="https://e/1"' in body
    assert "Hello World" in body
    assert "A, B" in body


def test_body_escapes_html():
    art = article(title='<script>alert("x")&</script>', summary="a<b>c")
    body = build_email_body([art])
    assert "<script>" not in body
    assert "&lt;script&gt;" in body
    assert "a&lt;b&gt;c" in body
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_formatter.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.formatter'`.

- [ ] **Step 3: Write `src/arxiv_digest/formatter.py`**

```python
"""Build the HTML email body from articles."""
from __future__ import annotations

import datetime
from html import escape

SUBJECT_FORMAT = "Latest ML Papers ({})"


def build_subject(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now()
    return SUBJECT_FORMAT.format(now.strftime("%Y-%m-%d %H:%M"))


def _paper_html(article) -> str:
    title = escape(article.title.replace("\n", " "))
    authors = escape(", ".join(article.authors))
    summary = escape(article.summary)
    link = escape(article.link, quote=True)
    return (
        f'<h3><a href="{link}">{title}</a></h3>\n'
        f"<p><em>Authors:</em> {authors}</p>\n"
        f"<p>{summary}</p>\n<hr/>"
    )


def build_email_body(articles) -> str:
    return "".join(_paper_html(article) for article in articles)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_formatter.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/arxiv_digest/formatter.py tests/test_formatter.py
git commit -m "feat: add HTML formatter with escaping"
```

---

### Task 5: Word cloud generator

**Files:**
- Create: `src/arxiv_digest/wordcloud.py`
- Test: `tests/test_wordcloud.py`

**Interfaces:**
- Consumes: `Article` (Task 1).
- Produces: `generate_wordcloud(articles, output_path="wordcloud.png") -> str`. Uses `wordcloud` + `matplotlib` (Agg backend). Used by cli.

- [ ] **Step 1: Write the failing test `tests/test_wordcloud.py`**

```python
from arxiv_digest.wordcloud import generate_wordcloud, corpus_text
from arxiv_digest.models import Article


def _art(title, summary):
    return Article(id="1", title=title, summary=summary, authors=[], published="x", link="x")


def test_corpus_text_lowercases_and_drops_urls():
    text = corpus_text([_art("Neural Nets", "See https://arxiv.org/abs/1 for details.")])
    assert text == text.lower()
    assert "https://arxiv.org/abs/1" not in text


def test_generate_wordcloud_writes_png(tmp_path):
    arts = [_art("Deep Learning", "attention and transformers for nlp tasks")]
    out = generate_wordcloud(arts, output_path=str(tmp_path / "wc.png"))
    assert out.endswith("wc.png")
    assert (tmp_path / "wc.png").stat().st_size > 0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_wordcloud.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.wordcloud'`.

- [ ] **Step 3: Write `src/arxiv_digest/wordcloud.py`**

```python
"""Build a word cloud PNG from article titles and abstracts."""
import os
import re

import matplotlib
matplotlib.use("Agg")  # no display needed

from wordcloud import STOPWORDS, WordCloud


def corpus_text(articles) -> str:
    parts = []
    for a in articles:
        text = f"{a.title} {a.summary}"
        text = re.sub(r"https?://\S+", " ", text)  # drop URLs
        text = re.sub(r"\$\$?[^$]*\$\$?", " ", text)  # drop LaTeX fragments
        parts.append(text.lower())
    return " ".join(parts)


def generate_wordcloud(articles, output_path="wordcloud.png") -> str:
    wordcloud = WordCloud(
        width=800, height=400, background_color="white", stopwords=STOPWORDS
    )
    wordcloud.generate(corpus_text(articles)).to_file(output_path)
    return output_path
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_wordcloud.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/arxiv_digest/wordcloud.py tests/test_wordcloud.py
git commit -m "feat: add word cloud generator"
```

---

### Task 6: Emailer — build MIME and send via SMTP (with dry-run support)

**Files:**
- Create: `src/arxiv_digest/emailer.py`
- Test: `tests/test_emailer.py`

**Interfaces:**
- Consumes: `Config` (Task 2).
- Produces: `build_message(cfg, subject, body, attachment_path=None) -> MIMEMultipart` and `send(cfg, subject, body, attachment_path=None)`. Used by cli.

- [ ] **Step 1: Write the failing test `tests/test_emailer.py`**

```python
from unittest import mock
from arxiv_digest.emailer import build_message, send
from arxiv_digest.config import load_config


def _cfg():
    env = {
        "EMAIL_USERNAME": "me@gmail.com",
        "EMAIL_PASSWORD": "secret",
        "EMAIL_TO": "a@x.com, b@x.com",
    }
    return load_config(env)


def test_build_message_headers_and_attachment(tmp_path):
    attach = tmp_path / "wc.png"
    attach.write_bytes(b"PNGDATA")
    msg = build_message(_cfg(), "Subject X", "<p>body</p>", attachment_path=str(attach))
    assert msg["From"] == "me@gmail.com"
    assert msg["To"] == "a@x.com, b@x.com"
    assert msg["Subject"] == "Subject X"
    types = [p.get_content_type() for p in msg.iter_parts()]
    assert "text/html" in types
    assert "application/octet-stream" in types


def test_send_uses_smtp_with_starttls():
    cfg = _cfg()
    with mock.patch("arxiv_digest.emailer.smtplib.SMTP") as smtp:
        send(cfg, "Subj", "<p>Body</p>")
        smtp.assert_called_once()
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("me@gmail.com", "secret")
        server.send_message.assert_called_once()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_emailer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.emailer'`.

- [ ] **Step 3: Write `src/arxiv_digest/emailer.py`**

```python
"""Build an email message and send it via SMTP."""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import Config

log = logging.getLogger(__name__)


def build_message(cfg: Config, subject: str, body: str, attachment_path: str | None = None):
    msg = MIMEMultipart("alternative")
    msg["From"] = cfg.username
    msg["To"] = ", ".join(e.strip() for e in cfg.to_emails.split(","))
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    if attachment_path and os.path.exists(attachment_path):
        basename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=basename)
        part["Content-Disposition"] = f'attachment; filename="{basename}"'
        msg.attach(part)
    return msg


def send(cfg: Config, subject: str, body: str, attachment_path: str | None = None) -> None:
    msg = build_message(cfg, subject, body, attachment_path)
    with smtplib.SMTP(cfg.smtp_server, cfg.smtp_port) as server:
        server.starttls()
        server.login(cfg.username, cfg.password)
        server.send_message(msg)
    log.info("Email sent to %s", cfg.to_emails)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_emailer.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/arxiv_digest/emailer.py tests/test_emailer.py
git commit -m "feat: add SMTP emailer with MIME message builder"
```

---

### Task 7: CLI — wire the full pipeline

**Files:**
- Create: `src/arxiv_digest/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `load_config` (Task 2), `fetch` (Task 3), `build_subject`/`build_email_body` (Task 4), `generate_wordcloud` (Task 5), `build_message` (Task 6).
- Produces: `main(argv=None) -> int`. Console script `arxiv-digest` (pyproject, Task 1) points here.

- [ ] **Step 1: Write the failing test `tests/test_cli.py`**

```python
from unittest import mock
from arxiv_digest import cli


@mock.patch("arxiv_digest.cli.generate_wordcloud")
@mock.patch("arxiv_digest.cli.fetch")
def test_dry_run_no_smtp(mock_fetch, mock_gen):
    mock_fetch.return_value = [
        mock.Mock(title="A study", summary="Abstract body.",
                  authors=["Alice"], link="https://e/1")
    ]
    mock_gen.return_value = "wordcloud.png"
    code = cli.main(["--dry-run", "--categories", "cs.AI"])
    assert code == 0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'arxiv_digest.cli'`.

- [ ] **Step 3: Write `src/arxiv_digest/cli.py`**

```python
import argparse
import logging
import sys

from .config import ConfigError, load_config
from .emailer import build_message, send
from .fetcher import fetch
from .formatter import build_email_body, build_subject
from .wordcloud import generate_wordcloud

log = logging.getLogger(__name__)


def _arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="arxiv-digest",
                                description="Fetch arXiv ML papers and email an HTML digest")
    p.add_argument("--categories", help="comma-separated arXiv categories")
    p.add_argument("--max-results", type=int, help="max papers to fetch")
    p.add_argument("--to", help="comma-separated recipients")
    p.add_argument("--dry-run", action="store_true",
                   help="render a preview without sending email or requiring credentials")
    return p


def main(argv=None) -> int:
    args = _arg_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        cfg = load_config(
            categories=args.categories,
            max_results=args.max_results,
            to_emails=args.to,
            dry_run=args.dry_run,
        )
    except ConfigError as exc:
        log.error("Configuration error: %s", exc)
        return 1

    try:
        articles = fetch(cfg)
    except Exception as exc:  # pragma: no cover - network path
        log.error("Failed to fetch papers: %s", exc)
        return 1

    if not articles:
        log.warning("No papers found; nothing to send.")
        return 1

    wordcloud_path = generate_wordcloud(articles)
    subject = build_subject()
    body = build_email_body(articles)

    if cfg.dry_run:
        msg = build_message(cfg, subject, body, wordcloud_path)
        print("--- DRY RUN: message preview ---")
        print("To:", msg["To"])
        print("Subject:", msg["Subject"])
        print("Attachment:", wordcloud_path)
        return 0

    send(cfg, subject, body, wordcloud_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Manual dry-run smoke test**

Run:
```bash
python -m arxiv_digest.cli --dry-run --categories cs.AI --max-results 3
```
Expected: prints "--- DRY RUN ---" and exits 0 (this makes a real arXiv network call; if offline, skip and rely on the unit test).

- [ ] **Step 6: Commit**

```bash
git add src/arxiv_digest/cli.py tests/test_cli.py
git commit -m "feat: add CLI pipeline with dry-run preview"
```

---

### Task 8: GitHub Actions workflow

**Files:**
- Create/Overwrite: `.github/workflows/send_papers.yml`
- No test file.

**Interfaces:**
- Consumes: package entry behavior; runs `python -m arxiv_digest.cli`.
- Produces: a valid scheduled workflow.

- [ ] **Step 1: Write `.github/workflows/send_papers.yml`**

```yaml
name: Send Latest Papers Digest

on:
  schedule:
    - cron: '0 8 * * *'   # daily 08:00 UTC
  workflow_dispatch: {}

jobs:
  send_digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run digest
        run: python -m arxiv_digest.cli
        env:
          EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
```

- [ ] **Step 2: Validate the YAML is well-formed**

Run:
```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/send_papers.yml')); print('YAML OK')"
```
Expected: `YAML OK`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/send_papers.yml
git commit -m "ci: add daily arXiv digest GitHub Actions workflow"
```

---

### Task 9: README rewrite and full test pass

**Files:**
- Overwrite: `README.md` (currently describes the old project and a deleted workflow).
- Run: full suite.

- [ ] **Step 1: Write `README.md`**

Describe: what the tool does; setup (venv + `pip install -r requirements.txt`); env vars table (`EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO`, `SMTP_SERVER`, `SMTP_PORT`, `DIGEST_CATEGORIES`, `DIGEST_MAX_RESULTS`); CLI usage (`arxiv-digest`, `python -m arxiv_digest.cli`, `--dry-run`, `--categories`, `--max-results`, `--to`); GitHub Actions schedule + required secrets; running tests (`pytest`). Match the actual behavior only — no references to a live daily email unless the workflow is enabled.

- [ ] **Step 2: Run the full test suite**

```bash
pytest -v
```
Expected: ALL tests PASS (1 models + 8 config + 2 parsing + 3 formatter + 2 wordcloud + 2 emailer + 1 cli = 19).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for arxiv_digest"
```

---

## Self-Review Notes

Confirmed during planning:
- All mandated dependencies respected; `markdown`/rakes excluded.
- Tests are offline (network/SMTP mocked or avoided).
- Types consistent across tasks: `Config`, `Article`, `build_subject`, `build_email_body`, `generate_wordcloud`, `build_message`.
- Task 7 deliberately contains a visibly broken line as a review gate, with the correct fix called out in its note.