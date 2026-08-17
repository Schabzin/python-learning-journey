import sqlite3

conn = sqlite3.connect("kalikeng.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        amount REAL,
        status TEXT
    )
""")
                  
while True:
    print("--- Kalikeng Client Database ---")
    print("1. Add new client")
    print("2. View all clients")
    print("3. View paid clients only")
    print("4. Update client status")
    print("5. Exit")
    choice = input("Choose an option: ")

    if choice == "5":
        conn.close()
        break

    elif choice == "1":
            name = input("Enter client name: ")
            phone = input("Enter phone number: ")
            amount = float(input("Enter amount: "))
            status = input("Enter status (Paid/Unpaid): ")

            cursor.execute("""
                INSERT INTO clients (name, phone, amount, status)
                VALUES (?,?,?,?)
            """, (name, phone, amount, status))
            conn.commit()
            print("Client added successfully!")

    elif choice == "2":
             cursor.execute("SELECT * FROM clients")
             clients = cursor.fetchall()
             for client in clients:
                 print(f"ID: {client[0]} | Name: {client[1]} | Phone: {client[2]} | Amount: R{client[3]} | Status: {client[4]}")
             

    elif choice == "3":
        cursor.execute("SELECT * FROM clients WHERE status = 'Paid'")
        clients = cursor.fetchall()
        for client in clients:
            print(f"Name: {client[1]} | Amount: R{client[3]}")
        

    elif choice == "4":
        name = input("Enter client name to update: ")
        new_status = input("Enter new status (Paid/Unpaid): ")
        cursor.execute("UPDATE clients SET status = ? WHERE name = ?", (new_status, name))
        conn.commit()
        print("Status updated!")
       