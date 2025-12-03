"""
Test cases for the Hold Key end-to-end functionality.
"""

import pytest
import time

class TestHoldKeyE2E:
    """End-to-end tests for the Hold Key functionality."""
    
    def test_user_starts_and_stops_hold_key(self, app_process, interact):
        """User starts hold key, then stops it."""
        time.sleep(0.5)
        
        window_region = interact.get_window_region("Nathan's Python Scripts")
        if not window_region:
            pytest.skip("Could not find application window")
        
        left, top, width, height = window_region
        
        # Select Hold Key
        dropdown_x = left + (width * 0.5)
        dropdown_y = top + (height * 0.3)
        interact.click_at(dropdown_x, dropdown_y)
        time.sleep(0.5)
        interact.click_at(dropdown_x, dropdown_y + 60)
        time.sleep(1)
        
        # Click Start button
        start_button_x = left + (width * 0.5)
        start_button_y = top + (height * 0.72)
        interact.click_at(start_button_x, start_button_y)
        time.sleep(1)
        
        # Click Stop button (same position as Start)
        interact.click_at(start_button_x, start_button_y)
        time.sleep(1)
        
        # Verify app is still running
        assert interact.get_window_region("Nathan's Python Scripts") is not None





