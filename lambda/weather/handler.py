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
    """AWS Lambda function to fetch weather data from an external API and return it as JSON."""
    location = event.get('queryStringParameters', {}).get('location', 'New York')
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'API key not configured'})
        }
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'

    try:
        response = http.request('GET', url)
        logging.debug(f"Weather API response status: {response.status}")
        if response.status != 200:
            return {
                'statusCode': response.status,
                'body': json.dumps({'error': 'Failed to fetch weather data'})
            }
        weather_data = json.loads(response.data.decode('utf-8'))
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(weather_data)
        }
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
