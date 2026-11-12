"""
invoice_maths.py - the money rules for Separaka quotes and invoices.
All amount are whole CENTS (int). Rands are only made at the end, for display.
"""


def check_cents(cents):
    """Refuse anything that is not a whole, non-negative number of cents."""
    if isinstance(cents, bool) or not isinstance(cents, int):
        raise ValueError(f"Amounts must be whole cents (int), got {cents!r}")
    if cents < 0:
        raise ValueError(f"Amounts can't be negative, got {cents}")
    return cents


def rand(cents):
    """175000 -> 'R1,750.00'"""
    check_cents(cents)
    return f"R{cents // 100:,}.{cents % 100:02d}"


def split_deposit(total_cents, percent=50):
    """Deposit first; the BALANCE takes whatever is left, so nothing is lost."""
    check_cents(total_cents)
    deposit = total_cents * percent // 100
    balance = total_cents - deposit
    return deposit, balance


def invoice_total(items):
    """items = [(description, quantity, unit_cents), ...] -> cents"""
    total = 0
    for description, quantity, unit_cents in items:
        check_cents(unit_cents)
        total += quantity * unit_cents
    return total


def invoice_number(n, prefix="SEP-INV"):
    """1 -> 'SEP-INV-0001'"""
    return f"{prefix}-{n:04d}"