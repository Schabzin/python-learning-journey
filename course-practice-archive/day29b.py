import json
import pandas as pd

clients = [
    {"name": "Sechaba", "phone": "0732239762", "amount": 5000, "status": "Unpaid"},
    {"name": "Nomvula", "phone": "0611813424", "amount": 3200, "status": "Paid"},
    {"name": "Rorisang", "phone": "0635922914", "amount": 4500, "status": "Unpaid"},
    {"name": "Atlehang", "phone": "0611813424", "amount": 4200, "status": "Paid"}
]

with open("kalikeng_clients.json", "w") as f:
    json.dump(clients,f, indent=4)
print("JSON saved!")

with open("kalikeng_clients.json", "r") as f:
    data = json.load(f)
print(data)
for client in data:
    print(f"{client['name']} - R{client['amount']}")

df = pd.DataFrame(data)
print(df)
print("JSON complete!")