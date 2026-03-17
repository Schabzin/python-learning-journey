# Contact Logger

while True:
    name = input("Enter name (or 'done' to stop):")
    if name.lower() == "done":
        break

    phone = input("Enter phone number: ")

    with open("contacts.txt", "a") as file:
        file.write(f"Name: {name} | Phone: {phone}\n")

    print("Contact saved!\n")

print("--- All Saved Contacts ---")
with open("contacts.txt", "r") as file:
    for line in file:
        print(line.strip())
