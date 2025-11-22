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

    class TestDisplayWeather:
        """Tests for the display_weather method."""

        def test_display_weather_success(self, mocker, weather_ui):
            """Test that display_weather updates labels correctly on success."""
            # Mocks
            fake_weather_data = {
                "weather": "Sunny",
                "temperature": 25,
                "humidity": 50,
                "description": "Clear sky",
                "icon_path": None,
            }
            weather_ui.weather_info_label = mocker.MagicMock()
            weather_ui.weather_icon = mocker.MagicMock()

            # Call method
            weather_ui.display_weather(fake_weather_data)

            # Asserts
            expected_info_text = (
                "Weather: Sunny\n"
                "Temperature: 25.0 °C | 77.0 °F\n"
                "Humidity: 50%\n"
                "Description: Clear sky"
            )
            weather_ui.weather_info_label.configure.assert_called_with(text=expected_info_text)
            weather_ui.weather_icon.configure.assert_called_with(image=None)
        
        def test_display_weather_error(self, mocker, weather_ui):
            """Test that display_weather updates labels correctly on error."""
            # Mocks
            fake_weather_data = {"error": "API error"}
            weather_ui.weather_info_label = mocker.MagicMock()
            weather_ui.weather_icon = mocker.MagicMock()

            # Call method
            weather_ui.display_weather(fake_weather_data)

            # Asserts
            weather_ui.weather_info_label.configure.assert_called_with(
                text="Error fetching data, please try again later."
            )
            weather_ui.weather_icon.configure.assert_called_with(image=None)

        def test_display_weather_with_icon(self, mocker, weather_ui):
            """Test that display_weather updates icon when icon_path is provided."""
            # Mocks
            fake_weather_data = {
                "weather": "Sunny",
                "temperature": 25,
                "humidity": 50,
                "description": "Clear sky",
                "icon_path": "path/to/icon.png",
            }
            weather_ui.weather_info_label = mocker.MagicMock()
            weather_ui.weather_icon = mocker.MagicMock()
            mock_image_open = mocker.patch("src.gui.weather_ui.Image.open")
            mock_ctk_image = mocker.patch("src.gui.weather_ui.ctk.CTkImage")

            # Call method
            weather_ui.display_weather(fake_weather_data)

            # Asserts
            weather_ui.weather_icon.configure.assert_called()
            mock_image_open.assert_called_once_with("path/to/icon.png")
            mock_ctk_image.assert_called_once()

        def test_display_weather_with_invalid_icon_path(self, mocker, weather_ui):
            """Test that display_weather handles invalid icon_path gracefully."""
            # Mocks
            fake_weather_data = {
                "weather": "Sunny",
                "temperature": 25,
                "humidity": 50,
                "description": "Clear sky",
                "icon_path": "invalid_path",
            }
            weather_ui.weather_info_label = mocker.MagicMock()
            weather_ui.weather_icon = mocker.MagicMock()
            mock_image_open = mocker.patch("src.gui.weather_ui.Image.open", side_effect=FileNotFoundError)

            # Call method
            weather_ui.display_weather(fake_weather_data)

            # Asserts
            weather_ui.weather_icon.configure.assert_called_with(image=None)
            mock_image_open.assert_called_once_with("invalid_path")