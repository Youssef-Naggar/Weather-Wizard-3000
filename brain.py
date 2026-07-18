import json
import litellm
from pydantic import BaseModel, Field
from prompts import example_forecast, example_response
from prompt_builder import load_model_settings
from dotenv import load_dotenv

load_dotenv()

class AiSuggestionOutput(BaseModel):
    ai_suggestion: str = Field()

class Brain:
    def __init__(self):
        pass

    def ai_suggestion(self, forecast_str: str, system_prompt: str) -> str:
        settings = load_model_settings()
        provider = settings.get("provider", "google")
        model = settings.get("model", "gemini-2.5-flash")
        api_key = settings.get("api_key", "")

        # Format model name for litellm (e.g., "gemini/gemini-2.5-flash")
        full_model_name = model
        if provider and "/" not in model:
            prov_prefix = "gemini" if provider.lower() == "google" else provider.lower()
            full_model_name = f"{prov_prefix}/{model}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example_forecast},
            {"role": "assistant", "content": example_response},
            {"role": "user", "content": forecast_str}
        ]

        response = litellm.completion(
            model=full_model_name,
            messages=messages,
            response_format=AiSuggestionOutput,
            api_key=api_key,
            temperature=0.25
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("ai_suggestion", content)