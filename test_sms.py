import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_sms(to_number, message):
    api_key = os.environ.get("SMS_API_KEY")
    response = requests.post(
        "https://api.winsms.co.za/api/rest/v1/sms/outgoing/send",
        headers={"AUTHORIZATION": api_key},
        json={
            "message": message,
            "recipients": [{"mobileNumber": 27732239762}]
        }
    )
    return response.json()

result = send_sms("27732239762", "Test SMS from Separaka")
print(result)