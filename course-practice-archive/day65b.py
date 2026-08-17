def process_owner_report(owner_name, taxis):
    def calculate_total(field):
        return sum(taxi[field] for taxi in taxis)
    
    total_trips = calculate_total("trips_today")
    total_collected = calculate_total("collected")

    return {
        "owner": owner_name,
        "total_trips": total_trips,
        "total_collected": total_collected
    }

taxis = [
    {"plate": "MT64TP GP", "trips_today": 3, "collected": 300},
    {"plate": "FGO9KL GP", "trips_today": 1, "collected": 150},
    {"plate": "LK65XB GP", "trips_today": 2, "collected": 200},
]
print(process_owner_report("Chahane", taxis))

