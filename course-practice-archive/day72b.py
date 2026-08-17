import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_API_KEY = os.environ.get("TEST_API_KEY")

def send_sms(phone, message):
    api_key = os.environ.get("TEST_API_KEY")
    try:
        response = requests.post(
            "http://api.smsmessenger.co.za/send",
            data={"to": phone, "message": message, "api_key": api_key},
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.Timeout:
        print("SMS provider took too long to respond")
        return False
    except requests.exceptions.RequestException as e:
        print(f"SMS failed: {e}")
        return False
    
def build_target_alert(taxi):
    if taxi["collected"] < taxi["target"]:
        shortfall = taxi["target"] - taxi["collected"]
        return f"{taxi['plate']}: R{shortfall} short of today's R{taxi['target']} target"
    return None
    

taxis = [
    {"plate": "MT64TP GP", "message": "Target Met", "collected": 900, "target": 900},
    {"plate": "FGO9KL GP", "message": "Target Not Met", "collected": 700, "target": 900},
    {"plate": "LK65XB GP", "message": "Target Below", "collected": 500, "target": 900}
]

for taxi in taxis:
    message = build_target_alert(taxi)
    print(message)
