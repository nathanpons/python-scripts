"""
Tests for hold_key_ui.py
"""
import pytest
from unittest.mock import Mock, patch
from src.gui.hold_key_ui import HoldKeyUI

class TestHoldKeyUIInitialization:
    @patch("src.gui.hold_key_ui.ctk")
    def test_initialization(self, mock_ctk):
        """Test that HoldKeyUI initializes correctly."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        assert ui.parent_frame == mock_parent_frame
        assert ui.title_font is not None
        assert ui.default_font is not None
        assert ui.script is None
        assert ui.hold_keys == ["left mouse", "right mouse", "w", "a", "s", "d"]
        assert ui.toggle_keys == ["f6", "f7", "f8", "f9"]

    def test_ui_components_created(self):
        """Test that UI components are created."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        assert hasattr(ui, "title_label")
        assert hasattr(ui, "hold_key_label")
        assert hasattr(ui, "hold_key_combobox")
        assert hasattr(ui, "toggle_key_label")
        assert hasattr(ui, "toggle_key_combobox")
        assert hasattr(ui, "spam_key_switch")
        assert hasattr(ui, "toggle_script_button")
        assert hasattr(ui, "status_label")

class TestHoldKeyUIToggleScript:
    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_toggle_script_starts_script(self, mock_hold_key_script):
        """Test that toggle_script starts the script when not running."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False

        ui.toggle_script()

        mock_hold_key_script.assert_called_once()
        mock_script_instance.start.assert_called_once()

    def test_toggle_script_stops_script(self):
        """Test that toggle_script stops the script when running."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        mock_script_instance = Mock()
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.toggle_script()

        mock_script_instance.stop.assert_called_once()

    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_toggle_script_multiple_times(self, mock_hold_key_script):
        """Test that toggle_script starts and stops the script multiple times"""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)
        
        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False

        ui.toggle_script()
        mock_hold_key_script.assert_called_once()
        mock_script_instance.start.assert_called_once()
        mock_script_instance.is_running = True

        ui.toggle_script()
        mock_script_instance.stop.assert_called_once()
        mock_script_instance.is_running = False

        ui.toggle_script()
        assert mock_script_instance.start.call_count == 2
        mock_script_instance.is_running = True

        ui.toggle_script()
        assert mock_script_instance.stop.call_count == 2
        
class TestHoldKeyUIToggleHold:
    def test_toggle_hold_when_running(self):
        """Test that toggle_hold calls script.toggle_hold when running."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        mock_script_instance = Mock()
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.toggle_hold()

        mock_script_instance.toggle_hold.assert_called_once()

class TestSpamKeySwitch:
    def test_toggle_interval_ui_shows_interval_frame(self):
        """Test that toggle_interval_ui shows the interval frame when spam key is enabled."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        ui.spam_key_switch.get = Mock(return_value=True)
        ui.interval_frame_visible = False

        ui.toggle_interval_ui()

        assert ui.interval_frame_visible is True

    def test_toggle_interval_ui_hides_interval_frame(self):
        """Test that toggle_interval_ui hides the interval frame when spam key is disabled."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        ui.spam_key_switch.get = Mock(return_value=False)
        ui.interval_frame_visible = True

        ui.toggle_interval_ui()

        assert ui.interval_frame_visible is False

class TestHoldKeyUICleanup:
    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_cleanup_stops_running_script(self, mock_hold_key_script):
        """Test that cleanup stops the script if it is running."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.cleanup()

        mock_script_instance.stop.assert_called_once()

    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_cleanup_does_nothing_if_script_not_running(self, mock_hold_key_script):
        """Test that cleanup does nothing if the script is not running."""
        mock_parent_frame = Mock()
        ui = HoldKeyUI(mock_parent_frame)

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False
        ui.script = mock_script_instance

        ui.cleanup()

        mock_script_instance.stop.assert_not_called()