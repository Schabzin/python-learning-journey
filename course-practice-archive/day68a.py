def count_up(start, end):
    current = start
    while current <= end:
        yield current
        current += 1

counter = count_up(1, 5)
print(next(counter))
print(next(counter))
print(next(counter))

def generate_active_taxis(taxis):
    for taxi in taxis:
        if taxi["status"] == "active":
            yield taxi

squares_gen = (t * t for t in range(1000000))

for num in count_up(1, 5):
    print(num)

taxis = [
    {"plate": "MT64TP GP", "status": "active"},
    {"plate": "FG09KL GP", "status": "inactive"},
    {"plate": "LK65XB GP", "status": "active"},
]

for taxi in generate_active_taxis(taxis):
    print(taxi["plate"])



