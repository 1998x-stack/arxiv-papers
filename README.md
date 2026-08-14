# arxiv-digest

Fetch the latest machine-learning, deep-learning, reinforcement-learning, and
computer-vision papers from arXiv, build a word cloud from their titles and
abstracts, and email a formatted HTML digest — as a local CLI and, optionally,
on a schedule via GitHub Actions.

## Features

- Fetches recent papers from arXiv categories (default `cs.LG`, `cs.AI`, `cs.NE`, `cs.CV`).
- Generates a word cloud PNG from paper titles and abstracts.
- Sends a clean HTML digest email with one linked entry per paper, plus the word
  cloud attached.
- `--dry-run` renders the message without sending anything or requiring credentials.
- Validated configuration via environment variables and CLI flags.
- Optional GitHub Actions scheduling (daily at 08:00 UTC).

## Project Structure

```
arxiv-papers/
├── .github/workflows/send_papers.yml   # GitHub Actions scheduler
├── src/arxiv_digest/
│   ├── config.py       # configuration + validation
│   ├── models.py       # Article dataclass
│   ├── fetcher.py      # arXiv fetch (network)
│   ├── formatter.py    # HTML email body
│   ├── wordcloud.py    # word cloud PNG
│   ├── emailer.py      # MIME + SMTP send
│   └── cli.py          # command-line entry point
└── tests/              # pytest suite (offline)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Settings are read from environment variables; `--categories`,
`--max-results`, and `--to` CLI flags override them.

| Variable              | Required              | Default                        |
|-----------------------|-----------------------|--------------------------------|
| `EMAIL_USERNAME`      | unless `--dry-run`    | —                              |
| `EMAIL_PASSWORD`      | unless `--dry-run`    | —                              |
| `EMAIL_TO`            | no                    | `EMAIL_USERNAME`               |
| `SMTP_SERVER`         | no                    | `smtp.gmail.com`               |
| `SMTP_PORT`           | no                    | `587`                          |
| `DIGEST_CATEGORIES`   | no                    | `cs.LG,cs.AI,cs.NE,cs.CV`      |
| `DIGEST_MAX_RESULTS`  | no                    | `50`                           |

## Usage

```bash
# Preview without sending (no credentials needed)
python -m arxiv_digest.cli --dry-run --categories cs.AI --max-results 5

# Send a digest
EMAIL_USERNAME=you@gmail.com \
EMAIL_PASSWORD='app password' \
EMAIL_TO=you@gmail.com \
python -m arxiv_digest.cli
```

The package also installs a console script: `arxiv-digest`.

Run the tests (all offline):

```bash
pytest -v
```

## GitHub Actions

The workflow at `.github/workflows/send_papers.yml` runs daily at 08:00 UTC
(and can be triggered manually via *Run workflow*). Configure the following
repository secrets under *Settings → Secrets and Variables → Actions*:

- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`
- `EMAIL_TO` (optional — recipients)

## License

MIT (see `LICENSE` if present).