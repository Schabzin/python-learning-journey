import os

print(os.getcwd())
files = os.listdir(".")
os.makedirs("kalikeng_reports", exist_ok=True)
py_files = [f for f in files if f.endswith(".py")]
print(py_files)

if os.path.exists("kalikeng_db"):
    print("Database found")
else:
    print("Database not found")

folder = "kalikeng_reports"
filename = "report.csv"
full_path = os.path.join(folder, filename)
print(full_path)

print("OS module complete!")