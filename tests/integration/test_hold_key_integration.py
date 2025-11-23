"""
Tests for hold key integration with the rest of the application.
"""

import pytest
import time
import customtkinter as ctk
from scripts.hold_key_script import HoldKeyScript
from src.gui.hold_key_ui import HoldKeyUI

@pytest.fixture()
def hold_key_ui(app_window, mocker):
    app_window.script_type.set("Hold Key")
    app_window.on_selection("Hold Key")

    hold_key_ui = app_window.current_ui

    yield hold_key_ui

    hold_key_ui.cleanup()

class TestHoldKeyIntegration:
    """Tests for Hold Key integration."""

    class TestScriptInitialization:
        """Tests for script initialization."""

        def test_script_not_initialized_on_ui_creation(self, hold_key_ui):
            """Test that the script is not initialized upon UI creation."""
            assert hold_key_ui.script is None
            assert hold_key_ui.status_label.cget("text") == "Status: Stopped"

        def test_script_initialized_on_start(self, hold_key_ui):
            """Test that the script is initialized when started."""
            # Call method
            hold_key_ui.toggle_script()

            # Assertions
            assert hold_key_ui.script is not None
            assert isinstance(hold_key_ui.script, HoldKeyScript)
            assert hold_key_ui.script.is_running is True
            assert hold_key_ui.status_label.cget("text") == "Status: Running"
            assert hold_key_ui.toggle_script_button_text.get() == "Stop"
            







