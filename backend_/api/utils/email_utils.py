import os
import requests

MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_FROM_EMAIL = os.getenv('MAILGUN_FROM_EMAIL')

def send_email(to_email: str, subject: str, text: str, html: str = None):
    """
    Send an email using Mailgun's sandbox domain.

    Args:
        to_email (str): The recipient's email (must be authorized in the sandbox environment).
        subject (str): The subject of the email.
        text (str): The plain-text version of the email.
        html (str): Optional HTML version of the email.
    """
    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": MAILGUN_FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "text": text,
            "html": html,
        }
    )
    return response.status_code, response.json()