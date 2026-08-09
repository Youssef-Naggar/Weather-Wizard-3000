import json
from typing import List
from wardrobe_item import WardrobeItem
import os

class Closet:
    def __init__(self, json_path: str = "closet.json"):
        self.json_path = json_path
        self._items: List[WardrobeItem] = self._load_items()

    def _load_items(self) -> List[WardrobeItem]:
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Closet dataset file not found: {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [WardrobeItem(**entry) for entry in data]




    def get_all_items(self) -> List[WardrobeItem]:
        return list(self._items)

    def get_items_by_seasonality(self, seasonality: str) -> List[WardrobeItem]:
        target = seasonality.lower()
        return [
            item for item in self._items
            if item.seasonality in (target, "all-weather")
        ]
