"""
Tests for the weather workflow
"""

import pytest
import time
from gui.weather_ui import WeatherUI
from scripts.weather_script import WeatherScript

@pytest.fixture()
def weather_ui(app_window):
    """Fixture to set up the Weather UI in the main application window."""
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
