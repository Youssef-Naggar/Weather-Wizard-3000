from prompts import system_prompt
import json
from pydantic import BaseModel, Field, ValidationError
from exceptions import SettingsValidationError, InvalidProviderError, InvalidModelError

def load_preferences() -> dict:
    try:
        with open('preferences.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return safe defaults if preferences file is missing or invalid
        return {
            "temp_unit": "C",
            "cold_threshold": 15,
            "hot_threshold": 25,
            "perfect_temp": 20,
            "favorite_color": "Blue",
            "clothing_style": "Casual",
            "age": 21,
            "sex": "Male",
            "weather_sensitivities": "High wind sensitivity"
        }

def save_preferences(prefs: dict) -> None:
    with open('preferences.json', 'w', encoding='utf-8') as file:
        json.dump(prefs, file, indent=2)

POPULAR_PROVIDERS = ["google", "openai", "anthropic", "groq", "cohere", "ollama"]

POPULAR_MODELS = {
    "google": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"],
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4"],
    "anthropic": ["claude-3-5-sonnet", "claude-3-5-haiku"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    "cohere": ["command-r-plus", "command-r"],
    "ollama": ["llama3", "mistral", "phi3"]
}

EXCLUDED_MODEL_SUBSTRINGS = [
    "dall-e", "image", "tts", "whisper", "embed", 
    "moderation", "sora", "audio", "transcribe", 
    "speech", "translation", "clip", "flux", 
    "imagen", "stable-diffusion", "veo"
]

def is_text_model(model_name: str) -> bool:
    name_lower = model_name.lower()
    return not any(sub in name_lower for sub in EXCLUDED_MODEL_SUBSTRINGS)

class ModelSettings(BaseModel):
    provider: str = Field(default="google")
    model: str = Field(default="gemini-2.5-flash")
    api_key: str = Field(default="")

def validate_model_settings(settings: dict) -> None:
    import litellm
    try:
        ModelSettings(**settings)
    except ValidationError as e:
        raise SettingsValidationError(f"Invalid model settings structure: {str(e)}")

    provider = settings.get("provider", "google")
    model = settings.get("model", "gemini-2.5-flash")

    if not isinstance(provider, str):
        raise InvalidProviderError("", list(litellm.models_by_provider.keys()))

    prov_lower = provider.lower()
    lookup_prov = "gemini" if prov_lower == "google" else prov_lower
    all_providers = list(litellm.models_by_provider.keys())

    if lookup_prov not in all_providers and prov_lower not in all_providers:
        raise InvalidProviderError(provider, all_providers)

    allowed_models = litellm.models_by_provider.get(lookup_prov, []) or litellm.models_by_provider.get(prov_lower, [])
    text_allowed = [m for m in allowed_models if is_text_model(m)]
    
    is_model_supported = False
    if model in text_allowed:
        is_model_supported = True
    elif f"{prov_lower}/{model}" in text_allowed:
        is_model_supported = True
    elif f"{lookup_prov}/{model}" in text_allowed:
        is_model_supported = True
    elif getattr(litellm, "check_valid_model", lambda m: False)(model) and is_text_model(model):
        is_model_supported = True
    elif getattr(litellm, "check_valid_model", lambda m: False)(f"{prov_lower}/{model}") and is_text_model(model):
        is_model_supported = True

    if not is_model_supported and text_allowed:
        raise InvalidModelError(model, provider, text_allowed)

def load_model_settings() -> dict:
    try:
        with open('model-settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
            validate_model_settings(settings)
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "api_key": ""
        }

def save_model_settings(settings: dict) -> None:
    validate_model_settings(settings)
    with open('model-settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=2)

def build_prompt(commute_type: str, trip_type: str, dress_code: str) -> str:
    if dress_code == "":
        dress_code = "there is no specific dress code"
    data = load_preferences()
    # 1. Merge function arguments directly into the JSON data dictionary
    data |= {"commute_type": commute_type, "trip_type": trip_type, "dress_code": dress_code}
    # 2. Unpack the dictionary into the system prompt template
    final_system_prompt = system_prompt.format(**data)
    return final_system_prompt