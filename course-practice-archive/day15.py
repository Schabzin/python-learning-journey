class Client:
    def __init__ (self, name, phone, amount):
        self.name = name
        self.phone = phone
        self.amount = amount

        
    def calculate_vat(self):
        return self.amount * 0.15
    
    def calculate_total(self):
        return self.amount + self.calculate_vat()
    
    def get_invoice(self):
        vat = self.calculate_vat()
        total = self.calculate_total()
        print("=" * 40)
        print(f"Client  : {self.name}")
        print(f"Phone   : {self.phone}")
        print("-" * 40)
        print(f"Amount  : R{self.amount:.2f}")
        print(f"VAT 15% : R{vat:.2f}")
        print("-" * 40)
        print(f"TOTAL   : R{total:.2f}")
        print("=" * 40)

    def get_summary(self):
        return f"Client: {self.name} | Phone: {self.phone} | Amount: R{self.amount:.2f}"

client1 = Client("Sechaba", "0732239762", 3500)
client2 = Client("Atli", "0614561235", 2550)
client3 = Client("Rori", "0631045889", 1200)

client1.get_invoice()
client2.get_invoice()
client3.get_invoice()




        
        
        