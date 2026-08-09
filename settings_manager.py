import json
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
import litellm
from exceptions import SettingsValidationError, InvalidProviderError, InvalidModelError
from model_registry import is_text_model

PREFERENCES_FILE = "preferences.json"
MODEL_SETTINGS_FILE = "model-settings.json"
SYNTHESIZER_SETTINGS_FILE = "synthesizer-settings.json"
DRAWER_SETTINGS_FILE = "drawer-settings.json"


def load_preferences() -> dict:
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
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
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(prefs, file, indent=2)


class ModelSettings(BaseModel):
    provider: str = Field(default="google")
    model: str = Field(default="gemini-2.5-flash")
    api_key: str = Field(default="")
    api_base: Optional[str] = Field(default=None)


def _validate_provider_exists(provider: str, api_base: Optional[str] = None) -> str:
    if not isinstance(provider, str):
        raise InvalidProviderError("", list(litellm.models_by_provider.keys()))
    prov_lower = provider.lower()
    custom_providers = {"custom", "ollama", "local", "lmstudio", "vllm"}
    if prov_lower in custom_providers or api_base:
        return prov_lower
    lookup_prov = "gemini" if prov_lower == "google" else prov_lower
    all_providers = list(litellm.models_by_provider.keys())
    if lookup_prov not in all_providers and prov_lower not in all_providers:
        raise InvalidProviderError(provider, all_providers)
    return lookup_prov


def _is_model_in_other_provider(model: str, prov_lower: str, lookup_prov: str) -> bool:
    for p, p_models in litellm.models_by_provider.items():
        if p not in (lookup_prov, prov_lower) and (model in p_models or f"{p}/{model}" in p_models):
            return True
    return False


def _check_model_in_provider_lists(model: str, provider: str, lookup_prov: str) -> bool:
    prov_lower = provider.lower()
    custom_providers = {"custom", "ollama", "local", "lmstudio", "vllm"}
    if prov_lower in custom_providers or lookup_prov in custom_providers:
        return True
    allowed_models = litellm.models_by_provider.get(lookup_prov, []) or litellm.models_by_provider.get(prov_lower, [])
    if model in allowed_models or f"{prov_lower}/{model}" in allowed_models:
        return is_text_model(model, provider)
    check_fn = getattr(litellm, "check_valid_model", lambda m: False)
    if check_fn(model) or check_fn(f"{prov_lower}/{model}"):
        return is_text_model(model, provider)
    if is_text_model(model, provider):
        return not _is_model_in_other_provider(model, prov_lower, lookup_prov)
    return False


def validate_model_settings(settings: dict) -> dict:
    try:
        model_obj = ModelSettings(**settings)
    except ValidationError as e:
        raise SettingsValidationError(f"Invalid model settings structure: {str(e)}")

    provider = settings.get("provider", "google")
    model = settings.get("model", "gemini-2.5-flash")
    api_base = settings.get("api_base")

    lookup_prov = _validate_provider_exists(provider, api_base)

    if not _check_model_in_provider_lists(model, provider, lookup_prov):
        allowed = list(litellm.models_by_provider.get(lookup_prov, []))
        raise InvalidModelError(model, provider, allowed)

    return model_obj.model_dump(exclude_none=False)

    lookup_prov = _validate_provider_exists(provider)
    if not _check_model_in_provider_lists(model, provider, lookup_prov):
        prov_lower = provider.lower()
        allowed_models = litellm.models_by_provider.get(lookup_prov, []) or litellm.models_by_provider.get(prov_lower, [])
        text_allowed = [m for m in allowed_models if is_text_model(m, provider)]
        raise InvalidModelError(model, provider, text_allowed)


def load_model_settings() -> dict:
    try:
        with open(MODEL_SETTINGS_FILE, "r", encoding="utf-8") as file:
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
    with open(MODEL_SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def validate_synthesizer_settings(settings: dict) -> None:
    if not isinstance(settings, dict):
        raise ValueError("Invalid synthesizer settings: must be a dictionary")
    required_keys = {"provider", "model", "api_key"}
    if not required_keys.issubset(settings.keys()):
        raise ValueError(f"Invalid synthesizer settings: missing required keys {required_keys - settings.keys()}")


def load_synthesizer_settings() -> dict:
    try:
        with open(SYNTHESIZER_SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
            validate_synthesizer_settings(settings)
            return settings
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "api_key": ""
        }


def save_synthesizer_settings(settings: dict) -> None:
    validate_synthesizer_settings(settings)
    with open(SYNTHESIZER_SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def validate_drawer_settings(settings: dict) -> None:
    if not isinstance(settings, dict):
        raise ValueError("Invalid drawer settings: must be a dictionary")
    required_keys = {"provider", "model", "api_key", "user_avatar_path"}
    if not required_keys.issubset(settings.keys()):
        raise ValueError(f"Invalid drawer settings: missing required keys {required_keys - settings.keys()}")


def load_drawer_settings() -> dict:
    try:
        with open(DRAWER_SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
            validate_drawer_settings(settings)
            return settings
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "api_key": "",
            "user_avatar_path": "user_avatar.png"
        }


def save_drawer_settings(settings: dict) -> None:
    validate_drawer_settings(settings)
    with open(DRAWER_SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)
