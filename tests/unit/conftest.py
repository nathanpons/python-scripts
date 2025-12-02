"""
Pytest configuration file.
"""
import os
import sys
import pytest
import requests
from pathlib import Path
from unittest.mock import MagicMock, mock_open

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

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

@pytest.fixture(autouse=True)
def mock_config_file(mocker):
    """Automatically mock config file for all unit tests."""
    mock_config_data = '{"api_gateway_url": "https://test-api.example.com"}'
    mocker.patch('builtins.open', mock_open(read_data=mock_config_data))


@pytest.fixture(autouse=True)
def mock_resource_paths(mocker):
    """Mock resource path functions to avoid file system dependencies."""
    mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
    
    original_join = os.path.join
    def mock_join(*args):
        if 'api_config.json' in args:
            return 'config/api_config.json'
        return original_join(*args)
    mocker.patch('os.path.join', side_effect=mock_join)