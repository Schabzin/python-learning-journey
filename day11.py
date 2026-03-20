<<<<<<< HEAD
import random
from datetime import datetime

quotes = [
    "Work hard in silence, let success make the noise.",
    "Every expert was once a beginner.",
    "Build something today.",
    "Discipline beats motivation every time.",
    "Small steps daily lead to big results."
]

while True:
    print("\n--- Kalikeng Business Toolkit ---")
    print("1. Quote of the day")
    print("2. Today's date and time")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        print(random.choice(quotes))
    elif choice == "2":
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid option. Choose 1, 2 or 3.")
=======
import random
from datetime import datetime

quotes = [
    "Work hard in silence, let success make the noise.",
    "Every expert was once a beginner.",
    "Build something today.",
    "Discipline beats motivation every time.",
    "Small steps daily lead to big results."
]

while True:
    print("\n--- Kalikeng Business Toolkit ---")
    print("1. Quote of the day")
    print("2. Today's date and time")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        print(random.choice(quotes))
    elif choice == "2":
        now = datetime.now()
        print(now.strftime("%d/%m/%Y %H:%M:%S"))
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid option. Choose 1, 2 or 3.")
>>>>>>> 483d8b47f697d6c982eaba2cb81310a7568426e5
        