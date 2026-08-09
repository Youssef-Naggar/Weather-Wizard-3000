from typing import Dict, Any
from forecast import Forecast
from utilities import convert_kelvin_to_celsius_fahrenheit


def determine_target_seasonality(forecast: Forecast, prefs: Dict[str, Any]) -> str:
    cold_threshold = prefs.get("cold_threshold", 15)
    hot_threshold = prefs.get("hot_threshold", 25)

    max_celsius = convert_kelvin_to_celsius_fahrenheit(forecast.max_temp_k)[0]
    min_celsius = convert_kelvin_to_celsius_fahrenheit(forecast.min_temp_k)[0]

    if max_celsius < cold_threshold or min_celsius < cold_threshold:
        return "cold"
    if max_celsius >= hot_threshold:
        return "hot"
    return "cold" if forecast.will_rain else "hot"
