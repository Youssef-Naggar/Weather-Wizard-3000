import json
import pytest
from pydantic import ValidationError
from wardrobe_item import WardrobeItem, RecommendedOutfit, AiSuggestionOutput


def test_wardrobe_item_valid_instantiation():
    item = WardrobeItem(
        id=1,
        category="top",
        sub_category="t-shirt",
        description="White cotton short-sleeve crewneck t-shirt",
        color="white",
        formality="casual",
        seasonality="hot",
        image_path="closet/white_t_shirt.png"
    )
    assert item.id == 1
    assert item.category == "top"
    assert item.sub_category == "t-shirt"
    assert item.formality == "casual"
    assert item.seasonality == "hot"


def test_wardrobe_item_list_field_coercion():
    item = WardrobeItem(
        id=1,
        category="top",
        sub_category=["t-shirt", "cotton"],
        description=["White cotton", "short-sleeve"],
        color=["red", "brown", "white"],
        formality="casual",
        seasonality="hot",
        image_path="closet/item.png"
    )
    assert item.color == "red, brown, white"
    assert item.sub_category == "t-shirt, cotton"
    assert item.description == "White cotton, short-sleeve"



def test_wardrobe_item_invalid_category():
    with pytest.raises(ValidationError):
        WardrobeItem(
            id=2,
            category="hat",  # Invalid category enum
            sub_category="cap",
            description="Baseball cap",
            color="black",
            formality="casual",
            seasonality="all-weather",
            image_path="closet/cap.png"
        )


def test_wardrobe_item_invalid_seasonality():
    with pytest.raises(ValidationError):
        WardrobeItem(
            id=3,
            category="top",
            sub_category="shirt",
            description="Warm shirt",
            color="red",
            formality="casual",
            seasonality="freezing",  # Invalid seasonality enum
            image_path="closet/shirt.png"
        )


def test_recommended_outfit_defaults():
    outfit = RecommendedOutfit(
        outfit_title="Casual Summer Breeze",
        top_id=1,
        top_description="White t-shirt",
        bottom_id=2,
        bottom_description="Blue shorts",
        shoes_id=3,
        shoes_description="White sneakers"
    )
    assert outfit.outfit_title == "Casual Summer Breeze"
    assert outfit.jacket_id is None
    assert outfit.accessory_ids == []
    assert outfit.accessory_descriptions == []


def test_ai_suggestion_output_structure():
    outfit = RecommendedOutfit(
        outfit_title="Warm Winter Outfit",
        top_id=10,
        top_description="Grey sweater",
        bottom_id=11,
        bottom_description="Black jeans",
        shoes_id=12,
        shoes_description="Boots",
        jacket_id=13,
        jacket_description="Heavy coat",
        accessory_ids=[14],
        accessory_descriptions=["Beanie"]
    )
    suggestion = AiSuggestionOutput(
        ai_suggestion="Stay warm today!",
        recommended_outfits=[outfit]
    )
    assert suggestion.ai_suggestion == "Stay warm today!"
    assert len(suggestion.recommended_outfits) == 1
    assert suggestion.recommended_outfits[0].top_id == 10


def test_closet_json_validity():
    with open("closet.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) >= 5

    items = [WardrobeItem(**entry) for entry in data]
    categories = {item.category for item in items}
    expected_categories = {"top", "bottom", "shoes", "jacket"}
    assert expected_categories.issubset(categories)



