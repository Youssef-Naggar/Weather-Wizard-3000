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

def test_brain_test_connection_success():
    brain = Brain()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "hi"
    
    with patch("litellm.completion", return_value=mock_response) as mock_complete:
        reply = brain.test_connection("google", "gemini-2.5-flash", "mock_key")
        assert reply == "hi"
        mock_complete.assert_called_once_with(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": "Acknowledge system boot. Say 'hi' in one word."}],
            api_key="mock_key",
            max_tokens=5,
            timeout=10.0
        )

def test_brain_test_connection_failure():
    brain = Brain()
    with patch("litellm.completion", side_effect=Exception("API Error")):
        import pytest
        with pytest.raises(Exception) as excinfo:
            brain.test_connection("openai", "gpt-4o", "mock_key")
        assert "API Error" in str(excinfo.value)
