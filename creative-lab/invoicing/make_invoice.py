"""make_invoice.py - run: python make_invoice.py clients/itumeleng.json"""
import json
import os
import sys
from invoice_pdf import draw_invoice, load_bank
from invoice_maths import invoice_number

if len(sys.argv) != 2:
    sys.exit("Usage: python make_invoice.py clients/<client>.json")

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

number = invoice_number(data["invoice_no"])
out_path = os.path.join("out", f"{number}.pdf")
if os.path.exists(out_path):
    sys.exit(f"{out_path} already exists. Invoice numbers are never reused.")

inv = {
    "number": number,
    "date": data["date"],
    "bill_to": data["bill_to"],
    "items": [tuple(item) for item in data["items"]],
    "deposit_percent": data["deposit_percent"],
}

os.makedirs("out", exist_ok=True)
draw_invoice(out_path, inv, load_bank())
print(f"Saved {out_path} for {data['bill_to'][0]} (quote {data['quote']})")
