"""
Pytest configuration file.
"""

import sys
import pytest
import requests
import time
import subprocess
import psutil
import os
import pyautogui
import logging
import customtkinter as ctk
from pathlib import Path
from src.gui.main_window import MainWindow

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
    return Path(__file__).parent / "reference_screenshots"

@pytest.fixture()
def interact():
    """Helper fixture for GUI interactions."""
    class GUIInteractor:
        def __init__(self, reference_screenshots_path):
            self.reference_screenshots = reference_screenshots_path

        def click_at(self, x, y, clicks=1, button='left'):
            """Click at specific coordinates."""
            pyautogui.click(x, y, clicks=clicks, button=button)
            time.sleep(0.3)
        
        def type_text(self, text, interval=0.1):
            """Type text with interval between keys."""
            pyautogui.write(text, interval=interval)
            time.sleep(0.2)
        
        def press_key(self, key):
            """Press a single key."""
            pyautogui.press(key)
            time.sleep(0.2)

        def find_on_screen(self, image_name, confidence=0.8, region=None):
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
                logging.error(f"Error finding image {image_name}: {e}")
                return None
        
        def click_image(self, image_path, confidence=0.8):
            """Find and click an image on screen."""
            try:
                location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
                if location:
                    x, y = pyautogui.center(location)
                    self.click_at(x, y)
                    return True
                return False
            except Exception as e:
                logging.error(f"Error clicking image: {e}")
                return False
        
        def assert_not_visible(self, image_name, confidence=0.8, region=None):
            """Assert that an image is not visible on screen."""
            location = self.find_on_screen(image_name, confidence=confidence, region=region)
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

@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network calls are disabled during tests.")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())

@pytest.fixture()
def app_window(mocker):
    mocker.patch('os.path.join', return_value="fake_icon.ico")
    mocker.patch.object(ctk.CTk, 'iconbitmap')

    mocker.patch('keyboard.add_hotkey')
    mocker.patch('keyboard.remove_hotkey')
    mocker.patch('keyboard.press')
    mocker.patch('keyboard.release')
    mocker.patch('pyautogui.mouseDown')
    mocker.patch('pyautogui.mouseUp')

    root = None
    main_window = None

    try:
        # Force Tkinter to use correct TCL/TK path
        os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python310\tcl\tcl8.6'
        os.environ['TK_LIBRARY'] = r'C:\Program Files\Python310\tcl\tk8.6'
        
        # Create root window
        root = ctk.CTk()
        root.update()
        
        # Create MainWindow
        main_window = MainWindow(root)
        root.update()
        
    except Exception as e:
        # Cleanup partial initialization
        if root:
            try:
                root.destroy()
            except:
                pass
        pytest.skip(f"Skipping test due to GUI initialization failure: {e}")

    yield main_window

    # Cleanup
    try:
        # Stop any running scripts
        if main_window and hasattr(main_window, 'current_ui') and main_window.current_ui:
            if hasattr(main_window.current_ui, 'script') and main_window.current_ui.script:
                if hasattr(main_window.current_ui.script, 'is_running'):
                    if main_window.current_ui.script.is_running:
                        if hasattr(main_window.current_ui.script, 'stop'):
                            main_window.current_ui.script.stop()
                        root.update()
                        time.sleep(0.3)
            
            # Cleanup UI
            if hasattr(main_window.current_ui, 'cleanup'):
                main_window.current_ui.cleanup()
        
        # Close main window
        if main_window:
            main_window.on_close()
        
        # Destroy root thoroughly
        if root:
            root.quit()
            root.update_idletasks()
            time.sleep(0.5)  # Increased delay
            
            # Force destruction
            try:
                root.destroy()
            except:
                pass
            
            # Clear Tkinter's internal state
            try:
                import tkinter
                if hasattr(tkinter, '_default_root'):
                    tkinter._default_root = None
            except:
                pass
            
    except Exception as e:
        logging.error(f"[Cleanup Warning] {e}")
        if root:
            try:
                root.destroy()
            except:
                pass

@pytest.fixture()
def mock_requests(mocker):
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    return mock_response


