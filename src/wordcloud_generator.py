import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import logging
import RAKE  # Importing the python-rake package

class WordCloudGenerator:
    """Generates a word cloud image from paper abstracts and titles using RAKE for keyword extraction."""

    @staticmethod
    def extract_keywords(papers):
        """Extract keywords from paper titles and abstracts using RAKE."""
        # Initialize RAKE with default stopwords
        rake = RAKE.Rake(RAKE.SmartStopList())
        
        # Combine paper titles and summaries into a single text
        text = ' '.join([paper['title'] + ' ' + paper['summary'] for paper in papers])
        
        # Extract keywords using RAKE
        keywords = rake.run(text)
        
        # Extract only the keyword phrases (ignore scores)
        keyword_phrases = [keyword[0] for keyword in keywords]
        
        logging.info(f"Extracted {len(keyword_phrases)} keywords.")
        return ' '.join(keyword_phrases)

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