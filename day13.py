<<<<<<< HEAD
def get_client_info():
    name = input("Enter name: ")
    service = input("Enter service: ")
    amount = int(input("Amount: "))
    return name, service, amount

def calculate_vat(amount):
    return amount * 0.15

def calculate_total(amount):
    vat = calculate_vat(amount)
    return amount + vat

while True:
    print("\n---Kalikeng Trading & Projects---")
    name, service, amount = get_client_info()
    vat = calculate_vat(amount)
    total = calculate_total(amount)
    print("=" * 40)
    print(f"Client  : {name}")
    print(f"Service : {service}")
    print(("-" * 40))
    print(f"Amount  : R{amount:.2f}")
    print(f"VAT 15% : R{vat:.2f}")
    print("-" * 40)
    print(f"TOTAL   : R{total:.2f}")
    print("-" * 40)
    again = input("Another invoice? (yes/no): ")
    if again.lower() != "yes":
=======
def get_client_info():
    name = input("Enter name: ")
    service = input("Enter service: ")
    amount = int(input("Amount: "))
    return name, service, amount

def calculate_vat(amount):
    return amount * 0.15

def calculate_total(amount):
    vat = calculate_vat(amount)
    return amount + vat

while True:
    print("\n---Kalikeng Trading & Projects---")
    name, service, amount = get_client_info()
    vat = calculate_vat(amount)
    total = calculate_total(amount)
    print("=" * 40)
    print(f"Client  : {name}")
    print(f"Service : {service}")
    print(("-" * 40))
    print(f"Amount  : R{amount:.2f}")
    print(f"VAT 15% : R{vat:.2f}")
    print("-" * 40)
    print(f"TOTAL   : R{total:.2f}")
    print("-" * 40)
    again = input("Another invoice? (yes/no): ")
    if again.lower() != "yes":
>>>>>>> 483d8b47f697d6c982eaba2cb81310a7568426e5
        break