import re

phones = ["0732239762", "12345", "0611813424", "073223976X"]
emails = ["sechaba@gmail.com", "notanemail", "info@kalikeng.co.za"]
prices = ["R 1,500.00", "R 3 200.50", "R750.00 (VAT incl.)"]

phone_pattern = re.compile(r"^0\d{9}$")
email_pattern = re.compile(r"^[\w.-]+@[\w.-]+\.\w{2,}$")

def validate_email(email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r"^0\d{9}$"
    return re.match(pattern, phone) is not None

for phone in phones:
    if phone_pattern.match(phone):
      print(f"{phone} - Valid")
    else:
        print(f"{phone} - Invalid")
for email in emails:
    if  email_pattern.match(email):
        print(f"{email}- Valid")
    else:
        print(f"{email} - Invalid")

for price in prices:
    clean = re.sub(r"[^\d.]", "", price)
    print(clean)