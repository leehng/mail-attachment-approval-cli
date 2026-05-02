import imaplib
import email
import os
import time
from dotenv import load_dotenv

# load env variables
load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASSWORD_SCANNER")

SAVE_FOLDER = os.getenv("SAVE_FOLDER", "./downloads")
SUBJECT_FILTER = os.getenv("SUBJECT_FILTER", "Request")

os.makedirs(SAVE_FOLDER, exist_ok=True)


def save_attachments(msg):
    for part in msg.walk():

        # skip containers
        if part.get_content_maintype() == "multipart":
            continue

        # only attachments
        if part.get("Content-Disposition") is None:
            continue

        filename = part.get_filename()
        if not filename:
            continue

        path = os.path.join(SAVE_FOLDER, filename)

        with open(path, "wb") as f:
            f.write(part.get_payload(decode=True))

        print(f"saved: {path}")


def process_mail(raw_email):
    msg = email.message_from_bytes(raw_email)

    subject = msg.get("Subject", "")

    # filter subject
    if SUBJECT_FILTER.lower() not in subject.lower():
        return

    print(f"hit: {subject}")
    save_attachments(msg)


def check_inbox(mail):
    mail.select("INBOX")

    _, data = mail.uid("search", None, "UNSEEN")

    if not data or not data[0]:
        return

    for uid in data[0].split():
        _, msg_data = mail.uid("fetch", uid, "(RFC822)")

        if not msg_data or not msg_data[0]:
            continue

        raw_email = msg_data[0][1]
        process_mail(raw_email)


def loop():
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL, PASSWORD)

            print("running...")

            while True:
                check_inbox(mail)
                time.sleep(5)

        except Exception as e:
            print("reconnect:", e)
            time.sleep(5)


if __name__ == "__main__":
    loop()
