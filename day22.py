from datetime import datetime, date, timedelta

invoices = [
    {"Client": "Lebohang", "Amount": "5000", "Invoice Date": "02/01/2026"},
    {"Client": "Nomvula", "Amount": "3000", "Invoice Date": "15/02/2026"},
    {"Client": "Rori", "Amount": "2500", "Invoice Date": "26/01/2026"},
    {"Client": "Atli", "Amount": "4200", "Invoice Date": "01/03/2026"},
    {"Client": "Thabo", "Amount":"1900", "Invoice Date": "10/02/2026"},
]

today = date.today()

for invoice in invoices:
    invoice_date = datetime.strptime(invoice["Invoice Date"], "%d/%m/%Y")

    due_date = invoice_date.date() + timedelta(days=30)
    days_old = (today - invoice_date.date()).days
    status = "OVERDUE" if due_date < today else "ON TIME"

    print(f"Client      : {invoice['Client']}")
    print(f"Amount      : R{float(invoice['Amount']):.2f}")
    print(f"Invoice Date: {invoice_date.strftime('%d/%m/%Y')}")
    print(f"Due Date    : {due_date.strftime('%d/%m/%Y')}")
    print(f"Days Old    : {days_old} days")
    print(f"Status      : {status}")
    print("-" * 40)



