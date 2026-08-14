# Arxiv-Papers Digest — Rebuild Design

Date: 2026-08-14
Status: Approved (user approved design section-by-section via brainstorming skill)

## Overview

Clean rebuild of the existing `arxiv-papers` project. Preserves the core function —
fetch recent arXiv ML papers → generate a word cloud → email a formatted digest —
but rewrites it with a clean, single-purpose modular architecture, fixes every known
issue in the original, and delivers both a local CLI and a correctly-written
GitHub Actions scheduler.

Decisions locked during brainstorming:
- **Goal:** Option A — same core function, clean rebuild + fix bugs.
- **Delivery:** Option C — CLI **and** GitHub Actions (both).
- **Config:** Option A — fully config-driven recipients (`EMAIL_TO`), validated config.
- **Word cloud:** Option B — no RAKE; use `wordcloud`'s built-in stopwords (drop
  `python-rake`/`rake-nltk` dependency churn).
- **Fetcher:** Option B — categories and max results configurable, original defaults.
- **Tests:** Option B — pytest unit coverage (mocked arXiv/SMTP) + `--dry-run` smoke test.
- **Structure:** Approach 1 — clean modular package with CLI entry point.

## Goals / Non-Goals

**Goals**
- Preserve the original behavior: fetch → word cloud → email digest.
- Clean, testable, single-purpose modules with clear boundaries.
- Fix every issue found in the original code (listed below).
- Re-enable GitHub Actions scheduling with a *valid* cron.
- Rewrite README to match actual behavior.

**Non-Goals (YAGNI)**
- GUI.
- Multi-account fan-out / multiple recipients groups beyond a comma list.
- Persistence or a database.
- A self-scheduling daemon process (GitHub Actions handles scheduling).
- Any live network / SMTP requirement during default test runs.

## Issues in the Original Code Addressed

1. `to_emails = [self.email_sender.username]` — digest sent to itself → replaced by
   configurable `EMAIL_TO`, defaulting to sender.
2. Unused `import matplotlib.pyplot as plt` and unused `matplotlib` in the word cloud path.
3. RAKE dependency churn (`rake-nltk` → `python-rake`) with an import/package mismatch
   risk — removed entirely.
4. Hardcoded SMTP server/port — now configurable (`SMTP_SERVER`, `SMTP_PORT`, default gmail/587).
5. Bare `KeyError` on missing `EMAIL_*` env vars — now validated with clear messages.
6. Unescaped paper title/summary inserted into HTML (`markdown_formatter.py`) — injection
   risk; now HTML-escaped.
7. Invalid/retired scheduler: cron `*/3600` invalid, then whole workflow deleted. Restored
   with valid cron `'0 8 * * *'` and provider-versioned actions.
8. README drift — fully rewritten.
9. `actions/setup-python@v2` with Py3.8 — bumped to `@v5` / 3.11.

## Architecture

## Diagrams

### End-to-end data flow

```
CLI (arguments / env)
      │
      ▼
config.py ──validates──► Config dataclass
                              │
                              ▼
fetcher.fetch(cfg) ──► arXiv API ──► list[Article]      ← network (feedparser)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      wordcloud.generate(articles)     formatter.build_email(articles)
        → wordcloud.png  (attach)          │
                │                         ▼
                └────────►  HTML body (MIME)
                              │
                              ▼
              emailer.send(msg)  OR  dry-run preview (no SMTP)
```

### Project structure

```
arxiv-papers/
├── .github/workflows/send_papers.yml
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
├── src/arxiv_digest/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py         # Article dataclass
│   ├── fetcher.py        # arXiv fetch (network layer)
│   ├── formatter.py      # HTML email body (pure logic)
│   ├── wordcloud.py      # PNG generation (pure logic)
│   ├── emailer.py        # MIME + SMTP send
│   └── cli.py            # argparse entry point
└── tests/
    ├── test_config.py
    ├── test_paper_parsing.py
    ├── test_formatter.py
    ├── test_wordcloud.py
    └── test_emailer.py
```

## Modules & Responsibilities

| Module | Responsibility | Depends on | Touches outside world? |
|--------|----------------|-----------|------------------------|
| `config.py` | Config dataclass; env + CLI overrides; validation | — | env vars |
| `models.py` | `Article` dataclass | — | no |
| `fetcher.py` | Fetch arXiv feed → `list[Article]` | config, models, feedparser | yes (network) |
| `formatter.py` | Build HTML email body from articles | models | no |
| `wordcloud.py` | Build word-cloud PNG from articles | wordcloud lib | no (writes file) |
| `emailer.py` | Build MIME message; send via SMTP; dry-run | config | yes (SMTP) |
| `cli.py` | Parse args, validate config, drive pipeline | all | orchestrates |

### `Article` dataclass (models.py)

Fields: `id`, `title`, `summary`, `authors: list[str]`, `published`, `link`.
Replaces the ad-hoc dicts of the original.

## Configuration

**Resolution order (low → high precedence):** defaults → env vars → CLI flags.

**Environment variables:**
- `EMAIL_USERNAME` (required unless `--dry-run`)
- `EMAIL_PASSWORD` (required unless `--dry-run`)
- `EMAIL_TO` (comma-separated recipients; defaults to `EMAIL_USERNAME`)
- `SMTP_SERVER` (default `smtp.gmail.com`), `SMTP_PORT` (default `587`)
- `DIGEST_CATEGORIES` (comma-separated; default `cs.LG,cs.AI,cs.NE,cs.CV`)
- `DIGEST_MAX_RESULTS` (default `50`)

**CLI flags:** `--categories`, `--max-results`, `--to`, `--dry-run`.

**Validation rules:**
- `EMAIL_USERNAME`/`EMAIL_PASSWORD` required unless `--dry-run`.
- `EMAIL_TO` defaults to sender username when unset.
- ≥1 category required; joinable into an arXiv query string.
- `max-results` positive int, ≤ 500 (arXiv cap).

## Word Cloud (no RAKE)

- Combine titles + abstracts.
- Preprocess: lowercase, strip URLs/LaTeX/unwanted tokens, drop stopwords via
  `wordcloud.STOPWORDS`.
- Generate 800×400 white-background PNG; return output path.

## Email Body

- Subject: `Latest ML Papers (YYYY-MM-DD HH:MM)` with generated timestamp.
- Body: one `h3` linked title + authors + summary per article, HTML-escaped.
- Word-cloud PNG attached.

## Error Handling

- Config errors → fail fast at startup, human-readable message, non-zero exit.
- Fetch errors (network/arXiv) → log clean warning; exit non-zero; no empty digest sent.
- Email send errors → logged; non-zero exit.
- `--dry-run` → never opens SMTP; writes rendered body + attachment path to
  stdout/stderr; returns success. Safe to run without credentials.

## Testing (pytest)

- `test_config.py` — defaults, precedence, validation failures.
- `test_paper_parsing.py` — parse a fixture feed into `Article`; verify fields/authors. No network.
- `test_formatter.py` — HTML structure, authors rendered, special chars escaped (fixes injection).
- `test_wordcloud.py` — output PNG created and non-empty (uses `tmp_path`).
- `test_emailer.py` — MIME built correctly (recipients/attachment); SMTP send mocked;
  dry-run never touches SMTP.
- `--dry-run` invocation doubles as a local end-to-end smoke test.
- All default tests run offline (no network, no live SMTP).

## GitHub Actions Workflow

```yaml
name: Send Latest Papers Digest
on:
  schedule:
    - cron: '0 8 * * *'        # valid: daily 08:00 UTC
  workflow_dispatch: {}
jobs:
  send_digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: python -m src.arxiv_digest.cli
        env:
          EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
```

Secrets: `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO` (optional).

## Build Tooling & Hygiene

- `pyproject.toml` with `[project.scripts] arxiv-digest = "src.arxiv_digest.cli:main"`.
- `requirements.txt` trimmed to: `feedparser`, `wordcloud`, `matplotlib`, `markdown`,
  plus `pytest` as dev extra. Removes `python-rake`/`rake-nltk`.
- `README.md` fully rewritten for the real config, CLI, workflow, setup.
- `.gitignore`: word-cloud output, `__pycache__`, venv, `.env`.

## Dependencies

- `feedparser` — arXiv API parse
- `wordcloud` — word cloud PNG
- `matplotlib` — word cloud renderer backend
- `markdown` — markdown → HTML for body
- `pytest` (dev)

## Open Questions / Placeholders

None — all decisions resolved during brainstorming.