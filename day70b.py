class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def instance_method(self):
        return f"I am {self.username}"
    
    @staticmethod
    def format_username(username):
        return username.lower().strip()
    
chahane = User("chahane", "owner")
print(chahane.format_username("Chahane"))
print(chahane.instance_method())

class TaxiOwner(User):
    def __init__(self, username, phone=None):
        super().__init__(username, role="owner")
        self.phone = phone

    @classmethod
    def from_registration_form(cls, form_data):
        username = User.format_username(form_data.get("username"))
        phone = form_data.get("phone")
        return cls(username, phone=phone)
    
    @staticmethod
    def validate_phone(phone):
        return phone and len(phone) == 10 and phone.isdigit()

form_data = {"username": "Chahane", "phone": "0726491080"}
owner = TaxiOwner.from_registration_form(form_data)
print(owner.username, owner.phone)

print(TaxiOwner.validate_phone("0726491080"))
print(TaxiOwner.validate_phone("s7410g2309"))