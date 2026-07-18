from abc import ABC, abstractmethod
import datetime
from typing import Dict
from utilities import get_auto_location
from forecast import Forecast, WeatherClient
from brain import Brain
from ui import WeatherUI
from prompt_builder import build_prompt

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
            raw_data = self.app.weather_client.fetch_weather_by_city(city)
            self.app.forecast_service.process_weather_data(raw_data, self.app.target_date)
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
            raw_data = self.app.weather_client.fetch_weather_by_coordinates(coords[0], coords[1])
            self.app.forecast_service.process_weather_data(raw_data, self.app.target_date)
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
            raw_data = self.app.weather_client.fetch_weather_by_coordinates(lat, lon)
            self.app.forecast_service.process_weather_data(raw_data, self.app.target_date)
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
        import os
        from prompt_builder import load_model_settings, save_preferences

        # 1. Check if model settings and API key are configured
        from exceptions import SettingsValidationError
        try:
            model_settings = load_model_settings()
        except SettingsValidationError as e:
            self.app.ui.print_error(f"LLM settings are invalid: {str(e)}")
            self.app.ui.print_message("Please go to Settings to configure them first.")
            self.app.ai_loop_running = False
            return False

        if not os.path.exists('model-settings.json') or not model_settings.get("api_key"):
            self.app.ui.print_error("LLM Provider or API key is not configured. Please go to Settings to configure them first.")
            self.app.ai_loop_running = False
            return False

        # 2. Check if preferences file exists
        if not os.path.exists('preferences.json'):
            self.app.ui.print_error("No personal preferences found. Redirecting to setup a new profile...")
            new_prefs = self.app.ui.create_new_profile_flow()
            save_preferences(new_prefs)
            self.app.ui.print_message("\n✅ Personal profile created successfully!")

        commute_type = self.app.ui.get_commute_type()
        trip_type = self.app.ui.get_trip_type()
        dress_code = self.app.ui.get_dress_code()

        self.app.ui.print_message("\n🧙‍♂️ Wizard suggestion:")
        try:
            system_prompt = build_prompt(commute_type, trip_type, dress_code)
            suggestion = self.app.brain.ai_suggestion(self.app.weather_summary, system_prompt)
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

class SettingsCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def execute(self) -> bool:
        from prompt_builder import (
            load_preferences, save_preferences,
            load_model_settings, save_model_settings
        )
        loop_running = True
        while loop_running:
            self.app.ui.print_settings_menu()
            choice = self.app.ui.get_choice()
            if choice == 1:
                from exceptions import SettingsValidationError
                try:
                    settings = load_model_settings()
                except SettingsValidationError as e:
                    self.app.ui.print_error(f"Configuration load error: {str(e)}")
                    self.app.ui.print_message("Resetting to default LLM settings...")
                    settings = {
                        "provider": "google",
                        "model": "gemini-2.5-flash",
                        "api_key": ""
                    }
                updated_settings = self.app.ui.edit_llm_settings(settings)
                
                self.app.ui.print_message("\n🔄 Verifying connection to LLM provider...")
                try:
                    # Test connection live via Brain before saving
                    reply = self.app.brain.test_connection(
                        updated_settings["provider"],
                        updated_settings["model"],
                        updated_settings["api_key"]
                    )
                    
                    save_model_settings(updated_settings)
                    self.app.ui.print_message(f"✅ Configuration updated successfully! (Agent replied: {reply})")
                except Exception as e:
                    self.app.ui.print_error(f"Failed to connect: {str(e)}")
                    self.app.ui.print_message("❌ Settings NOT saved. Please check your credentials and try again.")
            elif choice == 2:
                prefs = load_preferences()
                updated_prefs = self.app.ui.edit_weather_preferences(prefs)
                save_preferences(updated_prefs)
                self.app.ui.print_message("\n✅ Weather preferences updated successfully!")
            elif choice == 3:
                prefs = load_preferences()
                updated_prefs = self.app.ui.edit_personal_profile(prefs)
                save_preferences(updated_prefs)
                self.app.ui.print_message("\n✅ Personal profile updated successfully!")
            elif choice == 4:
                new_prefs = self.app.ui.create_new_profile_flow()
                save_preferences(new_prefs)
                self.app.ui.print_message("\n✅ New profile preferences saved successfully!")
            elif choice == 5:
                prefs = load_preferences()
                self.app.ui.view_current_settings(prefs)
            elif choice == 6:
                loop_running = False
            else:
                self.app.ui.print_error("Invalid option! Please try again.")
        return False


class WeatherApp:
    def __init__(self) -> None:
        self.weather_client = WeatherClient()
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
            6: SettingsCommand(self),
            7: ExitCommand(self),
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
