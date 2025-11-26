"""
Tests for hold_key_ui.py
"""
import pytest
from unittest.mock import MagicMock, Mock
from src.gui.main_window import MainWindow

@pytest.fixture
def mock_root():
    """Fixture to set up a mock CTK root window."""
    mock_root = MagicMock()

    mock_root.winfo_width = MagicMock(return_value=400)
    mock_root.winfo_height = MagicMock(return_value=500)
    mock_root.winfo_screenwidth = MagicMock(return_value=1920)
    mock_root.winfo_screenheight = MagicMock(return_value=1080)
    return mock_root

@pytest.fixture
def main_window(mock_root, mocker):
    """Fixture to set up MainWindow instance for tests."""
    mocker.patch('src.gui.main_window.ctk.CTkFont')
    mocker.patch('src.gui.main_window.ctk.CTkFrame')
    mocker.patch('src.gui.main_window.ctk.CTkLabel')
    mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
    mocker.patch('src.gui.main_window.ctk.StringVar')
    
    mocker.patch('os.path.join', return_value='fake_icon.ico')
    mocker.patch.object(mock_root, 'iconbitmap')
    
    window = MainWindow(mock_root)
    
    yield window
    window.on_close()

class TestMainWindowInitialization:
    """Test that MainWindow initializes correctly."""
    def test_window_root_variables_initialization(self, mock_root, mocker):
        """Test that window variables are set correctly."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        
        MainWindow(mock_root)

        mock_root.title.assert_called_with("Nathan's Python Scripts")
        mock_root.geometry.assert_called_with("400x500")
        mock_root.iconbitmap.assert_called_once()

    def test_window_initialization(self, main_window):
        """Test that MainWindow initializes correctly."""
        window = main_window

        assert window.root is not None
        assert window.WINDOW_SIZE == "400x500"
        assert window.current_ui is None
        assert window.scripts_list == ["None", "Hold Key", "Weather", "Recipe Finder"]

    def test_fonts_created(self, main_window):
        """Test that fonts are created."""
        assert main_window.default_font is not None
        assert main_window.title_font is not None

        assert hasattr(main_window.default_font, 'cget')
        assert hasattr(main_window.title_font, 'cget')

    def test_ui_setup_called(self, mock_root, mocker):
        """Test that setup_ui is called during initialization."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        
        mock_setup_ui = mocker.patch.object(MainWindow, 'setup_ui')
        MainWindow(mock_root)
        mock_setup_ui.assert_called_once()

    def test_close_protocol_registered(self, mock_root, main_window):
        """Test that WM_DELETE_WINDOW protocol is registered."""
        mock_root.protocol.assert_called_with("WM_DELETE_WINDOW", main_window.on_close)
        
class TestMainWindowSetupUI:
    """Test that UI components are created in setup_ui."""
    def test_ui_creates_frames(self, mock_root, mocker):
        """Test that main, header, and selection frames are created."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.StringVar')

        mock_frame = mocker.patch("src.gui.main_window.ctk.CTkFrame")
        mock_label = mocker.patch("src.gui.main_window.ctk.CTkLabel")
        mock_option_menu = mocker.patch("src.gui.main_window.ctk.CTkOptionMenu")

        window = MainWindow(mock_root)

        assert mock_frame.call_count == 4  # main, header, selection, dynamic frames
        assert mock_label.call_count == 3  # header, selection, default_ui labels
        mock_option_menu.assert_called_once()

        assert mock_label.call_args_list[0].kwargs['text'] == "Nathan's Python Scripts"
        assert mock_label.call_args_list[1].kwargs['text'] == "Select a script:"
        assert mock_label.call_args_list[2].kwargs['text'] == "Please select a script from the dropdown above."

    def test_combobox_values(self, mock_root, mocker):
        """Test that combobox has correct script values."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        
        mock_option_menu = mocker.patch("src.gui.main_window.ctk.CTkOptionMenu")

        window = MainWindow(mock_root)

        call_args = mock_option_menu.call_args
        assert call_args.kwargs['values'] == window.scripts_list
        assert call_args.kwargs['values'][0] == "None"

class TestMainWindowOnSelection:
    """Test on_selection method of MainWindow."""
    @pytest.mark.parametrize("selection,setup_method", [
        ("Hold Key", "setup_hold_key_ui"),
        ("Weather", "setup_weather_ui"),
        ("Recipe Finder", "setup_recipe_ui"),
        ("None", "setup_default_ui"),
    ])
    def test_on_selection_calls_correct_setup_method(self, main_window, mocker, selection, setup_method):
        """Test that on_selection calls the correct setup method for each selection."""
        mock_clear = mocker.patch.object(main_window, 'clear_dynamic_content')
        mock_setup = mocker.patch.object(main_window, setup_method)
        
        main_window.script_type.get.return_value = selection
        main_window.on_selection(None)
        
        mock_clear.assert_called_once()
        mock_setup.assert_called_once()

    def test_on_selection_does_not_call_other_setup_methods(self, main_window, mocker):
        """Test that on_selection does not call other setup methods."""
        mock_hold_key = mocker.patch.object(main_window, 'setup_hold_key_ui')
        mock_weather = mocker.patch.object(main_window, 'setup_weather_ui')
        mock_recipe = mocker.patch.object(main_window, 'setup_recipe_ui')

        main_window.script_type.get.return_value = "Hold Key"
        main_window.on_selection(None)

        mock_hold_key.assert_called_once()
        mock_weather.assert_not_called()
        mock_recipe.assert_not_called()

class TestMainWindowClearDynamicContent:
    """Test clear_dynamic_content method of MainWindow."""
    def test_clear_dynamic_content_calls_cleanup_on_existing_ui(self, main_window, mocker):
        """Test that clear_dynamic_content calls cleanup on existing current_ui."""
        mock_current_ui = mocker.Mock()
        main_window.current_ui = mock_current_ui

        main_window.clear_dynamic_content()

        mock_current_ui.cleanup.assert_called_once()

    def test_clear_destroys_all_widgets_in_frame(self, main_window, mocker):
        """Test that clear_dynamic_content destroys all widgets in dynamic content frame."""
        mock_widget1 = mocker.Mock()
        mock_widget2 = mocker.Mock()
        main_window.dynamic_content_frame.winfo_children.return_value = [mock_widget1, mock_widget2]

        main_window.clear_dynamic_content()

        mock_widget1.destroy.assert_called_once()
        mock_widget2.destroy.assert_called_once()

    def test_clear_when_current_ui_has_no_cleanup(self, main_window, mocker):
        """Test that clear_dynamic_content works when current_ui has no cleanup method."""
        mock_current_ui = mocker.Mock(spec=[])
        main_window.current_ui = mock_current_ui

        main_window.clear_dynamic_content()

class TestMainWindowSetupMethods:
    """Test UI setup methods of MainWindow."""
    @pytest.mark.parametrize("setup_method,ui_class", [
        ("setup_hold_key_ui", "HoldKeyUI"),
        ("setup_weather_ui", "WeatherUI"),
        ("setup_recipe_ui", "RecipeUI"),
    ])
    def test_setup_creates_correct_ui_instance(self, main_window, mocker, setup_method, ui_class):
        mock_ui_class = mocker.patch(f"src.gui.main_window.{ui_class}")

        main_window.root.geometry.reset_mock()

        getattr(main_window, setup_method)()

        mock_ui_class.assert_called_once_with(main_window.dynamic_content_frame)
        assert main_window.current_ui == mock_ui_class.return_value

    @pytest.mark.parametrize("setup_method,expected_size", [
        ("setup_hold_key_ui", "400x500"),
        ("setup_weather_ui", "1000x600"),
        ("setup_recipe_ui", "1000x600"),
    ])
    def test_setup_adjusts_window_size_when_smaller(self, mocker, setup_method, expected_size):
        """Test that setup methods adjust window size when the current size is smaller."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        mocker.patch('src.gui.main_window.HoldKeyUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.WeatherUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.RecipeUI', return_value=MagicMock())

        mock_root = MagicMock()
        mock_root.winfo_width = MagicMock(return_value=200)
        mock_root.winfo_height = MagicMock(return_value=300)
        
        
        window = MainWindow(mock_root)

        window.root.geometry.reset_mock()
        
        getattr(window, setup_method)()

        mock_root.geometry.assert_called_with(expected_size)
        
    @pytest.mark.parametrize("setup_method", [
        ("setup_hold_key_ui"),
        ("setup_weather_ui"),
        ("setup_recipe_ui"),
    ])
    def test_setup_does_not_adjust_size_when_larger(self, mocker, setup_method):
        """Test that setup methods do not adjust window size when the current size is larger."""
        
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        mocker.patch('src.gui.main_window.HoldKeyUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.WeatherUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.RecipeUI', return_value=MagicMock())

        mock_root = MagicMock()
        mock_root.winfo_width = MagicMock(return_value=2000)
        mock_root.winfo_height = MagicMock(return_value=1500)
        
        
        window = MainWindow(mock_root)

        window.root.geometry.reset_mock()
        
        getattr(window, setup_method)()

        mock_root.geometry.assert_not_called()

    @pytest.mark.parametrize("setup_method,expected_size", [
        ("setup_hold_key_ui", "400x500"),
        ("setup_weather_ui", "1000x600"),
        ("setup_recipe_ui", "1000x600"),
    ])
    def test_setup_does_not_adjust_size_when_equal(self, mocker, setup_method, expected_size):  
        """Test that setup methods do not adjust window size when the current size is equal."""
        mocker.patch('src.gui.main_window.ctk.CTkFont')
        mocker.patch('src.gui.main_window.ctk.CTkFrame')
        mocker.patch('src.gui.main_window.ctk.CTkLabel')
        mocker.patch('src.gui.main_window.ctk.CTkOptionMenu')
        mocker.patch('src.gui.main_window.ctk.StringVar')
        mocker.patch('src.gui.main_window.HoldKeyUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.WeatherUI', return_value=MagicMock())
        mocker.patch('src.gui.main_window.RecipeUI', return_value=MagicMock())

        mock_root = MagicMock()
        mock_root.winfo_width.return_value = int(expected_size.split('x')[0])
        mock_root.winfo_height.return_value = int(expected_size.split('x')[1])
        
        
        window = MainWindow(mock_root)

        window.root.geometry.reset_mock()
        
        getattr(window, setup_method)()

        mock_root.geometry.assert_not_called()

class TestMainWindowOnClose:
    """Test on_close method of MainWindow."""
    def test_on_close_calls_cleanup_on_current_ui(self, main_window, mocker):
        """Test that on_close calls cleanup on current_ui if it exists."""
        mock_current_ui = mocker.Mock()
        main_window.current_ui = mock_current_ui

        main_window.on_close()

        mock_current_ui.cleanup.assert_called_once()

    def test_on_close_destroys_root(self, main_window, mock_root):
        """Test that on_close destroys the root window."""
        main_window.on_close()

        mock_root.destroy.assert_called_once()

    def test_on_close_when_no_current_ui(self, main_window, mock_root):
        """Test that there is no exception when on_close is called with no current_ui."""
        main_window.current_ui = None

        main_window.on_close()

        mock_root.destroy.assert_called_once()

    def test_on_close_when_current_ui_has_no_cleanup(self, main_window, mocker, mock_root):
        """Test that on_close works when current_ui has no cleanup method."""
        mock_current_ui = mocker.Mock(spec=[])
        main_window.current_ui = mock_current_ui

        main_window.on_close()

        mock_root.destroy.assert_called_once()