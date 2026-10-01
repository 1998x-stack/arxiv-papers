# src/news_email_scheduler.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import logging
import os
import time
from src.paper_fetcher import PaperFetcher
from src.email_sender import EmailSender
from src.markdown_formatter import MarkdownFormatter
from src.wordcloud_generator import WordCloudGenerator
from src.logger import setup_logger
from typing import Optional

class NewsEmailScheduler:
     """Scheduler to fetch latest papers, generate word clouds, and send emails."""

     def __init__(self):
         """Initialize the NewsEmailScheduler instance."""
         setup_logger()
         self.fetcher = PaperFetcher()
         username = os.environ.get('EMAIL_USERNAME')
         password = os.environ.get('EMAIL_PASSWORD')
         if not username or not password:
             raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD environment variables must be set")
         self.email_sender = EmailSender(
             username=username,
             password=password
         )
         logging.debug("NewsEmailScheduler instance created.")

     def send_news_email(self):
         """Fetch papers, generate word cloud, and send email."""
         papers = self.fetcher.fetch_latest_papers()
         if papers:
             try:
                 # Format email content first
                 body = MarkdownFormatter.format_papers(papers)
                 subject = f"Latest ML Papers ({time.strftime('%Y-%m-%d %H:%M')})"
                 to_emails = [self.email_sender.username]  # Replace with actual recipients
                 
                 # Generate word cloud
                 wordcloud_path = WordCloudGenerator.generate_wordcloud(papers)
                 
                 # Prepare attachments - include wordcloud if generated successfully
                 attachments = [wordcloud_path] if wordcloud_path else None
                 
                 # Send email with optional word cloud attachment
                 self.email_sender.send_email(subject, body, to_emails, attachments=attachments)
                 logging.info("Email sent successfully.")
             except Exception as e:
                 logging.error(f"Error in email processing: {e}")
                 raise
         else:
             logging.warning("No new papers found; email not sent.")

     def start(self):
         """Start the process."""
         self.send_news_email()

if __name__ == "__main__":
     try:
         scheduler = NewsEmailScheduler()
         scheduler.start()
     except ValueError as e:
         logging.error(f"Configuration error: {e}")
         sys.exit(1)
     except Exception as e:
         logging.error(f"Unexpected error: {e}")
         sys.exit(1)