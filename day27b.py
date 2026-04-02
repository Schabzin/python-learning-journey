import re
import pandas as pd

contacts = [
    "Sechaba: 0732239762",
    "Nomvuls: 0611813424",
    "Rorisang: 0635922914",
    "Atlehang: 0611813424"
]
all_contacts = []
for contact in contacts:
    match = re.search(r"(?P<name>\w+):\s(?P<phone>\d{10})", contact)
    if match:
        all_contacts.append({
            "name": match.group("name"),
            "phone": match.group("phone")
        })

df =pd.DataFrame(all_contacts)
print(df)
df.to_csv("contacts_extracted.csv", index=False)