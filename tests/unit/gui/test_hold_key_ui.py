"""
Tests for hold_key_ui.py
"""
import pytest
from unittest.mock import Mock, patch
from src.gui.hold_key_ui import HoldKeyUI
from src.scripts.hold_key_script import HoldKeyScript

@pytest.fixture
def setup_hold_key_ui():
    """Fixture to set up HoldKeyUI instance for tests."""
    mock_parent_frame = Mock()
    ui = HoldKeyUI(mock_parent_frame)
    script = HoldKeyScript()

    ui.interval_var_milliseconds.get.return_value = script.interval * 1000
    yield ui
    ui.cleanup()

class TestHoldKeyUIInitialization:
    def test_initialization(self, setup_hold_key_ui):
        """Test that HoldKeyUI initializes correctly."""
        ui = setup_hold_key_ui

        assert ui.title_font is not None
        assert ui.default_font is not None
        assert ui.script is None
        assert ui.hold_keys == ["left mouse", "right mouse", "w", "a", "s", "d"]
        assert ui.toggle_keys == ["f6", "f7", "f8", "f9"]

    def test_ui_components_created(self, setup_hold_key_ui):
        """Test that UI components are created."""
        ui = setup_hold_key_ui

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
    def test_toggle_script_starts_script(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that toggle_script starts the script when not running."""
        ui = setup_hold_key_ui

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False

        ui.toggle_script()

        mock_hold_key_script.assert_called_once()
        mock_script_instance.start.assert_called_once()

    def test_toggle_script_stops_script(self, setup_hold_key_ui):
        """Test that toggle_script stops the script when running."""
        ui = setup_hold_key_ui

        mock_script_instance = Mock()
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.toggle_script()

        mock_script_instance.stop.assert_called_once()

    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_toggle_script_multiple_times(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that toggle_script starts and stops the script multiple times"""
        ui = setup_hold_key_ui
        
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
        
    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_toggle_script_ui_updates_on_start(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that toggle_script updates UI components correctly on start."""
        ui = setup_hold_key_ui

        ui.toggle_script_button_text = Mock()
        ui.toggle_script_button_text.get.return_value = "Start"
        ui.toggle_script_button_text.set = Mock()

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False
        
        ui.toggle_script()

        ui.toggle_script_button_text.set.assert_called_with("Stop")
        
        ui.status_label.configure.assert_called_with(text="Status: Running")
        ui.hold_key_combobox.configure.assert_called_with(state="disabled")
        ui.toggle_key_combobox.configure.assert_called_with(state="disabled")
        ui.spam_key_switch.configure.assert_called_with(state="disabled")

    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_toggle_script_ui_updates_on_stop(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that toggle_script updates UI components correctly on stop."""
        ui = setup_hold_key_ui

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = True

        ui.script = mock_script_instance

        ui.toggle_script()

        ui.toggle_script_button_text.set.assert_called_with("Start")
        
        ui.status_label.configure.assert_called_with(text="Status: Stopped")
        ui.hold_key_combobox.configure.assert_called_with(state="normal")
        ui.toggle_key_combobox.configure.assert_called_with(state="normal")
        ui.spam_key_switch.configure.assert_called_with(state="normal")

class TestHoldKeyUIToggleHold:
    def test_toggle_hold_when_running(self, setup_hold_key_ui):
        """Test that toggle_hold calls script.toggle_hold when running."""
        ui = setup_hold_key_ui

        mock_script_instance = Mock()
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.toggle_hold()

        mock_script_instance.toggle_hold.assert_called_once()

class TestSpamKeySwitch:
    def test_toggle_interval_ui_shows_interval_frame(self, setup_hold_key_ui):
        """Test that toggle_interval_ui shows the interval frame when spam key is enabled."""
        ui = setup_hold_key_ui

        ui.spam_key_switch.get = Mock(return_value=True)
        ui.interval_frame_visible = False

        ui.toggle_interval_ui()

        assert ui.interval_frame_visible is True

    def test_toggle_interval_ui_hides_interval_frame(self, setup_hold_key_ui):
        """Test that toggle_interval_ui hides the interval frame when spam key is disabled."""
        ui = setup_hold_key_ui

        ui.spam_key_switch.get = Mock(return_value=False)
        ui.interval_frame_visible = True

        ui.toggle_interval_ui()

        assert ui.interval_frame_visible is False

class TestHoldKeyUIIntervalValidation:
    """Tests for HoldKeyUI logic methods."""
    def test_interval_frame_initially_hidden(self, setup_hold_key_ui):
        """Test that the interval frame is initially hidden."""
        ui = setup_hold_key_ui

        assert ui.interval_frame_visible is False

    @pytest.mark.parametrize("invalid_value", [
        "-10", 
        -1,
        "0",
        "0.1",
        "10.5",
        "9.2*10^4",
        "abc",
        "",
        None
    ])
    def test_invalid_interval_values(self, invalid_value, setup_hold_key_ui):
        """Test that setting an invalid interval shows an error."""
        ui = setup_hold_key_ui

        ui.interval_var_milliseconds.get.return_value = invalid_value

        result = ui.validate_interval()

        assert result is False

    @pytest.mark.parametrize("valid_value", [
        "1", 
        1,
        "100", 
        "4000000"
        ])
    def test_valid_interval_values(self, valid_value, setup_hold_key_ui):
        """Test that setting a valid interval passes validation."""
        ui = setup_hold_key_ui

        ui.interval_var_milliseconds.get.return_value = valid_value

        result = ui.validate_interval()

        assert result is True
        
class TestHoldKeyUICleanup:
    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_cleanup_stops_running_script(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that cleanup stops the script if it is running."""
        ui = setup_hold_key_ui

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = True
        ui.script = mock_script_instance

        ui.cleanup()

        mock_script_instance.stop.assert_called_once()

    @patch("src.gui.hold_key_ui.HoldKeyScript")
    def test_cleanup_does_nothing_if_script_not_running(self, mock_hold_key_script, setup_hold_key_ui):
        """Test that cleanup does nothing if the script is not running."""
        ui = setup_hold_key_ui

        mock_script_instance = mock_hold_key_script.return_value
        mock_script_instance.is_running = False
        ui.script = mock_script_instance

        ui.cleanup()

        mock_script_instance.stop.assert_not_called()