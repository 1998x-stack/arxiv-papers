"""Unit tests for the WordCloudGenerator class."""

import unittest
from unittest.mock import patch, Mock
from src.wordcloud_generator import WordCloudGenerator


class TestWordCloudGenerator(unittest.TestCase):
    """Test suite for WordCloudGenerator class."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        papers = [
            {
                'title': 'Machine Learning Algorithm',
                'summary': 'This paper discusses machine learning algorithms.'
            }
        ]
        
        keywords = WordCloudGenerator.extract_keywords(papers)
        
        # Check if keywords contain expected terms
        self.assertIn('machine', keywords.lower())
        self.assertIn('learning', keywords.lower())

    def test_extract_keywords_with_length_filter(self):
        """Test keyword extraction with length filtering."""
        papers = [
            {
                'title': 'Deep Learning Neural Networks',
                'summary': 'This paper presents deep learning approaches using neural networks.'
            }
        ]
        
        # Test with min_length=1, max_length=2
        keywords = WordCloudGenerator.extract_keywords(papers, min_length=1, max_length=2)
        
        # The result should contain single words and 2-word phrases
        # but not longer phrases
        words = keywords.split()
        self.assertTrue(len(words) > 0)

    def test_extract_keywords_empty_papers(self):
        """Test keyword extraction with empty papers list."""
        papers = []
        
        keywords = WordCloudGenerator.extract_keywords(papers)
        
        self.assertEqual(keywords, '')

    @patch('src.wordcloud_generator.WordCloud')
    def test_generate_wordcloud_success(self, mock_wordcloud_class):
        """Test successful wordcloud generation."""
        # Mock the WordCloud instance and its methods
        mock_wordcloud_instance = Mock()
        mock_wordcloud_instance.generate.return_value = mock_wordcloud_instance  # generate returns self
        mock_wordcloud_class.return_value = mock_wordcloud_instance
        
        papers = [
            {
                'title': 'Machine Learning Research',
                'summary': 'Research on machine learning algorithms and applications.'
            }
        ]
        
        # Directly patch the static method to avoid complex mocking
        with patch('src.wordcloud_generator.WordCloudGenerator.extract_keywords', return_value='some keywords'):
            result = WordCloudGenerator.generate_wordcloud(papers, output_path='/tmp/test.png')
        
        # Verify the wordcloud was generated
        # Check that WordCloud was instantiated
        mock_wordcloud_class.assert_called_once()
        # The generate method is called on the instance returned by the constructor
        mock_wordcloud_instance.generate.assert_called_once()
        mock_wordcloud_instance.to_file.assert_called_once_with('/tmp/test.png')
        self.assertEqual(result, '/tmp/test.png')

    @patch('src.wordcloud_generator.WordCloud')
    def test_generate_wordcloud_empty_papers(self, mock_wordcloud_class):
        """Test wordcloud generation with empty papers list."""
        papers = []
        
        result = WordCloudGenerator.generate_wordcloud(papers)
        
        # Should return None when no papers are provided
        self.assertIsNone(result)
        # WordCloud should not be called
        mock_wordcloud_class.assert_not_called()

    @patch('src.wordcloud_generator.WordCloud')
    def test_generate_wordcloud_no_keywords(self, mock_wordcloud_class):
        """Test wordcloud generation when no keywords are extracted."""
        # Mock the extract_keywords method to return empty string
        with patch.object(WordCloudGenerator, 'extract_keywords', return_value=''):
            papers = [
                {
                    'title': 'Test',
                    'summary': 'Test summary'
                }
            ]
            
            result = WordCloudGenerator.generate_wordcloud(papers)
            
            # Should return None when no keywords are extracted
            self.assertIsNone(result)
            # WordCloud should not be called
            mock_wordcloud_class.assert_not_called()

    @patch('src.wordcloud_generator.WordCloud')
    def test_generate_wordcloud_exception(self, mock_wordcloud_class):
        """Test wordcloud generation with exception."""
        # Mock WordCloud to raise an exception
        mock_wordcloud_class.side_effect = Exception("WordCloud error")
        
        papers = [
            {
                'title': 'Machine Learning Research',
                'summary': 'Research on machine learning algorithms.'
            }
        ]
        
        result = WordCloudGenerator.generate_wordcloud(papers)
        
        # Should return None when an exception occurs
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()