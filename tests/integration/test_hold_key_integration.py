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

    class TestHoldKeyUIInteractions:
        """Tests for UI interactions."""

        def test_interval_ui_visibility_based_on_spam_key(self, hold_key_ui):
            """Test that interval UI visibility changes based on spam key option."""
            # Initially, interval UI should be hidden
            assert hold_key_ui.is_spam_key_var.get() is False
            assert hold_key_ui.interval_frame_visible is False

            # Enable spam key
            hold_key_ui.is_spam_key_var.set(True)
            hold_key_ui.toggle_interval_ui()

            # Assertions
            assert hold_key_ui.interval_frame_visible is True

            # Disable spam key
            hold_key_ui.is_spam_key_var.set(False)
            hold_key_ui.toggle_interval_ui()

            # Assertions
            assert hold_key_ui.interval_frame_visible is False

        def test_ui_components_disable_when_script_is_running(self, hold_key_ui):
            """Test that UI components disable when the script is running."""
            # Start the script
            hold_key_ui.toggle_script()

            # Assertions
            assert hold_key_ui.hold_key_optionmenu.cget("state") == "disabled"
            assert hold_key_ui.toggle_key_optionmenu.cget("state") == "disabled"
            assert hold_key_ui.spam_key_switch.cget("state") == "disabled"

            # Stop the script
            hold_key_ui.toggle_script()

            # Assertions after stopping
            assert hold_key_ui.hold_key_optionmenu.cget("state") == "normal"
            assert hold_key_ui.toggle_key_optionmenu.cget("state") == "normal"
            assert hold_key_ui.spam_key_switch.cget("state") == "normal"

        def test_spam_key_toggle_shows_interval_ui(self, hold_key_ui):
            """Test that toggling the spam key option shows/hides interval UI."""
            # Initially, interval UI should be hidden
            assert hold_key_ui.is_spam_key_var.get() is False
            assert hold_key_ui.interval_frame_visible is False

            # Enable spam key
            hold_key_ui.is_spam_key_var.set(True)
            hold_key_ui.toggle_interval_ui()

            # Assertions
            assert hold_key_ui.interval_frame_visible is True

            # Disable spam key
            hold_key_ui.is_spam_key_var.set(False)
            hold_key_ui.toggle_interval_ui()

            # Assertions
            assert hold_key_ui.interval_frame_visible is False

        @pytest.mark.parametrize("interval_value,is_valid", [
            ("100", True),
            ("1", True),
            ("0.999", False),
            ("0", False),
            ("-0.1", False),
            ("-1", False),
            ("abc", False),
            ("1.5e2", False),
            (1, True),
            (-1, False),
        ])
        def test_interval_validation(self, hold_key_ui, interval_value, is_valid):
            """Test the interval input validation."""
            # Assert script is stopped initially
            assert hold_key_ui.script is None
            assert hold_key_ui.status_label.cget("text") == "Status: Stopped"

            # Set invalid interval
            hold_key_ui.is_spam_key_var.set(True)
            hold_key_ui.toggle_interval_ui()
            hold_key_ui.interval_var_milliseconds.set(interval_value)
            hold_key_ui.toggle_script()

            # Assertions
            if is_valid:
                # Script should start
                assert hold_key_ui.script is not None
                assert hold_key_ui.script.is_running is True
                assert hold_key_ui.status_label.cget("text") == "Status: Running"

                # Stop the script for cleanup
                hold_key_ui.toggle_script()
                assert hold_key_ui.script is None
                assert hold_key_ui.status_label.cget("text") == "Status: Stopped"
            else:
                # Script should not start
                assert hold_key_ui.script is None
                assert hold_key_ui.status_label.cget("text") == "Status: Stopped"

            