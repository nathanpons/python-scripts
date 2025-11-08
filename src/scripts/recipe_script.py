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
    BASE_URL = "https://api.spoonacular.com/recipes"
    MAXIMIZE_USED_INGREDIENTS = 1
    MINIMIZE_MISSING_INGREDIENTS = 2

    def __init__(self, api_key):
        self.api_key = api_key
        self.ignore_pantry = True  # Whether to ignore typical pantry items, such as water, salt, flour, etc.

    def get_recipes(self, ingredients, number=1):
        params = {
            "apiKey": self.api_key,
            "ingredients": ingredients,
            "number": number,
            "ignorePantry": str(self.ignore_pantry).lower(),
            "ranking": self.MAXIMIZE_USED_INGREDIENTS,
        }
        try:
            response = requests.get(f"{self.BASE_URL}/findByIngredients", params=params)
            if response.status_code == 200:
                data = response.json()
                logging.debug(f"Recipes found: {data}")
                if data:
                    return data
                else:
                    return None
            else:
                response.raise_for_status()
                logging.error(f"Error finding recipes: {response.status_code}")
        except Exception as e:
            logging.error(f"Exception occurred while finding recipes: {e}")
            return None

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
                return None
        else:
            logging.warning("No image URL provided for recipe.")
            return None
