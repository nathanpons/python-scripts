import requests
import logging
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

class WeatherScript:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, location):
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'
        }
        logging.debug(f"Requesting weather data for location: {location}")
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"Weather Data Received: {data}")
            data_icon_code = data['weather'][0]['icon']
            icon_path = self.get_icon_path(data_icon_code)
            return {
                "icon_path": icon_path,
                "weather": data['weather'][0]['main'],
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
            }
        elif response.status_code == 404:
            logging.error(f"Location '{location}' not found.")
            return {"error": "Location not found"}
        else:
            logging.error(f"Error fetching weather data: {response.status_code}")
            return {"error": response.status_code}
    
    def get_icon_path(self, icon_code):
        icon_path = f"src/assets/weather/weather_icon_{icon_code}.png"
        if os.path.exists(icon_path):
            logging.debug(f"Icon already exists at path: {icon_path}")
            return icon_path
        else:
            response = requests.get(f"http://openweathermap.org/img/wn/{icon_code}@2x.png")
            if response.status_code == 200:
                with open(icon_path, "wb") as icon_file:
                    icon_file.write(response.content)
                logging.debug(f"Icon downloaded and saved at path: {icon_path}")
                return icon_path
            else:
                logging.error(f"Error fetching icon: {response.status_code}")
                return None