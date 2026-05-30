import bcrypt
import sqlite3

password = "kalikeng2026"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

conn = sqlite3.connect("test_day46.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
conn.commit()
conn.close()

def register_user(username, password, role):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect("test_day46.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed, role))
        conn.commit()
        print("Registration successful"), 201
    except sqlite3.IntegrityError:
        print("Username already exists"), 409
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect("test_day46.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if bcrypt.checkpw(password.encode(), user["password"]):
        print("Login successful")
    else:
        print("Invalid credentials")
    conn.close()

register_user("sechaba", "kalikeng2026", "admin")
register_user("thabo", "vaal123", "user")
register_user("sechaba", "kalikeng2026", "admin")
login_user("sechaba", "kalikeng2026")
login_user("sechaba", "wrongpassword")
    

      
