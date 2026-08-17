class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def can_access(self, required_role):
        return self.role == required_role
    
    def __repr__(self):
        return f"User({self.username}, {self.role})"
    
class Owner(User):
    def __init__(self, username):
        super().__init__(username, role="owner")

    def get_dashboard_title(self):
        return f"Fleet Dashboard - {self.username}"
    
class Marshall(User):
    def __init__(self, username):
        super().__init__(username, role="marshall")

    def get_dashboard_title(self):
        return f"Marshall Station - {self.username}"
    
    
class Driver(User):
    def __init__(self, username, driver_routes):
        super().__init__(username, role="driver")
        self.driver_routes = driver_routes

    def can_access(self, required_role):
        return required_role == "driver"
    
    def __repr__(self):
        return f"Driver({self.username}, routes={self.driver_routes})"

chahane = Owner("chahane")
marshall1 = Marshall("marshall1")
madela = Driver("madela", "MT64TP GP")

print(chahane)
print(marshall1)
print(madela)

print(chahane.can_access("owner"))
print(chahane.can_access("marshall"))
print(madela.can_access("driver"))
print(madela.can_access("owner"))