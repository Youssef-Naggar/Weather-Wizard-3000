from model_registry import (
    format_litellm_model_name,
    is_text_model,
    is_vision_model,
    is_image_model,
    is_imagegen_model
)


def test_format_litellm_model_name():
    assert format_litellm_model_name("google", "gemini-2.5-flash") == "gemini/gemini-2.5-flash"
    assert format_litellm_model_name("openai", "gpt-4o") == "openai/gpt-4o"
    assert format_litellm_model_name("anthropic", "claude-3-5-sonnet-20241022") == "anthropic/claude-3-5-sonnet-20241022"
    # If already prefixed, retain as is
    assert format_litellm_model_name("openai", "openai/gpt-4o") == "openai/gpt-4o"
    assert format_litellm_model_name("", "gpt-4o") == "gpt-4o"


def test_is_text_model():
    assert is_text_model("gpt-4o", "openai") is True
    assert is_text_model("dall-e-3", "openai") is False


def test_is_vision_model():
    assert is_vision_model("gpt-4o", "openai") is True
    assert is_vision_model("gemini-2.5-flash", "google") is True


def test_is_image_model():
    assert is_image_model("dall-e-3", "openai") is True
    assert is_image_model("gpt-4o", "openai") is False
    assert is_imagegen_model("flux-dev") is True
