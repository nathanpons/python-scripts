"""
Pytest configuration file.
"""
import sys
import time
import json
import pytest
import psutil
import logging
import requests
import keyboard
import pyautogui
import subprocess
import customtkinter as ctk
import pygetwindow as gw
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

@pytest.fixture(scope="session")
def pyautogui_config():
    """Configure pyautogui for testing."""
    # Slow down pyautogui to make actions more reliable
    pyautogui.PAUSE = 0.5
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    
    return {
        "screen_width": screen_width,
        "screen_height": screen_height,
        "pause": 0.5
    }

@pytest.fixture()
def app_process(mocker):
    """Start the actual application in a subprocess."""
    # Mock external API calls at the module level
    mocker.patch('requests.get', return_value=mocker.Mock(
        status_code=200,
        json=lambda: {"weather": [{"main": "Clear"}], "main": {"temp": 25.5}}
    ))
    
    # Start the app in a subprocess
    app_path = Path(__file__).parent.parent.parent / "src" / "main.py"
    
    process = subprocess.Popen(
        [sys.executable, str(app_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(3)
    
    yield process
    
    # Cleanup - kill the process and all children
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except:
        pass
    
    process.terminate()
    process.wait(timeout=5)

@pytest.fixture()
def reference_screenshots():
    """Path to reference screenshots for visual verification."""
    logging.debug(f"Reference screenshots path: {Path(__file__).parent / 'reference_screenshots'}")
    return Path(__file__).parent / "reference_screenshots"

@pytest.fixture()
def interact(reference_screenshots):
    """Helper fixture for GUI interactions."""
    class GUIInteractor:
        def __init__(self, reference_screenshots_path):
            self.reference_screenshots = reference_screenshots_path

        def click_at(self, x, y, clicks=1, button='left'):
            """Click at specific coordinates."""
            pyautogui.click(x, y, clicks=clicks, button=button)
            time.sleep(0.2)
        
        def type_text(self, text, interval=0.1):
            """Type text with interval between keys."""
            pyautogui.write(text, interval=interval)
            time.sleep(0.2)
        
        def press_key(self, key):
            """Press a single key."""
            try:
                logging.debug(f"Pressing key: {key}")
                keyboard.press_and_release(key)
                time.sleep(0.2)
            except Exception as e:
                logging.error(f"Error pressing key {key}: {e}")

        def find_on_screen(self, image_name, confidence=0.8, region=None, should_find=True):
            """
            Find a reference image on screen.
            
            Args:
                image_name: Name of image file (e.g., 'start_button.png')
                confidence: Match confidence (0.0 to 1.0)
                region: Optional (left, top, width, height) to search in
            
            Returns:
                Box coordinates (left, top, width, height) or None
            """
            image_path = self.reference_screenshots / "hold_key" / image_name
            logging.debug(f"Looking for image on screen: {image_path} in region: {region}")
            
            if not image_path.exists():
                logging.warning(f"Warning: Reference image not found: {image_path}")
                return None
            
            try:
                location = pyautogui.locateOnScreen(
                    str(image_path), 
                    confidence=confidence,
                    region=region
                )
                return location
            except Exception as e:
                if should_find:
                    logging.error(f"Error finding image {image_name} in region {region}: {e}")
                    debug_screenshot = pyautogui.screenshot(region=region)
                    debug_path = self.reference_screenshots / "debug_screenshots" / f"debug_{image_name}_not_found.png"
                    debug_screenshot.save(debug_path)
                return None
        
        def click_image(self, image_name, confidence=0.8, num_clicks=1,region=None):
            """Find and click an image on screen."""
            try:
                image_path = self.reference_screenshots / "hold_key" / image_name
                location = pyautogui.locateOnScreen(str(image_path), confidence=confidence, region=region)
                if location:
                    x, y = pyautogui.center(location)
                    for _ in range(num_clicks):
                        self.click_at(x, y)
                    return True
                raise Exception("Image not found")
            except Exception as e:
                logging.error(f"Error finding image {image_name} in region {region}: {e}")
                debug_screenshot = pyautogui.screenshot(region=region)
                debug_path = self.reference_screenshots / "debug_screenshots" / f"debug_{image_name}_not_found.png"
                debug_screenshot.save(debug_path)
                return False
            
        def assert_visible(self, image_name, confidence=0.8, region=None, timeout=5):
            """Assert that an image is visible on screen during the given timeout period."""
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                location = self.find_on_screen(image_name, confidence, region, should_find=True)
                if location:
                    return True
                time.sleep(0.5)
            
            raise AssertionError(
                f"Image '{image_name}' not found on screen within {timeout} seconds"
            )
        
        def assert_not_visible(self, image_name, confidence=0.8, region=None):
            """Assert that an image is not visible on screen."""
            location = self.find_on_screen(image_name, confidence=confidence, region=region, should_find=False)
            if location:
                raise AssertionError(f"Image {image_name} was found on screen but should not be.")
            return True

        def get_window_region(self, title_contains):
            """
            Get window region by title (Windows only).
            Returns (left, top, width, height) or None.
            """
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(title_contains)
                if windows:
                    window = windows[0]
                    return (window.left, window.top, window.width, window.height)
            except Exception as e:
                logging.error(f"Error getting window region: {e}")
                
            return None
        
        def take_screenshot(self, save_path, region=None):
            """Take a screenshot and save to path."""
            screenshot = pyautogui.screenshot(region=region)
            screenshot.save(save_path)
            logging.debug(f"Screenshot saved to {save_path}")
    
    return GUIInteractor(reference_screenshots)

@pytest.fixture()
def click_image_with_logging(interact):
    """Helper to click an image with logging."""
    def _click_image(image_name, confidence=0.8, num_clicks=1, region=None):
        logging.debug(f"Attempting to click image: {image_name} with confidence {confidence}")
        if not interact.click_image(image_name, confidence=confidence, num_clicks=num_clicks, region=region):
            logging.error(f"Could not find image: {image_name}")
            pytest.fail("Test Ended. Cannot proceed.")
        
        time.sleep(0.2)
        
    return _click_image

@pytest.fixture()
def key_logger_window():
    """Launch a test window for logging key and mouse events."""
    logger = Path(__file__).parent / "key_logger.py"
    log_file = Path(__file__).parent / "debug_files" / "key_log.txt"

    # Launch the key logger in a subprocess
    process = subprocess.Popen(
        [sys.executable, str(logger)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for the window to initialize
    time.sleep(2)

    yield {"process": process, "log_file": log_file}

    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=3)
    except:
        process.kill()
        
@pytest.fixture()
def read_key_log():
    """Helper to read the key log JSON file."""
    def _read(log_file_path):
        """Read and parse the key log file."""
        if not log_file_path.exists():
            return []
        
        try:
            with open(log_file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            logging.error(f"Error reading key log: {e}")
            return []
    
    return _read

@pytest.fixture()
def focus_window():
    """Helper to focus a window by title."""
    def _focus_window(title):
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.5)  # Wait for focus to take effect
                return True
        except Exception as e:
            logging.error(f"Error focusing window: {e}")
        return False
    
    return _focus_window

@pytest.fixture(autouse=True, scope="session")
def clear_debug_screenshots():
    """Clear debug screenshots before test session."""
    debug_dir = Path(__file__).parent / "reference_screenshots" / "debug_screenshots"
    if debug_dir.exists():
        for file in debug_dir.iterdir():
            if file.is_file():
                file.unlink()
    else:
        debug_dir.mkdir(parents=True, exist_ok=True)

@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network calls are disabled during tests.")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())

@pytest.fixture()
def mock_requests(mocker):
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    return mock_response


