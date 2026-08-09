"""
Prompt Builder module for Weather Wizard 3000.
Handles formatting of available wardrobe items and assembling system prompts.
"""
import json
from typing import List, Optional
from prompts import system_prompt
from wardrobe_item import WardrobeItem
from closet import Closet
from settings_manager import (
    load_preferences,
)


def format_wardrobe_items(items: List[WardrobeItem]) -> str:
    if not items:
        return "No specific wardrobe items available."
    lines = []
    for item in items:
        lines.append(
            f"- [ID: {item.id}] {item.category} ({item.sub_category}): {item.description} | Formality: {item.formality} | Color: {item.color}"
        )
    return "\n".join(lines)


def build_prompt(
    commute_type: str,
    trip_type: str,
    dress_code: str,
    target_seasonality: Optional[str] = None
) -> str:
    if dress_code == "":
        dress_code = "there is no specific dress code"
    data = load_preferences()

    # Load wardrobe items filtered by target_seasonality if provided
    try:
        closet = Closet()
        if target_seasonality:
            items = closet.get_items_by_seasonality(target_seasonality)
        else:
            items = closet.get_all_items()
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        items = []

    available_items_formatted = format_wardrobe_items(items)

    # Merge function arguments and formatted items into dictionary
    data |= {
        "commute_type": commute_type,
        "trip_type": trip_type,
        "dress_code": dress_code,
        "available_items_formatted": available_items_formatted
    }

    # Unpack dictionary into the system prompt template
    final_system_prompt = system_prompt.format(**data)
    return final_system_prompt