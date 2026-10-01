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