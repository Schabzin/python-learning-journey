import jwt
import datetime

SECRET_KEY = "kalikeng_secret_2026"

def create_token(username, role):
    payload = {
        "user": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
token = create_token("sechaba", "admin")
print("Token:", token)

payload = verify_token(token)
print("Payload:", payload)

fake = verify_token("thisisafaketoken")
print("Fake token result:", fake)