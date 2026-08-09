import litellm


def format_litellm_model_name(provider: str, model: str) -> str:
    """Formats provider and model into LiteLLM model routing string (e.g., 'gemini/gemini-2.5-flash')."""
    if not model:
        return ""
    clean_model = model.strip()
    if not provider:
        return clean_model
    clean_prov = provider.strip().lower()
    if "/" in clean_model:
        return clean_model
    prov_prefix = "gemini" if clean_prov in ("google", "gemini") else clean_prov
    return f"{prov_prefix}/{clean_model}"



def _get_litellm_info(model_name: str, provider: str = None) -> dict:
    """Helper to resolve the model info from LiteLLM's pricing map."""
    info = litellm.model_cost.get(model_name)
    if not info and provider:
        info = litellm.model_cost.get(f"{provider.lower()}/{model_name}")
    if not info and provider:
        prov_l = provider.lower()
        lookup_prov = "gemini" if prov_l == "google" else prov_l
        info = litellm.model_cost.get(f"{lookup_prov}/{model_name}")

    return info or {}


def is_text_model(model_name: str, provider: str = None) -> bool:
    """Check if model supports text chat / completion."""
    info = _get_litellm_info(model_name, provider)

    if info and "mode" in info:
        return info["mode"] in ("chat", "completion")

    name_lower = model_name.lower()
    excluded = [
        "dall-e", "image", "tts", "whisper", "embed",
        "moderation", "sora", "audio", "transcribe",
        "speech", "translation", "clip", "flux",
        "imagen", "stable-diffusion", "veo"
    ]
    return not any(sub in name_lower for sub in excluded)


def is_vision_model(model_name: str, provider: str = None) -> bool:
    """Check if model supports vision input."""
    info = _get_litellm_info(model_name, provider)

    if info and "supports_vision" in info:
        return info["supports_vision"] is True

    name_lower = model_name.lower()
    excluded = ["tts", "whisper", "embed", "moderation", "audio", "transcribe", "speech", "dall-e"]
    if any(sub in name_lower for sub in excluded):
        return False

    vision_keywords = [
        "vision", "flash", "4o", "gemini-2", "gemini-1.5", "gpt-4-turbo",
        "claude-3", "pixtral", "llava", "multimodal", "gemma", "omni", "computer-use"
    ]
    return any(sub in name_lower for sub in vision_keywords)


def is_image_model(model_name: str, provider: str = None) -> bool:
    """Check if model supports image generation."""
    info = _get_litellm_info(model_name, provider)

    if info and "mode" in info:
        return info["mode"] == "image_generation"

    name_lower = model_name.lower()
    image_keywords = [
        "dall-e", "imagen", "image", "flux", "stable-diffusion",
        "sdxl", "recraft", "fal", "midjourney", "veo", "sora", "canvas"
    ]
    return any(sub in name_lower for sub in image_keywords)


is_imagegen_model = is_image_model
