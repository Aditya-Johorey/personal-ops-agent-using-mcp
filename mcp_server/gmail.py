import base64
from email.mime.text import MIMEText

from google_auth import get_service

def send_email(to: str, subject:str, body:str) ->dict:
    """
    Send an email from the user's Gmail account.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.

    Returns:
        A dict with the sent message's id.
    """

    service = get_service("gmail", "v1")

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(
        userId = "me",
        body = {"raw": raw}
    ).execute()

    return {"message_id": sent["id"]}

