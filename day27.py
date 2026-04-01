import re

text = "Contact Sechaba on 0732239762 or Nomvula on 0611813424 for deliveries"
names = "Sechaba, Nomvula;R0risang; Atlehang"
phones = ["0732239762", "123456", "0611813424", "07322"]

text = "Contact Sechaba on 0732239762 or Nomvula on 0611813424"
clean = re.sub(r"\d", "*", text)
print(clean)

numbers = re.findall(r"\d{10}", text)
print(numbers)

text = "Sechaba,Nomvula,Rorisang,Atlehang"
parts = re.split(r"[,; ]+", text)
print(parts)

phone_pattern = re.compile(r"^0\d{9}$")

phones = ["0732239762", "123456", "0611813424", "07322"]
for phone in phones:
    if phone_pattern.match(phone):
        print(f"{phone} - Valid")
    else:
        print(f"{phone} - Invalid")

    