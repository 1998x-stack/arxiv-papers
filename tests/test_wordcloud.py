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