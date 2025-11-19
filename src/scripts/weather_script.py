import json
import requests
import logging
import os
import sys

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "src", relative_path)


class WeatherScript:
    def __init__(self):
        config_path = get_resource_path("config/api_config.json")
        logging.debug(f"Loading configuration from: {config_path}")

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                self.base_url = f"{config['api_gateway_url']}/weather"
                logging.debug(f"API Gateway URL set to: {self.base_url}")

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. Please ensure the file exists and try again."
            )
        except KeyError:
            raise KeyError(
                "API_GATEWAY_URL not found in configuration. Please check the config file."
            )
        except Exception as e:
            raise Exception(f"An error occurred while loading configuration: {e}")

    def get_weather(self, location):
        params = {"location": location}
        logging.debug(f"Requesting weather data for location: {location}")

        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                logging.debug(f"Weather Data Received: {data}")
                data_icon_code = data["weather"][0]["icon"]
                icon_path = self.get_icon_path(data_icon_code)
                return {
                    "icon_path": icon_path,
                    "weather": data["weather"][0]["main"],
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                }
            elif response.status_code == 404:
                logging.error(f"Location '{location}' not found.")
                return {"error": "Location not found"}
            else:
                logging.error(f"Error fetching weather data: {response.status_code}")
                return {"error": response.status_code}
        except requests.exceptions.RequestException as e:
            logging.error(f"RequestException during API request: {e}")
            return {"error": "Request exception occurred while fetching data"}
        except Exception as e:
            logging.error(f"Exception during API request: {e}")
            return {"error": "Exception occurred while fetching data"}

    def get_icon_path(self, icon_code):
        weather_dir = get_resource_path(os.path.join("assets", "weather"))
        if not os.path.exists(weather_dir):
            os.makedirs(weather_dir)
            logging.debug(f"Weather directory created at path: {weather_dir}")

        icon_path = os.path.join(weather_dir, f"weather_icon_{icon_code}.png")
        logging.debug(f"Icon path: {icon_path}")
        if os.path.exists(icon_path):
            logging.debug(f"Icon already exists at path: {icon_path}")
            return icon_path
        else:
            response = requests.get(
                f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            )
            if response.status_code == 200:
                with open(icon_path, "wb") as icon_file:
                    icon_file.write(response.content)
                logging.debug(f"Icon downloaded and saved at path: {icon_path}")
                return icon_path
            else:
                logging.error(f"Error fetching icon: {response.status_code}")
                return None
