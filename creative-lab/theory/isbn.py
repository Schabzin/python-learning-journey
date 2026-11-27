def clean_isbn(raw):
    digits = ""
    for ch in raw:
        if ch.isdigit():
            digits += ch
    return digits

def checksum_ok(isbn):
    total = 0
    for i, ch in enumerate(isbn):
        weight = 1 if i % 2 == 0 else 3
        total += int(ch) * weight
    return total % 10 == 0

def isbn_problem(raw):
    isbn = clean_isbn(raw)
    if len(isbn) != 13:
        return f"needs 13 digits, got {len(isbn)}"
    if not isbn.startswith(("978", "979")):
        return "an ISBN-13 starts with 978 or 979"
    if not checksum_ok(isbn):
        return "check digit does not match - a digit was mistyped"
    return None

def single_typos(isbn):
    caught = 0
    total = 0
    for pos in range(len(isbn)):
        for d in "0123456789":
            if d == isbn[pos]:
                continue
            typo = isbn[:pos] + d + isbn[pos + 1:]
            total += 1
            if not checksum_ok(typo):
                caught += 1
    return caught, total

def swapped_neighbours(isbn):
    caught = 0
    total = 0
    for pos in range(len(isbn) - 1):
        a = isbn[pos]
        b = isbn[pos + 1]
        if a == b:
            continue
        swapped = isbn[:pos] + b + a + isbn[pos + 2:]
        total += 1
        if not checksum_ok(swapped):
            caught += 1
    return caught, total

if __name__ == "__main__":
    for raw in ["978-0-19-852663-6", "978-0-19-852663-7", "978-0-19-85266", "123-0-19-852663-6"]:
        print(raw, "->", isbn_problem(raw) or "OK")
    for book in ["978-0-19-852663-6", "978-0-306-40615-7"]:
        isbn = clean_isbn(book)
        print(isbn, "typos caught:", single_typos(isbn), "swaps caught:", swapped_neighbours(isbn))