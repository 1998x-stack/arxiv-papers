"""Unit tests for the EmailSender class."""

import unittest
from unittest.mock import patch, Mock, mock_open
import smtplib
from src.email_sender import EmailSender


class TestEmailSender(unittest.TestCase):
    """Test suite for EmailSender class."""

    def setUp(self):
        """Set up test fixtures."""
        self.email_sender = EmailSender('test@example.com', 'password')

    def test_initialization(self):
        """Test EmailSender initialization."""
        self.assertEqual(self.email_sender.username, 'test@example.com')
        self.assertEqual(self.email_sender.password, 'password')
        self.assertEqual(self.email_sender.smtp_server, 'smtp.gmail.com')
        self.assertEqual(self.email_sender.smtp_port, 587)

    @patch('src.email_sender.smtplib.SMTP')
    @patch('src.email_sender.os.path.isfile', return_value=True)  # Mock file existence check
    @patch('src.email_sender.open', new_callable=mock_open, read_data=b'test file content')
    def test_send_email_success_with_attachments(self, mock_file, mock_isfile, mock_smtp_class):
        """Test successful email sending with attachments."""
        # Mock SMTP connection
        mock_smtp_instance = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test sending email
        subject = "Test Subject"
        body = "Test Body"
        to_emails = ["recipient@example.com"]
        attachments = ["test_file.pdf"]
        
        self.email_sender.send_email(subject, body, to_emails, attachments)
        
        # Verify SMTP methods were called
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test@example.com', 'password')
        mock_smtp_instance.send_message.assert_called_once()
        
        # Verify file was opened for attachment (only if file exists)
        mock_file.assert_called_once_with('test_file.pdf', 'rb')

    @patch('src.email_sender.smtplib.SMTP')
    def test_send_email_success_without_attachments(self, mock_smtp_class):
        """Test successful email sending without attachments."""
        # Mock SMTP connection
        mock_smtp_instance = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test sending email without attachments
        subject = "Test Subject"
        body = "Test Body"
        to_emails = ["recipient@example.com"]
        
        self.email_sender.send_email(subject, body, to_emails)
        
        # Verify SMTP methods were called
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test@example.com', 'password')
        mock_smtp_instance.send_message.assert_called_once()

    @patch('src.email_sender.smtplib.SMTP')
    @patch('src.email_sender.open', side_effect=FileNotFoundError("File not found"))
    def test_send_email_missing_attachment(self, mock_file, mock_smtp_class):
        """Test email sending with missing attachment file."""
        # Mock SMTP connection
        mock_smtp_instance = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test sending email with missing attachment
        subject = "Test Subject"
        body = "Test Body"
        to_emails = ["recipient@example.com"]
        attachments = ["nonexistent_file.pdf"]
        
        # Should not raise an exception, just issue a warning
        self.email_sender.send_email(subject, body, to_emails, attachments)
        
        # Verify email was still sent
        mock_smtp_instance.send_message.assert_called_once()

    @patch('src.email_sender.smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp_class):
        """Test handling of SMTP authentication error."""
        # Mock SMTP to raise authentication error
        mock_smtp_instance = Mock()
        mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test that authentication error is raised
        with self.assertRaises(smtplib.SMTPAuthenticationError):
            self.email_sender.send_email("Test", "Body", ["test@example.com"])

    @patch('src.email_sender.smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp_class):
        """Test handling of SMTP error."""
        # Mock SMTP to raise generic SMTP error
        mock_smtp_instance = Mock()
        mock_smtp_instance.login.side_effect = smtplib.SMTPException("SMTP error")
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test that SMTP error is raised
        with self.assertRaises(smtplib.SMTPException):
            self.email_sender.send_email("Test", "Body", ["test@example.com"])


if __name__ == '__main__':
    unittest.main()