import os
import smtplib
from email.message import EmailMessage
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Send response email back to sender
def response(receiver_mail, subject):
    # Get credentials from environment variables
    email = os.getenv("EMAIL_USER")
    key = os.getenv("EMAIL_PASS")

    # Static response message (can be extended later)
    message = "We accept the offer"

    # Build email
    text = EmailMessage()
    text["Subject"] = subject
    text["From"] = email
    text["To"] = receiver_mail
    text.set_content(message)

    # Connect to SMTP server (Gmail)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        # Login and send email
        server.login(email, key)
        server.send_message(text)
    finally:
        # Always close connection
        server.quit()


def sort_out():
    path_base = "/home/user/"                   # Base directory
    file_list = os.listdir(f"{path_base}new")   # Files waiting for review

    if len(file_list) == 0:
        print("no new files found!")

    # Iterate through all new files
    for fn_index in range(len(file_list)):
        path = f"{path_base}new/{file_list[fn_index]}"

        # Read file: first line = receiver mail, rest = content
        with open(path, "r", encoding="utf-8-sig") as file:
            receiver_mail = file.readline().strip()
            f_content = file.read()

        # Show info in CLI
        print(f"receiver is: {receiver_mail}")
        print(f_content)
        print("------------------------------------------------")

        # Ask user for decision
        mv_choice = input("Do you want to accept? [Y/n] > ").strip().lower()

        # Accept cases
        if mv_choice in ["y", "yes", "ja"]:
            print("moving your file...")
            os.rename(
                path,
                f"{path_base}accept/{file_list[fn_index]}"
            )
            response(receiver_mail, "Response")
            print(f"DEBUG: {receiver_mail} ({len(receiver_mail)})")

        # Decline cases (now also supports "nein")
        elif mv_choice in ["n", "no", "nein"]:
            print("moving your file...")
            os.rename(
                path,
                f"{path_base}decline/{file_list[fn_index]}"
            )
            response(receiver_mail, "Question Response")

        # Invalid input
        else:
            print("Invalid response!")


# Main loop: continuously check for new files
while True:
    sort_out()
    time.sleep(10)
