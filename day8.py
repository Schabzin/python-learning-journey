# New Client Recorder

name = input("Enter client name: ")
service = input("Enter service needed:" )

file = open("clients.txt", "a")
file.write(f"Client: {name} - Service: {service}\n")
file.close()

print("Client saved!")
