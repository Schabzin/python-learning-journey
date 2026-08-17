import re

contacts = [
    {"name": "Sechaba", "email": "sechaba@gmail.com", "phone": "0732239762"},
    {"name": "Thabo", "email": "thabo.gmail.com", "phone": "0821456983"},
    {"name": "Lerato", "email": "lerato@yahoo.com", "phone": "1234567890"},
    {"name": "Mpho", "email": "mpo@", "phone": "0711234567"},
    {"name": "Kagiso", "email": "kagiso@outlook.com", "phone": "0693456781"},
]

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r"^0\d{9}$"
    return re.match(pattern, phone) is not None

valid_email_count = 0
valid_phone_count = 0

print(f"{'Name':<10} | {'Email':<25} | {'Phone':<15}")
print("-" * 55)

for contact in contacts:
    email_valid = validate_email(contact["email"])
    phone_valid = validate_phone(contact["phone"])

    email_symbol = "✔" if email_valid else "X"
    phone_symbol = "✔" if phone_valid else "X"

    if email_valid:
        valid_email_count += 1
    if phone_valid:
        valid_phone_count += 1

    print(f"{contact['name']:<10} | {contact['email']:<25} {email_symbol} | {contact['phone']} {phone_symbol}")

    print("-" * 55)
    print(f"Valid emails: {valid_email_count}/5")
    print(f"Valid phones: {valid_phone_count}/5")