"""
Tests for hold key integration with the rest of the application.
"""

import pytest
import time
import customtkinter as ctk
from scripts.hold_key_script import HoldKeyScript
from gui.hold_key_ui import HoldKeyUI

@pytest.fixture()
def hold_key_ui(app_window):
    """Fixture to set up the Hold Key UI in the main application window."""
    app_window.script_type.set("Hold Key")
    app_window.on_selection("Hold Key")
    app_window.root.update()
    time.sleep(1)

    hold_key_ui = app_window.current_ui
    assert hold_key_ui is not None, "HoldKeyUI was not created"

    app_window.root.update()
    time.sleep(1)

    yield hold_key_ui

    try:
        hold_key_ui.cleanup()
        app_window.root.update()
        app_window.on_close()
        time.sleep(1)
    except Exception:
        print("Cleanup failed in hold_key_ui fixture.")

class TestHoldKeyIntegration:
    """Tests for Hold Key integration."""

    class TestInitialization:
        """Tests for script initialization."""

        def test_script_not_initialized_on_ui_creation(self, hold_key_ui):
            """Test that the script is not initialized upon UI creation."""
            assert hold_key_ui.script is None
            assert hold_key_ui.status_label.cget("text") == "Status: Stopped"
            assert hold_key_ui.toggle_script_button_text.get() == "Start"

    class TestHoldKeyWorkflow:
        """Tests for the script workflow"""

        def test_script_start_and_stop(self, hold_key_ui):
            """Test the script starts and stops correctly."""
            # Start the script
            ## Call method
            hold_key_ui.toggle_script()

            ## Assertions
            assert hold_key_ui.script is not None
            assert isinstance(hold_key_ui.script, HoldKeyScript)
            assert hold_key_ui.script.is_running is True
            assert hold_key_ui.status_label.cget("text") == "Status: Running"
            assert hold_key_ui.toggle_script_button_text.get() == "Stop"

            # Stop the script
            ## Call method
            hold_key_ui.toggle_script()

            ## Assertions after stopping
            assert hold_key_ui.script is None
            assert hold_key_ui.status_label.cget("text") == "Status: Stopped"
            assert hold_key_ui.toggle_script_button_text.get() == "Start"

        def test_hold_key_with_different_parameters(self, hold_key_ui):
            """Test the hold key script with different parameters."""
            # Set different parameters
            hold_key_ui.hold_key_var.set("a")
            hold_key_ui.toggle_key_var.set("f8")

            # Start the script
            hold_key_ui.toggle_script()

            # Assertions
            assert hold_key_ui.script is not None
            assert hold_key_ui.script.hold_key == "a"
            assert hold_key_ui.script.toggle_key == "f8"
            assert hold_key_ui.script.is_spam_key is False

            # Stop the script
            hold_key_ui.toggle_script()

            assert hold_key_ui.script is None

