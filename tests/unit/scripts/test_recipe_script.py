"""
Tests for recipe_script.py.
"""
import pytest
from src.scripts.recipe_script import RecipeScript

@pytest.fixture()
def script():
    script = RecipeScript()
    yield script

class TestRecipeScript:
    """Tests for RecipeScript methods."""
    class TestRecipeInitialization:
        """Tests for RecipeScript initialization."""
        def test_default_initialization(self, script):
            assert script.ignore_pantry is True
            assert script.base_url.startswith("https")

        def test_config_file_not_found(self, mocker):
            mocker.patch(
                "builtins.open",
                side_effect=FileNotFoundError,
            )
            with pytest.raises(FileNotFoundError, match="Configuration file not found"):
                RecipeScript()

        def test_missing_api_gateway_url(self, mocker):
            mocker.patch(
                "builtins.open",
                mocker.mock_open(read_data='{"some_other_key": "value"}'),)
            with pytest.raises(KeyError, match="API_GATEWAY_URL not found in configuration"):
                RecipeScript()

        def test_generic_exception_during_config_load(self, mocker):
            mocker.patch(
                "builtins.open",
                side_effect=Exception("Generic error"),
            )
            with pytest.raises(Exception, match="An error occurred while loading configuration"):
                RecipeScript()

    class TestGetRecipes:
        """Tests for get_recipes method."""
        def test_get_recipes_parameters(self, script, mocker):
            """Test that get_recipes constructs the correct parameters for the API call."""
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": 1, "title": "Test Recipe"}]
            mock_get = mocker.patch("requests.get", return_value=mock_response)

            ingredients = "tomato,cheese"
            number = 2
            script.get_recipes(ingredients, number=number)

            expected_params = {
                "ingredients": ingredients,
                "number": number,
                "ignorePantry": "true",
                "ranking": script.MAXIMIZE_USED_INGREDIENTS,
            }
            mock_get.assert_called_with(f"{script.base_url}/recipe", params=expected_params)
            
        def test_get_recipes_success(self, script, mocker):
            """Test successful recipe retrieval."""
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"id": 1, "title": "Test Recipe"}
            ]

            mocker.patch("requests.get", return_value=mock_response)

            result = script.get_recipes("tomato,cheese", number=2)
            assert result == [{"id": 1, "title": "Test Recipe"}]

        def test_get_recipes_no_recipes_found(self, script, mocker):
            """Test scenario where no recipes are found."""
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []

            mocker.patch("requests.get", return_value=mock_response)

            result = script.get_recipes("unknown_ingredient", number=1)
            assert result == '{"error": "No recipes found."}'

        def test_get_recipes_http_error(self, script, mocker):
            """Test HTTP error during recipe retrieval."""
            mock_response = mocker.Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")

            mocker.patch("requests.get", return_value=mock_response)

            result = script.get_recipes("tomato", number=1)
            assert result == '{"error": "Error finding recipes."}'

        def test_get_recipes_exception(self, script, mocker):
            """Test generic exception during recipe retrieval."""
            mocker.patch("requests.get", side_effect=Exception("Network error"))

            result = script.get_recipes("tomato", number=1)
            assert result == '{"error": "Error finding recipes."}'

    class TestGetRecipeImage:
        """Tests for get_recipe_image method."""
        def test_get_recipe_image_success(self, script, mocker):
            """Test successful image retrieval."""
            image_content = b"fake_image_data"
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.content = image_content

            mocker.patch("requests.get", return_value=mock_response)
            mock_image_open = mocker.patch("PIL.Image.open")
            mock_pil_image = mocker.Mock()
            mock_image_open.return_value = mock_pil_image

            result = script.get_recipe_image("http://example.com/image.jpg")
            assert result == mock_pil_image
            mock_image_open.assert_called_once()

        @pytest.mark.parametrize("invalid_url", [
            None, 
            "",
        ])
        def test_get_recipe_image_empty_url(self, script, invalid_url):
            """Test scenario where image URL is empty."""
            result = script.get_recipe_image(invalid_url)
            assert result == '{"error": "No image URL provided for recipe."}'

        def test_get_recipe_image_http_error(self, script, mocker):
            """Test HTTP error during image retrieval."""
            mock_response = mocker.Mock()
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            
            mocker.patch("requests.get", return_value=mock_response)

            result = script.get_recipe_image("http://example.com/image.jpg")
            assert result == '{"error": "Error fetching recipe image."}'
        
        def test_get_recipe_image_network_error(self, script, mocker):
            """Test network error during image retrieval."""
            mocker.patch("requests.get", side_effect=Exception("Network error"))

            result = script.get_recipe_image("http://example.com/image.jpg")
            assert result == '{"error": "Error fetching recipe image."}'

        def test_get_recipe_image_invalid_image_data(self, script, mocker):
            """Test scenario where image data is invalid."""
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            mock_response.content = b"not_an_image"

            mocker.patch("requests.get", return_value=mock_response)
            mocker.patch("PIL.Image.open", side_effect=Exception("Invalid image data"))

            result = script.get_recipe_image("http://example.com/image.jpg")
            assert result == '{"error": "Error fetching recipe image."}'