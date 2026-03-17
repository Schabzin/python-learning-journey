# Question 1
name = "Sechaba"
age = 43
city ="Sebokeng"
print(f"My name is {name}, I am {age}")

# Question 2
number = int(input("Enter a number:"))
if number > 100:
    print("Big number!")
elif number >=50:
    print("Medium number!")
else:
    print("Small number!")

# Question 3
for i in range(1, 21):
    if i % 2 == 0:
        print(i)
# Question 4
def multiply(a, b):
    return a * b
print(multiply(3, 4))
print(multiply(10, 5))
print(multiply(7, 8))

# Question 5
kalikeng = {
    "name": "Kalikeng Trading and Projects",
    "location": "Sebokeng",
    "services": "Stationery and Transport",
    "registration": "2010/007041/23"
}
for key, value in kalikeng.items():
    print(f"{key}: {value}")