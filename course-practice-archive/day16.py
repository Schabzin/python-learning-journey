class Business:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def describe(self):
        return f"{self.name} owner {self.owner}"
    
    def get_info(self):
        return f"Business: {self.name} | Owner: {self.owner}"
       
    
    
class Kalikeng(Business):
    def __init__(self, name, owner, gardening):
        super().__init__(name, owner)
        self.gardening = gardening

    def describe(self):

        return f"{self.name} | {self.gardening} gardening | {self.owner}"
    
    def get_info(self):
        return f"Business: {self.name} | Owner: {self.owner} | Services: {self.gardening}"

    
    def get_quote(self,amount):
        vat = amount * 0.15
        total = amount * 1.15
        return f"Amount: R{amount:.2f} | VAT: R{vat:.2f} | Total: R{total:.2f}"
    
class Separaka(Business):
    def __init__(self, name, owner, transport):
        super().__init__(name,owner)
        self.transport = transport

    def describe(self):

        return f"{self.name} | {self.transport} transport | {self.owner}"
    
    def get_info(self):
        return f"Business: {self.name} | Owner: {self.owner} | Services: {self.transport}"
    
    def get_quote(self,amount):
        vat = amount * 0.15
        total = amount * 1.15
        return f"Amount: R{amount:.2f} | VAT: R{vat:.2f} | Total: R{total:.2f}"
    
kalikeng = Kalikeng("Kalikeng", "Sechaba", "Gardening")
print("=" * 40)
print("   KALIKENG TRADING & PROJECTS")
print("=" * 40)
print(kalikeng.get_info())
print(kalikeng.get_quote(5000))

separaka = Separaka("Separaka", "Sechaba", "Transport")
print("=" * 40)
print("   SEPARAKA HOLDINGS (PTY)Ltd")
print("=" * 40)
print(separaka.get_info())
print(separaka.get_quote(3000))

        
        