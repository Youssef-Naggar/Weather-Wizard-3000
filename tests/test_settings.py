import json
from unittest.mock import MagicMock, patch, mock_open
from settings_manager import load_preferences, save_preferences
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
    # 1. Configure AI Models (Sub-menu: 1. Text LLM, 4. Back)
    # 2. Edit weather preferences
    # 3. Edit personal profile
    # 4. Create new profile flow
    # 5. View settings
    # 8. Exit main menu
    app.ui.get_choice.side_effect = [1, 1, 4, 2, 3, 4, 5, 8]
    
    cmd = SettingsCommand(app)
    
    mock_prefs = {"age": 21}
    mock_settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": "some_key"}
    
    with patch("settings_manager.load_preferences", return_value=mock_prefs), \
         patch("settings_manager.save_preferences") as mock_save, \
         patch("settings_manager.load_model_settings", return_value=mock_settings), \
         patch("settings_manager.save_model_settings") as mock_save_model:
        
        result = cmd.execute()
        
        assert result is False
        app.ui.edit_llm_settings.assert_called_once_with(mock_settings, mode="text")
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
    from settings_manager import validate_model_settings
    from exceptions import InvalidProviderError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         pytest.raises(InvalidProviderError) as excinfo:
        validate_model_settings({"provider": "invalid_provider", "model": "gemini-2.5-flash", "api_key": "key"})
    assert "Invalid provider 'invalid_provider'" in str(excinfo.value)

def test_validate_model_settings_invalid_model():
    from settings_manager import validate_model_settings
    from exceptions import InvalidModelError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_cost", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError) as excinfo:
        validate_model_settings({"provider": "google", "model": "gpt-4o", "api_key": "key"})
    assert "Invalid model 'gpt-4o' for provider 'google'" in str(excinfo.value)

def test_edit_llm_settings_mcq_success():
    from ui import WeatherUI
    ui = WeatherUI()
    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_cost", mock_model_prices_and_context_window, create=True), \
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
         patch("litellm.model_cost", mock_model_prices_and_context_window, create=True), \
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
    from model_registry import is_text_model
    with patch("litellm.model_cost", mock_model_prices_and_context_window, create=True):
        assert is_text_model("gpt-4o") is True
        assert is_text_model("gemini-2.5-pro") is True
        assert is_text_model("dall-e-3") is False
        assert is_text_model("imagen-3.0-generate-001") is False
        
        # Test fallback
        assert is_text_model("unknown-custom-text-model") is True
        assert is_text_model("unknown-custom-image-model") is False


def test_is_vision_model_filters():
    from model_registry import is_vision_model
    with patch("litellm.model_cost", {"gpt-4o": {"supports_vision": True}, "text-only": {"supports_vision": False}}, create=True):
        assert is_vision_model("gpt-4o") is True
        assert is_vision_model("text-only") is False

    with patch("litellm.model_cost", {"google/custom-vision": {"supports_vision": True}}, create=True):
        assert is_vision_model("custom-vision", provider="google") is True


def test_is_image_model_filters():
    from model_registry import is_image_model, is_imagegen_model
    with patch("litellm.model_cost", {"dall-e-3": {"mode": "image_generation"}, "text-only": {"mode": "chat"}}, create=True):
        assert is_image_model("dall-e-3") is True
        assert is_imagegen_model("dall-e-3") is True
        assert is_image_model("text-only") is False

    with patch("litellm.model_cost", {"custom-gen-model": {"mode": "image_generation"}}, create=True):
        assert is_imagegen_model("custom-gen-model") is True




def test_validate_model_settings_rejects_non_text_models():
    from settings_manager import validate_model_settings
    from exceptions import InvalidModelError
    import pytest
    
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_cost", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError):
        validate_model_settings({"provider": "openai", "model": "dall-e-3", "api_key": "key"})
        
    with patch("litellm.models_by_provider", mock_models_by_provider), \
         patch("litellm.model_cost", mock_model_prices_and_context_window, create=True), \
         pytest.raises(InvalidModelError):
        validate_model_settings({"provider": "google", "model": "imagen-3.0-generate-001", "api_key": "key"})

def test_settings_command_flow_verification_failure():
    app = MagicMock()
    app.ui.get_choice.side_effect = [1, 1, 4, 8]
    app.brain.test_connection.side_effect = Exception("Test connection failed")
    
    cmd = SettingsCommand(app)
    
    mock_settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": "some_key"}
    
    with patch("settings_manager.load_model_settings", return_value=mock_settings), \
         patch("settings_manager.save_model_settings") as mock_save_model:
        
        app.ui.edit_llm_settings.return_value = mock_settings
        result = cmd.execute()
        
        assert result is False
        app.brain.test_connection.assert_called_once_with("google", "gemini-2.5-flash", "some_key")
        # Ensure model settings were NOT saved due to connection failure
        mock_save_model.assert_not_called()
        app.ui.print_error.assert_called_once_with("Failed to connect: Test connection failed")


def test_edit_llm_settings_custom_model_option():
    from ui import WeatherUI
    ui = WeatherUI()
    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}
    
    mock_ollama_providers = {
        "ollama": ["llama2"],
        "google": ["gemini-2.5-flash"]
    }
    
    with patch("litellm.models_by_provider", mock_ollama_providers), \
         patch.object(ui, "_select_provider", return_value="ollama"), \
         patch("builtins.input", side_effect=["2", "llama3:70b", "custom_key"]):
        res = ui.edit_llm_settings(settings)
        assert res["provider"] == "ollama"
        assert res["model"] == "llama3:70b"
        assert res["api_key"] == "custom_key"


def test_validate_custom_model_name_success():
    from settings_manager import validate_model_settings
    
    mock_ollama_providers = {
        "ollama": ["llama2"],
        "google": ["gemini-2.5-flash"]
    }
    
    with patch("litellm.models_by_provider", mock_ollama_providers):
        # Custom model should be valid and not raise InvalidModelError
        validate_model_settings({"provider": "ollama", "model": "llama3:70b", "api_key": "key"})


def test_model_settings_schema_with_api_base():
    from settings_manager import ModelSettings, validate_model_settings

    settings_dict = {
        "provider": "custom",
        "model": "ollama/llama3:8b",
        "api_key": "not-needed",
        "api_base": "http://localhost:11434"
    }
    model_obj = ModelSettings(**settings_dict)
    assert model_obj.api_base == "http://localhost:11434"

    validated = validate_model_settings(settings_dict)
    assert validated["api_base"] == "http://localhost:11434"
    assert validated["provider"] == "custom"


def test_edit_llm_settings_custom_endpoint_flow():
    from ui import WeatherUI
    ui = WeatherUI()
    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}

    with patch.object(ui, "_select_provider", return_value="custom"), \
         patch("builtins.input", side_effect=["http://localhost:11434", "ollama/llama3:8b", "my_key"]):
        res = ui.edit_llm_settings(settings)
        assert res["provider"] == "custom"
        assert res["model"] == "ollama/llama3:8b"
        assert res["api_base"] == "http://localhost:11434"
        assert res["api_key"] == "my_key"


def test_get_tryon_outfit_choice():
    from ui import WeatherUI
    ui = WeatherUI()

    with patch("builtins.input", side_effect=["abc", "5", "1"]):
        choice = ui.get_tryon_outfit_choice(2)
        assert choice == 1

    with patch("builtins.input", side_effect=["0"]):
        choice = ui.get_tryon_outfit_choice(2)
        assert choice == 0


def test_ask_create_demo_yes_no():
    from ui import WeatherUI
    ui = WeatherUI()

    with patch("builtins.input", side_effect=["y"]):
        assert ui.ask_create_demo_yes_no() is True

    with patch("builtins.input", side_effect=["no"]):
        assert ui.ask_create_demo_yes_no() is False


def test_configure_avatar_path_flow(tmp_path):
    from ui import WeatherUI
    ui = WeatherUI()

    avatar_file = tmp_path / "my_avatar.png"
    avatar_file.write_bytes(b"avatar bytes")

    # Flow when path exists: user chooses 2 (back to settings)
    with patch("os.path.exists", return_value=True), \
         patch("builtins.input", side_effect=["2"]):
        res = ui.configure_avatar_path_flow(str(avatar_file))
        assert res is None

    # Flow when path exists: user chooses 1 (configure new path) -> enters path
    with patch("os.path.exists", return_value=True), \
         patch("builtins.input", side_effect=["1", str(avatar_file)]):
        res = ui.configure_avatar_path_flow("old_path.png")
        assert res == str(avatar_file)

    # Flow when path is empty: directly prompts for path
    with patch("builtins.input", side_effect=[str(avatar_file)]):
        res = ui.configure_avatar_path_flow("")
        assert res == str(avatar_file)



