import datetime
from unittest.mock import patch
import pytest
from forecast import Forecast, WeatherClient

# --- WeatherClient Tests ---

@patch("forecast.make_api_request")
def test_weather_client_fetch_by_coordinates(mock_make_request):
    mock_make_request.return_value = {"status": "ok"}
    client = WeatherClient()
    
    result = client.fetch_weather_by_coordinates(12.34, 56.78)
    
    mock_make_request.assert_called_once_with(
        "https://api.openweathermap.org/data/2.5/forecast",
        {"lat": 12.34, "lon": 56.78, "appid": "mock_owm_key"}
    )
    assert result == {"status": "ok"}


@patch("forecast.make_api_request")
def test_weather_client_fetch_by_city(mock_make_request):
    mock_make_request.return_value = {"status": "ok"}
    client = WeatherClient()
    
    result = client.fetch_weather_by_city("London")
    
    mock_make_request.assert_called_once_with(
        "https://api.openweathermap.org/data/2.5/forecast",
        {"q": "London", "appid": "mock_owm_key"}
    )
    assert result == {"status": "ok"}


# --- Forecast Tests ---

def test_forecast_initial_state():
    forecast = Forecast()
    assert forecast.city_name == ""
    assert forecast.will_rain is False
    assert forecast.max_temp_k == 0.0
    assert forecast.feels_like_temp_k == 0.0
    assert forecast.min_temp_k == 0.0
    assert forecast.avg_humidity == 0.0


@pytest.mark.parametrize(
    "condition_code, expected_rain",
    [
        (500, True),   # Rain code (< 700)
        (699, True),   # Rain code (< 700)
        (700, False),  # Atmosphere code (>= 700)
        (800, False),  # Clear code (>= 700)
    ]
)
def test_forecast_rain_detection(condition_code, expected_rain):
    target_date = datetime.date(2026, 7, 2)
    weather_data = {
        "city": {"name": "Sample City"},
        "list": [
            {
                "dt_txt": "2026-07-02 12:00:00",
                "main": {"temp_max": 300.0, "temp_min": 290.0, "feels_like": 295.0, "humidity": 50.0},
                "weather": [{"id": condition_code}]
            }
        ]
    }
    
    forecast = Forecast()
    forecast.process_weather_data(weather_data, target_date)
    assert forecast.will_rain == expected_rain
    assert forecast.city_name == "Sample City"


def test_forecast_aggregations_over_target_date():
    target_date = datetime.date(2026, 7, 2)
    weather_data = {
        "city": {"name": "Aggregation City"},
        "list": [
            {
                # Matching date, hour 1
                "dt_txt": "2026-07-02 09:00:00",
                "main": {"temp_max": 295.0, "temp_min": 290.0, "feels_like": 292.0, "humidity": 60.0},
                "weather": [{"id": 800}]
            },
            {
                # Matching date, hour 2
                "dt_txt": "2026-07-02 15:00:00",
                "main": {"temp_max": 305.0, "temp_min": 295.0, "feels_like": 300.0, "humidity": 40.0},
                "weather": [{"id": 800}]
            },
            {
                # Non-matching date
                "dt_txt": "2026-07-03 12:00:00",
                "main": {"temp_max": 310.0, "temp_min": 300.0, "feels_like": 305.0, "humidity": 30.0},
                "weather": [{"id": 500}]
            }
        ]
    }
    
    forecast = Forecast()
    forecast.process_weather_data(weather_data, target_date)
    
    assert forecast.city_name == "Aggregation City"
    # Max of matching: max(295.0, 305.0) = 305.0
    assert forecast.max_temp_k == 305.0
    # Min of matching: min(290.0, 295.0) = 290.0
    assert forecast.min_temp_k == 290.0
    # Avg feels_like: (292.0 + 300.0) / 2 = 296.0
    assert forecast.feels_like_temp_k == 296.0
    # Avg humidity: (60.0 + 40.0) / 2 = 50.0
    assert forecast.avg_humidity == 50.0
    # Condition codes 800, 800 -> no rain expected
    assert not forecast.will_rain


def test_forecast_no_matching_date():
    target_date = datetime.date(2026, 7, 2)
    weather_data = {
        "city": {"name": "No Match City"},
        "list": [
            {
                "dt_txt": "2026-07-03 12:00:00",
                "main": {"temp_max": 300.0, "temp_min": 290.0, "feels_like": 295.0, "humidity": 50.0},
                "weather": [{"id": 800}]
            }
        ]
    }
    
    forecast = Forecast()
    forecast.process_weather_data(weather_data, target_date)
    
    # State should remain unchanged (initial values) except for the city name
    assert forecast.city_name == "No Match City"
    assert not forecast.will_rain
    assert forecast.max_temp_k == 0.0
    assert forecast.min_temp_k == 0.0


def test_forecast_get_weather_message():
    forecast = Forecast()
    forecast.city_name = "Message City"
    # Kelvin: 273.15 -> Celsius: 0, Fahrenheit: 32
    # Kelvin: 283.15 -> Celsius: 10, Fahrenheit: 50
    # Kelvin: 293.15 -> Celsius: 20, Fahrenheit: 68
    forecast.max_temp_k = 293.15
    forecast.feels_like_temp_k = 283.15
    forecast.min_temp_k = 273.15
    forecast.avg_humidity = 45.5
    forecast.will_rain = True
    
    msg = forecast.get_weather_message()
    
    expected_rain_msg = (
        "🌡️ Today's weather in Message City:\n"
        "- Max Temp: 20.00°C / 68.00°F\n"
        "- Feels Like: 10.00°C / 50.00°F\n"
        "- Min Temp: 0.00°C / 32.00°F\n"
        "- Avg Humidity: 45.50%\n"
        "☔ Rain expected! Bring an umbrella!\n"
    )
    assert msg == expected_rain_msg

    forecast.will_rain = False
    msg_no_rain = forecast.get_weather_message()
    expected_no_rain_msg = (
        "🌡️ Today's weather in Message City:\n"
        "- Max Temp: 20.00°C / 68.00°F\n"
        "- Feels Like: 10.00°C / 50.00°F\n"
        "- Min Temp: 0.00°C / 32.00°F\n"
        "- Avg Humidity: 45.50%\n"
        "🌤️ No rain today!\n"
    )
    assert msg_no_rain == expected_no_rain_msg
