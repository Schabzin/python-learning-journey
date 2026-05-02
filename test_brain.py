import os
files = os.listdir("price_lists")
for f in files:
    if "Brain" in f or "brain" in f:
        print(repr(f))

