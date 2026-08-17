<<<<<<< HEAD
# Day 4 - Challenge
def calculate(a, b, operation):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation  == "multiply":
        return a * b
num1 = int(input("Enter firts number: "))
num2 = int(input("Enter second number: "))
op = input ("Enter operation (add/subtract/miltiply): ")

result = calculate(num1, num2, op)
=======
# Day 4 - Challenge
def calculate(a, b, operation):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation  == "multiply":
        return a * b
num1 = int(input("Enter firts number: "))
num2 = int(input("Enter second number: "))
op = input ("Enter operation (add/subtract/miltiply): ")

result = calculate(num1, num2, op)
>>>>>>> 483d8b47f697d6c982eaba2cb81310a7568426e5
print(f"Result: {result}")