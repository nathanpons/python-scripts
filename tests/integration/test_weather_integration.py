"""
Tests for the weather workflow
"""

import pytest
import time
from gui.weather_ui import WeatherUI
from scripts.weather_script import WeatherScript

@pytest.fixture()
def weather_ui(app_window, mocker):
    """Fixture to set up the Weather UI in the main application window."""
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"api_gateway_url": "http://fakeapi.test"}'))
    mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
    mocker.patch('os.path.join', return_value="fake_icon.ico")

    app_window.script_type.set("Weather")
    app_window.on_selection("Weather")
    app_window.root.update()
    time.sleep(1)

    weather_ui = app_window.current_ui
    assert weather_ui is not None, "WeatherUI was not created"

    app_window.root.update()
    time.sleep(1)

    yield weather_ui

    try:
        weather_ui.cleanup()
        app_window.root.update()
        app_window.on_close()
        time.sleep(1)
    except Exception:
        print("Cleanup failed in weather_ui fixture.")

@pytest.fixture
def mock_weather_response():
    """Mock successful weather API response."""
    return {
        "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
        "main": {"temp": 25.5, "humidity": 60}
    }

class TestWeatherIntegration:
    """Integration tests for the Weather Workflow."""

    class TestWeatherInitialization:
        """Tests for WeatherUI initialization."""

        def test_weather_ui_initialization(self, weather_ui):
            """Test that the WeatherUI initializes correctly."""
            assert isinstance(weather_ui, WeatherUI)
            assert weather_ui.location_entry is not None
            assert weather_ui.get_weather_button is not None

        def test_weather_script_selection_creates_ui(self, app_window, mocker):
            """Test that selecting the Weather script creates the WeatherUI."""
            mocker.patch('builtins.open', mocker.mock_open(read_data='{"api_gateway_url": "http://fakeapi.test"}'))
            mocker.patch('os.path.join', return_value="fake_icon.ico")
            
            app_window.script_type.set("Weather")
            app_window.on_selection("Weather")
            app_window.root.update()
            time.sleep(0.1)

            assert app_window.current_ui is not None
            assert isinstance(app_window.current_ui, WeatherUI)

    class TestWeatherWorkflow:
        """Tests for the Weather workflow functionality."""

        def test_full_weather_workflow_success(self, mocker, weather_ui, mock_weather_response, mock_requests):
            """Test complete workflow: select script -> enter location -> fetch weather."""
            mock_requests.json.return_value = mock_weather_response
            mocker.patch.object(weather_ui.weather_script, 'get_icon_path', return_value=None)

            # Enter location
            weather_ui.location_entry.insert(0, "New York")
            weather_ui.parent.update()
            time.sleep(1)
            
            # Fetch weather
            weather_ui.fetch_and_display_weather()
            
            # Verify display updated
            weather_info_text = weather_ui.weather_info_label.cget("text")
            assert "Clear" in weather_info_text
            assert "25.5" in weather_info_text
            assert "60%" in weather_info_text