"""
Pytest configuration file.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

sys.modules['customtkinter'] = MagicMock()