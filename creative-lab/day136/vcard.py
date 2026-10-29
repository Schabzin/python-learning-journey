def escape(text):
    """Mark , ; \\ as plain text so the phone doesn't treat them as separators."""
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def make_vcard(name, phone, email=None, company=None, website=None):
    name = name.strip()
    if name == "":
        raise ValueError("A contact needs a name.")
    parts = name.split(" ", 1)
    first = parts[0]
    last = parts[1] if len(parts) == 2 else ""

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape(last)};{escape(first)};;;",
        f"FN:{escape(name)}",
        f"TEL;TYPE=CELL:{phone}",
    ]
    if email:
        lines.append(f"EMAIL;TYPE=WORK:{email}")
    if company:
        lines.append(f"ORG:{escape(company)}")
    if website:
        lines.append(f"URL:{website}")
    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def save_vcard(text, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


if __name__ == "__main__":
    card = make_vcard("Sechaba Mofokeng", "+27732239762",
                      email="info@separaka.co.za",
                      company="Separaka Holdings (Pty) Ltd",
                      website="https://separaka.co.za")
    save_vcard(card, "sechaba.vcf")
    print(card)