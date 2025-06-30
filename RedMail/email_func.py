import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase # Import for general attachments
from email import encoders # Import for base64 encoding
import ssl
import csv
import os # Import os for file path operations

# --- Configuration ---
SENDER_EMAIL = "sagelensanalytics@gmail.com"
SENDER_PASSWORD = "opve oyjs hlvw owae" # IMPORTANT: Use an App Password for Gmail/Outlook
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 # or 465 for SSL


# --- Function to send a single email ---
def send_single_email(recipient_email, subject, html_content, attachment_paths=None):
    """
    Sends a single email with HTML content and optional attachments.

    Args:
        recipient_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        html_content (str): The HTML body of the email.
        attachment_paths (list, optional): A list of file paths to attach. Defaults to None.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Plain text version (optional but recommended)
    plain_text_content = "Please view this email in an HTML-compatible email client."
    msg.attach(MIMEText(plain_text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Add attachments
    if attachment_paths:
        for attachment_path in attachment_paths:
            if not os.path.exists(attachment_path):
                print(f"Warning: Attachment file not found: {attachment_path}")
                continue # Skip to the next attachment if file doesn't exist

            try:
                # Open the file in binary mode
                with open(attachment_path, "rb") as attachment_file:
                    # Create a MIMEBase object
                    part = MIMEBase("application", "octet-stream") # Generic binary file
                    part.set_payload(attachment_file.read())

                # Encode the attachment in base64
                encoders.encode_base64(part)

                # Add headers for the attachment
                # filename = os.path.basename(attachment_path) ensures only the file name is used
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )

                # Attach the part to the message
                msg.attach(part)
                #print(f"  Attached: {os.path.basename(attachment_path)}")

            except Exception as e:
                print(f"  Error attaching {attachment_path}: {e}")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context) as smtp: # Use 465 for SSL
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print(f"Email sent successfully to {recipient_email}")
            return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")
        return False


