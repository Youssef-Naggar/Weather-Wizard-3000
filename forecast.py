from typing import Dict, List, Any
import os
import datetime
from utilities import make_api_request, convert_kelvin_to_celsius_fahrenheit

class Forecast:
    OWM_ENDPOINT: str = "https://api.openweathermap.org/data/2.5/forecast"
    API_KEY: str = os.environ.get("OWM_API_KEY", "")

    def __init__(self) -> None:
        self.city_name: str = ""
        self.will_rain: bool = False
        self.max_temp_k: float = 0.0
        self.feels_like_temp_k: float = 0.0
        self.min_temp_k: float = 0.0
        self.avg_humidity: float = 0.0

    def fetch_weather_data(self, lat: float, lon: float, target_date: datetime.date) -> None:
        url_string: str = f"{self.OWM_ENDPOINT}?lat={lat}&lon={lon}&appid={self.API_KEY}"
        weather_data: Dict[str, Any] = make_api_request(url_string)
        self.process_weather_data(weather_data, target_date)

    def fetch_weather_data_with_city_name(self, city_name: str, target_date: datetime.date) -> None:
        url_string: str = f"{self.OWM_ENDPOINT}?q={city_name}&appid={self.API_KEY}"
        weather_data: Dict[str, Any] = make_api_request(url_string)
        self.process_weather_data(weather_data, target_date)

    def process_weather_data(self, weather_data: Dict[str, Any], target_date: datetime.date) -> None:
        self.city_name = weather_data["city"]["name"]
        forecasts: List[Dict[str, Any]] = weather_data["list"]

        temp_max: float = float('-inf')
        temp_min: float = float('inf')
        feels_like_total: float = 0.0
        humidity_total: float = 0.0
        count: int = 0
        rain_detected: bool = False

        for hour_data in forecasts:
            dt_txt: str = hour_data["dt_txt"]
            date_time: datetime.date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()

            if date_time == target_date:
                main: Dict[str, Any] = hour_data["main"]
                weather: Dict[str, Any] = hour_data["weather"][0]

                condition_code: int = weather["id"]
                if condition_code < 700:
                    rain_detected = True

                current_temp_max: float = main["temp_max"]
                current_temp_min: float = main["temp_min"]
                current_feels_like: float = main["feels_like"]

                temp_max = max(temp_max, current_temp_max)
                temp_min = min(temp_min, current_temp_min)
                feels_like_total += current_feels_like
                humidity_total += main["humidity"]
                count += 1

        if count > 0:
            self.will_rain = rain_detected
            self.max_temp_k = temp_max
            self.min_temp_k = temp_min
            self.feels_like_temp_k = feels_like_total / count
            self.avg_humidity = humidity_total / count

    def get_weather_message(self) -> str:
        max_converted: List[float] = convert_kelvin_to_celsius_fahrenheit(self.max_temp_k)
        feels_like_converted: List[float] = convert_kelvin_to_celsius_fahrenheit(self.feels_like_temp_k)
        min_converted: List[float] = convert_kelvin_to_celsius_fahrenheit(self.min_temp_k)

        rain_message: str = "☔ Rain expected! Bring an umbrella!" if self.will_rain else "🌤️ No rain today!"

        return (
            f"🌡️ Today's weather in {self.city_name}:\n"
            f"- Max Temp: {max_converted[0]:.2f}°C / {max_converted[1]:.2f}°F\n"
            f"- Feels Like: {feels_like_converted[0]:.2f}°C / {feels_like_converted[1]:.2f}°F\n"
            f"- Min Temp: {min_converted[0]:.2f}°C / {min_converted[1]:.2f}°F\n"
            f"- Avg Humidity: {self.avg_humidity:.2f}%\n"
            f"{rain_message}\n"
        )