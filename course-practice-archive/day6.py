<<<<<<< HEAD
# Creating a Dictionarry
person = {
    "name": "Sechaba",
    "age": 43,
    "city": "Sebokeng",
    "business": "Kalikeng Trading"
}
# Access values
print(person["name"])
print(person["city"])

# Print everything
print(person)

# Add a new key
person["phone"] = "073 223 9762"
print(person)

# Update a value
person["city"] = "Johannesburg"
print(person["city"])

# Loop through dictionary
print("\nAll my info:")
for key, value in person.items():
    print(f"{key}: {value}")
=======
# Creating a Dictionarry
person = {
    "name": "Sechaba",
    "age": 43,
    "city": "Sebokeng",
    "business": "Kalikeng Trading"
}
# Access values
print(person["name"])
print(person["city"])

# Print everything
print(person)

# Add a new key
person["phone"] = "073 223 9762"
print(person)

# Update a value
person["city"] = "Johannesburg"
print(person["city"])

# Loop through dictionary
print("\nAll my info:")
for key, value in person.items():
    print(f"{key}: {value}")
>>>>>>> 483d8b47f697d6c982eaba2cb81310a7568426e5
    