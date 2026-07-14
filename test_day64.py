print("FILE IS RUNNING")

def describe_km_status(current_km, next_service_km):
    km_remaining = next_service_km - current_km
    if km_remaining <= 0:
        return "Overdue for service"
    elif km_remaining <= 500:
        return "Service due soon"
    else:
        return "Service not due yet"
    
def get_subscription_status(days_remaining):
    if days_remaining <= 0:
        return "Subscription expired"
    elif days_remaining <= 7:
        return "Subscription expiring soon"
    else:
        return "Subscription active"

def get_target_status(collected, target):
    if collected >= target:
        return "Target met"
    elif collected >= target * 0.75:
        return "Target almost there"
    else:
        return " Below target"
    
print(describe_km_status(145000, 140000))
print(describe_km_status(139600, 140000))
print(describe_km_status(120000, 140000))

print(get_subscription_status(-1))
print(get_subscription_status(5))
print(get_subscription_status(20))

print(get_target_status(800, 750))
print(get_target_status(600, 750))
print(get_target_status(200, 750))

    
