"""Unit tests for the PaperFetcher class."""

import unittest
from unittest.mock import patch, Mock
import feedparser
from src.paper_fetcher import PaperFetcher


class TestPaperFetcher(unittest.TestCase):
    """Test suite for PaperFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PaperFetcher()

    def test_initialization(self):
        """Test PaperFetcher initialization."""
        self.assertEqual(self.fetcher.query, 'cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.CV')
        self.assertEqual(self.fetcher.max_results, 50)
        self.assertEqual(self.fetcher.BASE_URL, 'http://export.arxiv.org/api/query?')

    @patch('src.paper_fetcher.feedparser.parse')
    def test_fetch_latest_papers_success(self, mock_parse):
        """Test successful paper fetching."""
        # Mock feedparser response
        mock_author1 = Mock()
        mock_author1.name = 'Author 1'
        mock_author2 = Mock()
        mock_author2.name = 'Author 2'
        
        mock_entry = Mock()
        mock_entry.id = 'test_id'
        mock_entry.title = 'Test Title'
        mock_entry.summary = 'Test Summary'
        mock_entry.authors = [mock_author1, mock_author2]
        mock_entry.published = '2023-01-01'
        mock_entry.link = 'http://example.com/test'
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        
        mock_parse.return_value = mock_feed
        
        papers = self.fetcher.fetch_latest_papers()
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]['id'], 'test_id')
        self.assertEqual(papers[0]['title'], 'Test Title')
        self.assertEqual(papers[0]['summary'], 'Test Summary')
        self.assertEqual(papers[0]['authors'], ['Author 1', 'Author 2'])
        self.assertEqual(papers[0]['published'], '2023-01-01')
        self.assertEqual(papers[0]['link'], 'http://example.com/test')

    @patch('src.paper_fetcher.feedparser.parse')
    def test_fetch_latest_papers_empty_response(self, mock_parse):
        """Test handling of empty response."""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        papers = self.fetcher.fetch_latest_papers()
        
        self.assertEqual(len(papers), 0)

    @patch('src.paper_fetcher.feedparser.parse')
    def test_fetch_latest_papers_missing_fields(self, mock_parse):
        """Test handling of entries with missing fields."""
        # Mock entry with missing title/summary to trigger warning
        mock_entry = Mock()
        mock_entry.id = 'test_id'
        # Don't set title or summary attributes to simulate missing fields
        # hasattr will return False for title and summary
        
        mock_feed = Mock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        papers = self.fetcher.fetch_latest_papers()
        
        # Should skip the entry with missing summary
        self.assertEqual(len(papers), 0)

    @patch('src.paper_fetcher.feedparser.parse')
    def test_fetch_latest_papers_exception(self, mock_parse):
        """Test handling of exceptions during fetching."""
        mock_parse.side_effect = Exception("Network error")
        
        papers = self.fetcher.fetch_latest_papers()
        
        self.assertEqual(len(papers), 0)


if __name__ == '__main__':
    unittest.main()