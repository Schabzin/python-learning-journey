from functools import wraps

def my_decorator(f):
    def wrapper(*args, **kwargs):
        print("Before the function runs")
        result = f(*args, **kwargs)
        print("After the function runs")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}")

greet("Chahane")

def log_action(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(f"Action: {f.__name__} called")
        result = f(*args, **kwargs)
        print(f"Action: {f.__name__} completed")
        return result
    return decorated

@log_action
def say_hello(name):
    print(f"Hello, {name}")

say_hello("Lehlohonolo")

@log_action
def update_km(taxi_id, km):
    print(f"Updating taxi {taxi_id} to {km}km")

greet("Chahane")
say_hello("Lehlohonolo")
update_km(1, 127000)    
