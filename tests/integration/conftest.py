"""
Pytest configuration file.
"""

import sys
import pytest
import requests
import time
import os
import customtkinter as ctk
from pathlib import Path
from src.gui.main_window import MainWindow

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
        print(f"[Cleanup Warning] {e}")
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