"""
Unit and integration tests for the Multimodal Closet Synthesizer module.
"""
import json
import pytest
from settings_manager import (

    load_synthesizer_settings,
    save_synthesizer_settings,
    validate_synthesizer_settings,
)
from prompts import vision_synthesizer_prompt

SETTINGS_PATH = "synthesizer-settings.json"


def test_vision_synthesizer_prompt_contains_required_keys():
    """Verify system prompt contains instructions for extracting WardrobeItem fields."""
    prompt = vision_synthesizer_prompt
    assert isinstance(prompt, str)
    assert "category" in prompt
    assert "sub_category" in prompt
    assert "description" in prompt
    assert "color" in prompt
    assert "formality" in prompt
    assert "seasonality" in prompt


def test_load_default_synthesizer_settings(tmp_path, monkeypatch):
    """Verify load_synthesizer_settings returns default settings if file doesn't exist."""
    fake_path = str(tmp_path / "non_existent.json")
    monkeypatch.setattr("settings_manager.SYNTHESIZER_SETTINGS_FILE", fake_path)
    
    settings = load_synthesizer_settings()
    assert settings["provider"] == "google"
    assert settings["model"] == "gemini-2.5-flash"
    assert "api_key" in settings


def test_save_and_load_synthesizer_settings(tmp_path, monkeypatch):
    """Verify save_synthesizer_settings writes JSON and load_synthesizer_settings reads it back."""
    fake_path = str(tmp_path / "synthesizer-settings.json")
    monkeypatch.setattr("settings_manager.SYNTHESIZER_SETTINGS_FILE", fake_path)
    
    new_settings = {
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": "sk-test12345"
    }
    save_synthesizer_settings(new_settings)
    
    loaded = load_synthesizer_settings()
    assert loaded["provider"] == "openai"
    assert loaded["model"] == "gpt-4o"
    assert loaded["api_key"] == "sk-test12345"


def test_validate_synthesizer_settings_valid():
    """Verify validate_synthesizer_settings passes for valid configuration."""
    valid_settings = {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "api_key": "test-key"
    }
    # Should not raise exception
    validate_synthesizer_settings(valid_settings)


def test_validate_synthesizer_settings_missing_keys():
    """Verify validate_synthesizer_settings raises ValueError on missing keys."""
    invalid_settings = {"provider": "google"}
    with pytest.raises(ValueError, match="Invalid synthesizer settings"):
        validate_synthesizer_settings(invalid_settings)


def test_scan_untagged_images(tmp_path):
    """Verify scan_untagged_images identifies new image files not present in closet.json."""
    from synthesizer import ClosetSynthesizer
    
    closet_dir = tmp_path / "closet"
    closet_dir.mkdir()
    
    # Create sample image files
    img1 = closet_dir / "item1.jpg"
    img2 = closet_dir / "item2.png"
    img1.write_bytes(b"dummy image 1")
    img2.write_bytes(b"dummy image 2")
    
    # Create a dummy closet.json with item1.jpg already ingested
    json_file = tmp_path / "dummy_closet.json"
    dummy_data = [
        {
            "id": 1,
            "category": "Top",
            "sub_category": "Shirt",
            "description": "Existing shirt",
            "color": "Blue",
            "formality": "Casual",
            "seasonality": "Summer",
            "image_path": str(img1)
        }
    ]
    json_file.write_text(json.dumps(dummy_data))
    
    synthesizer = ClosetSynthesizer(closet_dir=str(closet_dir), json_path=str(json_file))
    untagged = synthesizer.scan_untagged_images()
    
    # img1 is already in closet.json, so only img2 should be returned
    assert len(untagged) == 1
    assert str(img2) in untagged[0] or img2.name in untagged[0]


def test_encode_image_to_base64(tmp_path):
    """Verify encode_image_to_base64 creates valid base64 data URI."""
    from synthesizer import ClosetSynthesizer
    
    img_file = tmp_path / "test.jpg"
    img_file.write_bytes(b"hello world image")
    
    synthesizer = ClosetSynthesizer(closet_dir=str(tmp_path), json_path=str(tmp_path / "closet.json"))
    uri = synthesizer.encode_image_to_base64(str(img_file))
    
    assert uri.startswith("data:image/jpeg;base64,")


def test_build_batch_payload(tmp_path):
    """Verify build_batch_payload constructs valid LiteLLM messages list."""
    from synthesizer import ClosetSynthesizer
    
    img1 = tmp_path / "img1.png"
    img1.write_bytes(b"data1")
    
    synthesizer = ClosetSynthesizer(closet_dir=str(tmp_path), json_path=str(tmp_path / "closet.json"))
    messages = synthesizer.build_batch_payload([str(img1)])
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert isinstance(messages[1]["content"], list)


def test_synthesize_batch_and_ingest(tmp_path, monkeypatch):
    """Verify synthesize_batch and ingest_new_photos append items to closet.json."""
    from synthesizer import ClosetSynthesizer
    
    closet_dir = tmp_path / "closet"
    closet_dir.mkdir()
    img1 = closet_dir / "new_top.jpg"
    img1.write_bytes(b"top_data")
    
    json_file = tmp_path / "closet.json"
    json_file.write_text("[]")
    
    # Mock litellm completion response
    class MockMessage:
        content = json.dumps([
            {
                "category": "Top",
                "sub_category": "T-Shirt",
                "description": "Graphic T-Shirt",
                "color": "Black",
                "formality": "Casual",
                "seasonality": "Summer"
            }
        ])
        
    class MockChoice:
        message = MockMessage()
        
    class MockResponse:
        choices = [MockChoice()]
        
    monkeypatch.setattr("litellm.completion", lambda **kwargs: MockResponse())
    
    synthesizer = ClosetSynthesizer(closet_dir=str(closet_dir), json_path=str(json_file))
    count = synthesizer.ingest_new_photos(batch_size=5)
    
    assert count == 1
    
    # Verify json_file contains new item
    with open(json_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    assert len(items) == 1
    assert items[0]["id"] == 1
    assert items[0]["category"] == "top"
    assert items[0]["sub_category"] == "T-Shirt"


def test_synthesize_closet_command_execute(monkeypatch, capsys):
    """Verify SynthesizeClosetCommand executes ingest_new_photos and outputs summary."""
    from controller import SynthesizeClosetCommand
    
    class DummySynthesizer:
        def __init__(self, **kwargs):
            pass
        def ingest_new_photos(self, **kwargs):
            return 3

    monkeypatch.setattr("controller.ClosetSynthesizer", DummySynthesizer)
    
    cmd = SynthesizeClosetCommand()
    cmd.execute()
    
    captured = capsys.readouterr()
    assert "3" in captured.out or "synthesized" in captured.out.lower()


def test_synthesizer_passes_api_base_to_litellm(monkeypatch):
    from synthesizer import ClosetSynthesizer
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "[]"

    mock_settings = {
        "provider": "custom",
        "model": "ollama/llava",
        "api_key": "key",
        "api_base": "http://localhost:11434"
    }

    with patch("synthesizer.load_synthesizer_settings", return_value=mock_settings), \
         patch("litellm.completion", return_value=mock_resp) as mock_comp:

        synth = ClosetSynthesizer(closet_dir="closet", json_path="closet.json")
        synth._call_vision_llm([{"role": "user", "content": "hi"}])
        assert mock_comp.called
        assert mock_comp.call_args[1].get("api_base") == "http://localhost:11434"


def test_synthesize_batch_handles_list_inputs(monkeypatch, tmp_path):
    """Verify synthesize_batch handles LLM output returning list values for attributes like color, category, etc."""
    from synthesizer import ClosetSynthesizer

    json_file = tmp_path / "closet.json"
    json_file.write_text("[]")

    class MockMessage:
        content = json.dumps([
            {
                "category": ["outerwear", "jacket"],
                "sub_category": ["Blazer", "Casual"],
                "description": ["Navy blue blazer", "gold buttons"],
                "color": ["red", "brown", "white"],
                "formality": ["smart casual"],
                "seasonality": ["cold", "winter"]
            }
        ])

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]

    monkeypatch.setattr("litellm.completion", lambda **kwargs: MockResponse())

    synth = ClosetSynthesizer(closet_dir=str(tmp_path), json_path=str(json_file))
    img1 = tmp_path / "img1.png"
    img1.write_bytes(b"dummy image content")
    items = synth.synthesize_batch([str(img1)])


    assert len(items) == 1
    assert items[0].category == "jacket"
    assert items[0].sub_category == "Blazer, Casual"
    assert items[0].description == "Navy blue blazer, gold buttons"
    assert items[0].color == "red, brown, white"
    assert items[0].formality == "business casual"
    assert items[0].seasonality == "cold"



