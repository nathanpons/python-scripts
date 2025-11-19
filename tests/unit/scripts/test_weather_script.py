"""
Tests for weather_script.py
"""
import pytest
import os
import requests
from src.scripts.weather_script import WeatherScript

@pytest.fixture
def weather_script():
    """Fixture to create a WeatherScript instance."""
    script = WeatherScript()
    yield script

@pytest.fixture
def mock_get_weather_success():
    """Fixture to mock successful API response for get_weather."""
    return ({
        "coord": {
            "lon": -18,
            "lat": 65
        },
        "weather": [
            {
                "id": 804,
                "main": "Clouds",
                "description": "overcast clouds",
                "icon": "04n"
            }
        ],
        "base": "stations",
        "main": {
            "temp": -7.78,
            "feels_like": -13.13,
            "temp_min": -7.78,
            "temp_max": -7.78,
            "pressure": 1030,
            "humidity": 96,
            "sea_level": 1030,
            "grnd_level": 928
        },
        "visibility": 2355,
        "wind": {
            "speed": 3.26,
            "deg": 225,
            "gust": 4.4
        },
        "clouds": {
            "all": 99
        },
        "dt": 1763577120,
        "sys": {
            "country": "IS",
            "sunrise": 1763546576,
            "sunset": 1763567533
        },
        "timezone": 0,
        "id": 2629691,
        "name": "Iceland",
        "cod": 200
    }, 200)

@pytest.fixture()
def mock_get_weather_not_found():
    """Fixture to mock 404 API response for get_weather."""
    return ({"error": "Failed to fetch weather data"}, 404)


@pytest.fixture()
def icon_path_mocks(mocker):
    """Fixture for common mocks used in get_icon_path tests."""
    mock_get_resource_path = mocker.patch("src.scripts.weather_script.get_resource_path")
    weather_dir = os.path.join("mocked_path", "assets", "weather")
    mock_get_resource_path.return_value = weather_dir

    mock_exists = mocker.patch("src.scripts.weather_script.os.path.exists")

    mock_makedirs = mocker.patch("src.scripts.weather_script.os.makedirs")

    mock_get = mocker.patch("src.scripts.weather_script.requests.get")

    mock_open_file = mocker.patch("builtins.open", mocker.mock_open())

    return {
        "get_resource_path": mock_get_resource_path,
        "exists": mock_exists,
        "makedirs": mock_makedirs,
        "get": mock_get,
        "open": mock_open_file,
        "weather_dir": weather_dir
    }

class TestWeatherScript:
    """Tests for the WeatherScript class."""

    class TestWeatherGetWeather:
        """Tests for WeatherScript get_weather method."""

        def test_get_weather_success(self, weather_script, mocker, mock_get_weather_success):
            """Test get_weather with successful API response."""
            mock_response_data, mock_status_code = mock_get_weather_success

            mock_get = mocker.patch("requests.get")
            mock_get.return_value.status_code = mock_status_code
            mock_get.return_value.json.return_value = mock_response_data

            result = weather_script.get_weather("Iceland")

            assert result == {
                "icon_path": weather_script.get_icon_path("04n"),
                "weather": "Clouds",
                "temperature": -7.78,
                "humidity": 96,
                "description": "overcast clouds",
            }

        def test_get_weather_not_found(self, weather_script, mocker, mock_get_weather_not_found):
            """Test get_weather with 404 API response."""
            mock_response_data, mock_status_code = mock_get_weather_not_found

            mock_get = mocker.patch("requests.get")
            mock_get.return_value.status_code = mock_status_code
            mock_get.return_value.json.return_value = mock_response_data

            result = weather_script.get_weather("UnknownLocation")

            assert result == {"error": "Location not found"}

        def test_get_weather_request_exception(self, weather_script, mocker):
            """Test get_weather handling of RequestException."""
            mock_get = mocker.patch("requests.get")
            mock_get.side_effect = Exception("Request failed")

            result = weather_script.get_weather("Iceland")

            assert result == {"error": "Exception occurred while fetching data"}

    class TestGetIconPath:
        """Tests for WeatherScript get_icon_path method."""

        def test_get_icon_path_already_exists(self, weather_script, icon_path_mocks):
            """Test get_icon_path when icon already exists."""
            icon_code = "04n"
            mocks = icon_path_mocks
            expected_icon_path = os.path.join(mocks["weather_dir"], f"weather_icon_{icon_code}.png")

            mocks["exists"].return_value = True
            mocks["get"].return_value = None

            result = weather_script.get_icon_path(icon_code)

            assert result == expected_icon_path
            mocks["get"].assert_not_called()
            mocks["makedirs"].assert_not_called()
            mocks["open"].assert_not_called()

        def test_get_icon_path_download_success(self, weather_script, icon_path_mocks, mocker):
            """Test get_icon_path when icon needs to be downloaded."""
            icon_code = "02d"
            mocks = icon_path_mocks
            expected_icon_path = os.path.join(mocks["weather_dir"], f"weather_icon_{icon_code}.png")

            mocks["exists"].side_effect = lambda path: path == mocks["weather_dir"]  # Dir exists, file doesn't
            mock_response = mocker.Mock()  # Note: Use mocker here if needed, or define in fixture
            mock_response.status_code = 200
            mock_response.content = b"fake_icon_data"
            mocks["get"].return_value = mock_response
            
            result = weather_script.get_icon_path(icon_code)
            
            assert result == expected_icon_path
            mocks["get"].assert_called_once_with(f"https://openweathermap.org/img/wn/{icon_code}@2x.png")
            mocks["open"].assert_called_once_with(expected_icon_path, "wb")
            mocks["open"]().write.assert_called_once_with(b"fake_icon_data")
            mocks["makedirs"].assert_not_called()

        @pytest.mark.parametrize("status_code", [404, 500])
        def test_get_icon_path_download_failure(self, weather_script, icon_path_mocks, mocker, status_code):
            """Test get_icon_path when icon download fails."""
            icon_code = "03d"
            mocks = icon_path_mocks

            mocks["exists"].side_effect = lambda path: path == mocks["weather_dir"]
            mock_response = mocker.Mock()
            mock_response.status_code = status_code
            mocks["get"].return_value = mock_response
            
            result = weather_script.get_icon_path(icon_code)
            
            assert result is None
            mocks['get'].assert_called_once()
            mocks["makedirs"].assert_not_called()
            mocks["open"].assert_not_called()

        def test_icon_path_network_exception(self, weather_script, icon_path_mocks, mocker):
            """Test get_icon_path handling of network exception during icon download."""
            icon_code = "04n"
            mocks = icon_path_mocks

            mocks["exists"].side_effect = lambda path: path == mocks["weather_dir"]
            mocks["get"].side_effect = requests.exceptions.RequestException("Network error")

            with pytest.raises(requests.exceptions.RequestException):
                weather_script.get_icon_path(icon_code)

        @pytest.mark.parametrize("icon_code", ["01d", "01n", "02d", "10n", "500d", "-6n", "abc"])
        def test_get_icon_path_icon_codes(self, weather_script, icon_path_mocks, mocker, icon_code):
            """Test get_icon_path with various icon codes."""
            mocks = icon_path_mocks
            expected_icon_path = os.path.join(mocks["weather_dir"], f"weather_icon_{icon_code}.png")

            mocks["exists"].return_value = True
            mocks["get"].return_value = None

            result = weather_script.get_icon_path(icon_code)

            assert result == expected_icon_path
            mocks["get"].assert_not_called()

        def test_get_icon_path_file_write_permission_error(self, weather_script, icon_path_mocks, mocker):
            """Test get_icon_path handling of file write permission error."""
            icon_code = "02d"
            mocks = icon_path_mocks

            mocks["exists"].side_effect = lambda path: path == mocks["weather_dir"]
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.content = b"fake_icon_data"
            mocks["get"].return_value = mock_response
            mocks["open"].side_effect = PermissionError("No permission to write file")

            with pytest.raises(PermissionError):
                weather_script.get_icon_path(icon_code)