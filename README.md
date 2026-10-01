# arxiv-digest

Stay current with machine-learning research without leaving your inbox.

`arxiv-digest` fetches the latest papers from arXiv, distils them into a compact
HTML digest, and emails it on a schedule you control — optionally paired with a
word-cloud image that visualizes the dominant themes of the day's submissions.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Environment variables](#environment-variables)
  - [Precedence](#precedence)
- [Usage](#usage)
- [Automated Scheduling (GitHub Actions)](#automated-scheduling-github-actions)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **Fetches the latest papers** from configurable arXiv categories — defaults to
  machine learning, AI, neural networks, and computer vision.
- **Keyword word cloud** generated from paper titles and abstracts, attached to
  every digest email.
- **Clean HTML digest** with one linked entry per paper (title, authors, abstract),
  with all content HTML-escaped to prevent injection.
- **Safe preview mode** (`--dry-run`) that renders the message locally without
  sending anything or requiring credentials.
- **Validated, layered configuration** through environment variables and CLI
  flags, with clear error messages instead of silent crashes.
- **Runs anywhere** via a console script or `python -m`, and can be scheduled
  automatically with GitHub Actions.

## Requirements

- Python 3.9+
- Internet access when fetching papers or sending email

## Installation

```bash
git clone <repository-url>
cd arxiv-papers

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install runtime dependencies
pip install -r requirements.txt

# (Optional) Install the package in editable mode for the `arxiv-digest` command
pip install -e .
```

## Quick Start

Generate a preview digest (no credentials needed, no email sent):

```bash
arxiv-digest --dry-run --categories cs.AI --max-results 5
```

Check the rendered output, then send a real digest:

```bash
EMAIL_USERNAME=you@gmail.com \
EMAIL_PASSWORD='your-app-password' \
EMAIL_TO=you@gmail.com \
arxiv-digest
```

## Configuration

All settings are read from environment variables. CLI flags override them for a
single invocation, and both fall back to sensible defaults.

### Environment variables

| Variable              | Required          | Default                     | Description                              |
|-----------------------|-------------------|-----------------------------|------------------------------------------|
| `EMAIL_USERNAME`      | unless `--dry-run`| —                           | SMTP account used to send the digest     |
| `EMAIL_PASSWORD`      | unless `--dry-run`| —                           | SMTP account password or app password     |
| `EMAIL_TO`            | no                | `EMAIL_USERNAME`            | Recipients (comma-separated)              |
| `SMTP_SERVER`         | no                | `smtp.gmail.com`            | SMTP server host                          |
| `SMTP_PORT`           | no                | `587`                       | SMTP port (STARTTLS)                      |
| `DIGEST_CATEGORIES`   | no                | `cs.LG,cs.AI,cs.NE,cs.CV`   | arXiv categories to query                 |
| `DIGEST_MAX_RESULTS`  | no                | `50`                        | Maximum papers to fetch                   |

### Precedence

Configuration is resolved in order of increasing priority:

1. Built-in defaults
2. Environment variables
3. CLI flags (`--categories`, `--max-results`, `--to`)

## Usage

```text
usage: arxiv-digest [-h] [--categories CATEGORIES] [--max-results MAX_RESULTS]
                    [--to TO] [--dry-run]

Fetch arXiv ML papers and email an HTML digest

optional arguments:
  -h, --help            show this help message and exit
  --categories CATEGORIES  comma-separated arXiv categories
  --max-results MAX_RESULTS max papers to fetch
  --to TO                   comma-separated recipients
  --dry-run                 render a preview without sending email
```

### Preview a digest

```bash
arxiv-digest --dry-run --categories cs.CL --max-results 10
```

### Send a digest to yourself

```bash
export EMAIL_USERNAME="you@gmail.com"
export EMAIL_PASSWORD="your-app-password"
arxiv-digest
```

### Override categories and recipients for a single run

```bash
EMAIL_TO="alice@example.com, bob@example.com" \
arxiv-digest --categories "cs.LG,cs.CV,cs.CL" --max-results 20
```

## Automated Scheduling (GitHub Actions)

The repository includes a workflow (``.github/workflows/send_papers.yml`) that
sends a digest every day at 08:00 UTC, and can also be triggered manually from
the Actions tab.

Configure these repository **secrets** under
*Settings → Secrets and Variables → Actions*:

| Secret name      | Purpose                                  |
|------------------|------------------------------------------|
| `EMAIL_USERNAME` | Email account that sends the digest       |
| `EMAIL_PASSWORD` | Account password / app-specific password  |
| `EMAIL_TO`       | Optional — recipients (comma-separated)   |

The workflow also runs the offline test suite on every push to `main` and on
pull requests, so changes are verified before they ship.

## Testing

The test suite is fully offline — it never calls the live arXiv API or a real
SMTP server. Network and mail are mocked.

```bash
pip install -e '.[dev]'   # installs pytest
pytest -v
```

## Project Structure

```
arxiv-papers/
├── .github/
│   └── workflows/
│       └── send_papers.yml      # CI (tests) + scheduled digest job
├── src/arxiv_digest/
│   ├── __init__.py
│   ├── cli.py                   # argparse entry point; drives the pipeline
│   ├── config.py                # defaults, env/CLI overrides, validation
│   ├── models.py                # Article dataclass
│   ├── fetcher.py               # arXiv fetch (the only network dependency)
│   ├── formatter.py             # HTML email body (pure logic, escapes content)
│   ├── wordcloud.py             # word cloud PNG (pure logic)
│   └── emailer.py               # MIME construction + SMTP send
├── tests/                       # offline pytest suite
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.