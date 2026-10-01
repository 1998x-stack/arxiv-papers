# src/email_sender.py
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
from typing import List, Optional

class EmailSender:
     """Handles sending emails with optional attachments."""

     def __init__(self, username: str, password: str):
         """Initialize the EmailSender instance."""
         self.username = username
         self.password = password
         self.smtp_server = 'smtp.gmail.com'
         self.smtp_port = 587
         logging.debug("EmailSender instance created.")

     def send_email(self, subject: str, body: str, to_emails: List[str], attachments: Optional[List[str]] = None):
         """Send an email with the given subject, body, and attachments."""
         msg = MIMEMultipart()
         msg['From'] = self.username
         msg['To'] = ', '.join(to_emails)
         msg['Subject'] = subject
         msg.attach(MIMEText(body, 'html'))

         # Attach files if any
         if attachments:
             for filepath in attachments:
                 if os.path.isfile(filepath):  # Only attach if file exists
                     with open(filepath, 'rb') as f:
                         part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
                     part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                     msg.attach(part)
                 else:
                     logging.warning(f"Attachment file not found: {filepath}")

         try:
             with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                 server.starttls()
                 server.login(self.username, self.password)
                 server.send_message(msg)
             logging.info(f"Email sent successfully to {to_emails}")
         except smtplib.SMTPAuthenticationError:
             logging.error("SMTP Authentication failed. Check your username and password.")
             raise
         except smtplib.SMTPException as e:
             logging.error(f"SMTP error occurred while sending email: {e}")
             raise
         except Exception as e:
             logging.error(f"Unexpected error while sending email: {e}")
             raise