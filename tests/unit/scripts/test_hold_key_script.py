"""
Tests for hold_key_script.py
"""
import pytest
from unittest.mock import Mock, patch
from src.scripts.hold_key_script import HoldKeyScript

class TestHoldKeyScriptInitialization:
    def test_default_initialization(self):
        """Test that HoldKeyScript initializes with default parameters."""
        script = HoldKeyScript()

        assert script.hold_key == "w"
        assert script.toggle_key == "f6"
        assert script.is_spam_key is False
        assert script.interval == 0.01


class TestHoldKeyScriptStartStop:
    @patch("src.scripts.hold_key_script.keyboard")
    @patch("src.scripts.hold_key_script.threading.Thread")
    def test_start_script(self, mock_thread, mock_keyboard):
        """Test starting the HoldKeyScript."""
        script = HoldKeyScript()

        assert not script.is_running

        script.start()
        assert script.is_running