import csv

while True:
    print("\n--- Kalikeng Client Register ---")
    print("1. Add new client")
    print("2. View all clients")
    print("3. Exit")

    choice = input("Choose an option:")
    if choice == "1":
        name = input("Enter name: ")
        phone = input("Enter phone: ")
        amount = input("Enter amount: ")
        with open("clients.csv" , "a" , newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, phone , amount])
        print("Client saved!")
   
    elif choice == "3":
       print("Goodbye!")
       break

    
    elif choice == "2":
        
        with open("clients.csv" , "r" ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(f"Client: {row['Name']} | Amount:R{row['Amount']} | ")

    