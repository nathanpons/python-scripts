"""
Test cases for the Hold Key end-to-end functionality.
"""

import pytest
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class TestHoldKeyE2E:
    """End-to-end tests for the Hold Key functionality."""
    
    def test_user_starts_and_stops_hold_key(self, app_process, interact):
        """User starts hold key, then stops it with screenshot verification."""
        time.sleep(0.5)
        
        # Map the application window
        window_region = interact.get_window_region("Nathan's Python Scripts")
        if not window_region:
            pytest.skip("Could not find application window")
        
        left, top, width, height = window_region
        
        # Click on dropdown
        dropdown_x = left + (width * 0.5)
        dropdown_y = top + (height * 0.3)
        interact.click_at(dropdown_x, dropdown_y)
        time.sleep(0.5)
        
        # Search within dropdown area only
        dropdown_region = (
            int(left + width * 0.2),
            int(top + height * 0.25),
            int(width * 0.6),
            int(height * 0.4)
        )
        
        # Click the Hold Key option 
        logging.debug(f"Attempting to click Hold Key option using image detection")
        if not interact.click_image('hold_key_option.png', confidence=0.9, region=dropdown_region):
            # Fallback to coordinate-based click if screenshot not found
            logging.debug("Using fallback coordinate click for Hold Key option")
            interact.click_at(dropdown_x, dropdown_y + 60)
        
        time.sleep(1)

        # Assert start button is visible
        interact.assert_visible('start_button.png', confidence=0.8, timeout=3)
        
        # Assert status shows "Stopped"
        status_region = (
            int(left + width * 0.2),
            int(top + height * 0.72),
            int(width * 0.6),
            int(height * 0.2)
        )
        interact.assert_visible('status_stopped.png', confidence=0.7, region=status_region, timeout=2)
        
        # Click start button using screenshot detection
        logging.debug(f"Attempting to click Start button using image detection")
        if not interact.click_image('start_button.png', confidence=0.7, region=status_region):
            # Fallback to coordinate-based click
            logging.debug("Using fallback coordinate click for Start button")
            start_button_x = left + (width * 0.5)
            start_button_y = top + (height * 0.78)
            interact.click_at(start_button_x, start_button_y)
        
        time.sleep(1)
        
        # Assert stop button is visible and status is running
        logging.debug("Asserting that Stop button is visible and status is running")
        interact.assert_visible('stop_button_hovered.png', confidence=0.9, region=status_region, timeout=3)
        interact.assert_visible('status_running.png', confidence=0.7, region=status_region, timeout=2)
        interact.assert_not_visible('start_button_hovered.png', confidence=0.9, region=status_region)
        interact.assert_not_visible('status_stopped.png', confidence=0.7, region=status_region)
        

        # Click stop button using screenshot detection
        logging.debug(f"Attempting to click Stop button using image detection")
        if not interact.click_image('stop_button_hovered.png', confidence=0.8, region=status_region):
            # Fallback to coordinate-based click
            logging.debug("Using fallback coordinate click for Stop button")
            start_button_x = left + (width * 0.5)
            start_button_y = top + (height * 0.72)
            interact.click_at(start_button_x, start_button_y)
        
        time.sleep(1)
        
        # Assert stop button is pressed and status is stopped
        logging.debug("Asserting that Start button is visible and status is stopped")
        interact.assert_visible('start_button_hovered.png', confidence=0.9, region=status_region, timeout=3)
        interact.assert_visible('status_stopped.png', confidence=0.7, region=status_region, timeout=2)
        interact.assert_not_visible('stop_button_hovered.png', confidence=0.9, region=status_region)
        interact.assert_not_visible('status_running.png', confidence=0.7, region=status_region)
        
        # Verify app is still running
        assert interact.get_window_region("Nathan's Python Scripts") is not None





