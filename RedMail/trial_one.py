from db import Emails, init_db, change_status
from RedMail.email_func import *

from sqlalchemy import text

dummy_pdf_path = "/home/tilaemia/Leather Brands.pdf"

if not os.path.exists(dummy_pdf_path):
    print(f"\n--- WARNING: '{dummy_pdf_path}' not found. Creating a dummy file for testing. ---")
    try:
        with open(dummy_pdf_path, 'w') as f:
            f.write("This is a dummy PDF file for testing attachments.\n")
        print(f"--- '{dummy_pdf_path}' created. ---")
    except Exception as e:
        print(f"--- Could not create dummy PDF: {e}. Please create it manually. ---")

# --- HTML Email Template (example) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A Quick Win for Leather Brands on Instagram</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f7f7f7; font-family: Arial, sans-serif; line-height: 1.6; color: #333333;">

    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: #f7f7f7;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="padding: 20px 30px;">
                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                Hey {recipient_name}! 👋,
                            </p>
                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                Creating content on Instagram shouldn’t feel like guesswork — but for most leather brands, it does.
                            </p>
                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                That’s what we fix. ✨
                            </p>
                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                We recently analyzed hundreds of posts from successful leather businesses on Instagram, and we broke down the patterns behind what actually works.
                            </p>
                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                We found 4 content patterns that are working quietly behind the scenes—yet most businesses miss them.
                            </p>

                            <p style="font-size: 16px; margin: 0 0 20px 0;">
                                We shared our findings in the attached report below:
                            </p>
                            <p style="font-size: 16px; margin: 0;">
                                Thought you might find it helpful 🙂.
                            </p>
                        </td>
                    </tr>
                   
                </table>
            </td>
        </tr>
    </table>

</body>
</html>"""


# Example recipient data
session = init_db('emails')
recipients_data = session.execute(text('''select * from emails where priority = 'Low' and status = 'unsent';''')).fetchall()[:50]


# --- Attachments list ---
# Provide a list of file paths you want to attach for each email.
# For a specific email, you might want different attachments.
# In this example, we'll attach the same dummy PDF to all.
attachments_for_this_email = [dummy_pdf_path]

for recipient in recipients_data:
    recipient_email = recipient[3]
    recipient_name = recipient[2] if recipient[2] else ''
    # recipient_email = recipient['email']
    # recipient_name = recipient['name']


    subject = f"Still guessing what to post? Here's what actually works for leather brands on IG"
    personalized_html = HTML_TEMPLATE.format(
        recipient_name=recipient_name
    )

    if send_single_email(recipient_email, subject, personalized_html, attachment_paths=attachments_for_this_email):
        change_status(session, recipient_email, 'sent')
    else:
        change_status(session, recipient_email, 'error')

    sent_emails = len(session.query(Emails).filter_by(status='sent').all())
    total_emails = len(session.query(Emails).all())
    print(f"{sent_emails}/{total_emails}", end='\r')

    # Optional: Add a delay to avoid hitting SMTP rate limits
    # import time
    # time.sleep(5)