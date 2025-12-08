"""
Test cases for the Hold Key end-to-end functionality.
"""

import pytest
import time
import logging

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

    def test_custom_settings(self, app_process, interact, click_image_with_logging, key_logger_window, read_key_log, focus_window):
        """Test that the correct key is being pressed with custom key and interval."""
        time.sleep(0.5)

        log_file = key_logger_window["log_file"]
        focus_window("Nathan's Python Scripts")

        # Map the application window
        window_region = interact.get_window_region("Nathan's Python Scripts")
        if not window_region:
            pytest.skip("Could not find application window")
        
        left, top, width, height = window_region

        # USER STEPS
        
        # # Click Dropdown
        # # Select Hold Key
        # # Click Switch to Keyboard Input
        # # Set Key to "b"
        # # Set Toggle key to "F7"
        # # Enable Rapid pressing
        # # Set Interval to "200"
        # # Click Start
        # # Open Key Logger Window
        # # Focus Key Logger Window
        # # Press Toggle Key (F7)
        # # Wait one second
        # # Verify "b" is being pressed at ~200ms intervals in Key Logger Window
        
        # Click Dropdown
        dropdown_x = left + (width * 0.5)
        dropdown_y = top + (height * 0.3)
        interact.click_at(dropdown_x, dropdown_y)
        time.sleep(0.2)
        
        # # Search within dropdown area only
        # dropdown_region = (
        #     int(left + width * 0.2),
        #     int(top + height * 0.25),
        #     int(width * 0.6),
        #     int(height * 0.4)
        # )
        
        # Select Hold Key 
        click_image_with_logging('hold_key_option.png', confidence=0.9, region=window_region)
        
        # Click Switch to Keyboard Input
        click_image_with_logging('switch_mouse.png', region=window_region)

        # Set Key to "b"
        click_image_with_logging('select_key_a.png', num_clicks=2, region=window_region)
        interact.type_text("b")

        # Set Toggle key to "F7"
        click_image_with_logging('select_toggle_f8.png', region=window_region)
        click_image_with_logging('toggle_option_f7.png', confidence=0.9, region=window_region)

        # Enable Rapid pressing
        click_image_with_logging('switch_rapid.png', region=window_region)

        # Set Interval to "200"
        click_image_with_logging('interval_default.png', num_clicks=2, region=window_region)
        interval_time_milliseconds = "200"
        interact.type_text(interval_time_milliseconds)

        # Click Start
        click_image_with_logging('start_button.png', region=window_region)
        
        # Focus Key Logger Window
        focus_window("Key Logger")

        # Press Toggle Key
        interact.press_key("f7")
        time.sleep(1)
        interact.press_key("f7")

        # Verify "b" is being pressed at ~200ms intervals in Key Logger Window
        key_log = read_key_log(log_file)

        key_presses = [
            entry for entry in key_log
                if entry["type"] == "key" and entry["key"] == "b"
        ]

        # Assertions
        assert len(key_presses) >= 4, f"Expected multiple 'b' key presses, found {len(key_presses)}"
        






