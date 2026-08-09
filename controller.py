from abc import ABC, abstractmethod
import datetime
import os
from typing import Dict, Any, Optional

from utilities import get_auto_location
from forecast import Forecast, WeatherClient
from brain import Brain
from ui import WeatherUI
from prompt_builder import build_prompt, load_preferences
from weather_filter import determine_target_seasonality
from synthesizer import ClosetSynthesizer
from drawer import AvatarDrawer
from closet import Closet



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
        from settings_manager import load_model_settings, save_preferences
        from wardrobe_item import AiSuggestionOutput

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
            prefs = load_preferences()
            target_seasonality = determine_target_seasonality(self.app.forecast_service, prefs)
            system_prompt = build_prompt(commute_type, trip_type, dress_code, target_seasonality=target_seasonality)
            suggestion = self.app.brain.ai_suggestion(self.app.weather_summary, system_prompt)
            self.app.ui.print_ai_suggestion(suggestion)
            closet_configured = False
            if os.path.exists("closet.json"):
                try:
                    closet_configured = bool(Closet().get_all_items())
                except Exception:
                    closet_configured = False

            if isinstance(suggestion, AiSuggestionOutput) and suggestion.recommended_outfits and closet_configured:
                from settings_manager import load_drawer_settings
                drawer_settings = load_drawer_settings()
                avatar_path = drawer_settings.get("user_avatar_path", "")
                avatar_configured = bool(avatar_path) and os.path.exists(avatar_path)

                if not avatar_configured:
                    self.app.ui.print_message("\nℹ️ Virtual Avatar photo is not configured. Skipping try-on demo prompt.")
                    self.app.ui.print_message("   (Configure avatar photo in Settings -> 7. Configure Virtual Avatar Photo Path)")
                else:
                    if self.app.ui.ask_create_demo_yes_no():
                        choice = self.app.ui.get_tryon_outfit_choice(len(suggestion.recommended_outfits))
                        if choice > 0:
                            selected_outfit = suggestion.recommended_outfits[choice - 1]
                            self.app.ui.print_message(f"\n🎨 Generating Virtual Avatar Try-On for Outfit {choice}: {selected_outfit.outfit_title}...")
                            GenerateAvatarTryOnCommand(self.app, selected_outfit, outfit_num=choice).execute()
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


class SynthesizeClosetCommand(Command):
    def __init__(self, app: Optional['WeatherApp'] = None) -> None:
        self.app = app

    def execute(self) -> bool:
        try:
            synthesizer = ClosetSynthesizer()
            count = synthesizer.ingest_new_photos()
            if self.app and hasattr(self.app, "ui"):
                self.app.ui.print_synthesis_results(count)
            else:
                print(f"\n✅ Synthesized and ingested {count} new clothing items!")
        except Exception as e:
            msg = f"⚠️ Closet synthesis failed: {str(e)}"
            if self.app and hasattr(self.app, "ui"):
                self.app.ui.print_error(msg)
            else:
                print(msg)
        return False


class GenerateAvatarTryOnCommand(Command):
    def __init__(self, app: 'WeatherApp', outfit: Any, outfit_num: int = 1) -> None:
        self.app = app
        self.outfit = outfit
        self.outfit_num = outfit_num

    def execute(self) -> bool:
        from settings_manager import load_drawer_settings
        drawer_settings = load_drawer_settings()
        avatar_path = drawer_settings.get("user_avatar_path", "")
        if not avatar_path or not os.path.exists(avatar_path):
            msg = "⚠️ Virtual Avatar photo is not configured or file not found. Skipping try-on demo preview.\n(Please configure avatar photo in Settings -> 7. Configure Virtual Avatar Photo Path)"
            if self.app and hasattr(self.app, "ui"):
                self.app.ui.print_error(msg)
            else:
                print(msg)
            return False

        drawer = AvatarDrawer()
        closet = Closet()
        output_path = drawer.generate_tryon_preview(self.outfit, closet, outfit_num=self.outfit_num)
        if output_path is None:
            return False
        if self.app and hasattr(self.app, "ui") and hasattr(self.app.ui, "print_tryon_result"):
            self.app.ui.print_tryon_result(output_path)
        else:
            print(f"\n✨ Virtual Avatar Try-On Preview generated at: {output_path}")
        return True


class SettingsCommand(Command):
    def __init__(self, app: 'WeatherApp') -> None:
        self.app = app

    def _configure_ai_models_sub_menu(self) -> None:
        from settings_manager import (
            load_model_settings, save_model_settings,
            load_synthesizer_settings, save_synthesizer_settings,
            load_drawer_settings, save_drawer_settings
        )
        sub_loop = True
        while sub_loop:
            self.app.ui.print_unified_ai_models_menu()
            choice = self.app.ui.get_choice()
            if choice == 1:
                from exceptions import SettingsValidationError
                try:
                    settings = load_model_settings()
                except SettingsValidationError as e:
                    self.app.ui.print_error(f"Configuration load error: {str(e)}")
                    settings = {"provider": "google", "model": "gemini-2.5-flash", "api_key": ""}
                updated = self.app.ui.edit_llm_settings(settings, mode="text")
                self.app.ui.print_message("\n🔄 Verifying connection to LLM provider...")
                try:
                    reply = self.app.brain.test_connection(updated["provider"], updated["model"], updated["api_key"])
                    save_model_settings(updated)
                    self.app.ui.print_message(f"✅ Weather Brain model saved! (Agent replied: {reply})")
                except Exception as e:
                    self.app.ui.print_error(f"Failed to connect: {str(e)}")
            elif choice == 2:
                settings = load_synthesizer_settings()
                updated = self.app.ui.edit_llm_settings(settings, mode="vision")
                self.app.ui.print_message("\n🔄 Verifying connection for Closet Synthesizer...")
                try:
                    reply = self.app.brain.test_connection(updated["provider"], updated["model"], updated["api_key"])
                    save_synthesizer_settings(updated)
                    self.app.ui.print_message(f"✅ Closet Synthesizer model saved! (Agent replied: {reply})")
                except Exception as e:
                    self.app.ui.print_error(f"Failed to connect: {str(e)}")
            elif choice == 3:
                settings = load_drawer_settings()
                updated = self.app.ui.edit_llm_settings(settings, mode="image")
                self.app.ui.print_message("\n🔄 Verifying connection for Virtual Avatar Drawer...")
                try:
                    reply = self.app.brain.test_connection(updated["provider"], updated["model"], updated["api_key"])
                    save_drawer_settings(updated)
                    self.app.ui.print_message(f"✅ Virtual Avatar Drawer model saved! (Agent replied: {reply})")
                except Exception as e:
                    self.app.ui.print_error(f"Failed to connect: {str(e)}")

            elif choice == 4:
                sub_loop = False
            else:
                self.app.ui.print_error("Invalid option! Please try again.")

    def execute(self) -> bool:
        from settings_manager import load_preferences, save_preferences, load_drawer_settings, save_drawer_settings
        loop_running = True
        while loop_running:
            self.app.ui.print_settings_menu()
            choice = self.app.ui.get_choice()
            if choice == 1:
                self._configure_ai_models_sub_menu()
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
                SynthesizeClosetCommand(self.app).execute()
            elif choice == 7:
                settings = load_drawer_settings()
                current_avatar_path = settings.get("user_avatar_path", "")
                new_avatar_path = self.app.ui.configure_avatar_path_flow(current_avatar_path)
                if new_avatar_path:
                    settings["user_avatar_path"] = new_avatar_path
                    save_drawer_settings(settings)
                    self.app.ui.print_message("\n✅ Virtual Avatar photo path saved successfully!")
            elif choice == 8:
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
                        closet_configured = False
                        if os.path.exists("closet.json"):
                            try:
                                closet_configured = bool(Closet().get_all_items())
                            except Exception:
                                closet_configured = False

                        if closet_configured:
                            self.ai_loop_running = True
                        else:
                            self.ui.print_message("\nℹ️ Closet is not scanned/configured (no closet.json). AI outfit recommendations are unavailable.")
                            self.ui.print_message("   (You can synthesize your closet in Settings -> 6. Synthesize Closet)")
                            self.ai_loop_running = False
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
