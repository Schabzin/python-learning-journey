def fmt_rand(amount):
    """Money the way a statement shows it: R6,420.00. None (no deposit) shows R0.00."""
    if amount is None:
        return "R0.00"
    if amount < 0:
        return f"-R{-amount:,.2f}"
    return f"R{amount:,.2f}"
        