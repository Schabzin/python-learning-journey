import requests
import logging
import pandas as pd
import sqlite3

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers =[
        logging.FileHandler("kalikeng_api.log"),
    ]
)
fx_url = f"https://openexchangerates.org/api/latest.json"
fx_params = {"app_id": "YOUR_REAL_KEY"}
fx_response = requests.get(fx_url, params=fx_params)
fx_data = fx_response.json()
zar_rate = fx_data["rates"]["ZAR"]
logging.info("Exchange rate retrieved")

weather_url = "https://api.openweathermap.org/data/2.5/weather"
weather_params = {"q": "Sebokeng", "appid": "YOUR_WEARTHER_KEY", "units": "metric"}
weather_response = requests.get(weather_url, params=weather_params)
weather_data = weather_response.json()
temp = weather_data["main"]["temp"]
description = weather_data["weather"][0]["description"]
logging.info("Weather retrieved")

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)

unpaid_df = df[df["status"] == "Unpaid"]
total_zar = unpaid_df["amount"].sum()
total_usd = total_zar / zar_rate
zar_rate = fx_data["rates"]["ZAR"]

with open("kalikeng_intelligence_report.txt", "w") as f:
    f.write(f"Weather: {temp}°C\n")
    f.write(f"ZAR/USD: {zar_rate}\n")
    f.write(f"Total debt ZAR: R{total_zar:.2f}\n")
    f.write(f"Total debt USD: ${total_usd:.2f}\n")

print(f"Current weather in Sebokeng: {temp}°C - {description}")
print(f"Today's ZAR/USD rate: {zar_rate}")
print(f"Total clients: {len(df)}")
print(f"Total outstanding debt ZAR: R{total_zar:.2f}")
print(f"Total outstanding debt USD: ${total_usd:.2f}")
logging.info(f"Major step, {len}")
print("Kalikeng Intelligence Report complete!")