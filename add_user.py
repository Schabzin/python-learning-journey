import sqlite3
import bcrypt

def add_user(username, password, role):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed, role)
    )
    conn.commit()
    conn.close()
    print(f"User {username} added as {role}")

add_user("chahane", "chahane2026", "owner")
add_user("marshall1", "marshall2026", "marshall")