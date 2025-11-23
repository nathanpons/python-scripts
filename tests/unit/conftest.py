"""
Pytest configuration file.
"""

import sys
import pytest
import requests
import customtkinter as ctk
from pathlib import Path
from unittest.mock import MagicMock
from src.gui.main_window import MainWindow

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

sys.modules['customtkinter'] = MagicMock()

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