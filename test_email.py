import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

msg = MIMEText("This is a real test email from Separaka.")
msg["Subject"] = "Test Email"
msg["From"] = os.environ.get("EMAIL_ADDRESS")
msg["To"] = "info@separaka.co.za"

with smtplib.SMTP("lon106.truehost.cloud", 587) as server:
    server.starttls()
    server.login(os.environ.get("EMAIL_ADDRESS"), os.environ.get("EMAIL_PASSWORD"))
    server.send_message(msg)

print("Email sent successfully")