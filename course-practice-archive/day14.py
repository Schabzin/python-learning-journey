<<<<<<< HEAD
def get_client_info():
    name = input("Enter name: ")
    service = input("Enter service: ")
    while True:
        try:
            amount = int(input("Enter amount: "))
            break
        except ValueError:
            print("Number only please!")
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
        break

while True:
    print("\n---Kalikeng Trading & Projects---")
    name, service, amount = get_client_info()
    vat = calculate_vat(amount)
    total = calculate_total(amount)
    try:
        print("=" * 40)
        print(f"Client  : {name}")
        print(f"Service : {service}")
        print("-" * 40)
        print(f"Amount  : R{amount:.2f}")
        print(f"VAT 15% : R{vat:.2f}")
        print("_" * 40)
    except Exception:
        print("Something went wrong printing the invoice.")
    finally:
        print("Thank you for using Kalikeng Trading & Projects")
    again = input("Another invoice? (yes/no): ")
    if again.lower() != "yes":
        break
        



=======
def get_client_info():
    name = input("Enter name: ")
    service = input("Enter service: ")
    while True:
        try:
            amount = int(input("Enter amount: "))
            break
        except ValueError:
            print("Number only please!")
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
        break

while True:
    print("\n---Kalikeng Trading & Projects---")
    name, service, amount = get_client_info()
    vat = calculate_vat(amount)
    total = calculate_total(amount)
    try:
        print("=" * 40)
        print(f"Client  : {name}")
        print(f"Service : {service}")
        print("-" * 40)
        print(f"Amount  : R{amount:.2f}")
        print(f"VAT 15% : R{vat:.2f}")
        print("_" * 40)
    except Exception:
        print("Something went wrong printing the invoice.")
    finally:
        print("Thank you for using Kalikeng Trading & Projects")
    again = input("Another invoice? (yes/no): ")
    if again.lower() != "yes":
        break
        



>>>>>>> 483d8b47f697d6c982eaba2cb81310a7568426e5
