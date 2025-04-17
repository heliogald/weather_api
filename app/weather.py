import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def fetch_weather(city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }
