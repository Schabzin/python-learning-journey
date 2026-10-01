from geofencing import start_trip_from_current_zone

trip_id = start_trip_from_current_zone(taxi_id=1, logged_by=1)
print(f"Trip {trip_id} created.")