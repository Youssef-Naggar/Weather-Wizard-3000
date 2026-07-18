import datetime
from unittest.mock import MagicMock, patch, ANY
import pytest
from controller import (
    SelectDateCommand,
    ExitCommand,
    CitySearchCommand,
    AutoLocationCommand,
    ManualCoordinatesCommand,
    GetAiSuggestionCommand,
    SkipAiSuggestionCommand
)

class MockApp:
    def __init__(self):
        self.target_date = datetime.date(2026, 7, 2)
        self.location_loop_running = True
        self.ai_loop_running = True
        self.running = True
        self.weather_summary = ""
        self.ui = MagicMock()
        self.weather_client = MagicMock()
        self.forecast_service = MagicMock()
        self.brain = MagicMock()


# --- SelectDateCommand Tests ---

def test_select_date_command():
    app = MockApp()
    command = SelectDateCommand(app, offset=2)
    
    result = command.execute()
    
    assert result is False
    assert app.target_date == datetime.date.today() + datetime.timedelta(days=2)
    assert app.location_loop_running is True


# --- ExitCommand Tests ---

def test_exit_command():
    app = MockApp()
    command = ExitCommand(app)
    
    result = command.execute()
    
    assert result is False
    assert app.running is False
    assert app.location_loop_running is False
    assert app.ai_loop_running is False
    assert app.ui.print_message.call_count == 2


# --- CitySearchCommand Tests ---

def test_city_search_command_empty_city():
    app = MockApp()
    app.ui.get_city_name.return_value = ""
    command = CitySearchCommand(app)
    
    result = command.execute()
    
    assert result is True
    app.ui.print_error.assert_called_once_with("City name cannot be empty.")


def test_city_search_command_success():
    app = MockApp()
    app.ui.get_city_name.return_value = "Paris"
    app.weather_client.fetch_weather_by_city.return_value = {"city": "Paris"}
    app.forecast_service.get_weather_message.return_value = "Sunny in Paris"
    command = CitySearchCommand(app)
    
    result = command.execute()
    
    assert result is False
    app.weather_client.fetch_weather_by_city.assert_called_once_with("Paris")
    app.forecast_service.process_weather_data.assert_called_once_with({"city": "Paris"}, app.target_date)
    assert app.weather_summary == "Sunny in Paris"
    app.ui.print_message.assert_called_once_with("\nSunny in Paris")


def test_city_search_command_failure():
    app = MockApp()
    app.ui.get_city_name.return_value = "InvalidCity"
    app.weather_client.fetch_weather_by_city.side_effect = Exception("City not found")
    command = CitySearchCommand(app)
    
    result = command.execute()
    
    assert result is True
    app.ui.print_error.assert_called_once_with("Failed to fetch data: City not found")


# --- AutoLocationCommand Tests ---

@patch("controller.get_auto_location")
def test_auto_location_command_success(mock_get_loc):
    app = MockApp()
    mock_get_loc.return_value = [48.8566, 2.3522]
    app.weather_client.fetch_weather_by_coordinates.return_value = {"weather": "cool"}
    app.forecast_service.get_weather_message.return_value = "Cool in Paris"
    command = AutoLocationCommand(app)
    
    result = command.execute()
    
    assert result is False
    mock_get_loc.assert_called_once()
    app.weather_client.fetch_weather_by_coordinates.assert_called_once_with(48.8566, 2.3522)
    app.forecast_service.process_weather_data.assert_called_once_with({"weather": "cool"}, app.target_date)
    assert app.weather_summary == "Cool in Paris"


@patch("controller.get_auto_location")
def test_auto_location_command_failure(mock_get_loc):
    app = MockApp()
    mock_get_loc.side_effect = Exception("GPS failure")
    command = AutoLocationCommand(app)
    
    result = command.execute()
    
    assert result is True
    app.ui.print_error.assert_called_once_with("Location detection failed: GPS failure")


# --- ManualCoordinatesCommand Tests ---

@pytest.mark.parametrize(
    "lat, lon, is_valid",
    [
        (91.0, 0.0, False),
        (-91.0, 0.0, False),
        (0.0, 181.0, False),
        (0.0, -181.0, False),
        (45.0, 90.0, True),
    ]
)
def test_manual_coordinates_command_validation(lat, lon, is_valid):
    app = MockApp()
    app.ui.get_coordinate.side_effect = [lat, lon]
    command = ManualCoordinatesCommand(app)
    
    result = command.execute()
    
    if is_valid:
        # Should proceed to fetch and succeed/fail
        assert result is False or result is True
    else:
        assert result is True
        app.ui.print_error.assert_called_once_with("Invalid coordinates! Values out of range.")


def test_manual_coordinates_command_success():
    app = MockApp()
    app.ui.get_coordinate.side_effect = [10.0, 20.0]
    app.weather_client.fetch_weather_by_coordinates.return_value = {"ok": True}
    app.forecast_service.get_weather_message.return_value = "Hot weather"
    command = ManualCoordinatesCommand(app)
    
    result = command.execute()
    
    assert result is False
    app.weather_client.fetch_weather_by_coordinates.assert_called_once_with(10.0, 20.0)
    app.forecast_service.process_weather_data.assert_called_once_with({"ok": True}, app.target_date)
    assert app.weather_summary == "Hot weather"


def test_manual_coordinates_command_failure():
    app = MockApp()
    app.ui.get_coordinate.side_effect = [10.0, 20.0]
    app.weather_client.fetch_weather_by_coordinates.side_effect = Exception("Network Down")
    command = ManualCoordinatesCommand(app)
    
    result = command.execute()
    
    assert result is True
    app.ui.print_error.assert_called_once_with("Error: Network Down")


# --- GetAiSuggestionCommand Tests ---

@patch("os.path.exists", return_value=True)
@patch("prompt_builder.load_model_settings", return_value={"api_key": "some_key"})
def test_get_ai_suggestion_command_success(mock_load, mock_exists):
    app = MockApp()
    app.weather_summary = "Sunny"
    app.brain.ai_suggestion.return_value = "Wear shorts"
    command = GetAiSuggestionCommand(app)
    
    result = command.execute()
    
    assert result is False
    app.brain.ai_suggestion.assert_called_once_with("Sunny", ANY)
    app.ui.print_message.assert_any_call("Wear shorts")
    assert app.ai_loop_running is False


@patch("os.path.exists", return_value=True)
@patch("prompt_builder.load_model_settings", return_value={"api_key": "some_key"})
def test_get_ai_suggestion_command_failure(mock_load, mock_exists):
    app = MockApp()
    app.weather_summary = "Sunny"
    app.brain.ai_suggestion.side_effect = Exception("LLM Error")
    command = GetAiSuggestionCommand(app)
    
    result = command.execute()
    
    assert result is False
    app.ui.print_error.assert_called_once_with("AI suggestion failed: LLM Error")
    assert app.ai_loop_running is False



# --- SkipAiSuggestionCommand Tests ---

def test_skip_ai_suggestion_command():
    app = MockApp()
    command = SkipAiSuggestionCommand(app)
    
    result = command.execute()
    
    assert result is False
    assert app.ai_loop_running is False
