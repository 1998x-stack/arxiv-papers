import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import logging
import RAKE  # Importing the python-rake package
from typing import List, Dict, Any, Optional

class WordCloudGenerator:
     """Generates a word cloud image from paper abstracts and titles using RAKE for keyword extraction."""

     @staticmethod
     def extract_keywords(papers: List[Dict[str, Any]], min_length: int = 1, max_length: int = 3) -> str:
         """
         Extract keywords from paper titles and abstracts using RAKE with keyword length control.

         Args:
             papers (list): List of papers with titles and summaries.
             min_length (int): Minimum number of words in a keyword phrase.
             max_length (int): Maximum number of words in a keyword phrase.

         Returns:
             str: A string of extracted keywords filtered by the given length.
         """
         # Initialize RAKE with default stopwords
         rake = RAKE.Rake(RAKE.SmartStopList())
         
         # Combine paper titles and summaries into a single text
         text = ' '.join([paper['title'] + ' ' + paper['summary'] for paper in papers])
         
         # Extract keywords using RAKE
         keywords = rake.run(text)
         
         # Filter keywords based on the length of the phrases
         keyword_phrases = [
             keyword[0] for keyword in keywords
             if min_length <= len(keyword[0].split()) <= max_length  # Control the length of phrases
         ]
         
         logging.info(f"Extracted {len(keyword_phrases)} keywords with length between {min_length} and {max_length}.")
         return ' '.join(keyword_phrases)

     @staticmethod
     def generate_wordcloud(papers: List[Dict[str, Any]], output_path: str = 'wordcloud.png', min_length: int = 2, max_length: int = 4) -> Optional[str]:
         """
         Generate a word cloud image from the extracted keywords.

         Args:
             papers (list): List of papers with titles and summaries.
             output_path (str): File path to save the word cloud image.
             min_length (int): Minimum number of words in a keyword phrase.
             max_length (int): Maximum number of words in a keyword phrase.

         Returns:
             str: The output file path of the word cloud image.
         """
         if not papers:
             logging.warning("No papers provided for word cloud generation.")
             return None
             
         # Extract keywords using RAKE and apply length filter
         keywords_text = WordCloudGenerator.extract_keywords(papers, min_length, max_length)
         
         if not keywords_text.strip():
             logging.warning("No keywords extracted for word cloud generation.")
             return None
         
         try:
             # Generate word cloud from the keywords
             wordcloud = WordCloud(width=800, height=400, background_color='white').generate(keywords_text)
             wordcloud.to_file(output_path)
             logging.info(f"Word cloud saved to {output_path}")
             return output_path
         except Exception as e:
             logging.error(f"Error generating word cloud: {e}")
             return None