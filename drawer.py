import os
import re
from datetime import datetime

from typing import List, Optional
import litellm
from wardrobe_item import RecommendedOutfit
from closet import Closet
from settings_manager import load_drawer_settings
from image_utils import image_to_data_uri
from model_registry import format_litellm_model_name

litellm.suppress_debug_info = True


class AvatarDrawer:
    def __init__(self, user_avatar_path: str = "user_avatar.png", output_dir: str = "outfits") -> None:
        self.user_avatar_path = user_avatar_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_garment_image_paths(self, outfit: RecommendedOutfit, closet: Closet) -> List[str]:
        items_dict = {item.id: item for item in closet.get_all_items()}
        target_ids = []
        if outfit.top_id:
            target_ids.append(outfit.top_id)
        if outfit.bottom_id:
            target_ids.append(outfit.bottom_id)
        if outfit.shoes_id:
            target_ids.append(outfit.shoes_id)
        if outfit.jacket_id:
            target_ids.append(outfit.jacket_id)
        if outfit.accessory_ids:
            target_ids.extend(outfit.accessory_ids)

        paths = []
        for item_id in target_ids:
            item = items_dict.get(item_id)
            if item and item.image_path:
                paths.append(item.image_path)
        return paths

    def encode_image_to_base64(self, image_path: str) -> str:
        return image_to_data_uri(image_path)

    def build_tryon_prompt_payload(
        self,
        user_avatar_uri: str,
        garment_uris: List[str],
        outfit_title: str
    ) -> List[dict]:
        user_content: List[dict] = [
            {
                "type": "text",
                "text": f"Generate a full-body virtual avatar try-on preview image showing the person in the user avatar photo wearing the following outfit titled '{outfit_title}'. Preserve facial features, body shape, and pose while cleanly dressing them in the provided garment images."
            },
            {
                "type": "image_url",
                "image_url": {"url": user_avatar_uri}
            }
        ]

        for idx, uri in enumerate(garment_uris, 1):
            user_content.append({
                "type": "text",
                "text": f"Garment item {idx}:"
            })
            user_content.append({
                "type": "image_url",
                "image_url": {"url": uri}
            })

        return [{"role": "user", "content": user_content}]

    def _slugify_title(self, title: str) -> str:
        clean = re.sub(r'[^a-zA-Z0-9\s_-]', '', title)
        return re.sub(r'[\s]+', '_', clean).strip('_').lower()

    def _get_model_routing(self) -> tuple[str, str, str]:
        settings = load_drawer_settings()
        provider = settings.get("provider", "google")
        model = settings.get("model", "gemini-2.5-flash")
        api_key = settings.get("api_key", "")

        full_model_name = format_litellm_model_name(provider, model)
        return full_model_name, api_key, settings.get("user_avatar_path", self.user_avatar_path)

    def generate_tryon_preview(self, outfit: RecommendedOutfit, closet: Closet, outfit_num: int = 1) -> Optional[str]:
        full_model_name, api_key, avatar_path = self._get_model_routing()

        garment_paths = self.get_garment_image_paths(outfit, closet)
        garment_uris = [
            self.encode_image_to_base64(p) for p in garment_paths if os.path.exists(p)
        ]

        active_avatar = avatar_path if os.path.exists(avatar_path) else self.user_avatar_path
        if not os.path.exists(active_avatar):
            return None

        avatar_uri = self.encode_image_to_base64(active_avatar)
        payload = self.build_tryon_prompt_payload(avatar_uri, garment_uris, outfit.outfit_title)

        settings = load_drawer_settings()
        api_base = settings.get("api_base")
        kwargs = {
            "model": full_model_name,
            "messages": payload,
            "api_key": api_key
        }
        if api_base:
            kwargs["api_base"] = api_base

        response = litellm.completion(**kwargs)

        ids_parts = []
        if outfit.top_id:
            ids_parts.append(f"top{outfit.top_id}")
        if outfit.bottom_id:
            ids_parts.append(f"bottom{outfit.bottom_id}")
        if outfit.shoes_id:
            ids_parts.append(f"shoes{outfit.shoes_id}")
        if outfit.jacket_id:
            ids_parts.append(f"jacket{outfit.jacket_id}")
        if outfit.accessory_ids:
            acc_str = "_".join(f"acc{aid}" for aid in outfit.accessory_ids)
            ids_parts.append(acc_str)

        ids_str = "_".join(ids_parts) if ids_parts else "none"
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{date_str}_outfit_{outfit_num}_ids_{ids_str}.png"
        output_path = os.path.join(self.output_dir, output_filename)

        # Write result description / preview output file
        with open(output_path, "wb") as f:
            content = response.choices[0].message.content or "Synthesized try-on preview"
            f.write(content.encode("utf-8"))

        return output_path
