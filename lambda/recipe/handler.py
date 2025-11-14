import json
import os
import urllib3
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

http = urllib3.PoolManager()


def lambda_handler(event, context):
    """AWS Lambda function to fetch recipe data from an external API and return it as JSON."""
    ingredients = event.get("queryStringParameters", {}).get(
        "ingredients", "chicken,tomato"
    )
    number_of_recipes = event.get("queryStringParameters", {}).get("number", "5")
    ignore_pantry = event.get("queryStringParameters", {}).get("ignorePantry", "true")
    ranking = event.get("queryStringParameters", {}).get("ranking", "1")
    api_key = os.getenv("SPOONACULAR_API_KEY")

    if not api_key:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "API key not configured"}),
        }
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={api_key}&number={number_of_recipes}&ignorePantry={ignore_pantry}&ranking={ranking}"

    try:
        response = http.request("GET", url)
        logging.debug(f"Recipe API response status: {response.status}")
        if response.status == 429:
            return {
                "statusCode": 429,
                "body": json.dumps(
                    {"error": "Rate limit exceeded, please try again later"}
                ),
            }
        if response.status != 200:
            return {
                "statusCode": response.status,
                "body": json.dumps({"error": "Failed to fetch recipe data"}),
            }
        recipe_data = json.loads(response.data.decode("utf-8"))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(recipe_data),
        }
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Error parsing recipe data"}),
        }
    except Exception as e:
        logging.error(f"Error fetching recipe data: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
