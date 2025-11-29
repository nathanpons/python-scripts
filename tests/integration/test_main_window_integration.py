"""
Tests for the main window integration.
"""
import pytest
import time
import os
from gui.hold_key_ui import HoldKeyUI
from gui.weather_ui import WeatherUI
from gui.recipe_ui import RecipeUI

class TestMainWindowIntegration:
    """Integration tests for the Main Window."""

    def test_main_window_initialization(self, app_window):
        """Test that the main window initializes correctly."""
        assert app_window.root is not None
        assert app_window.dynamic_content_frame is not None
        assert app_window.current_ui is None
        assert app_window.script_type.get() == "None"

    class TestScriptSelection:
        """Tests for script selection functionality."""

        def test_hold_key_selection(self, app_window, mocker):
            """Test selecting Hold Key script."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            time.sleep(0.1)

            assert app_window.current_ui is not None
            assert isinstance(app_window.current_ui, HoldKeyUI)

        def test_weather_selection(self, app_window, mocker):
            """Test selecting Weather script."""
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
            
            app_window.script_type.set("Weather")
            app_window.on_selection("Weather")
            app_window.root.update()
            time.sleep(0.5)

            assert app_window.current_ui is not None
            assert isinstance(app_window.current_ui, WeatherUI)

        def test_recipe_selection(self, app_window, mocker):
            """Test selecting Recipe Finder script."""
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            
            import os
            original_join = os.path.join
            def mock_join(*args):
                if 'api_config.json' in args:
                    return 'config/api_config.json'
                return original_join(*args)
            mocker.patch('os.path.join', side_effect=mock_join)
            
            app_window.script_type.set("Recipe Finder")
            app_window.on_selection("Recipe Finder")
            app_window.root.update()
            time.sleep(0.5)

            assert app_window.current_ui is not None
            assert isinstance(app_window.current_ui, RecipeUI)

        def test_none_selection(self, app_window):
            """Test selecting None (default state)."""
            app_window.script_type.set("None")
            app_window.on_selection("None")
            app_window.root.update()
            time.sleep(0.1)

            assert app_window.current_ui is None
            assert app_window.default_ui_label is not None

    class TestUICleanup:
        """Tests for UI cleanup when switching scripts."""

        def test_cleanup_when_switching_scripts(self, app_window, mocker):
            """Test that UI is cleaned up when switching between scripts."""
            # Setup mocks
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
            
            # Select Hold Key
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            time.sleep(0.1)
            
            hold_key_ui = app_window.current_ui
            assert isinstance(hold_key_ui, HoldKeyUI)
            
            # Switch to Weather
            app_window.script_type.set("Weather")
            app_window.on_selection("Weather")
            app_window.root.update()
            time.sleep(0.5)
            
            # Verify old UI was cleaned up
            assert app_window.current_ui is not hold_key_ui
            assert isinstance(app_window.current_ui, WeatherUI)

        def test_cleanup_on_none_selection(self, app_window, mocker):
            """Test cleanup when selecting None."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            
            # Select Hold Key first
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            time.sleep(0.1)
            
            assert app_window.current_ui is not None
            
            # Select None
            app_window.script_type.set("None")
            app_window.on_selection("None")
            app_window.root.update()
            time.sleep(0.1)
            
            assert app_window.current_ui is None

    class TestWindowResizing:
        """Tests for window resizing when scripts are selected."""

        def test_weather_resizes_window(self, app_window, mocker):
            """Test that selecting Weather resizes the window."""
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
            
            app_window.script_type.set("Weather")
            app_window.on_selection("Weather")
            app_window.root.update()
            time.sleep(0.5)
            
            # Window should be at least 1000x600
            assert app_window.root.winfo_width() >= 1000
            assert app_window.root.winfo_height() >= 600

        def test_recipe_resizes_window(self, app_window, mocker):
            """Test that selecting Recipe Finder resizes the window."""
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            
            original_join = os.path.join
            def mock_join(*args):
                if 'api_config.json' in args:
                    return 'config/api_config.json'
                return original_join(*args)
            mocker.patch('os.path.join', side_effect=mock_join)
            
            app_window.script_type.set("Recipe Finder")
            app_window.on_selection("Recipe Finder")
            app_window.root.update()
            time.sleep(0.5)
            
            # Window should be at least 1000x600
            assert app_window.root.winfo_width() >= 1000 or "1000x600" in app_window.root.geometry()

        def test_hold_key_maintains_default_size(self, app_window, mocker):
            """Test that Hold Key maintains default window size."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            time.sleep(0.1)
            
            # Assertions
            assert app_window.root.winfo_width() >= 400
            assert app_window.root.winfo_height() >= 500

    class TestDynamicContentFrame:
        """Tests for dynamic content frame management."""

        def test_dynamic_content_cleared_on_selection(self, app_window, mocker):
            """Test that dynamic content is cleared when switching scripts."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            
            # Add Hold Key UI
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            
            initial_children = len(app_window.dynamic_content_frame.winfo_children())
            assert initial_children > 0
            
            # Switch to None
            app_window.script_type.set("None")
            app_window.on_selection("None")
            app_window.root.update()
            
            # Different children should exist (default UI)
            final_children = len(app_window.dynamic_content_frame.winfo_children())
            assert final_children > 0
            assert final_children != initial_children

        def test_multiple_script_switches(self, app_window, mocker):
            """Test switching between multiple scripts."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            mock_config_data = '{"api_gateway_url": "http://fakeapi.test"}'
            mocker.patch('builtins.open', mocker.mock_open(read_data=mock_config_data))
            mocker.patch('scripts.weather_script.get_resource_path', return_value='config/api_config.json')
            
            scripts = ["Hold Key", "None", "Weather", "None", "Hold Key"]
            
            for script in scripts:
                app_window.script_type.set(script)
                app_window.on_selection(script)
                app_window.root.update()
                time.sleep(0.2)
                
                # Verify state
                if script == "None":
                    assert app_window.current_ui is None
                else:
                    assert app_window.current_ui is not None

    class TestOnClose:
        """Tests for window close handling."""

        def test_on_close_with_no_ui(self, app_window):
            """Test closing window with no UI loaded."""
            app_window.current_ui = None
            # Should not raise exception
            try:
                app_window.on_close()
            except Exception as e:
                pytest.fail(f"on_close raised exception: {e}")

        def test_on_close_with_hold_key_ui(self, app_window, mocker):
            """Test closing window with Hold Key UI loaded."""
            mocker.patch('keyboard.add_hotkey')
            mocker.patch('keyboard.remove_hotkey')
            
            app_window.script_type.set("Hold Key")
            app_window.on_selection("Hold Key")
            app_window.root.update()
            
            mock_cleanup = mocker.patch.object(app_window.current_ui, 'cleanup')
            mock_destroy = mocker.patch.object(app_window.root, 'destroy')
            
            app_window.on_close()
            
            assert mock_cleanup.called
            assert mock_destroy.called







