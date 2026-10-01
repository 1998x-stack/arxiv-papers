"""Integration tests for the arxiv-papers project."""

import unittest
import os
from unittest.mock import patch, Mock
from src.paper_fetcher import PaperFetcher
from src.markdown_formatter import MarkdownFormatter
from src.wordcloud_generator import WordCloudGenerator


class TestIntegration(unittest.TestCase):
    """Integration tests for the arxiv-papers workflow."""

    def test_end_to_end_workflow_simulated(self):
        """Test the end-to-end workflow with simulated data."""
        # Create sample papers data
        sample_papers = [
            {
                'id': 'test_id_1',
                'title': 'Test Paper 1',
                'summary': 'This is the summary of test paper 1.',
                'authors': ['Author 1', 'Author 2'],
                'published': '2023-01-01',
                'link': 'http://example.com/paper1'
            },
            {
                'id': 'test_id_2',
                'title': 'Test Paper 2',
                'summary': 'This is the summary of test paper 2.',
                'authors': ['Author 3'],
                'published': '2023-01-02',
                'link': 'http://example.com/paper2'
            }
        ]
        
        # Test formatting
        html_content = MarkdownFormatter.format_papers(sample_papers)
        self.assertIn('Test Paper 1', html_content)
        self.assertIn('Test Paper 2', html_content)
        
        # Test word cloud generation (mocked to avoid actual image creation)
        with patch('src.wordcloud_generator.WordCloud') as mock_wordcloud_class:
            mock_wordcloud_instance = Mock()
            mock_wordcloud_class.return_value = mock_wordcloud_instance
            
            wordcloud_result = WordCloudGenerator.generate_wordcloud(sample_papers, '/tmp/test_cloud.png')
            
            # Verify word cloud was attempted to be generated
            mock_wordcloud_instance.generate.assert_called_once()
            self.assertEqual(wordcloud_result, '/tmp/test_cloud.png')

    @patch('src.paper_fetcher.feedparser.parse')
    def test_fetch_and_format_integration(self, mock_parse):
        """Test integration between paper fetching and formatting."""
        # Mock feedparser response
        mock_author = Mock()
        mock_author.name = 'Test Author'
        
        mock_entry = Mock()
        mock_entry.id = 'test_id'
        mock_entry.title = 'Integrated Test Paper'
        mock_entry.summary = 'This is a test summary for integration.'
        mock_entry.authors = [mock_author]
        mock_entry.published = '2023-01-01'
        mock_entry.link = 'http://example.com/integrated_test'
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        # Fetch papers
        fetcher = PaperFetcher()
        papers = fetcher.fetch_latest_papers()
        
        # Format papers
        html_content = MarkdownFormatter.format_papers(papers)
        
        # Verify integration worked
        self.assertEqual(len(papers), 1)
        self.assertIn('Integrated Test Paper', html_content)
        self.assertIn('http://example.com/integrated_test', html_content)

    def test_empty_papers_handling(self):
        """Test how empty papers list is handled across components."""
        # Test with empty papers list
        html_content = MarkdownFormatter.format_papers([])
        self.assertEqual(html_content, '')
        
        # Test word cloud generation with empty list
        with patch('src.wordcloud_generator.WordCloud') as mock_wordcloud_class:
            result = WordCloudGenerator.generate_wordcloud([])
            self.assertIsNone(result)
            mock_wordcloud_class.assert_not_called()


if __name__ == '__main__':
    unittest.main()