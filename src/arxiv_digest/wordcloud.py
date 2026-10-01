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