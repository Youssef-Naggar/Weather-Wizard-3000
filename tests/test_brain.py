from unittest.mock import patch, MagicMock
from brain import Brain
from wardrobe_item import AiSuggestionOutput


def test_brain_ai_suggestion_structured_output():
    brain = Brain()

    mock_json = """{
        "ai_suggestion": "Wear a blue shirt today.",
        "recommended_outfits": [
            {
                "outfit_title": "Casual Blue",
                "top_id": 1,
                "top_description": "White t-shirt",
                "bottom_id": 6,
                "bottom_description": "Blue jeans",
                "shoes_id": 8,
                "shoes_description": "White sneakers",
                "jacket_id": null,
                "jacket_description": null,
                "accessory_ids": [],
                "accessory_descriptions": []
            }
        ]
    }"""

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = mock_json

    mock_settings = {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "api_key": "mock_gemini_key"
    }

    with patch("brain.load_model_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_response) as mock_complete:

        result = brain.ai_suggestion("sunny", "Wear blue")

        assert isinstance(result, AiSuggestionOutput)
        assert result.ai_suggestion == "Wear a blue shirt today."
        assert len(result.recommended_outfits) == 1
        assert result.recommended_outfits[0].top_id == 1

        assert mock_complete.called


def test_brain_passes_api_base_to_litellm():
    brain = Brain()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"ai_suggestion": "Local test"}'

    mock_settings = {
        "provider": "custom",
        "model": "ollama/llama3:8b",
        "api_key": "not-needed",
        "api_base": "http://localhost:11434"
    }

    with patch("brain.load_model_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_response) as mock_complete:

        brain.ai_suggestion("sunny", "Wear blue")
        assert mock_complete.called
        assert mock_complete.call_args[1].get("api_base") == "http://localhost:11434"


def test_brain_ai_suggestion_plain_text_fallback():
    brain = Brain()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Wear a warm coat."

    mock_settings = {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": "mock_openai_key"
    }

    with patch("brain.load_model_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_response):

        result = brain.ai_suggestion("cold", "Wear warm")

        assert isinstance(result, AiSuggestionOutput)
        assert result.ai_suggestion == "Wear a warm coat."


def test_brain_test_connection_success():
    brain = Brain()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "hi"

    with patch("litellm.completion", return_value=mock_response) as mock_complete:
        reply = brain.test_connection("google", "gemini-2.5-flash", "mock_key")
        assert reply == "hi"
        assert mock_complete.called


def test_brain_test_connection_failure():
    brain = Brain()
    with patch("litellm.completion", side_effect=Exception("API Error")):
        import pytest
        with pytest.raises(Exception) as excinfo:
            brain.test_connection("openai", "gpt-4o", "mock_key")
        assert "API Error" in str(excinfo.value)
