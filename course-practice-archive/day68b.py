taxis = [
    {"plate": "MT64TP GP", "driver_name": "Chahane", "status": "active", "collected": 800, "target": 750},
    {"plate": "FG09KL GP", "driver_name": "Madela", "status": "inactive", "collected": 200, "target": 750},
    {"plate": "LK65XB GP", "driver_name": "Tsietsi", "status": "active", "collected": 600, "target": 750},
]

def generate_owner_summary(owner_name, taxis):
    """Yields a summary line per taxi - for a report or dashboard"""
    for taxi in taxis:
        status = "✓" if taxi["collected"] >= taxi["target"] else "✗"
        yield f"{taxi['plate']} | {taxi['driver_name']} | R{taxi['collected']}/R{taxi['target']} {status}"

for line in generate_owner_summary("Chahane", taxis):
    print(line)

def trip_id_generator(start=1):
    """Generates unique trip IDs forever"""
    current = start
    while True:
        yield f"TRIP-{current:04d}"
        current += 1

id_gen = trip_id_generator()
print(next(id_gen))
print(next(id_gen))
print(next(id_gen))
print(next(id_gen))
print(next(id_gen))

def filter_by_status(taxis, status):
    """Yields only status taxis"""
    for taxi in taxis:
        if taxi["status"] == status:
            yield taxi

def get_plate(taxis):
    for taxi in taxis:
        yield taxi["plate"]

active = filter_by_status(taxis, "active")
plates = get_plate(active)
for plate in plates:
    print(plate)