"""
Tests for recipe_ui.py
"""

import pytest
from src.gui.recipe_ui import RecipeUI


@pytest.fixture()
def recipe_ui(mocker):
    mock_parent_frame = mocker.MagicMock()
    recipe_ui = RecipeUI(mock_parent_frame)
    yield recipe_ui


class TestRecipeUI:
    """Tests for the RecipeUI class."""

    class TestRecipeUIInitialization:
        """Tests for the __init__ method of RecipeUI."""

        def test_recipe_ui_initialization(self, recipe_ui):
            """Test that the RecipeUI instance initializes correctly."""
            assert recipe_ui.parent_frame is not None
            assert hasattr(recipe_ui, "script")
            assert recipe_ui.default_font is not None
            assert recipe_ui.title_font is not None

    class TestSetupUI:
        """Tests for the setup_ui method of RecipeUI."""

        def test_setup_ui_components(self, recipe_ui):
            """Test that the UI components are set up correctly."""
            # Main Frame Components
            assert hasattr(recipe_ui, "recipe_dashboard_frame")
            assert hasattr(recipe_ui, "dashboard_title_label")

            # Ingredients Input Components
            assert hasattr(recipe_ui, "ingredients_frame")
            assert hasattr(recipe_ui, "ingredients_label")
            assert hasattr(recipe_ui, "ingredients_entry")
            assert hasattr(recipe_ui, "num_of_ingredients_label")
            assert hasattr(recipe_ui, "num_of_ingredients_entry")
            assert hasattr(recipe_ui, "get_recipe_button")

            # Recipe Display Components
            assert hasattr(recipe_ui, "recipe_display_frame")
            assert hasattr(recipe_ui, "recipe_title_label")
            assert hasattr(recipe_ui, "recipe_info_label")

    class TestGetAndDisplayRecipes:
        """Tests for the get_and_display_recipes method of RecipeUI."""

        def test_get_and_display_recipes_success(self, recipe_ui, mocker):
            """Test that get_and_display_recipes calls the script and updates the UI."""
            # Mocks
            mock_ingredients = mocker.patch.object(
                recipe_ui.ingredients_entry,
                "get",
                return_value="tomato, cheese",
            )
            mock_num_of_ingredients = mocker.patch.object(
                recipe_ui.num_of_ingredients_entry, "get", return_value="3"
            )
            # Debug: Verify mocks are working
            print(f"ingredients_entry.get() returns: {recipe_ui.ingredients_entry.get()}")
            print(f"num_of_ingredients_entry.get() returns: {recipe_ui.num_of_ingredients_entry.get()}")
    
            fake_recipes = [
                {"title": "Tomato Soup", "ingredients": "tomato, water, salt"},
                {"title": "Cheese Sandwich", "ingredients": "bread, cheese, butter"},
            ]
            mock_get_recipes = mocker.patch.object(
                recipe_ui.script,
                "get_recipes",
                return_value=fake_recipes,
            )
            mock_update_ui = mocker.patch.object(
                recipe_ui, "display_recipes"
            )

            # Call method
            recipe_ui.get_and_display_recipes()
            
            print(f"get_recipes called with: {mock_get_recipes.call_args}")

            # Asserts
            mock_get_recipes.assert_called_once_with("tomato, cheese", '3')
            mock_update_ui.assert_called_once_with(fake_recipes)
