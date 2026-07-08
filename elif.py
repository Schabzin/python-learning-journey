def describe_km_status(current_km, next_service_km):
    km_remaining = next_service_km - current_km
    if km_remaining <= 0:
        return "Overdue for service"
    elif km_remaining <= 500:
        return "Service due soon"
    else:
        return "Service not due yet"