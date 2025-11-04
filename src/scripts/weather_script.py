import requests
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class WeatherScript:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        logging.debug(f"Requesting weather data for city: {city}")
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"Weather Data Received: {data}")
            return {
                "weather": data['weather'][0]['main'],
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],

            }
        elif response.status_code == 404:
            logging.error(f"City '{city}' not found.")
            return {"error": "Location not found"}
        else:
            logging.error(f"Error fetching weather data: {response.status_code}")
            return {"error": response.status_code}