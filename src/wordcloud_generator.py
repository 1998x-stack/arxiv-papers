import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import logging
from rake_nltk import Rake  # Import RAKE

class WordCloudGenerator:
    """Generates a word cloud image from paper abstracts and titles using RAKE for keyword extraction."""

    @staticmethod
    def extract_keywords(papers):
        """Extract keywords from paper titles and abstracts using RAKE."""
        rake = Rake()  # Initialize RAKE
        text = ' '.join([paper['title'] + ' ' + paper['summary'] for paper in papers])
        rake.extract_keywords_from_text(text)
        # Extract ranked phrases (keywords) from the text
        keywords = rake.get_ranked_phrases()
        logging.info(f"Extracted {len(keywords)} keywords.")
        return ' '.join(keywords)

    @staticmethod
    def generate_wordcloud(papers, output_path='wordcloud.png'):
        """Generate a word cloud image from the extracted keywords."""
        # Extract keywords using RAKE
        keywords_text = WordCloudGenerator.extract_keywords(papers)
        # Generate word cloud from the keywords
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(keywords_text)
        wordcloud.to_file(output_path)
        logging.info(f"Word cloud saved to {output_path}")
        return output_path