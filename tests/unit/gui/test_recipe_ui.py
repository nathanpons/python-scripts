"""
Tests for recipe_ui.py
"""
import pytest
from src.gui.recipe_ui import RecipeUI

@pytest.fixture()
def recipe_ui_instance(mocker):
    mock_parent_frame = mocker.MagicMock()
    recipe_ui_instance = RecipeUI(mock_parent_frame)
    yield recipe_ui_instance

class TestRecipeUI:
    """Tests for the RecipeUI class."""
    
    class TestRecipeUIInitialization:
        """Tests for the __init__ method of RecipeUI."""
        
        def test_recipe_ui_initialization(self, recipe_ui_instance):
            """Test that the RecipeUI instance initializes correctly."""
            assert recipe_ui_instance.parent_frame is not None
            assert hasattr(recipe_ui_instance, 'script')
            assert recipe_ui_instance.default_font is not None
            assert recipe_ui_instance.title_font is not None