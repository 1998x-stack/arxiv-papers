"""Unit tests for the NewsEmailScheduler class."""

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
from src.news_email_scheduler import NewsEmailScheduler
from src.paper_fetcher import PaperFetcher
from src.email_sender import EmailSender


class TestNewsEmailScheduler(unittest.TestCase):
    """Test suite for NewsEmailScheduler class."""

    def setUp(self):
        """Set up test fixtures."""
        # Temporarily set environment variables for testing
        os.environ['EMAIL_USERNAME'] = 'test@example.com'
        os.environ['EMAIL_PASSWORD'] = 'password'

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove environment variables after testing
        if 'EMAIL_USERNAME' in os.environ:
            del os.environ['EMAIL_USERNAME']
        if 'EMAIL_PASSWORD' in os.environ:
            del os.environ['EMAIL_PASSWORD']

    @patch('src.news_email_scheduler.PaperFetcher')
    @patch('src.news_email_scheduler.EmailSender')
    @patch('src.news_email_scheduler.setup_logger')
    def test_initialization_success(self, mock_setup_logger, mock_email_sender_class, mock_paper_fetcher_class):
        """Test successful initialization of NewsEmailScheduler."""
        # Mock the classes
        mock_paper_fetcher_instance = Mock(spec=PaperFetcher)
        mock_email_sender_instance = Mock(spec=EmailSender)
        
        mock_paper_fetcher_class.return_value = mock_paper_fetcher_instance
        mock_email_sender_class.return_value = mock_email_sender_instance
        
        scheduler = NewsEmailScheduler()
        
        # Verify initialization
        self.assertIsInstance(scheduler.fetcher, PaperFetcher)
        self.assertIsInstance(scheduler.email_sender, EmailSender)

    def test_initialization_missing_env_vars(self):
        """Test initialization with missing environment variables."""
        # Remove environment variables temporarily
        username_backup = os.environ.get('EMAIL_USERNAME')
        password_backup = os.environ.get('EMAIL_PASSWORD')
        
        if 'EMAIL_USERNAME' in os.environ:
            del os.environ['EMAIL_USERNAME']
        if 'EMAIL_PASSWORD' in os.environ:
            del os.environ['EMAIL_PASSWORD']
        
        try:
            with self.assertRaises(ValueError):
                NewsEmailScheduler()
        finally:
            # Restore environment variables
            if username_backup is not None:
                os.environ['EMAIL_USERNAME'] = username_backup
            if password_backup is not None:
                os.environ['EMAIL_PASSWORD'] = password_backup

    @patch('src.news_email_scheduler.PaperFetcher')
    @patch('src.news_email_scheduler.EmailSender')
    @patch('src.news_email_scheduler.WordCloudGenerator')
    @patch('src.news_email_scheduler.MarkdownFormatter')
    @patch('src.news_email_scheduler.setup_logger')
    def test_send_news_email_with_papers(self, mock_setup_logger, mock_markdown_formatter, 
                                         mock_wordcloud_generator, mock_email_sender_class, 
                                         mock_paper_fetcher_class):
        """Test sending news email with papers."""
        # Mock dependencies
        mock_paper_fetcher_instance = Mock()
        mock_email_sender_instance = Mock()
        mock_markdown_formatter_class = Mock()
        
        mock_paper_fetcher_class.return_value = mock_paper_fetcher_instance
        mock_email_sender_class.return_value = mock_email_sender_instance
        mock_markdown_formatter.format_papers = Mock(return_value="Formatted HTML content")
        mock_wordcloud_generator.generate_wordcloud = Mock(return_value="/tmp/wordcloud.png")
        
        # Mock papers data
        mock_papers = [{'id': 'test_id', 'title': 'Test Paper', 'summary': 'Test Summary', 
                       'authors': ['Author'], 'published': '2023-01-01', 'link': 'http://example.com'}]
        mock_paper_fetcher_instance.fetch_latest_papers.return_value = mock_papers
        
        scheduler = NewsEmailScheduler()
        scheduler.send_news_email()
        
        # Verify methods were called appropriately
        mock_paper_fetcher_instance.fetch_latest_papers.assert_called_once()
        mock_markdown_formatter.format_papers.assert_called_once_with(mock_papers)
        mock_wordcloud_generator.generate_wordcloud.assert_called_once_with(mock_papers)
        mock_email_sender_instance.send_email.assert_called_once()

    @patch('src.news_email_scheduler.PaperFetcher')
    @patch('src.news_email_scheduler.EmailSender')
    @patch('src.news_email_scheduler.WordCloudGenerator')
    @patch('src.news_email_scheduler.MarkdownFormatter')
    @patch('src.news_email_scheduler.setup_logger')
    def test_send_news_email_no_papers(self, mock_setup_logger, mock_markdown_formatter, 
                                       mock_wordcloud_generator, mock_email_sender_class, 
                                       mock_paper_fetcher_class):
        """Test sending news email with no papers."""
        # Mock dependencies
        mock_paper_fetcher_instance = Mock()
        mock_email_sender_instance = Mock()
        
        mock_paper_fetcher_class.return_value = mock_paper_fetcher_instance
        mock_email_sender_class.return_value = mock_email_sender_instance
        
        # Mock empty papers list
        mock_paper_fetcher_instance.fetch_latest_papers.return_value = []
        
        scheduler = NewsEmailScheduler()
        scheduler.send_news_email()
        
        # Verify that email sending was not called
        mock_paper_fetcher_instance.fetch_latest_papers.assert_called_once()
        mock_email_sender_instance.send_email.assert_not_called()

    @patch('src.news_email_scheduler.PaperFetcher')
    @patch('src.news_email_scheduler.EmailSender')
    @patch('src.news_email_scheduler.WordCloudGenerator')
    @patch('src.news_email_scheduler.MarkdownFormatter')
    @patch('src.news_email_scheduler.setup_logger')
    def test_send_news_email_wordcloud_failure(self, mock_setup_logger, mock_markdown_formatter, 
                                               mock_wordcloud_generator, mock_email_sender_class, 
                                               mock_paper_fetcher_class):
        """Test sending news email when wordcloud generation fails."""
        # Mock dependencies
        mock_paper_fetcher_instance = Mock()
        mock_email_sender_instance = Mock()
        mock_markdown_formatter_class = Mock()
        
        mock_paper_fetcher_class.return_value = mock_paper_fetcher_instance
        mock_email_sender_class.return_value = mock_email_sender_instance
        mock_markdown_formatter.format_papers = Mock(return_value="Formatted HTML content")
        mock_wordcloud_generator.generate_wordcloud = Mock(return_value=None)  # Simulate failure
        
        # Mock papers data
        mock_papers = [{'id': 'test_id', 'title': 'Test Paper', 'summary': 'Test Summary', 
                       'authors': ['Author'], 'published': '2023-01-01', 'link': 'http://example.com'}]
        mock_paper_fetcher_instance.fetch_latest_papers.return_value = mock_papers
        
        scheduler = NewsEmailScheduler()
        scheduler.send_news_email()
        
        # Verify email was sent without attachments
        mock_email_sender_instance.send_email.assert_called_once()
        # Check that attachments parameter was passed as None
        args, kwargs = mock_email_sender_instance.send_email.call_args
        self.assertIsNone(kwargs.get('attachments'))


if __name__ == '__main__':
    unittest.main()