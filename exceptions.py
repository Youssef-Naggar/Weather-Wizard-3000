class WeatherWizardError(Exception):
    """Base exception class for all errors in Weather Wizard 3000."""
    pass


class SettingsValidationError(WeatherWizardError):
    """Base exception for all settings-related validation errors."""
    pass


class InvalidProviderError(SettingsValidationError):
    """Raised when the selected LLM provider is invalid or unsupported."""
    def __init__(self, provider: str, allowed_providers: list[str]) -> None:
        self.provider = provider
        self.allowed_providers = allowed_providers
        display_list = sorted(list(allowed_providers))
        if len(display_list) > 8:
            display_list = display_list[:8] + [f"... and {len(display_list) - 8} more"]
        msg = (
            f"Invalid provider '{provider}'. "
            f"Supported providers include: {', '.join(display_list)}. "
            "Please choose a supported provider."
        )
        super().__init__(msg)


class InvalidModelError(SettingsValidationError):
    """Raised when the selected LLM model is invalid for the chosen provider."""
    def __init__(self, model: str, provider: str, allowed_models: list[str]) -> None:
        self.model = model
        self.provider = provider
        self.allowed_models = allowed_models
        display_list = sorted(list(allowed_models))
        if len(display_list) > 8:
            display_list = display_list[:8] + [f"... and {len(display_list) - 8} more"]
        msg = (
            f"Invalid model '{model}' for provider '{provider}'. "
            f"Supported models for '{provider}' include: {', '.join(display_list)}. "
            "Please choose a supported model."
        )
        super().__init__(msg)


class InvalidApiKeyError(SettingsValidationError):
    """Raised when the API key is invalid, empty, or whitespace-only."""
    def __init__(self, provider: str) -> None:
        self.provider = provider
        msg = (
            f"API Key cannot be empty or only whitespace for provider '{provider}'. "
            "Please provide a valid API key to authenticate your LLM requests."
        )
        super().__init__(msg)
