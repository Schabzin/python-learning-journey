def make_target_checker(target_amount):
    def check(collected):
        if collected >= target_amount:
            return f"Target met - R{collected} collected"
        remaining = target_amount - collected
        return f"R{remaining} remaining to reach target"
    return check

check_chahane = make_target_checker(750)
check_jake = make_target_checker(900)
check_lehlohonolo = make_target_checker(1000)

print(check_chahane(800))
print(check_chahane(400))
print(check_jake(400))
print(check_lehlohonolo(1000))

def make_km_checker(km_service):
    def check(current):
        if current >= km_service:
            return f"Service overdue - currently at {current}km"
        remaining = km_service - current
        return f"{remaining}km until next service"
    return check

check_chahane = make_km_checker(140000)
check_jake = make_km_checker(111000)

print(check_chahane(150000))
print(check_jake(105000))