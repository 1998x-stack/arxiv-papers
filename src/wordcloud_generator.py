# src/wordcloud_generator.py
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import logging

class WordCloudGenerator:
    """Generates a word cloud image from paper abstracts and titles."""

    @staticmethod
    def generate_wordcloud(papers, output_path='wordcloud.png'):
        """Generate a word cloud image from the given papers."""
        text = ' '.join([paper['title'] + ' ' + paper['summary'] for paper in papers])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        wordcloud.to_file(output_path)
        logging.info(f"Word cloud saved to {output_path}")
        return output_path