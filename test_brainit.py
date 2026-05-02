import pandas as pd

xl = pd.ExcelFile("price_lists/BrainbIT Theory and Dandel10n Delphi Books 2026.xlsx")
print("Sheets:", xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel("price_lists/BrainbIT Theory and Dandel10n Delphi Books 2026.xlsx", sheet_name=sheet, header=None)
    print(f"\nSheet: {sheet} — Shape: {df.shape}")
    if df.shape[0] > 0:
        for i, row in df.iterrows():
            print(f"Row {i}: {list(row)}")
            if i > 5:
                break

import pandas as pd

xl = pd.ExcelFile("price_lists/LUX VERBI PRICE LIST - PRYSLYS 1 APRIL 2025.xlsx")
print("Sheets:", xl.sheet_names)

df = pd.read_excel("price_lists/LUX VERBI PRICE LIST - PRYSLYS 1 APRIL 2025.xlsx", sheet_name=0, header=None)
for i, row in df.iterrows():
    print(f"Row {i}: {list(row)}")
    if i > 15:
        break
    