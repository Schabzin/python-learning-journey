class Fleet:
    def __init__(self, owner_name, taxis):
        self.owner_name = owner_name
        self.taxis = taxis

    def __len__(self):
        return len(self.taxis)
    
    def __iter__(self):
        return iter(self.taxis)
    
    def __contains__(self, plate):
        return any(t["plate"] == plate for t in self.taxis)
    
    def __repr__(self):
        return f"Fleet({self.owner_name}, {len(self.taxis)} taxis)"
    
    def active_taxis(self):
        for taxi in self.taxis:
            if taxi["status"] == "active":
                yield taxi

    def daily_summary(self):
        yield f"=== {self.owner_name}'s Fleet Summary ==="
        for taxi in self.active_taxis():
            yield f"  {taxi['plate']} - active"
        yield f"Total active: {sum(1 for _ in self.active_taxis())}"

chahane_fleet = Fleet("Chahane", [
    {"plate": "MT64TP GP", "status": "active"},
    {"plate": "FG09KL GP", "status": "active"},
    {"plate": "LK65XB GP", "status": "inactive"}
])

print(len(chahane_fleet))
print("MT64TP GP" in chahane_fleet)
print("XX99XX GP" in chahane_fleet)

for taxi in chahane_fleet:
    print(taxi["plate"])

for line in chahane_fleet.daily_summary():
    print(line)