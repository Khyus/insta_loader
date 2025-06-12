import smtplib
from email.mime.text import MIMEText

# Email content
msg = MIMEText("Hello, this is another test email.")
msg["Subject"] = "another Test"
msg["From"] = "sagelensanalytics@gmail.com"
msg["To"] = "yunusa4success@gmail.com"

# Send using Gmail SMTP
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("sagelensanalytics@gmail.com", "opve oyjs hlvw owae")  # use app password if 2FA is enabled
        server.send_message(msg)
        print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
