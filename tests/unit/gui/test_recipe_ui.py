"""
Tests for recipe_ui.py
"""

import pytest
import sys
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
            assert hasattr(recipe_ui, "ingredients_error_label")
            assert hasattr(recipe_ui, "num_of_recipes_label")
            assert hasattr(recipe_ui, "num_of_recipes_entry")
            assert hasattr(recipe_ui, "num_of_recipes_error_label")
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
            recipe_ui.ingredients_entry_var = mocker.MagicMock()
            recipe_ui.num_of_recipes_entry_var = mocker.MagicMock()
            recipe_ui.ingredients_error_label = mocker.MagicMock()
            recipe_ui.num_of_recipes_error_label = mocker.MagicMock()

            recipe_ui.ingredients_entry_var.get.return_value = "tomato, cheese"
            recipe_ui.num_of_recipes_entry_var.get.return_value = '3'

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

            # Asserts
            mock_get_recipes.assert_called_once_with("tomato, cheese", number='3')
            mock_update_ui.assert_called_once_with(fake_recipes)
            recipe_ui.ingredients_error_label.pack_forget.assert_called_once()
            recipe_ui.num_of_recipes_error_label.pack_forget.assert_called_once()

        @pytest.mark.parametrize("entry_value", ["", "   ", None])
        def test_get_and_display_recipes_empty_ingredients_entry(self, recipe_ui, mocker, entry_value):
            """Test that get_and_display_recipes handles empty ingredients entry."""
            # Mocks
            recipe_ui.ingredients_entry_var = mocker.MagicMock()
            recipe_ui.ingredients_error_label = mocker.MagicMock()
            recipe_ui.num_of_recipes_entry_var = mocker.MagicMock()
            recipe_ui.num_of_recipes_error_label = mocker.MagicMock()

            recipe_ui.ingredients_entry_var.get.return_value = entry_value
            
            mock_get_recipes = mocker.patch.object(
                recipe_ui.script, 
                "get_recipes", 
                return_value=[{"error": "Should not call"}]
            )
            mock_update_ui = mocker.patch.object(
                recipe_ui, "display_recipes"
            )

            # Call method
            recipe_ui.get_and_display_recipes()

            # Asserts
            recipe_ui.ingredients_error_label.configure.assert_called_once_with(text="Ingredients cannot be empty.")
            recipe_ui.ingredients_error_label.pack.assert_called_once_with(padx=10, pady=5)

            mock_get_recipes.assert_not_called()
            mock_update_ui.assert_not_called()
        
        @pytest.mark.parametrize("entry_value,is_valid", [
            ("", False),
            ("   ", False),
            (None, False),
            ("abc", False), 
            ("-5", False), 
            ("0", False),
            (sys.float_info.min, False),
            ("0.1", False),
            ("1", True),
            ("20", True),
            ("21", False),
            ("1.5e6", False),
            (sys.maxsize, False),
            (sys.float_info.max, False),
        ])
        def test_get_and_display_recipes_num_of_recipes_entry(self, recipe_ui, mocker, entry_value, is_valid):
            """Test that get_and_display_recipes handles invalid entries within the num_of_recipes entry."""
            # Mocks
            recipe_ui.ingredients_entry_var = mocker.MagicMock()
            recipe_ui.num_of_recipes_entry_var = mocker.MagicMock()
            recipe_ui.ingredients_error_label = mocker.MagicMock()
            recipe_ui.num_of_recipes_error_label = mocker.MagicMock()

            recipe_ui.ingredients_entry_var.get.return_value = "tomato"
            recipe_ui.num_of_recipes_entry_var.get.return_value = str(entry_value)

            mock_get_recipes = mocker.patch.object(
                recipe_ui.script,
                "get_recipes",
                return_value=[{"title": "Tomato Soup", "ingredients": "tomato, water, salt"}],
            )
            mock_update_ui = mocker.patch.object(
                recipe_ui, "display_recipes"
            )

            # Call method
            recipe_ui.get_and_display_recipes()
    
            if not is_valid:
                recipe_ui.num_of_recipes_error_label.configure.assert_called_once()
                recipe_ui.num_of_recipes_error_label.pack.assert_called_once()

                mock_get_recipes.assert_not_called()
                mock_update_ui.assert_not_called()
            else:
                mock_get_recipes.assert_called_once_with("tomato", number=str(entry_value))
                mock_update_ui.assert_called_once()

        def test_get_and_display_recipes_return_empty(self, recipe_ui, mocker):
            """Test that get_and_display_recipes handles empty return from script."""
            # Mocks
            recipe_ui.ingredients_entry_var = mocker.MagicMock()
            recipe_ui.num_of_recipes_entry_var = mocker.MagicMock()
            recipe_ui.recipe_info_label = mocker.MagicMock()

            recipe_ui.ingredients_entry_var.get.return_value = "tomato, cheese"
            recipe_ui.num_of_recipes_entry_var.get.return_value = '2'

            mock_get_recipes = mocker.patch.object(
                recipe_ui.script,
                "get_recipes",
                return_value=[],
            )
            mock_update_ui = mocker.patch.object(
                recipe_ui, "display_recipes"
            )

            # Call method
            recipe_ui.get_and_display_recipes()

            # Asserts
            mock_get_recipes.assert_called_once_with("tomato, cheese", number='2')
            mock_update_ui.assert_not_called()
            recipe_ui.recipe_info_label.configure.assert_called_once_with(text="No recipes found.")

        def test_get_and_display_recipes_exception(self, recipe_ui, mocker):
            """Test that get_and_display_recipes handles exceptions from the script."""
            # Mocks
            recipe_ui.ingredients_entry_var = mocker.MagicMock()
            recipe_ui.num_of_recipes_entry_var = mocker.MagicMock()
            recipe_ui.recipe_info_label = mocker.MagicMock()

            recipe_ui.ingredients_entry_var.get.return_value = "tomato, cheese"
            recipe_ui.num_of_recipes_entry_var.get.return_value = '2'

            mock_get_recipes = mocker.patch.object(
                recipe_ui.script,
                "get_recipes",
                side_effect=Exception("API Error"),
            )
            mock_update_ui = mocker.patch.object(
                recipe_ui, "display_recipes"
            )

            # Call method
            recipe_ui.get_and_display_recipes()

            # Asserts
            mock_get_recipes.assert_called_once_with("tomato, cheese", number='2')
            mock_update_ui.assert_not_called()
            recipe_ui.recipe_info_label.configure.assert_called_once_with(text="An error occurred while fetching recipes. Please try again later.")




