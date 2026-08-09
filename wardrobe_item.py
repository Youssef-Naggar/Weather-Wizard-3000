from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class WardrobeItem(BaseModel):
    id: Optional[int] = None
    category: Literal["top", "bottom", "shoes", "jacket", "accessory"]
    sub_category: str
    description: str
    color: str
    formality: Literal["casual", "formal", "business casual", "sporty"]
    seasonality: Literal["cold", "hot", "all-weather"]
    image_path: str

    @field_validator("color", "sub_category", "description", mode="before")
    @classmethod
    def coerce_list_or_non_str_to_str(cls, v: Any) -> str:
        if isinstance(v, list):
            return ", ".join(str(item) for item in v if item is not None)
        if isinstance(v, dict):
            return ", ".join(f"{k}: {val}" for k, val in v.items() if val is not None)
        return str(v) if v is not None else ""



class RecommendedOutfit(BaseModel):
    outfit_title: str = Field(description="Title of the outfit")
    top_id: Optional[int] = Field(None, description="Database ID of matching top garment, or null")
    top_description: str = Field(description="Description of top garment")
    bottom_id: Optional[int] = Field(None, description="Database ID of matching lower garment, or null")
    bottom_description: str = Field(description="Description of lower garment")
    shoes_id: Optional[int] = Field(None, description="Database ID of matching shoes, or null")
    shoes_description: str = Field(description="Description of shoes")
    jacket_id: Optional[int] = Field(None, description="Database ID of matching jacket, or null")
    jacket_description: Optional[str] = Field(None, description="Description of jacket if recommended")
    accessory_ids: List[int] = Field(default_factory=list, description="Database IDs of matching accessories")
    accessory_descriptions: List[str] = Field(default_factory=list, description="Descriptions of accessories")


class AiSuggestionOutput(BaseModel):
    ai_suggestion: str = Field(description="Overall styling explanation and notes")
    recommended_outfits: List[RecommendedOutfit] = Field(
        default_factory=list,
        description="List of weather-appropriate outfits with grounded wardrobe IDs"
    )
