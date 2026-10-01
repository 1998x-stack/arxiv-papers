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