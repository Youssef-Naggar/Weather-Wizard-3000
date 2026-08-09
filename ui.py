import datetime
from typing import Any, List, Optional
from prettytable import PrettyTable
from wardrobe_item import AiSuggestionOutput



class WeatherUI:
    def print_welcome(self) -> None:
        print("\n=== 🌦️ Weather Wizard 3000 🌈 ===")
        print("Your personal weather forecasting assistant!\n")

    def print_time_menu(self, today: datetime.date) -> None:
        print("\n-------- Main Menu --------")
        print("1. Today")
        print("2. Tomorrow")
        print(f"3. {today + datetime.timedelta(days=2)}")
        print(f"4. {today + datetime.timedelta(days=3)}")
        print(f"5. {today + datetime.timedelta(days=4)}")
        print("6. Settings")
        print("7. Exit")
        print("Enter your choice (1-7): ", end="")

    def print_location_menu(self) -> None:
        print("\nChoose one of the following search methods:")
        print("1. Search by city name")
        print("2. Use my current location")
        print("3. Enter coordinates manually")
        print("4. Exit")
        print("Enter your choice (1-4): ", end="")

    def print_settings_menu(self) -> None:
        print("\n⚙️  WEATHER WIZARD 3000 SETTINGS")
        print("--------------------------------")
        print("1. Configure AI Models & Credentials")
        print("2. Edit Weather & Temperature Preferences")
        print("3. Edit Personal Style & Profile")
        print("4. Create New Profile Preferences")
        print("5. View Current Settings")
        print("6. Synthesize Closet (Scan Photo Folder)")
        print("7. Configure Virtual Avatar Photo Path")
        print("8. Back to Main Menu")
        print("Enter your choice (1-8): ", end="")

    def print_unified_ai_models_menu(self) -> None:
        print("\n⚙️  CONFIGURE AI MODELS & CREDENTIALS")
        print("------------------------------------")
        print("1. Configure Weather Wizard Brain (Text LLM)")
        print("2. Configure Closet Synthesizer (Vision LLM)")
        print("3. Configure Virtual Avatar Drawer (Image AI)")
        print("4. Back to Settings Menu")
        print("Enter your choice (1-4): ", end="")


    def print_ai_menu(self) -> None:
        print("Do you want our AI Weather Wizard 3000 help you to dress properly in this weather?")
        print("1. Yes")
        print("2. No")
        print("Enter your choice (1-2): ", end="")

    def get_commute_type(self) -> str:
        print("\nHow will you go today?")
        print("1. Walking/Cycling")
        print("2. Public Transit")
        print("3. Driving/Indoor")
        print("Enter your choice (1-3): ", end="")
        while True:
            choice = self.get_choice()
            if choice == 1:
                return "Walking/Cycling"
            elif choice == 2:
                return "Public Transit"
            elif choice == 3:
                return "Driving/Indoor"
            else:
                print("Invalid option! Please enter a number between 1 and 3: ", end="")

    def get_trip_type(self) -> str:
        print("\nWhat is the type of the trip you're going for today? (e.g., Work, School, Casual, Sporty): ", end="")
        while True:
            val = input().strip()
            if val:
                return val
            print("Trip type cannot be empty. Please enter a value: ", end="")

    def get_dress_code(self) -> str:
        print("\nIs there a specific dress code? (Optional - press Enter to skip): ", end="")
        return input().strip()

    def get_choice(self) -> int:
        try:
            return int(input().strip())
        except ValueError:
            return -1

    def get_city_name(self) -> str:
        print("\nEnter city name (e.g., Tokyo): ", end="")
        return input().strip()

    def get_coordinate(self, coord_type: str) -> float:
        range_str = "(-90 to 90)" if coord_type.lower() == "latitude" else "(-180 to 180)"
        print(f"\nEnter {coord_type.lower()} {range_str}: ", end="")
        while True:
            try:
                return float(input().strip())
            except ValueError:
                print(f"Invalid {coord_type.lower()}! Please enter a valid number: ", end="")

    def print_message(self, message: str) -> None:
        print(message)

    def print_error(self, message: str) -> None:
        print(f"⚠️  {message}")

    def _print_outfit_details(self, outfit: Any, idx: int) -> None:
        print(f"\n✨ Outfit {idx}: {outfit.outfit_title}")
        top_id_str = f" [Closet ID: {outfit.top_id}]" if outfit.top_id else " [Not in Closet]"
        bottom_id_str = f" [Closet ID: {outfit.bottom_id}]" if outfit.bottom_id else " [Not in Closet]"
        shoes_id_str = f" [Closet ID: {outfit.shoes_id}]" if outfit.shoes_id else " [Not in Closet]"
        print(f"   - Top: {outfit.top_description}{top_id_str}")
        print(f"   - Bottom: {outfit.bottom_description}{bottom_id_str}")
        print(f"   - Shoes: {outfit.shoes_description}{shoes_id_str}")
        if outfit.jacket_description:
            jacket_id_str = f" [Closet ID: {outfit.jacket_id}]" if outfit.jacket_id else " [Not in Closet]"
            print(f"   - Jacket: {outfit.jacket_description}{jacket_id_str}")
        if outfit.accessory_descriptions:
            acc_strs = []
            for desc, acc_id in zip(outfit.accessory_descriptions, outfit.accessory_ids or []):
                acc_strs.append(f"{desc} [Closet ID: {acc_id}]" if acc_id else desc)
            print(f"   - Accessories: {', '.join(acc_strs)}")

    def print_ai_suggestion(self, suggestion: Any) -> None:
        if isinstance(suggestion, str):
            print(suggestion)
            return

        if isinstance(suggestion, AiSuggestionOutput):
            if suggestion.ai_suggestion:
                print(f"\n💬 {suggestion.ai_suggestion}\n")

            if suggestion.recommended_outfits:
                print("👔 RECOMMENDED OUT FITS FROM YOUR CLOSET:")
                print("========================================")
                for idx, outfit in enumerate(suggestion.recommended_outfits, 1):
                    self._print_outfit_details(outfit, idx)
                print("========================================\n")
            return

        print(str(suggestion))

    def get_input_with_default(self, prompt: str, default_val: str) -> str:
        print(f"{prompt} [{default_val}]: ", end="")
        val = input().strip()
        return val if val else default_val

    def get_int_input_with_default(self, prompt: str, default_val: int) -> int:
        while True:
            val_str = self.get_input_with_default(prompt, str(default_val))
            try:
                return int(val_str)
            except ValueError:
                self.print_error("Invalid number! Please enter an integer.")

    def edit_weather_preferences(self, prefs: dict) -> dict:
        print("\n--- Edit Weather & Temperature Preferences ---")
        unit = self.get_input_with_default("Temperature Unit (C/F)", prefs.get("temp_unit", "C")).upper()
        while unit not in ["C", "F"]:
            self.print_error("Invalid unit! Please enter C or F.")
            unit = self.get_input_with_default("Temperature Unit (C/F)", prefs.get("temp_unit", "C")).upper()
        
        cold = self.get_int_input_with_default("Cold Threshold (temp you need a jacket)", prefs.get("cold_threshold", 15))
        hot = self.get_int_input_with_default("Hot Threshold (temp you want shorts/shorts sleeves)", prefs.get("hot_threshold", 25))
        perfect = self.get_int_input_with_default("Perfect Temperature", prefs.get("perfect_temp", 20))
        
        prefs["temp_unit"] = unit
        prefs["cold_threshold"] = cold
        prefs["hot_threshold"] = hot
        prefs["perfect_temp"] = perfect
        return prefs

    def edit_personal_profile(self, prefs: dict) -> dict:
        print("\n--- Edit Personal Style & Profile ---")
        print("Available Styles: Casual, Sporty/Athletic, Business/Formal, Streetwear, Minimalist")
        style = self.get_input_with_default("Preferred Clothing Style", prefs.get("clothing_style", "Casual"))
        
        color = self.get_input_with_default("Favorite Color", prefs.get("favorite_color", "Blue"))
        age = self.get_int_input_with_default("Age", prefs.get("age", 21))
        
        sex = self.get_input_with_default("Sex (Male/Female)", prefs.get("sex", "Male"))
        while sex.lower() not in ["male", "female"]:
            self.print_error("Invalid sex! Please enter Male or Female.")
            sex = self.get_input_with_default("Sex (Male/Female)", prefs.get("sex", "Male"))
        
        sensitivities = self.get_input_with_default("Weather Sensitivities", prefs.get("weather_sensitivities", ""))
        
        prefs["clothing_style"] = style
        prefs["favorite_color"] = color
        prefs["age"] = age
        prefs["sex"] = sex.capitalize()
        prefs["weather_sensitivities"] = sensitivities
        return prefs

    def view_current_settings(self, prefs: dict) -> None:
        print("\n⚙️  CURRENT SETTINGS & PREFERENCES")
        print("--------------------------------")
        print(f"Temperature Unit:      {prefs.get('temp_unit')}")
        print(f"Cold Threshold:        {prefs.get('cold_threshold')}°{prefs.get('temp_unit')}")
        print(f"Hot Threshold:         {prefs.get('hot_threshold')}°{prefs.get('temp_unit')}")
        print(f"Perfect Temperature:   {prefs.get('perfect_temp')}°{prefs.get('temp_unit')}")
        print(f"Clothing Style:        {prefs.get('clothing_style')}")
        print(f"Favorite Color:        {prefs.get('favorite_color')}")
        print(f"Age:                   {prefs.get('age')}")
        print(f"Sex:                   {prefs.get('sex')}")
        print(f"Sensitivities:         {prefs.get('weather_sensitivities')}")
        print("--------------------------------")

    def _print_provider_choices_grid(self, providers: list[str]) -> None:
        table = PrettyTable()
        table.header = False
        for i in range(0, len(providers), 4):
            row = []
            for j in range(4):
                if i + j < len(providers):
                    idx = i + j + 1
                    name = providers[i + j]
                    row.append(f"{idx:2d}. {name}")
                else:
                    row.append("")
            table.add_row(row)
        print(table)

    def _select_provider(self, current_provider: str) -> str:
        import litellm
        
        providers = sorted(list(litellm.models_by_provider.keys()))
        custom_opt = "[C] Custom Endpoint / Localhost (Ollama, LM Studio, vLLM)"
        display_providers = providers + [custom_opt]
        
        current_p = current_provider.lower()
        if current_p == "google":
            current_p = "gemini"
            
        provider = None
        while not provider:
            print("\nSelect LLM Provider:")
            self._print_provider_choices_grid(display_providers)
            
            default_idx = -1
            if current_p in providers:
                default_idx = providers.index(current_p) + 1
            elif current_p in ("custom", "ollama", "local", "lmstudio", "vllm"):
                default_idx = len(display_providers)
                
            prompt = f"Enter choice (1-{len(display_providers)})"
            choice_str = self.get_input_with_default(prompt, str(default_idx)) if default_idx != -1 else input(f"{prompt}: ").strip()
                
            try:
                val = int(choice_str)
                if 1 <= val <= len(providers):
                    provider = providers[val - 1]
                elif val == len(display_providers):
                    provider = "custom"
                else:
                    raise ValueError()
            except ValueError:
                self.print_error(f"Invalid choice! Please enter a number between 1 and {len(display_providers)}.")
                
        return provider

    def _print_model_choices_grid(self, provider: str, models: list[str]) -> None:
        print(f"\nSelect Model for {provider.capitalize()}:")
        table = PrettyTable()
        table.header = False
        for i in range(0, len(models), 3):
            row = []
            for j in range(3):
                if i + j < len(models):
                    idx = i + j + 1
                    name = models[i + j]
                    row.append(f"{idx:2d}. {name}")
                else:
                    row.append("")
            table.add_row(row)
        print(table)

    def _filter_models_for_capability(self, provider: str, mode: str) -> List[str]:
        import litellm
        from model_registry import is_text_model, is_vision_model, is_image_model

        prov_lookup = "gemini" if provider.lower() == "google" else provider.lower()
        raw_models = litellm.models_by_provider.get(prov_lookup, [])

        checker_map = {
            "vision": is_vision_model,
            "image": is_image_model,
        }
        checker = checker_map.get(mode, is_text_model)
        models = sorted([m for m in raw_models if checker(m, provider)])

        if not models:
            self.print_error(f"No {mode} models found for provider '{provider}'. Showing all provider models.")
            models = sorted(list(raw_models))
        return models

    def _select_model(self, provider: str, current_model: str, mode: str = "text") -> str:
        models = self._filter_models_for_capability(provider, mode)
        custom_option = "[Enter custom model name...]"
        display_models = models + [custom_option]

        model = None
        while not model:
            self._print_model_choices_grid(provider, display_models)

            default_idx = models.index(current_model) + 1 if current_model in models else (len(display_models) if current_model else -1)
            prompt = f"Enter choice (1-{len(display_models)})"
            choice_str = self.get_input_with_default(prompt, str(default_idx)) if default_idx != -1 else input(f"{prompt}: ").strip()

            try:
                val = int(choice_str)
                if 1 <= val <= len(models):
                    model = display_models[val - 1]
                elif val == len(display_models):
                    custom_name = input(f"Enter custom model name for {provider.capitalize()}: ").strip()
                    if custom_name:
                        model = custom_name
                    else:
                        self.print_error("Model name cannot be empty. Please enter a valid custom model name.")
                else:
                    raise ValueError()
            except ValueError:
                self.print_error(f"Invalid choice! Please enter a number between 1 and {len(display_models)}.")

        return model

    def _get_api_key(self, provider: str, current_api_key: str) -> str:
        from exceptions import InvalidApiKeyError
        api_key = None
        while api_key is None:
            prompt_key = "API Key"
            if current_api_key:
                masked = current_api_key[:4] + "..." + current_api_key[-4:] if len(current_api_key) > 8 else "***"
                prompt_key = f"API Key [{masked}]"
            else:
                prompt_key = "API Key"
                
            print(f"{prompt_key}: ", end="")
            input_key = input().strip()
            
            if not input_key:
                if current_api_key:
                    return current_api_key
                else:
                    try:
                        raise InvalidApiKeyError(provider)
                    except InvalidApiKeyError as e:
                        self.print_error(str(e))
            else:
                api_key = input_key
        return api_key

    def edit_llm_settings(self, settings: dict, mode: str = "text") -> dict:
        print(f"\n--- Configure LLM Provider & Model ({mode.capitalize()} Mode) ---")
        
        current_provider = settings.get("provider", "google").lower()
        provider = self._select_provider(current_provider)
        
        if provider == "custom":
            current_api_base = settings.get("api_base") or "http://localhost:11434"
            api_base = self.get_input_with_default("Enter Custom API Base URL (e.g. http://localhost:11434)", current_api_base)
            current_model = settings.get("model") or "ollama/llama3:8b"
            model = self.get_input_with_default("Enter Custom Model Identifier (e.g. ollama/llama3:8b)", current_model)
            current_api_key = settings.get("api_key", "")
            print(f"API Key (Optional for local server) [{current_api_key or 'None'}]: ", end="")
            input_key = input().strip()
            api_key = input_key if input_key else current_api_key
            settings["provider"] = provider
            settings["model"] = model
            settings["api_key"] = api_key
            settings["api_base"] = api_base
            return settings

        current_model = settings.get("model", "")
        model = self._select_model(provider, current_model, mode=mode)
        
        current_api_key = settings.get("api_key", "")
        api_key = self._get_api_key(provider, current_api_key)
                
        settings["provider"] = provider
        settings["model"] = model
        settings["api_key"] = api_key
        settings["api_base"] = None
        return settings


    def create_new_profile_flow(self) -> dict:
        print("\n==============================================")
        print("🌟 CREATE NEW PROFILE PREFERENCES SETUP 🌟")
        print("==============================================")
        prefs = {}
        prefs = self.edit_weather_preferences(prefs)
        prefs = self.edit_personal_profile(prefs)
        return prefs

    def print_synthesis_results(self, count: int) -> None:
        print("\n==============================================")
        print("📸 CLOSET MULTIMODAL SYNTHESIS COMPLETE 📸")
        print("==============================================")
        if count == 0:
            print("ℹ️ No new untagged clothing photos found in closet/ directory.")
        else:
            print(f"✅ Successfully ingested {count} new clothing items into closet.json!")
        print("==============================================\n")

    def print_tryon_result(self, output_path: str) -> None:
        print("\n==============================================")
        print("👕 VIRTUAL AVATAR TRY-ON PREVIEW GENERATED 👕")
        print("==============================================")
        print(f"🖼️ Preview file: [tryon_outfit](file:///{output_path.replace('\\', '/')})")
        print(f"📁 Local Path: {output_path}")
        print("==============================================\n")

    def get_tryon_outfit_choice(self, num_outfits: int) -> int:
        if num_outfits <= 0:
            return 0
        print(f"Enter outfit number (1-{num_outfits}), or 0 to skip: ", end="")
        while True:
            try:
                val = int(input().strip())
                if 0 <= val <= num_outfits:
                    return val
                self.print_error(f"Invalid choice! Please enter a number between 0 and {num_outfits}.")
            except ValueError:
                self.print_error(f"Invalid choice! Please enter a number between 0 and {num_outfits}.")

    def ask_create_demo_yes_no(self) -> bool:
        print("\n🎨 Do you want to create a demo try-on preview for an outfit? (y/n): ", end="")
        ans = input().strip().lower()
        return ans in ("y", "yes")

    def configure_avatar_path_flow(self, current_path: str) -> Optional[str]:
        import os
        print("\n🖼️  CONFIGURE VIRTUAL AVATAR PHOTO PATH")
        print("---------------------------------------")
        if current_path and os.path.exists(current_path):
            print(f"Current Avatar Photo Path: {current_path}")
            print("1. Configure new avatar photo path")
            print("2. Back to AI settings")
            print("Enter choice (1-2): ", end="")
            choice = input().strip()
            if choice == "2":
                return None

        print("Enter path to your avatar photo (e.g. user_avatar.png or C:/path/photo.jpg): ", end="")
        new_path = input().strip()
        return new_path if new_path else None


