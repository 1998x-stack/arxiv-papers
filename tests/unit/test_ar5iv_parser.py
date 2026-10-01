"""Unit tests for the ar5iv_parser module."""

import unittest
from unittest.mock import patch, Mock, MagicMock
from ai_paper.paper_fetch.ar5iv_parser import ArxivHtmlParser, parse_html


class TestArxivHtmlParser(unittest.TestCase):
    """Test suite for ArxivHtmlParser class and parse_html function."""

    def test_initialization(self):
        """Test ArxivHtmlParser initialization."""
        parser = ArxivHtmlParser('1234.5678')
        
        self.assertEqual(parser.arxiv_id, '1234.5678')
        self.assertEqual(parser.base_url, 'https://ar5iv.labs.arxiv.org/html/1234.5678')
        self.assertIsNone(parser.soup)

    @patch('ai_paper.paper_fetch.ar5iv_parser.requests.get')
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<html><body>Test content</body></html>'
        mock_get.return_value = mock_response
        
        parser = ArxivHtmlParser('1234.5678')
        result = parser.fetch_html()
        
        self.assertTrue(result)
        self.assertIsNotNone(parser.soup)

    @patch('ai_paper.paper_fetch.ar5iv_parser.requests.get')
    def test_fetch_html_failure_status_code(self, mock_get):
        """Test HTML fetching with failed status code."""
        # Mock response with failure status
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        parser = ArxivHtmlParser('1234.5678')
        result = parser.fetch_html()
        
        self.assertFalse(result)

    @patch('ai_paper.paper_fetch.ar5iv_parser.requests.get')
    def test_fetch_html_request_exception(self, mock_get):
        """Test HTML fetching with request exception."""
        # Mock request to raise an exception
        mock_get.side_effect = Exception("Network error")
        
        parser = ArxivHtmlParser('1234.5678')
        result = parser.fetch_html()
        
        self.assertFalse(result)

    def test_parse_arxiv_html_function(self):
        """Test the parse_arxiv_html function."""
        # Mock the parser class
        with patch('ai_paper.paper_fetch.ar5iv_parser.ArxivHtmlParser') as mock_parser_class:
            mock_parser_instance = Mock()
            mock_parser_instance.fetch_html.return_value = True
            mock_parser_instance.parse_full_paper.return_value = {'title': 'Test Title'}
            mock_parser_class.return_value = mock_parser_instance
            
            result = parse_html('1234.5678')
            
            self.assertEqual(result, {'title': 'Test Title'})
            mock_parser_instance.fetch_html.assert_called_once()
            mock_parser_instance.parse_full_paper.assert_called_once()

    def test_parse_arxiv_html_function_failure(self):
        """Test the parse_arxiv_html function when fetching fails."""
        # Mock the parser class
        with patch('ai_paper.paper_fetch.ar5iv_parser.ArxivHtmlParser') as mock_parser_class:
            mock_parser_instance = Mock()
            mock_parser_instance.fetch_html.return_value = False  # Simulate failure
            mock_parser_class.return_value = mock_parser_instance
            
            result = parse_html('1234.5678')
            
            self.assertEqual(result, {})  # Should return empty dict on failure


if __name__ == '__main__':
    unittest.main()