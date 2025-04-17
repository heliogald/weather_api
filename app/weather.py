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
    
    
#Fluxo ETL (Extract, Transform, Load)

def transform_weather_data(data):
    """
    Função de transformação para garantir que os dados sejam válidos
    e bem formatados antes de serem armazenados no banco de dados.
    """
    # Exemplo de transformação: garantir que a temperatura seja um número
    temperature = data["temperature"]
    description = data["description"]

    if temperature < -50 or temperature > 60:  # Temperaturas extremamente altas ou baixas
        raise ValueError("Temperatura fora do intervalo esperado!")

    # Você pode adicionar outras validações ou formatações aqui.

    # Retornar os dados transformados
    return {
        "temperature": temperature,
        "description": description
    }
