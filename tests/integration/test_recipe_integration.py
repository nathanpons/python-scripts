"""
Tests for the recipe workflow
"""

import pytest
import time
import os
from PIL import Image
from gui.recipe_ui import RecipeUI
from scripts.recipe_script import RecipeScript

@pytest.fixture()
def recipe_ui(app_window, mocker, mock_requests):
    """Fixture to set up the Recipe UI in the main application window."""
    # Mock the config file reading for RecipeScript
    mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
    mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
    
    # Mock os.path.join to return a valid path
    original_join = os.path.join
    def mock_join(*args):
        # Only mock the config path, let other paths work normally
        if 'api_config.json' in args:
            return 'config/api_config.json'
        return original_join(*args)
    mocker.patch('os.path.join', side_effect=mock_join)

    app_window.script_type.set("Recipe Finder")
    app_window.on_selection("Recipe Finder")
    app_window.root.update()
    time.sleep(0.5)

    recipe_ui = app_window.current_ui
    assert recipe_ui is not None, "RecipeUI was not created"

    app_window.root.update()
    time.sleep(0.5)

    yield recipe_ui

    try:
        if hasattr(recipe_ui, 'cleanup'):
            recipe_ui.cleanup()
        app_window.root.update()
        time.sleep(0.1)
    except Exception as e:
        print(f"Cleanup failed in recipe_ui fixture: {e}")

@pytest.fixture()
def mock_recipe_response():
    """Provides a mock response for recipe fetching."""
    return [
        {
            "id": 641122,
            "title": "Curry Leaves Potato Chips",
            "image": "https://img.spoonacular.com/recipes/641122-312x231.jpg",
            "imageType": "jpg",
            "usedIngredientCount": 1,
            "missedIngredientCount": 2,
            "missedIngredients": [
                {
                    "id": 2009,
                    "amount": 1.0,
                    "unit": "tsp",
                    "unitLong": "teaspoon",
                    "unitShort": "tsp",
                    "aisle": "Spices and Seasonings",
                    "name": "chili powder",
                    "original": "1 tsp plain chili powder",
                    "originalName": "plain chili powder",
                    "meta": ["plain"],
                    "extendedName": "plain chili powder",
                    "image": "https://img.spoonacular.com/ingredients_100x100/chili-powder.jpg",
                },
                {
                    "id": 93604,
                    "amount": 3.0,
                    "unit": "sprigs",
                    "unitLong": "sprigs",
                    "unitShort": "sprigs",
                    "aisle": "Ethnic Foods",
                    "name": "curry leaves",
                    "original": "3-4 sprigs curry leaves",
                    "originalName": "curry leaves",
                    "meta": [],
                    "image": "https://img.spoonacular.com/ingredients_100x100/curry-leaves.jpg",
                },
            ],
            "usedIngredients": [
                {
                    "id": 10011355,
                    "amount": 3.0,
                    "unit": "",
                    "unitLong": "",
                    "unitShort": "",
                    "aisle": "Produce",
                    "name": "potatoes - remove skin",
                    "original": "3 potatoes - remove skin, sliced thinly and soaked in ice water for 10-15 minutes.",
                    "originalName": "potatoes - remove skin, sliced thinly and soaked in ice water for 10-15 minutes",
                    "meta": ["sliced", "for 10-15 minutes."],
                    "image": "https://img.spoonacular.com/ingredients_100x100/red-potatoes.jpg",
                }
            ],
            "unusedIngredients": [],
            "likes": 4,
        }
    ]

class TestRecipeIntegration:
    """Integration tests for the Recipe Finder script."""

    class TestRecipeInitialization:
        """Tests for RecipeUI initialization."""

        def test_recipe_ui_initialization(self, recipe_ui):
            """Test that the RecipeUI initializes correctly."""
            assert isinstance(recipe_ui, RecipeUI)
            assert recipe_ui.ingredients_entry is not None
            assert recipe_ui.get_recipe_button is not None

        def test_recipe_script_selection_creates_ui(self, app_window, mocker):
            """Test that selecting the Recipe script creates the RecipeUI."""
            mocker.patch('builtins.open', mocker.mock_open(read_data='{"api_gateway_url": "http://fakeapi.test"}'))
            mocker.patch('os.path.join', return_value="fake_icon.ico")
            
            app_window.script_type.set("Recipe Finder")
            app_window.on_selection("Recipe Finder")
            app_window.root.update()
            time.sleep(0.1)

            assert app_window.current_ui is not None
            assert isinstance(app_window.current_ui, RecipeUI)

    class TestRecipeWorkflow:
        """Tests for the Recipe workflow functionality."""

        def test_full_recipe_workflow_success(self, mocker, recipe_ui, mock_recipe_response, mock_requests):
            """Test complete successful workflow."""
            mock_requests.json.return_value = mock_recipe_response
            mock_requests.status_code = 200

            mock_image = Image.new('RGB', (200, 200), color='red')
            mocker.patch.object(recipe_ui.script, 'get_recipe_image', return_value=mock_image)
                
            # Enter ingredients
            recipe_ui.ingredients_entry.insert(0, "tomato, cheese")
            recipe_ui.num_of_recipes_entry.insert(0, "5")
            
            recipe_ui.parent_frame.update()
            time.sleep(0.1)
            
            # Fetch recipes
            recipe_ui.get_and_display_recipes()
            recipe_ui.parent_frame.update()
            time.sleep(0.1)
            
            # Assertion
            assert mock_requests.json.called

        def test_recipe_workflow_empty_ingredients(self, recipe_ui):
            """Test workflow with empty ingredients."""
            recipe_ui.get_and_display_recipes()
            
            # Verify error is shown
            if hasattr(recipe_ui, 'ingredients_error_label'):
                error_text = recipe_ui.ingredients_error_label.cget("text")
                assert "cannot be empty" in error_text.lower()

        def test_recipe_workflow_without_images(self, mocker, recipe_ui, mock_recipe_response, mock_requests):
            """Test workflow when image loading fails."""
            mock_requests.json.return_value = mock_recipe_response
            mock_requests.status_code = 200
            
            # Mock get_recipe_image to return None (simulating failed image load)
            mocker.patch.object(recipe_ui.script, 'get_recipe_image', return_value=None)
            
            recipe_ui.ingredients_entry.insert(0, "tomato, cheese")
            recipe_ui.num_of_recipes_entry.insert(0, "5")
            
            # This should not crash even if images fail to load
            recipe_ui.get_and_display_recipes()
            recipe_ui.parent_frame.update()
            time.sleep(0.1)
            
            assert mock_requests.json.called




