"""
Pytest configuration file.
"""

import sys
import pytest
import requests
from pathlib import Path
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

sys.modules['customtkinter'] = MagicMock()

@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network calls are disabled during tests.")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())