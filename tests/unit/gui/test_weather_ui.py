"""
Tests for weather_ui.py.
"""

import pytest
from scripts.weather_script import WeatherScript
from src.gui.weather_ui import WeatherUI


@pytest.fixture()
def weather_ui(mocker):
    """Fixture for WeatherUI instance."""
    mock_parent_frame = mocker.MagicMock()
    weather_ui = WeatherUI(mock_parent_frame)
    yield weather_ui


class TestWeatherUI:
    """Tests for WeatherUI methods."""

    class TestWeatherUIInitialization:
        """Tests for WeatherUI initialization."""

        def test_default_initialization(self, weather_ui):
            """Test that WeatherUI initializes with correct attributes."""
            assert weather_ui.parent is not None
            assert isinstance(weather_ui.weather_script, WeatherScript)
            assert weather_ui.default_font is not None
            assert weather_ui.title_font is not None

    class TestSetupUI:
        """Tests for setup_ui method."""

        def test_ui_components_created(self, weather_ui):
            """Test that UI components are created."""

            # Main Dashboard Components
            assert hasattr(weather_ui, "dashboard_frame")
            assert hasattr(weather_ui, "title_label")

            # Location Input Components
            assert hasattr(weather_ui, "location_frame")
            assert hasattr(weather_ui, "location_label")
            assert hasattr(weather_ui, "location_entry")
            assert hasattr(weather_ui, "get_weather_button")

            # Weather Display Components
            assert hasattr(weather_ui, "weather_frame")
            assert hasattr(weather_ui, "weather_icon")
            assert hasattr(weather_ui, "weather_info_label")

    class TestFetchAndDisplayWeather:
        """Tests for the fetch_and_display_weather method."""

        def test_fetch_and_display_weather_success(self, mocker, weather_ui):
            """Test that fetch_and_display_weather calls get_weather and display_weather."""
            # Mocks
            mocker.patch.object(
                weather_ui.location_entry, "get", return_value="New York"
            )
            mock_display_weather = mocker.patch.object(weather_ui, "display_weather")
            fake_weather_data = {
                "location": "New York",
                "temperature": "25°C",
                "condition": "Sunny",
            }
            mock_get_weather = mocker.patch.object(
                weather_ui.weather_script, "get_weather", return_value=fake_weather_data
            )

            # Call method
            weather_ui.fetch_and_display_weather()

            # Asserts
            mock_get_weather.assert_called_once_with("New York")
            mock_display_weather.assert_called_once_with(fake_weather_data)

        @pytest.mark.parametrize("location_input", ["", "   ", None])
        def test_fetch_and_display_weather_empty_location(
            self, mocker, weather_ui, location_input
        ):
            """Test that fetch_and_display_weather handles empty location input."""
            # Mocks
            mocker.patch.object(
                weather_ui.location_entry, "get", return_value=location_input
            )
            mock_get_weather = mocker.patch.object(
                weather_ui.weather_script, "get_weather"
            )
            mock_display_weather = mocker.patch.object(weather_ui, "display_weather")

            # Call method
            weather_ui.fetch_and_display_weather()

            # Asserts
            mock_get_weather.assert_not_called()
            mock_display_weather.assert_not_called()

        def test_fetch_and_display_weather_error(self, mocker, weather_ui):
            """Test that fetch_and_display_weather handles error in weather data."""
            # Mocks
            mocker.patch.object(
                weather_ui.location_entry, "get", return_value="InvalidLocation"
            )
            mock_get_weather = mocker.patch.object(
                weather_ui.weather_script,
                "get_weather",
                side_effect=Exception("API error"),
            )
            mock_display_weather = mocker.patch.object(weather_ui, "display_weather")

            # Call method
            weather_ui.fetch_and_display_weather()

            # Asserts
            mock_get_weather.assert_called_once_with("InvalidLocation")
            mock_display_weather.assert_called_once()
