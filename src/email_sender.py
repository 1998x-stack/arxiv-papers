# src/email_sender.py
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

class EmailSender:
    """Handles sending emails with optional attachments."""

    def __init__(self, username, password):
        """Initialize the EmailSender instance."""
        self.username = username
        self.password = password
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        logging.debug("EmailSender instance created.")

    def send_email(self, subject, body, to_emails, attachments=None):
        """Send an email with the given subject, body, and attachments."""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Attach files if any
        if attachments:
            for filepath in attachments:
                with open(filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            logging.info(f"Email sent to {to_emails}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")