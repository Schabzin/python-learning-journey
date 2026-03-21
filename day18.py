
clients = [
         {"name":    "SECHABA",  "amount":  5000},
         {"name":    "NOMVULA",  "amount":   6000},
         {"name":    "RORISANG", "amount":   3000},
         {"name":    "ATLEHANG", "amount":   4000},
         {"name":    "LELO", "amount":   2200},
    ]
names_upper = [c["name"].upper() for c in clients]
print(names_upper)
sorted_clients = sorted(clients, key=lambda c: c["amount"])
for client in sorted_clients:
        print(f"{client['name']:<12} : R{client['amount']:>8.2f}") 
amounts = [c["amount"]for c in clients]
big_amounts = list(filter(lambda x: x > 3000, amounts))

total = sum([c["amount"] for c in clients])
print(big_amounts)

amount = [2200, 3000,   4000,   5000,   6000]
with_vat = list(map(lambda x: round(x * 1.15, 2), amounts))
print(with_vat)
print(f"Total: R{total:.2f}")