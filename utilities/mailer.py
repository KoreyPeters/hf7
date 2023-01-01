import os

import requests


def send_simple_message(user_email, subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/mail.humanflourishing.online/messages",
        auth=("api", os.environ["MAILGUN_KEY"]),
        data={
            "from": "User Services <service@humanflourishing.online>",
            "to": [user_email],
            "subject": subject,
            "text": text,
        },
    )
