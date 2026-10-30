import time

SIZES = [1_000, 10_000, 100_000]
REPEATS = 200


def fake_isbns(n):
    return [f"978-0-{i:07d}" for i in range(n)]


def time_it(search, target):
    start = time.perf_counter()
    for _ in range(REPEATS):
        search(target)
    seconds = time.perf_counter() - start
    return seconds / REPEATS * 1_000_000


for n in SIZES:
    isbns = fake_isbns(n)
    as_list = isbns
    as_dict = {isbn: 150.00 for isbn in isbns}
    missing = "978-9-9999999"

    list_us = time_it(lambda t: t in as_list, missing)
    dict_us = time_it(lambda t: t in as_dict, missing)
    print(f"{n:>7} books | list: {list_us:10.1f} microseconds | dict: {dict_us:5.2f} microseconds")