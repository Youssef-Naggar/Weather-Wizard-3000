from abc import ABC, abstractmethod
import datetime
from typing import Dict
from utilities import get_auto_location
from forecast import Forecast
from brain import Brain
from ui import WeatherUI

class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        """
        Executes the command.
        Returns:
            bool: True if the loop should retry, False if execution finished successfully.
        """
        pass

class SelectDateCommand(Command):
    def __init__(self, app: 'WeatherApp', offset: int) -> None:
        self.app = app
        self.offset = offset

    def execute(self) -> bool:
        self.app.target_date = datetime.date.today() + datetime.timedelta(days=self.offset)
        self.app.location_loop_running = True
        return False

class ExitCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        self.app.running = False
        self.app.location_loop_running = False
        self.app.ai_loop_running = False
        self.app.ui.print_message("\n✨ Thank you for using Weather Wizard 3000!")
        self.app.ui.print_message("☁️  Stay dry and have a wonderful day!\n")
        return False

class CitySearchCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        city = self.app.ui.get_city_name()
        if not city:
            self.app.ui.print_error("City name cannot be empty.")
            return True
        try:
            self.app.forecast_service.fetch_weather_data_with_city_name(city, self.app.target_date)
            self.app.weather_summary = self.app.forecast_service.get_weather_message()
            self.app.ui.print_message("\n" + self.app.weather_summary)
            return False
        except Exception as err:
            self.app.ui.print_error(f"Failed to fetch data: {str(err)}")
            return True

class AutoLocationCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        self.app.ui.print_message("\n🔍 Detecting your location...")
        try:
            coords = get_auto_location()
            self.app.ui.print_message(f"📍 Detected coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            self.app.forecast_service.fetch_weather_data(coords[0], coords[1], self.app.target_date)
            self.app.weather_summary = self.app.forecast_service.get_weather_message()
            self.app.ui.print_message("\n" + self.app.weather_summary)
            return False
        except Exception as err:
            self.app.ui.print_error(f"Location detection failed: {str(err)}")
            return True

class ManualCoordinatesCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        lat = self.app.ui.get_coordinate("Latitude")
        lon = self.app.ui.get_coordinate("Longitude")

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            self.app.ui.print_error("Invalid coordinates! Values out of range.")
            return True

        try:
            self.app.forecast_service.fetch_weather_data(lat, lon, self.app.target_date)
            self.app.weather_summary = self.app.forecast_service.get_weather_message()
            self.app.ui.print_message("\n" + self.app.weather_summary)
            return False
        except Exception as err:
            self.app.ui.print_error(f"Error: {str(err)}")
            return True

class GetAiSuggestionCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        self.app.ui.print_message("\n🧙‍♂️ Wizard suggestion:")
        try:
            suggestion = self.app.brain.ai_suggestion(self.app.weather_summary)
            self.app.ui.print_message(suggestion)
        except Exception as err:
            self.app.ui.print_error(f"AI suggestion failed: {str(err)}")
        self.app.ai_loop_running = False
        return False

class SkipAiSuggestionCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        self.app.ai_loop_running = False
        return False

class WeatherApp:
    def __init__(self) -> None:
        self.forecast_service = Forecast()
        self.brain = Brain()
        self.ui = WeatherUI()
        self.target_date = datetime.date.today()
        self.weather_summary = ""
        self.running = True
        self.location_loop_running = True
        self.ai_loop_running = True

        self.time_commands: Dict[int, Command] = {
            1: SelectDateCommand(self, 0),
            2: SelectDateCommand(self, 1),
            3: SelectDateCommand(self, 2),
            4: SelectDateCommand(self, 3),
            5: SelectDateCommand(self, 4),
            6: ExitCommand(self),
        }

        self.location_commands: Dict[int, Command] = {
            1: CitySearchCommand(self),
            2: AutoLocationCommand(self),
            3: ManualCoordinatesCommand(self),
            4: ExitCommand(self),
        }

        self.ai_commands: Dict[int, Command] = {
            1: GetAiSuggestionCommand(self),
            2: SkipAiSuggestionCommand(self),
        }

    def run(self) -> None:
        self.ui.print_welcome()
        while self.running:
            self.location_loop_running = False
            self.ai_loop_running = False

            self.ui.print_time_menu(datetime.date.today())
            choice = self.ui.get_choice()
            cmd = self.time_commands.get(choice)
            if cmd:
                cmd.execute()
            else:
                self.ui.print_error("Invalid option! Please try again.")
                continue

            if not self.running:
                break

            while self.location_loop_running:
                self.ui.print_location_menu()
                choice = self.ui.get_choice()
                cmd = self.location_commands.get(choice)
                if cmd:
                    retry = cmd.execute()
                    if not retry:
                        self.ai_loop_running = True
                        break
                else:
                    self.ui.print_error("Invalid option! Please try again.")

            if not self.running:
                break

            while self.ai_loop_running:
                self.ui.print_ai_menu()
                choice = self.ui.get_choice()
                cmd = self.ai_commands.get(choice)
                if cmd:
                    cmd.execute()
                else:
                    self.ui.print_error("Invalid option! Please try again.")
