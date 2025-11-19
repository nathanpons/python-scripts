"""
Tests for weather_script.py
"""
import pytest
from src.scripts.weather_script import WeatherScript

@pytest.fixture
def weather_script():
    """Fixture to create a WeatherScript instance."""
    script = WeatherScript(api_key="test_api_key", location="TestLocation")
    yield script