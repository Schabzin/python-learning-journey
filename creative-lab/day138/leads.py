import csv

KNOWN_CODES = {"WEB7", "REC1", "LB1", "LB2", "GBP1", "FB1", "FB2", "FB3", "FB4"}


def read_leads(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tally(leads):
    counts = {code: 0 for code in KNOWN_CODES}
    unknown = []
    for lead in leads:
        code = lead["code"].strip().upper()
        if code not in KNOWN_CODES:
            unknown.append(lead["name"])
            continue
        counts[code] = counts.get(code, 0) + 1
    return counts, unknown


if __name__ == "__main__":
    counts, unknown = tally(read_leads("leads.csv"))
    for code, n in sorted(counts.items(), key=lambda pair: pair[1], reverse=True):
        print(f"{code:<5} {n} leads(s)")
    if unknown:
        print("Check these codes by hand:", ", ".join(unknown))