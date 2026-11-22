"""make_secret.py - print a new random secret for SECRET_KEY."""
import secrets

key = secrets.token_hex(32)
print(key)
print(len(key), "characters")