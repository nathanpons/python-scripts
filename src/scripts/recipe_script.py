import json
import os
import requests
import logging
from PIL import Image
from io import BytesIO

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


class RecipeScript:
    MAXIMIZE_USED_INGREDIENTS = 1
    MINIMIZE_MISSING_INGREDIENTS = 2

    def __init__(self):
        self.ignore_pantry = True  # Whether to ignore typical pantry items, such as water, salt, flour, etc.

        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "api_config.json"
        )
        logging.debug(f"Loading configuration from: {config_path}")

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                self.base_url = f"{config['api_gateway_url']}"
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

    def get_recipes(self, ingredients, number=1):
        params = {
            "ingredients": ingredients,
            "number": number,
            "ignorePantry": str(self.ignore_pantry).lower(),
            "ranking": self.MAXIMIZE_USED_INGREDIENTS,
        }
        try:
            response = requests.get(f"{self.base_url}/recipe", params=params)
            if response.status_code == 200:
                data = response.json()
                logging.debug(f"Recipes found: {data}")
                if data:
                    return data
                else:
                    return json.dumps({"error": "No recipes found."})
            else:
                response.raise_for_status()
                logging.error(f"Error finding recipes: {response.status_code}")
        except Exception as e:
            logging.error(f"Exception occurred while finding recipes: {e}")
            return json.dumps({"error": "Error finding recipes."})

    def get_recipe_image(self, image_url):
        if image_url:

            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = BytesIO(response.content)
                pil_image = Image.open(image_data)
                return pil_image
            except Exception as e:
                logging.error(f"Error fetching recipe image: {e}")
                return json.dumps({"error": "Error fetching recipe image."})
        else:
            logging.warning("No image URL provided for recipe.")
            return json.dumps({"error": "No image URL provided for recipe."})
