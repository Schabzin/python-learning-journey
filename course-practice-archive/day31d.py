import requests
import logging

url = "https://api.openweathermap.org/data/2.5/weather"
cities = ["Johannesburg", "Cape Town", "Durban", "Sebokeng"]
params = {"app_id": "API KEY"}
API_KEY = "your_real_key_here"
temperatures ={}


try:
    for city in cities:
        params = {"q": city, "appid": "API_KEY","units": "metric"}
        response = requests.get(url, params=params)
        data = response.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        temperatures[city] = temp
        logging.info(f"Retrieved weather for {city}")
        print(f"{city}: {temp}°C | Humidity: {humidity}% | {description}")

    hottest = max(temperatures, key=temperatures.get)
    print(f"Hottest city: {hottest} - {temperatures[hottest]}°C")
    print("SA Weather Report complete!")

except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")