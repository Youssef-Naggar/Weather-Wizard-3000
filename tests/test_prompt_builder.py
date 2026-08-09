import json
from unittest.mock import patch, mock_open
from prompt_builder import build_prompt, format_wardrobe_items
from wardrobe_item import WardrobeItem


def test_format_wardrobe_items():
    items = [
        WardrobeItem(
            id=1,
            category="top",
            sub_category="t-shirt",
            description="White t-shirt",
            color="white",
            formality="casual",
            seasonality="hot",
            image_path="closet/white.png"
        ),
        WardrobeItem(
            id=2,
            category="shoes",
            sub_category="sneakers",
            description="White sneakers",
            color="white",
            formality="casual",
            seasonality="all-weather",
            image_path="closet/sneakers.png"
        )
    ]

    formatted = format_wardrobe_items(items)
    assert "[ID: 1]" in formatted
    assert "top (t-shirt): White t-shirt" in formatted
    assert "[ID: 2]" in formatted
    assert "shoes (sneakers): White sneakers" in formatted


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
        assert "Sex: Male" in prompt
        assert "Preferred Style: Casual" in prompt

        assert "Favorite Color: Blue" in prompt
        assert "Commute: Walking" in prompt
        assert "Trip Type: Work" in prompt
        assert "Dress Code: Formal" in prompt
        assert "AVAILABLE WARDROBE ITEMS" in prompt


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


def test_build_prompt_with_seasonality_filter():
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
        prompt = build_prompt("Walking", "Work", "Formal", target_seasonality="cold")
        assert "AVAILABLE WARDROBE ITEMS" in prompt
