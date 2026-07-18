import datetime
from prettytable import PrettyTable
from prompt_builder import is_text_model

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
        print("1. Configure LLM Provider & Model")
        print("2. Edit Weather & Temperature Preferences")
        print("3. Edit Personal Style & Profile")
        print("4. Create New Profile Preferences")
        print("5. View Current Settings")
        print("6. Back to Main Menu")
        print("Enter your choice (1-6): ", end="")


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

    def _print_provider_choices(self, popular_providers: list[str], current_provider: str) -> None:
        print("\nSelect LLM Provider:")
        for i, prov in enumerate(popular_providers, 1):
            suffix = " (default)" if prov == current_provider else ""
            print(f"{i}. {prov.capitalize()}{suffix}")
        print(f"{len(popular_providers) + 1}. Show all supported providers")
        print(f"{len(popular_providers) + 2}. Enter custom provider name")

    def _handle_all_providers(self, all_providers: list[str]) -> str:
        from exceptions import InvalidProviderError
        print("\nAll Supported Providers:")
        table = PrettyTable()
        table.header = False
        for i in range(0, len(all_providers), 4):
            chunk = all_providers[i:i + 4]
            while len(chunk) < 4:
                chunk.append("")
            table.add_row(chunk)
        print(table)
        print("\nEnter provider name from the list: ", end="")
        prov_name = input().strip().lower()
        if prov_name not in all_providers:
            raise InvalidProviderError(prov_name, all_providers)
        return prov_name

    def _handle_custom_provider(self, all_providers: list[str]) -> str:
        from exceptions import InvalidProviderError
        print("\nEnter custom provider name: ", end="")
        prov_name = input().strip().lower()
        if prov_name not in all_providers:
            raise InvalidProviderError(prov_name, all_providers)
        return prov_name

    def _parse_provider_choice(self, choice_str: str, popular_providers: list[str], current_provider: str) -> str:
        import litellm
        from exceptions import InvalidProviderError
        
        all_providers = sorted(list(litellm.models_by_provider.keys()))
        if not choice_str:
            return current_provider
            
        try:
            val = int(choice_str)
            if 1 <= val <= len(popular_providers):
                return popular_providers[val - 1]
            elif val == len(popular_providers) + 1:
                return self._handle_all_providers(all_providers)
            elif val == len(popular_providers) + 2:
                return self._handle_custom_provider(all_providers)
            raise ValueError()
        except ValueError:
            raise InvalidProviderError(choice_str, popular_providers)

    def _select_provider(self, current_provider: str) -> str:
        from prompt_builder import POPULAR_PROVIDERS
        from exceptions import InvalidProviderError
        provider = None
        while not provider:
            self._print_provider_choices(POPULAR_PROVIDERS, current_provider)
            print(f"Enter choice (1-{len(POPULAR_PROVIDERS) + 2}): ", end="")
            choice_str = input().strip()
            try:
                provider = self._parse_provider_choice(choice_str, POPULAR_PROVIDERS, current_provider)
            except InvalidProviderError as e:
                self.print_error(str(e))
        return provider

    def _get_provider_models(self, provider: str) -> list[str]:
        import litellm
        from prompt_builder import POPULAR_MODELS
        popular_list = POPULAR_MODELS.get(provider.lower())
        raw_list = litellm.models_by_provider.get(provider.lower(), [])
        all_list = sorted([m for m in raw_list if is_text_model(m)])
        if popular_list:
            return popular_list, all_list
        else:
            return all_list[:10], all_list

    def _print_model_choices(self, provider: str, display_models: list[str], current_model: str, has_more: bool) -> None:
        print(f"\nSelect Model for {provider.capitalize()}:")
        for i, mdl in enumerate(display_models, 1):
            suffix = " (default)" if mdl == current_model else ""
            print(f"{i}. {mdl}{suffix}")
            
        idx = len(display_models)
        if has_more:
            print(f"{idx + 1}. Show all supported models")
            print(f"{idx + 2}. Enter custom model name")
        else:
            print(f"{idx + 1}. Enter custom model name")

    def _validate_custom_model(self, model_name: str, provider: str, all_models: list[str]) -> str:
        import litellm
        from exceptions import InvalidModelError
        prov_l = provider.lower()
        is_valid = (
            (model_name in all_models) or 
            (f"{prov_l}/{model_name}" in all_models) or 
            getattr(litellm, "check_valid_model", lambda m: False)(model_name) or 
            getattr(litellm, "check_valid_model", lambda m: False)(f"{prov_l}/{model_name}")
        )
        if not is_valid:
            raise InvalidModelError(model_name, provider, all_models)
        return model_name

    def _handle_all_models(self, provider: str, all_models: list[str]) -> str:
        print("\nAll Supported Models:")
        sorted_models = sorted(list(all_models))
        table = PrettyTable()
        table.header = False
        for i in range(0, len(sorted_models), 3):
            chunk = sorted_models[i:i + 3]
            while len(chunk) < 3:
                chunk.append("")
            table.add_row(chunk)
        print(table)
        print("\nEnter model name from the list: ", end="")
        model_name = input().strip()
        return self._validate_custom_model(model_name, provider, all_models)

    def _parse_model_choice(self, choice_str: str, provider: str, display_models: list[str], all_models: list[str], current_model: str, has_more: bool) -> str:
        from exceptions import InvalidModelError
        if not choice_str:
            return current_model
            
        idx_show_all = len(display_models) + 1
        idx_custom = len(display_models) + (2 if has_more else 1)
        
        try:
            val = int(choice_str)
            if 1 <= val <= len(display_models):
                return display_models[val - 1]
            elif has_more and val == idx_show_all:
                return self._handle_all_models(provider, all_models)
            elif val == idx_custom:
                print("\nEnter custom model name: ", end="")
                model_name = input().strip()
                return self._validate_custom_model(model_name, provider, all_models)
            raise ValueError()
        except ValueError:
            raise InvalidModelError(choice_str, provider, display_models)

    def _select_model(self, provider: str, current_model: str) -> str:
        from exceptions import InvalidModelError
        display_models, all_models = self._get_provider_models(provider)
        has_more = len(all_models) > len(display_models)
        model = None
        while not model:
            self._print_model_choices(provider, display_models, current_model, has_more)
            prompt_limit = len(display_models) + (2 if has_more else 1)
            print(f"Enter choice (1-{prompt_limit}): ", end="")
            choice_str = input().strip()
            try:
                model = self._parse_model_choice(choice_str, provider, display_models, all_models, current_model, has_more)
            except InvalidModelError as e:
                self.print_error(str(e))
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

    def edit_llm_settings(self, settings: dict) -> dict:
        print("\n--- Configure LLM Provider & Model ---")
        
        current_provider = settings.get("provider", "google").lower()
        provider = self._select_provider(current_provider)
        
        current_model = settings.get("model", "")
        model = self._select_model(provider, current_model)
        
        current_api_key = settings.get("api_key", "")
        api_key = self._get_api_key(provider, current_api_key)
                
        settings["provider"] = provider
        settings["model"] = model
        settings["api_key"] = api_key
        return settings

    def create_new_profile_flow(self) -> dict:
        print("\n==============================================")
        print("🌟 CREATE NEW PROFILE PREFERENCES SETUP 🌟")
        print("==============================================")
        prefs = {}
        prefs = self.edit_weather_preferences(prefs)
        prefs = self.edit_personal_profile(prefs)
        return prefs
