import json
from unittest.mock import MagicMock, patch, mock_open
from prompt_builder import load_preferences, save_preferences
from controller import SettingsCommand

def test_load_preferences_success():
    mock_data = {
        "temp_unit": "F",
        "cold_threshold": 10,
        "hot_threshold": 30,
        "perfect_temp": 22,
        "favorite_color": "Red",
        "clothing_style": "Minimalist",
        "age": 30,
        "sex": "Female",
        "weather_sensitivities": "None"
    }
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        prefs = load_preferences()
        assert prefs == mock_data

def test_load_preferences_defaults_on_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        prefs = load_preferences()
        assert prefs["age"] == 21
        assert prefs["clothing_style"] == "Casual"
        assert prefs["temp_unit"] == "C"

def test_load_preferences_defaults_on_invalid_json():
    with patch("builtins.open", mock_open(read_data="invalid json data")):
        prefs = load_preferences()
        assert prefs["age"] == 21
        assert prefs["clothing_style"] == "Casual"

def test_save_preferences_success():
    mock_data = {"age": 25}
    m = mock_open()
    with patch("builtins.open", m):
        save_preferences(mock_data)
        m.assert_called_once_with("preferences.json", "w", encoding="utf-8")
        
        # Verify that json.dump was called with mock_data
        handle = m()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed_written = json.loads(written_data)
        assert parsed_written == mock_data

def test_settings_command_flow():
    app = MagicMock()
    # Mocking choices:
    # 1. Configure LLM
    # 2. Edit weather preferences
    # 3. Edit personal profile
    # 4. Create new profile flow
    # 5. View settings
    # 6. Exit
    app.ui.get_choice.side_effect = [1, 2, 3, 4, 5, 6]
    
    cmd = SettingsCommand(app)
    
    mock_prefs = {"age": 21}
    mock_settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": "some_key"}
    
    with patch("prompt_builder.load_preferences", return_value=mock_prefs), \
         patch("prompt_builder.save_preferences") as mock_save, \
         patch("prompt_builder.load_model_settings", return_value=mock_settings), \
         patch("prompt_builder.save_model_settings") as mock_save_model:
        
        result = cmd.execute()
        
        assert result is False
        assert app.ui.print_settings_menu.call_count == 6
        app.ui.edit_llm_settings.assert_called_once_with(mock_settings)
        app.ui.edit_weather_preferences.assert_called_once_with(mock_prefs)
        app.ui.edit_personal_profile.assert_called_once_with(mock_prefs)
        app.ui.create_new_profile_flow.assert_called_once()
        app.ui.view_current_settings.assert_called_once_with(mock_prefs)
        assert mock_save.call_count == 3
        assert mock_save_model.call_count == 1

mock_models_by_provider = {
    "gemini": ["gemini-2.5-flash", "gemini-2.5-pro", "imagen-3.0-generate-001"],
    "openai": ["gpt-4o", "gpt-4o-mini", "dall-e-3"]
}

mock_model_prices_and_context_window = {
    "gemini-2.5-flash": {"mode": "chat"},
    "gemini-2.5-pro": {"mode": "chat"},
    "gpt-4o": {"mode": "chat"},
    "gpt-4o-mini": {"mode": "chat"},
    "imagen-3.0-generate-001": {"mode": "image_generation"},
    "dall-e-3": {"mode": "image_generation"}
}

def test_validate_model_settings_invalid_provider():
    from prompt_builder import validate_model_settings
    from exceptions import InvalidProviderError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         pytest.raises(InvalidProviderError) as excinfo:
        validate_model_settings({"provider": "invalid_provider", "model": "gemini-2.5-flash", "api_key": "key"})
    assert "Invalid provider 'invalid_provider'" in str(excinfo.value)

def test_validate_model_settings_invalid_model():
    from prompt_builder import validate_model_settings
    from exceptions import InvalidModelError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError) as excinfo:
        validate_model_settings({"provider": "google", "model": "gpt-4o", "api_key": "key"})
    assert "Invalid model 'gpt-4o' for provider 'google'" in str(excinfo.value)

def test_edit_llm_settings_mcq_success():
    from ui import WeatherUI
    ui = WeatherUI()
    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True), \
         patch("builtins.input", side_effect=["2", "1", "new_key"]):
        res = ui.edit_llm_settings(settings)
        assert res["provider"] == "openai"
        assert res["model"] == "gpt-4o"
        assert res["api_key"] == "new_key"

def test_edit_llm_settings_invalid_then_valid():
    from ui import WeatherUI
    ui = WeatherUI()
    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True), \
         patch("builtins.input", side_effect=["99", "1", "99", "2", "", "valid_key"]), \
         patch.object(ui, "print_error") as mock_print_error:
        res = ui.edit_llm_settings(settings)
        assert res["provider"] == "gemini"
        assert res["model"] == "gemini-2.5-pro"
        assert res["api_key"] == "valid_key"
        
        assert mock_print_error.call_count == 3
        calls = [c[0][0] for c in mock_print_error.call_args_list]
        assert "Invalid choice" in calls[0]
        assert "Invalid choice" in calls[1]
        assert "API Key cannot be empty" in calls[2]

def test_is_text_model_filters():
    from prompt_builder import is_text_model
    with patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True):
        assert is_text_model("gpt-4o") is True
        assert is_text_model("gemini-2.5-pro") is True
        assert is_text_model("dall-e-3") is False
        assert is_text_model("imagen-3.0-generate-001") is False
        
        # Test fallback
        assert is_text_model("unknown-custom-text-model") is True
        assert is_text_model("unknown-custom-image-model") is False

def test_validate_model_settings_rejects_non_text_models():
    from prompt_builder import validate_model_settings
    from exceptions import InvalidModelError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError):
        validate_model_settings({"provider": "openai", "model": "dall-e-3", "api_key": "key"})
        
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_prices_and_context_window", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError):
        validate_model_settings({"provider": "google", "model": "imagen-3.0-generate-001", "api_key": "key"})

def test_settings_command_flow_verification_failure():
    app = MagicMock()
    app.ui.get_choice.side_effect = [1, 6]
    app.brain.test_connection.side_effect = Exception("Test connection failed")
    
    cmd = SettingsCommand(app)
    
    mock_settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": "some_key"}
    
    with patch("prompt_builder.load_model_settings", return_value=mock_settings), \
         patch("prompt_builder.save_model_settings") as mock_save_model:
        
        app.ui.edit_llm_settings.return_value = mock_settings
        result = cmd.execute()
        
        assert result is False
        app.brain.test_connection.assert_called_once_with("google", "gemini-2.5-flash", "some_key")
        # Ensure model settings were NOT saved due to connection failure
        mock_save_model.assert_not_called()
        app.ui.print_error.assert_called_once_with("Failed to connect: Test connection failed")
