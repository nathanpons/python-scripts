"""
Tests for hold_key_script.py
"""
import pytest
from unittest.mock import Mock, patch, call
from src.scripts.hold_key_script import HoldKeyScript, MOUSE_KEYS

class TestHoldKeyScriptInitialization:
    def test_default_initialization(self):
        """Test that HoldKeyScript initializes with default parameters."""
        script = HoldKeyScript()

        assert script.hold_key == "w"
        assert script.toggle_key == "f6"
        assert script.interval == 0.01
        assert script.is_spam_key is False
        assert script.is_running is False
        assert script.toggle is False
        assert script.is_mouse_key is False

    def test_custom_initialization(self):
        """Test that HoldKeyScript initializes with custom parameters."""
        script = HoldKeyScript(
            hold_key="left mouse",
            toggle_key="f5",
            interval=0.05,
            is_spam_key=True,
        )

        assert script.hold_key == "left mouse"
        assert script.toggle_key == "f5"
        assert script.interval == 0.05
        assert script.is_spam_key is True
        assert script.is_mouse_key is True
        assert script.is_running is False
        assert script.toggle is False

    def test_mouse_key_detection(self):
        """Test that is_mouse_key is set correctly based on hold_key."""
        script1 = HoldKeyScript(hold_key="left mouse")
        assert script1.is_mouse_key is True

        script2 = HoldKeyScript(hold_key="right mouse")
        assert script2.is_mouse_key is True

        script3 = HoldKeyScript(hold_key="w")
        assert script3.is_mouse_key is False

class TestHoldKeyScriptToggle:
    def test_toggle_hold_key(self):
        """Test toggling the hold state of the script."""
        script = HoldKeyScript()

        assert script.toggle is False

        script.toggle_hold()
        assert script.toggle is True

        script.toggle_hold()
        assert script.toggle is False

    def test_multiple_toggles(self):
        """Test multiple toggles of the hold state."""
        script = HoldKeyScript()
        assert script.toggle is False

        for i in range(5):
            expected = (i % 2 == 0)
            script.toggle_hold()
            assert script.toggle is expected

class TestMouseKeys:
    """Test MOUSE_KEYS dictionary."""
    def test_mouse_keys_mapping(self):
        """Test that MOUSE_KEYS contains correct mappings."""
        assert MOUSE_KEYS["left mouse"] == "left"
        assert MOUSE_KEYS["right mouse"] == "right"
        assert MOUSE_KEYS["middle mouse"] == "middle"

    def test_mouse_keys_count(self):
        """Test that MOUSE_KEYS contains exactly three entries."""
        assert len(MOUSE_KEYS) == 3

class TestHoldKeyScriptStartStop:
    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_start_script(self, mock_thread, mock_keyboard):
        """Test starting the HoldKeyScript."""
        script = HoldKeyScript()

        assert not script.is_running

        script.start()
        assert script.is_running
        assert mock_thread.called
        assert mock_keyboard.add_hotkey.called

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_start_already_running(self, mock_thread, mock_keyboard):
        """Test starting the HoldKeyScript when it's already running."""
        script = HoldKeyScript()
        script.is_running = True

        script.start()
        assert script.is_running is True
        assert not mock_thread.called
        assert not mock_keyboard.add_hotkey.called

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_stop_keyboard_script(self, mock_thread, mock_keyboard):
        """Test stopping the HoldKeyScript for keyboard key."""
        script = HoldKeyScript(hold_key="a")
        script.is_running = True
        script.toggle = True
        script.hotkey_handler = Mock()
        script.thread = Mock()

        script.stop()

        assert script.is_running is False
        assert script.toggle is False
        mock_keyboard.release.assert_called_with("a")
        mock_keyboard.release.assert_called_once()

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.pyautogui")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_stop_mouse_script(self, mock_thread, mock_pyautogui, mock_keyboard):
        """Test stopping the HoldKeyScript for mouse key."""
        script = HoldKeyScript(hold_key="left mouse")
        script.is_running = True
        script.toggle = True
        script.hotkey_handler = Mock()
        script.thread = Mock()

        script.stop()

        assert script.is_running is False
        assert script.toggle is False
        mock_pyautogui.mouseUp.assert_called_with(button="left")
        mock_keyboard.remove_hotkey.assert_called_once()

class TestHoldKeyLoopKeyboard():
    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.time.sleep")
    def test_hold_key_loop_hold(self, mock_sleep, mock_keyboard):
        """Test that keyboard key is pressed and released."""
        script = HoldKeyScript(hold_key="a", is_spam_key=False)
        script.is_running = True

        # Simulate toggle changes
        def side_effect(*args):
            if mock_sleep.call_count == 1:
                script.toggle = True
            elif mock_sleep.call_count == 3:
                script.toggle = False
            elif mock_sleep.call_count == 5:
                script.is_running = False

        mock_sleep.side_effect = side_effect

        script.hold_key_loop()

        mock_keyboard.press.assert_called_with("a")
        mock_keyboard.release.assert_called_with("a")

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.time.sleep")
    def test_hold_key_loop_spam(self, mock_sleep, mock_keyboard):
        """Test that keyboard key is spammed."""
        script = HoldKeyScript(hold_key="a", is_spam_key=True)
        script.is_running = True
        script.toggle = True

        call_count = [0]
        # Run for 3 iterations
        def side_effect(*args):
            call_count[0] += 1
            if call_count[0] >= 3:
                script.is_running = False
                script.toggle = False

        mock_sleep.side_effect = side_effect

        script.hold_key_loop()

        assert mock_keyboard.press_and_release.call_count >= 3

class TestHoldKeyLoopMouse():
    @patch("src.scripts.hold_key_script.pyautogui")
    @patch("src.scripts.hold_key_script.time.sleep")
    def test_hold_key_loop_hold(self, mock_sleep, mock_pyautogui):
        """Test that mouse button is pressed and released."""
        script = HoldKeyScript(hold_key="left mouse", is_spam_key=False)
        script.is_running = True

        # Simulate toggle changes
        def side_effect(*args):
            if mock_sleep.call_count == 1:
                script.toggle = True
            elif mock_sleep.call_count == 3:
                script.toggle = False
            elif mock_sleep.call_count == 5:
                script.is_running = False

        mock_sleep.side_effect = side_effect

        script.hold_key_loop()

        mock_pyautogui.mouseDown.assert_called_with(button="left")
        mock_pyautogui.mouseUp.assert_called_with(button="left")

    @patch("src.scripts.hold_key_script.pyautogui")
    @patch("src.scripts.hold_key_script.time.sleep")
    def test_hold_key_loop_spam(self, mock_sleep, mock_pyautogui):
        """Test that mouse button is spammed."""
        script = HoldKeyScript(hold_key="left mouse", is_spam_key=True)
        script.is_running = True
        script.toggle = True

        call_count = [0]
        # Run for 3 iterations
        def side_effect(*args):
            call_count[0] += 1
            if call_count[0] >= 3:
                script.is_running = False
                script.toggle = False
        mock_sleep.side_effect = side_effect

        script.hold_key_loop()

        assert mock_pyautogui.click.call_count >= 3

class TestHoldKeyScriptEdgeCases:
    """Test edge cases and error handling"""

    @patch("src.scripts.hold_key_script.keyboard")
    def test_invalid_mouse_key(self, mock_keyboard):
        """Test handling of invalid mouse key."""
        script = HoldKeyScript(hold_key="invalid mouse", is_spam_key=False)

        assert script.is_mouse_key is False

    def test_interval_validation(self):
        """Test different interval values."""
        script = HoldKeyScript(interval=0)
        assert script.interval == 0

        script = HoldKeyScript(interval=0.01)
        assert script.interval == 0.01

        script = HoldKeyScript(interval=1)
        assert script.interval == 1

    def test_interval_is_positive(self):
        """Test that interval is positive."""
        script = HoldKeyScript(interval=-0.1)
        
        with pytest.raises(ValueError, match="Interval must be a positive number."):
            script.start()

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.time.sleep")
    def test_exception_in_loop(self, mock_sleep, mock_keyboard):
        """Test that exceptions in hold_key_loop are handled and logged."""
        script = HoldKeyScript()
        script.is_running = True

        mock_keyboard.press.side_effect = Exception("Test Exception")

        def side_effect(*args):
            script.toggle = True
            script.is_running = False

        mock_sleep.side_effect = side_effect

        script.hold_key_loop()

class TestHoldKeyScriptIntegration:
    """Integration tests for HoldKeyScript"""

    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_full_start_stop_cycle(self, mock_thread, mock_keyboard):
        """Test full start and stop cycle of the script."""
        script = HoldKeyScript(hold_key="s", toggle_key="f8")

        # Start
        script.start()
        assert script.is_running is True
        assert script.toggle is False
        assert mock_thread.called
        assert mock_keyboard.add_hotkey.called

        # Toggle
        script.toggle_hold()
        assert script.toggle is True

        # Stop
        script.stop()
        assert script.is_running is False
        assert script.toggle is False
        mock_keyboard.release.assert_called_with("s")

class TestParameterizedScenarios:
    """Test multiple scenarios with parametrize"""
    
    @pytest.mark.parametrize("hold_key,is_mouse", [
        ("w", False),
        ("a", False),
        ("space", False),
        ("left mouse", True),
        ("right mouse", True),
        ("middle mouse", True),
    ])
    def test_key_type_detection(self, hold_key, is_mouse):
        """Test that various keys are correctly identified"""
        script = HoldKeyScript(hold_key=hold_key)
        assert script.is_mouse_key == is_mouse
    
    @pytest.mark.parametrize("interval", [0.001, 0.01, 0.1, 1.0])
    def test_various_intervals(self, interval):
        """Test script with various intervals"""
        script = HoldKeyScript(interval=interval)
        assert script.interval == interval

