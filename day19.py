import pandas as pd

data = {
    "Name": ["Sechaba", "Nomvula", "Rorisang", "Atlehang", "Lelo"],
    "Amount": [5000, 2200, 6000, 4000, 3000],
    "Status": ["Paid","Pending","Paid","Pending","Paid"]
        
}

data["Status"] = [s.strip() for s in data["Status"]]
df = pd.DataFrame(data)
print(df)

df["VAT"] = df["Amount"] * 0.15
df["Total"] = df["Amount"] + df["VAT"]
print(df)
print(df["Status"].tolist())

paid = df[df["Status"] == "Paid"]
print(paid)

print(df["Amount"].sum())
big = df[df["Amount"] > 3000]
print(big)
print(df["Amount"].mean())

df.to_csv("kalikeng_report.csv", index=False)
