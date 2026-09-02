from build_textbooks_db import find_pricelist_sheet

excel_path = "C:/Users/Sechaba/Documents/business/price list 2026-2027/Macmillan SA Retail Price List 2026-2027.xlsx"

detected_sheet = find_pricelist_sheet(excel_path)
print(f"Detected sheet: {detected_sheet!r}")