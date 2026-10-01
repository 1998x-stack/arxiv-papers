"""Command-line entry point for the digest pipeline."""
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