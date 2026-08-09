from forecast import Forecast
from weather_filter import determine_target_seasonality


def test_determine_seasonality_cold():
    forecast = Forecast()
    # 283.15 K = 10.0°C (Cold weather)
    forecast.max_temp_k = 283.15
    forecast.min_temp_k = 278.15
    prefs = {"cold_threshold": 15, "hot_threshold": 25}

    seasonality = determine_target_seasonality(forecast, prefs)
    assert seasonality == "cold"


def test_determine_seasonality_hot():
    forecast = Forecast()
    # 303.15 K = 30.0°C (Hot weather)
    forecast.max_temp_k = 303.15
    forecast.min_temp_k = 295.15
    prefs = {"cold_threshold": 15, "hot_threshold": 25}

    seasonality = determine_target_seasonality(forecast, prefs)
    assert seasonality == "hot"


def test_determine_seasonality_moderate_cold_bias():
    forecast = Forecast()
    # 291.15 K = 18.0°C (Moderate, but min temp 12°C < 15°C cold threshold)
    forecast.max_temp_k = 291.15
    forecast.min_temp_k = 285.15  # 12°C
    prefs = {"cold_threshold": 15, "hot_threshold": 25}

    seasonality = determine_target_seasonality(forecast, prefs)
    assert seasonality == "cold"


def test_determine_seasonality_default_prefs():
    forecast = Forecast()
    forecast.max_temp_k = 280.0  # ~6.85°C
    seasonality = determine_target_seasonality(forecast, {})
    assert seasonality == "cold"
