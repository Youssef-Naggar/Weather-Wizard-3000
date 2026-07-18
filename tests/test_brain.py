from unittest.mock import patch, MagicMock, ANY
from brain import Brain

def test_brain_ai_suggestion_google_provider():
    brain = Brain()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"ai_suggestion": "Wear a blue shirt"}'
    
    mock_settings = {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "api_key": "mock_gemini_key"
    }
    
    with patch("brain.load_model_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_response) as mock_complete:
             
        suggestion = brain.ai_suggestion("sunny", "Wear blue")
        
        assert suggestion == "Wear a blue shirt"
        mock_complete.assert_called_once_with(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "Wear blue"},
                {"role": "user", "content": ANY},
                {"role": "assistant", "content": ANY},
                {"role": "user", "content": "sunny"}
            ],
            response_format=ANY,
            api_key="mock_gemini_key",
            temperature=0.25
        )

def test_brain_ai_suggestion_other_provider():
    brain = Brain()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"ai_suggestion": "Wear business formal"}'
    
    mock_settings = {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": "mock_openai_key"
    }
    
    with patch("brain.load_model_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_response) as mock_complete:
             
        suggestion = brain.ai_suggestion("rainy", "Wear formal")
        
        assert suggestion == "Wear business formal"
        mock_complete.assert_called_once_with(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "Wear formal"},
                {"role": "user", "content": ANY},
                {"role": "assistant", "content": ANY},
                {"role": "user", "content": "rainy"}
            ],
            response_format=ANY,
            api_key="mock_openai_key",
            temperature=0.25
        )
