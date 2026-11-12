"""make_example.py - a FAKE invoice to test the layout. Safe to push: no real data."""
import os
from invoice_pdf import draw_invoice, load_bank
from invoice_maths import invoice_number

os.makedirs("out", exist_ok=True)

example = {
    "number": invoice_number(999),
    "date": "12 November 2026",
    "bill_to": ["Test Crèche (EXAMPLE)", "1 Example Street, Sebokeng"],
    "items": [("Starter website, founding price", 1, 350000)],
    "deposit_percent": 50,
}

draw_invoice("out/example.pdf", example, load_bank("bank.example.json"))
print("Saved out/example.pdf")