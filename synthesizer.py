"""
Multimodal Closet Synthesizer module for Weather Wizard 3000.
Handles image scanning, base64 encoding, Vision LLM batch synthesis, and atomic closet JSON updates.
"""
import os
import json
import tempfile
from typing import List, Dict, Any
import litellm
from wardrobe_item import WardrobeItem
from prompts import vision_synthesizer_prompt
from settings_manager import load_synthesizer_settings
from image_utils import image_to_data_uri
from model_registry import format_litellm_model_name

litellm.suppress_debug_info = True


class ClosetSynthesizer:
    def __init__(self, closet_dir: str = "closet", json_path: str = "closet.json") -> None:
        self.closet_dir = closet_dir
        self.json_path = json_path
        self.existing_items = self._load_existing_items()


    def _load_existing_items(self) -> List[dict]:
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _is_new_image_file(self, filename: str, full_path: str, existing_paths: set, existing_filenames: set) -> bool:
        valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_exts:
            return False
        return full_path not in existing_paths and filename not in existing_filenames

    def scan_untagged_images(self) -> List[str]:
        if not os.path.exists(self.closet_dir):
            return []
        existing_paths = {
            os.path.normpath(item.get("image_path", ""))
            for item in self.existing_items if item.get("image_path")
        }
        existing_filenames = {
            os.path.basename(path) for path in existing_paths if path
        }

        untagged = []
        for root, _, files in os.walk(self.closet_dir):
            for file in files:
                full_path = os.path.normpath(os.path.join(root, file))
                if self._is_new_image_file(file, full_path, existing_paths, existing_filenames):
                    untagged.append(full_path)

        return sorted(untagged)

    def encode_image_to_base64(self, image_path: str) -> str:
        return image_to_data_uri(image_path)

    def build_batch_payload(self, image_paths: List[str]) -> List[dict]:
        user_content = [
            {"type": "text", "text": f"Please analyze these {len(image_paths)} clothing items."}
        ]
        for path in image_paths:
            base64_url = self.encode_image_to_base64(path)
            user_content.append({"type": "image_url", "image_url": {"url": base64_url}})

        return [
            {"role": "system", "content": vision_synthesizer_prompt},
            {"role": "user", "content": user_content}
        ]

    def _call_vision_llm(self, messages: List[dict]) -> str:
        settings = load_synthesizer_settings()
        model_name = settings.get("model", "gemini-2.5-flash")
        provider = settings.get("provider", "google")
        api_key = settings.get("api_key", "")

        full_model = format_litellm_model_name(provider, model_name)
        kwargs: Dict[str, Any] = {"model": full_model, "messages": messages}
        api_base = settings.get("api_base")
        if api_key:
            kwargs["api_key"] = api_key
        if api_base:
            kwargs["api_base"] = api_base

        response = litellm.completion(**kwargs)
        return response.choices[0].message.content

    def _clean_json_str(self, raw_content: str) -> str:
        cleaned = raw_content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def _parse_llm_response(self, raw_content: str, image_paths: List[str]) -> List[dict]:
        try:
            cleaned = self._clean_json_str(raw_content)
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            return []

    def _first_str_or_val(self, val: Any) -> str:
        if isinstance(val, list) and len(val) > 0:
            return str(val[0])
        return str(val) if val is not None else ""

    def _to_string(self, val: Any, default: str = "") -> str:
        if isinstance(val, list):
            return ", ".join(str(item) for item in val if item is not None)
        if isinstance(val, dict):
            return ", ".join(f"{k}: {v}" for k, v in val.items() if v is not None)
        if val is None:
            return default
        return str(val).strip()

    def _normalize_category(self, raw_cat: Any) -> str:
        cat = self._first_str_or_val(raw_cat).lower().strip()
        if cat in ("top", "bottom", "shoes", "jacket", "accessory"):
            return cat
        if cat in ("outerwear", "coat", "blazer"):
            return "jacket"
        if cat in ("footwear", "sneakers", "boots"):
            return "shoes"
        if cat in ("pants", "trousers", "shorts", "skirt", "bottoms"):
            return "bottom"
        return "top"

    def _normalize_formality(self, raw_form: Any) -> str:
        form = self._first_str_or_val(raw_form).lower().strip()
        if form in ("casual", "formal", "business casual", "sporty"):
            return form
        if form in ("smart casual", "business"):
            return "business casual"
        return "casual"

    def _normalize_seasonality(self, raw_season: Any) -> str:
        season = self._first_str_or_val(raw_season).lower().strip()
        if season in ("cold", "hot", "all-weather"):
            return season
        if season in ("winter", "fall", "autumn"):
            return "cold"
        if season in ("summer",):
            return "hot"
        return "all-weather"

    def _normalize_item_dict(self, item_dict: dict, item_id: int, image_path: str) -> dict:
        normalized = dict(item_dict)
        normalized["id"] = item_id
        normalized["image_path"] = image_path
        normalized["sub_category"] = self._to_string(item_dict.get("sub_category"), default="General")
        normalized["description"] = self._to_string(item_dict.get("description"), default="No description provided")
        normalized["color"] = self._to_string(item_dict.get("color"), default="unknown")
        normalized["category"] = self._normalize_category(item_dict.get("category"))
        normalized["formality"] = self._normalize_formality(item_dict.get("formality"))
        normalized["seasonality"] = self._normalize_seasonality(item_dict.get("seasonality"))
        return normalized

    def synthesize_batch(self, image_paths: List[str]) -> List[WardrobeItem]:
        if not image_paths:
            return []

        messages = self.build_batch_payload(image_paths)
        raw_content = self._call_vision_llm(messages)
        parsed_list = self._parse_llm_response(raw_content, image_paths)

        new_items = []
        max_id = max([item.get("id", 0) for item in self.existing_items], default=0)

        for idx, item_dict in enumerate(parsed_list):
            max_id += 1
            img_path = image_paths[idx] if idx < len(image_paths) else image_paths[-1]
            norm_dict = self._normalize_item_dict(item_dict, max_id, img_path)
            try:
                new_items.append(WardrobeItem(**norm_dict))
            except Exception as err:
                print(f"⚠️ Warning: Failed to parse clothing item for '{img_path}': {err}")

        return new_items

    def ingest_new_photos(self, batch_size: int = 5) -> int:
        untagged_paths = self.scan_untagged_images()
        if not untagged_paths:
            return 0

        newly_ingested = []
        for i in range(0, len(untagged_paths), batch_size):
            batch = untagged_paths[i:i + batch_size]
            synthesized_items = self.synthesize_batch(batch)
            newly_ingested.extend(synthesized_items)
            self.existing_items.extend([item.model_dump() for item in synthesized_items])

        dir_name = os.path.dirname(self.json_path) or "."
        temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="closet_", suffix=".tmp")
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(self.existing_items, f, indent=2)
        os.replace(temp_path, self.json_path)

        return len(newly_ingested)
