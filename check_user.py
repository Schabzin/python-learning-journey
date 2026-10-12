"""
check_user.py
Read-only: shows whether a user exists, exactly how the name is stored,
and what shape the stored password has. Never prints the password or its hash.
Usage: python check_user.py sechaba_admin
"""
import sqlite3
import sys

from utils import get_db_path

wanted = sys.argv[1].lower().strip()

path = get_db_path()
conn = sqlite3.connect(path)
try:
    rows = conn.execute(
        "SELECT id, username, role, active, password FROM users "
        "WHERE LOWER(TRIM(username)) = ?",
        (wanted,),
    ).fetchall()
finally:
    conn.close()

print("Database:", path)
print("Matches:", len(rows))
for user_id, username, role, active, password in rows:
    size = len(password) if password else 0
    print(f"  id={user_id} username={username!r} role={role} active={active} "
          f"password stored as {type(password).__name__}, length {size}")

