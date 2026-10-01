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