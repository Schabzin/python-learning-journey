import re

clients = [
    ("Sechaba", "0732239762", 5000, "Paid"),
    ("Nomvula", "12345", 3000, "Unpaid"),
    ("Rorisang", "0635922914", -500, "Paid"),
    ("Atlehang", "0611813424", 4000, "Unknown")
]

class InvalidAmountError(Exception):
    pass

def add_client(name, amount):
    if amount < 0:
        raise InvalidAmountError(f"Amount cannot be negative: {amount}")
    print(f"Client {name} added with amount R{amount}")

    try:
        add_client("Rorisang", -500)
    except InvalidAmountError as e:
        print(f"Business rule violation: {e}")

class InvalidPhoneError(Exception):
    pass

def validate_phone(phone):
    pattern = r"^0\d{9}$"
    if not re.match(pattern, phone):
        raise InvalidPhoneError(f"Invalid phone number: {phone}")
    return True

try:
    validate_phone("12345")
except InvalidPhoneError as e:
    print(f"Validation failed: {e}")

class InvalidStatusError(Exception):
    pass

def validate_status(status):
    if status not in ["Paid", "Unpaid"]:
        raise InvalidStatusError(f"Invalid status: {status}")
    return True

try:
    validate_status("Unknown")
except InvalidStatusError as e:
    print(f"Validation failed: {e}")

def validate_client(name, phone, amount, status):
    if amount < 0:
        raise InvalidAmountError(f"Amount cannot be negative: {amount}")
    validate_phone(phone)
    validate_status(status)
    print(f"Client {name} is valid")

for client in clients:
    try:
        validate_client(client[0], client[1], client[2], client[3])
    except (InvalidAmountError, InvalidPhoneError, InvalidStatusError) as e:
        print(f"Error for {client[0]}: {e}")
    
