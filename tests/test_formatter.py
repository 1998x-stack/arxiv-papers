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