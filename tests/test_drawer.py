import json
import pytest
from unittest.mock import patch, mock_open
from settings_manager import (
    DRAWER_SETTINGS_FILE,
    load_drawer_settings,
    save_drawer_settings,
    validate_drawer_settings
)


def test_validate_drawer_settings_success():
    valid = {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "api_key": "test_key",
        "user_avatar_path": "user_avatar.png"
    }
    # Should not raise
    validate_drawer_settings(valid)


def test_validate_drawer_settings_missing_keys():
    invalid = {"provider": "google"}
    with pytest.raises(ValueError, match="missing required keys"):
        validate_drawer_settings(invalid)


def test_validate_drawer_settings_not_dict():
    with pytest.raises(ValueError, match="must be a dictionary"):
        validate_drawer_settings("not a dict")  # type: ignore


def test_load_drawer_settings_success():
    data = {
        "provider": "openai",
        "model": "dall-e-3",
        "api_key": "sk-test",
        "user_avatar_path": "my_avatar.png"
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        res = load_drawer_settings()
        assert res["provider"] == "openai"
        assert res["model"] == "dall-e-3"
        assert res["api_key"] == "sk-test"
        assert res["user_avatar_path"] == "my_avatar.png"


def test_load_drawer_settings_fallback_on_error():
    with patch("builtins.open", side_effect=FileNotFoundError):
        res = load_drawer_settings()
        assert res["provider"] == "google"
        assert res["model"] == "gemini-2.5-flash"
        assert res["api_key"] == ""
        assert res["user_avatar_path"] == "user_avatar.png"


def test_save_drawer_settings_success():
    data = {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "api_key": "test_key",
        "user_avatar_path": "user_avatar.png"
    }
    m = mock_open()
    with patch("builtins.open", m):
        save_drawer_settings(data)
        m.assert_called_once_with(DRAWER_SETTINGS_FILE, "w", encoding="utf-8")


def test_avatar_drawer_get_garment_image_paths(tmp_path):
    from wardrobe_item import RecommendedOutfit
    from drawer import AvatarDrawer

    from closet import Closet

    # Create dummy closet json
    closet_file = tmp_path / "closet.json"
    items_data = [
        {"id": 1, "category": "top", "sub_category": "t-shirt", "description": "White tee", "color": "white", "formality": "casual", "seasonality": "hot", "image_path": "closet/top.jpg"},
        {"id": 2, "category": "bottom", "sub_category": "jeans", "description": "Blue jeans", "color": "blue", "formality": "casual", "seasonality": "all-weather", "image_path": "closet/bottom.jpg"},
        {"id": 3, "category": "shoes", "sub_category": "sneakers", "description": "Sneakers", "color": "white", "formality": "casual", "seasonality": "all-weather", "image_path": "closet/shoes.jpg"}
    ]
    closet_file.write_text(json.dumps(items_data), encoding="utf-8")

    closet = Closet(str(closet_file))
    outfit = RecommendedOutfit(
        outfit_title="Casual White Tee Outfit",
        top_id=1,
        top_description="White tee",
        bottom_id=2,
        bottom_description="Blue jeans",
        shoes_id=3,
        shoes_description="Sneakers"
    )

    drawer = AvatarDrawer()
    paths = drawer.get_garment_image_paths(outfit, closet)
    assert len(paths) == 3
    assert "closet/top.jpg" in paths
    assert "closet/bottom.jpg" in paths
    assert "closet/shoes.jpg" in paths


def test_avatar_drawer_encode_image_to_base64(tmp_path):
    from drawer import AvatarDrawer
    img_file = tmp_path / "test.png"
    img_file.write_bytes(b"dummy image bytes")

    drawer = AvatarDrawer()
    data_uri = drawer.encode_image_to_base64(str(img_file))
    assert data_uri.startswith("data:image/png;base64,")


def test_avatar_drawer_generate_tryon_preview(tmp_path):
    from wardrobe_item import RecommendedOutfit
    from closet import Closet
    from drawer import AvatarDrawer

    closet_file = tmp_path / "closet.json"
    items_data = [
        {"id": 1, "category": "top", "sub_category": "t-shirt", "description": "White tee", "color": "white", "formality": "casual", "seasonality": "hot", "image_path": str(tmp_path / "top.jpg")},
        {"id": 2, "category": "bottom", "sub_category": "jeans", "description": "Blue jeans", "color": "blue", "formality": "casual", "seasonality": "all-weather", "image_path": str(tmp_path / "bottom.jpg")},
        {"id": 3, "category": "shoes", "sub_category": "sneakers", "description": "Sneakers", "color": "white", "formality": "casual", "seasonality": "all-weather", "image_path": str(tmp_path / "shoes.jpg")}
    ]
    closet_file.write_text(json.dumps(items_data), encoding="utf-8")
    (tmp_path / "top.jpg").write_bytes(b"top")
    (tmp_path / "bottom.jpg").write_bytes(b"bottom")
    (tmp_path / "shoes.jpg").write_bytes(b"shoes")

    avatar_file = tmp_path / "user_avatar.png"
    avatar_file.write_bytes(b"avatar")

    outfit = RecommendedOutfit(
        outfit_title="Casual White Tee",
        top_id=1,
        top_description="White tee",
        bottom_id=2,
        bottom_description="Blue jeans",
        shoes_id=3,
        shoes_description="Sneakers"
    )

    closet = Closet(str(closet_file))
    drawer = AvatarDrawer(user_avatar_path=str(avatar_file), output_dir=str(tmp_path / "outfits"))

    from unittest.mock import MagicMock
    with patch("litellm.completion") as mock_comp, patch("settings_manager.load_drawer_settings", return_value={"provider": "google", "model": "gemini-2.5-flash", "api_key": "key", "user_avatar_path": str(avatar_file)}):
        mock_resp_obj = MagicMock()
        mock_resp_obj.choices = [MagicMock()]
        mock_resp_obj.choices[0].message.content = "Synthesized try-on response text"
        mock_comp.return_value = mock_resp_obj

        result_path = drawer.generate_tryon_preview(outfit, closet, outfit_num=1)
        assert result_path is not None
        assert "_outfit_1_ids_top1_bottom2_shoes3.png" in result_path


def test_generate_avatar_tryon_command_execute():
    from unittest.mock import MagicMock
    from controller import GenerateAvatarTryOnCommand
    from wardrobe_item import RecommendedOutfit

    app = MagicMock()
    outfit = RecommendedOutfit(
        outfit_title="Summer Vibe",
        top_id=1,
        top_description="Shirt",
        bottom_id=2,
        bottom_description="Shorts",
        shoes_id=3,
        shoes_description="Sandals"
    )

    cmd = GenerateAvatarTryOnCommand(app, outfit)

    with patch("settings_manager.load_drawer_settings", return_value={"user_avatar_path": "valid_avatar.png"}), \
         patch("os.path.exists", return_value=True), \
         patch("drawer.AvatarDrawer.generate_tryon_preview", return_value="outfits/2026-08-08_outfit_1_ids_top1.png") as mock_gen:
        res = cmd.execute()
        assert res is True
        mock_gen.assert_called_once()
        app.ui.print_tryon_result.assert_called_once_with("outfits/2026-08-08_outfit_1_ids_top1.png")


def test_drawer_passes_api_base_to_litellm(tmp_path):
    from drawer import AvatarDrawer
    from wardrobe_item import RecommendedOutfit
    from unittest.mock import patch, MagicMock

    avatar_file = tmp_path / "avatar.png"
    avatar_file.write_bytes(b"fake avatar image")

    outfit = RecommendedOutfit(
        outfit_title="Test Outfit",
        top_id=1,
        top_description="White Shirt",
        bottom_id=2,
        bottom_description="Blue Jeans",
        shoes_id=3,
        shoes_description="Sneakers"
    )

    closet = MagicMock()
    closet.get_all_items.return_value = []
    drawer = AvatarDrawer(user_avatar_path=str(avatar_file), output_dir=str(tmp_path / "outfits"))

    mock_settings = {
        "provider": "custom",
        "model": "local/sdxl",
        "api_key": "key",
        "api_base": "http://localhost:11434",
        "user_avatar_path": str(avatar_file)
    }

    mock_resp_obj = MagicMock()
    mock_resp_obj.choices = [MagicMock()]
    mock_resp_obj.choices[0].message.content = "preview text"

    with patch("drawer.load_drawer_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_resp_obj) as mock_comp:

        drawer.generate_tryon_preview(outfit, closet)
        assert mock_comp.called
        assert mock_comp.call_args[1].get("api_base") == "http://localhost:11434"



