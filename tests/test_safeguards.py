from unittest.mock import patch, MagicMock
from controller import GetAiSuggestionCommand

class MockApp:
    def __init__(self):
        self.weather_summary = "Sunny"
        self.ai_loop_running = True
        self.ui = MagicMock()
        self.brain = MagicMock()

def test_suggestion_command_blocks_if_no_api_key():
    app = MockApp()
    command = GetAiSuggestionCommand(app)
    
    # Mocking load_model_settings returning empty key
    with patch("os.path.exists", return_value=True), \
         patch("prompt_builder.load_model_settings", return_value={"api_key": ""}):
        
        result = command.execute()
        assert result is False
        assert app.ai_loop_running is False
        app.ui.print_error.assert_called_once_with(
            "LLM Provider or API key is not configured. Please go to Settings to configure them first."
        )

def test_suggestion_command_redirects_if_no_preferences():
    app = MockApp()
    app.ui.get_commute_type.return_value = "Walking"
    app.ui.get_trip_type.return_value = "Work"
    app.ui.get_dress_code.return_value = ""
    app.brain.ai_suggestion.return_value = "Suggestion output"
    
    command = GetAiSuggestionCommand(app)
    
    # preferences.json missing (False), but model-settings.json exists (True)
    def mock_exists_func(path):
        if path == "preferences.json":
            return False
        return True
        
    mock_new_profile = {"age": 21}
    
    with patch("os.path.exists", side_effect=mock_exists_func), \
         patch("prompt_builder.load_model_settings", return_value={"api_key": "valid_key"}), \
         patch("prompt_builder.save_preferences") as mock_save, \
         patch("controller.build_prompt", return_value="formatted prompt"):
             
        app.ui.create_new_profile_flow.return_value = mock_new_profile
        
        result = command.execute()
        
        assert result is False
        app.ui.print_error.assert_called_once_with(
            "No personal preferences found. Redirecting to setup a new profile..."
        )
        app.ui.create_new_profile_flow.assert_called_once()
        mock_save.assert_called_once_with(mock_new_profile)
        app.brain.ai_suggestion.assert_called_once_with("Sunny", "formatted prompt")
