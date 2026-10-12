"""
reset_password.py
Sets a New password for one user. The password is typed twice, hidden,
and never printed or saved anywhere except as a bcrypt hash.
Usage: python reset_password.py sechaba_admin
"""
import getpass
import sqlite3
import sys

import bcrypt

from utils import get_db_path

MIN_LENGTH = 12

username = sys.argv[1].lower().strip()

first = getpass.getpass("New password: ")
second = getpass.getpass("Type it again: ")
if first != second:
    sys.exit("STOP: the two passwords don't match. Nothing changed.")
if len(first) < MIN_LENGTH:
    sys.exit(f"STOP: use at least {MIN_LENGTH} characters. Nothing changed. ")

hashed = bcrypt.hashpw(first.encode(), bcrypt.gensalt())

conn = sqlite3.connect(get_db_path())
try:
    with conn:
        changed = conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed, username),
        ).rowcount
finally:
    conn.close()

if changed != 1:
    sys.exit(f"STOP: expected to update 1 user, updated {changed}.")
print(f"Password updated for {username}. Log in to confirm.")