import json
from unittest.mock import patch, mock_open
from prompt_builder import build_prompt

def test_build_prompt_basic():
    mock_preferences = {
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
    
    mock_preferences_str = json.dumps(mock_preferences)
    
    with patch("builtins.open", mock_open(read_data=mock_preferences_str)):
        prompt = build_prompt("Walking", "Work", "Formal")
        
        assert "Age: 21" in prompt
        assert "Preferred Style: Casual" in prompt
        assert "Favorite Color: Blue" in prompt
        assert "Commute: Walking" in prompt
        assert "Trip Type: Work" in prompt
        assert "Dress Code: Formal" in prompt

def test_build_prompt_empty_dress_code():
    mock_preferences = {
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
    mock_preferences_str = json.dumps(mock_preferences)
    
    with patch("builtins.open", mock_open(read_data=mock_preferences_str)):
        prompt = build_prompt("Driving", "Casual", "")
        assert "Dress Code: there is no specific dress code" in prompt
