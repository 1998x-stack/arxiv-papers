# src/news_email_scheduler.py
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import logging
import os
import time
from src.paper_fetcher import PaperFetcher
from src.email_sender import EmailSender
from src.markdown_formatter import MarkdownFormatter
from src.wordcloud_generator import WordCloudGenerator
from src.logger import setup_logger

class NewsEmailScheduler:
    """Scheduler to fetch latest papers, generate word clouds, and send emails."""

    def __init__(self):
        """Initialize the NewsEmailScheduler instance."""
        setup_logger()
        self.fetcher = PaperFetcher()
        self.email_sender = EmailSender(
            username=os.environ['EMAIL_USERNAME'],
            password=os.environ['EMAIL_PASSWORD']
        )
        logging.debug("NewsEmailScheduler instance created.")

    def send_news_email(self):
        """Fetch papers, generate word cloud, and send email."""
        papers = self.fetcher.fetch_latest_papers()
        if papers:
            # Generate word cloud
            wordcloud_path = WordCloudGenerator.generate_wordcloud(papers)
            # Format email content
            body = MarkdownFormatter.format_papers(papers)
            subject = f"Latest ML Papers ({time.strftime('%Y-%m-%d %H:%M')})"
            to_emails = [self.email_sender.username]  # Replace with actual recipients
            # Send email with word cloud attachment
            self.email_sender.send_email(subject, body, to_emails, attachments=[wordcloud_path])
            logging.info("Email sent successfully.")
        else:
            logging.warning("No new papers found; email not sent.")

    def start(self):
        """Start the process."""
        self.send_news_email()

if __name__ == "__main__":
    scheduler = NewsEmailScheduler()
    scheduler.start()