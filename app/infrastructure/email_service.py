import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from app.infrastructure.logs_service import LogService

load_dotenv()

class SMTPService:
    """
    Simple SMTP Service for sending emails (text or HTML).
    """

    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        self.logger = LogService(name="SMTPService")

        if not all([self.host, self.port, self.username, self.password]):
            raise ValueError("SMTP environment variables missing.")

    def send_email(self, to_email: str, subject: str, body: str, html: bool = False):
        """
        Sends an email to a recipient.
        Params:
            to_email (str): Recipient email
            subject (str): Email subject
            body (str): Email body
            html (bool): Whether body is HTML or plain text
        """
        try:
            # create message
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html" if html else "plain"))

            # connect to SMTP server
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            self.logger.error(f"[SMTP ERROR] {e}")
            return False
