# Shopping list challeng
items = ["milk", "bread", "eggs"]
print(f"Original list: {items}")

# Add an item
items.append("coffee")
print("Item added!")

# Remove a item
items.remove("bread")
print("Item removed!")

# Print final list
print("Your final shopping list:")
for item in items:
    print (f"- {item}")
