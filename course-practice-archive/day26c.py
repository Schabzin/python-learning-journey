import pandas as pd
tables = pd.read_html("test_table.html")
print(f"Ttables found: {len(tables)}")
df = tables[0]
print(df)
df.to_csv("world_population.csv", index=False)
print("Done!")