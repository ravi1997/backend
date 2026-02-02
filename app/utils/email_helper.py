
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email_notification(to_emails: list[str], subject: str, body_html: str) -> bool:
    """
    Sends an email to the specified list of recipients.
    
    Args:
        to_emails (list): List of email addresses.
        subject (str): Email subject.
        body_html (str): Email body (HTML).
        
    Returns:
        bool: True if successful (or mocked), False otherwise.
    """
    if not to_emails:
        return False

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM", "noreply@form-system.com")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password]):
        current_app.logger.warning(
            f"SMTP configuration missing. Mocking email send to {to_emails}. Subject: {subject}"
        )
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_from, to_emails, text)
        server.quit()
        
        current_app.logger.info(f"Email sent successfully to {to_emails}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_emails}: {str(e)}")
        return False
