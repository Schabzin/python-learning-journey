"""binary_tools.py - Theory #4: turning a whole number into binary by hand."""

def to_binary(n):
    """13 -> '1101'. Repeated division by 2; remainders read bottom-up."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError(f"Only whole numbers 0 or more, got {n!r}")
    if n == 0:
        return "0"
    digits = ""
    while n > 0:
        remainder = n % 2
        digits = str(remainder) + digits
        n = n // 2
    return digits
    