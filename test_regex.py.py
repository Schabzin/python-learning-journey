import re
import pandas as pd

clients = [
    "Sechaba | 0732239762 | R5000",
    "Nomvula | 12345 | R3200",
    "Rorisang | 0635922914 | R4500",
    "Atlehang | 0611813424 | R2200x"
]

numbers = re.findall(r"\d{10}", "".join(clients))
print(numbers)

phone_pattern = re.compile(r"^0\d{9}$")
for phone in numbers:
    if phone_pattern.match(phone):
        print(f"{phone} - Valid")
    else:
        print(f"{phone} - Invalid")

all_clients = []
for client in clients:
    match = re.search(r"(?P<name>\w+)\s*\|\s*(?P<phone>[\d]+)\s*\|\s*R(?P<price>[\d]+)", client)
    if match:
        all_clients.append({
            "name": match.group("name"),
            "phone": match.group("phone"),
            "price": match.group("price")
        })

df = pd.DataFrame(all_clients)
print(df)
              
        