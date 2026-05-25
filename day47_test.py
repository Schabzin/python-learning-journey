from dotenv import load_dotenv
import os


load_dotenv()

secrete = os.environ.get("SECRET_KEY")
print(secrete)

database = os.environ.get("DATABASE_URL")
print(database)

JWT_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))
print(JWT_HOURS)

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
print(DEBUG)