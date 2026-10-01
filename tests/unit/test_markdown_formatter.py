"""Unit tests for the MarkdownFormatter class."""

import unittest
from src.markdown_formatter import MarkdownFormatter


class TestMarkdownFormatter(unittest.TestCase):
    """Test suite for MarkdownFormatter class."""

    def test_format_papers_basic(self):
        """Test basic paper formatting."""
        papers = [{
            'title': 'Test Paper Title',
            'summary': 'This is a test paper summary.',
            'link': 'http://example.com/paper',
            'authors': ['John Doe', 'Jane Smith']
        }]
        
        html_content = MarkdownFormatter.format_papers(papers)
        
        # Check that all elements are present in the formatted output
        self.assertIn('Test Paper Title', html_content)
        self.assertIn('This is a test paper summary.', html_content)
        self.assertIn('http://example.com/paper', html_content)
        self.assertIn('John Doe', html_content)
        self.assertIn('Jane Smith', html_content)

    def test_format_papers_special_characters(self):
        """Test formatting with special characters."""
        papers = [{
            'title': 'Title with [brackets] and (parentheses)',
            'summary': 'Summary with <script>alert("xss")</script> potential XSS',
            'link': 'http://example.com/paper',
            'authors': ['Author with <tag>', 'Another Author']
        }]
        
        html_content = MarkdownFormatter.format_papers(papers)
        
        # Check that HTML tags are properly escaped (the main concern)
        self.assertIn('&lt;script&gt;', html_content)  # Escaped HTML tag in summary
        self.assertIn('&lt;tag&gt;', html_content)  # Escaped HTML tag in author name
        # The brackets and parentheses are escaped in markdown but converted by markdown parser
        # The important thing is that HTML tags are properly escaped to prevent XSS

    def test_format_papers_empty_list(self):
        """Test formatting with empty papers list."""
        papers = []
        html_content = MarkdownFormatter.format_papers(papers)
        
        self.assertEqual(html_content, '')

    def test_format_papers_multiple_papers(self):
        """Test formatting with multiple papers."""
        papers = [
            {
                'title': 'First Paper',
                'summary': 'Summary of first paper.',
                'link': 'http://example.com/paper1',
                'authors': ['Author 1']
            },
            {
                'title': 'Second Paper',
                'summary': 'Summary of second paper.',
                'link': 'http://example.com/paper2',
                'authors': ['Author 2', 'Author 3']
            }
        ]
        
        html_content = MarkdownFormatter.format_papers(papers)
        
        self.assertIn('First Paper', html_content)
        self.assertIn('Second Paper', html_content)
        self.assertIn('Summary of first paper.', html_content)
        self.assertIn('Summary of second paper.', html_content)

    def test_format_papers_unicode_characters(self):
        """Test formatting with Unicode characters."""
        papers = [{
            'title': '论文标题 with Unicode characters',
            'summary': 'Résumé with accents and ñoñ-Latin characters',
            'link': 'http://example.com/paper',
            'authors': ['José María', 'François']
        }]
        
        html_content = MarkdownFormatter.format_papers(papers)
        
        self.assertIn('论文标题', html_content)
        self.assertIn('Résumé', html_content)
        self.assertIn('José María', html_content)
        self.assertIn('François', html_content)


if __name__ == '__main__':
    unittest.main()