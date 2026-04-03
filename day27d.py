import pandas as pd

data = {
    "name": ["Sechaba", "Nomvula", "Rorisang", "Atlehang"],
    "phone": ["0732239762", "12345", "0635922914", "0611813424"],
    "price": ["R 5000.00", "R 3,200.50", "R1500", "R 4,200.00"]
}

df = pd.DataFrame(data)

df["phone_valid"] = df["phone"].str.match(r"^0\d{9}$")
df["clean_price"] = df["price"].str.replace(r"[^\d.]","", regex=True)
df["extracted"] = df["phone"].str.extract(r"(\d{3})")

print(df)
df.to_csv("kalikeng_cleaned.csv", index=False)