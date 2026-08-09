import json
import litellm
from prompts import example_forecast, example_response
from settings_manager import load_model_settings
from wardrobe_item import AiSuggestionOutput
from pydantic import ValidationError
from model_registry import format_litellm_model_name
from dotenv import load_dotenv

load_dotenv()
litellm.suppress_debug_info = True


class Brain:
    def __init__(self):
        pass

    def test_connection(self, provider: str, model: str, api_key: str, api_base: str = None) -> str:
        full_model_name = format_litellm_model_name(provider, model)

        messages = [
            {"role": "user", "content": "Acknowledge system boot. Say 'hi' in one word."}
        ]

        kwargs = {
            "model": full_model_name,
            "messages": messages,
            "api_key": api_key,
            "max_tokens": 5,
            "timeout": 60.0
        }
        if api_base:
            kwargs["api_base"] = api_base

        response = litellm.completion(**kwargs)

        content = response.choices[0].message.content
        return content.strip() if content else ""

    def ai_suggestion(self, forecast_str: str, system_prompt: str) -> AiSuggestionOutput:
        settings = load_model_settings()
        provider = settings.get("provider", "google")
        model = settings.get("model", "gemini-2.5-flash")
        api_key = settings.get("api_key", "")
        api_base = settings.get("api_base")

        full_model_name = format_litellm_model_name(provider, model)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example_forecast},
            {"role": "assistant", "content": example_response},
            {"role": "user", "content": forecast_str}
        ]

        kwargs = {
            "model": full_model_name,
            "messages": messages,
            "response_format": AiSuggestionOutput,
            "api_key": api_key,
            "temperature": 0.25
        }
        if api_base:
            kwargs["api_base"] = api_base

        response = litellm.completion(**kwargs)

        content = response.choices[0].message.content
        if not content:
            return AiSuggestionOutput(ai_suggestion="")

        try:
            return AiSuggestionOutput.model_validate_json(content)
        except (json.JSONDecodeError, ValidationError, ValueError):
            # Fallback if raw text returned
            return AiSuggestionOutput(ai_suggestion=content)