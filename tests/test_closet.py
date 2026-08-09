import pytest
from closet import Closet


def test_closet_initialization_default_path():
    closet = Closet()
    items = closet.get_all_items()
    assert isinstance(items, list)
    assert len(items) >= 5


def test_closet_filter_hot_seasonality():
    closet = Closet()
    hot_items = closet.get_items_by_seasonality("hot")
    seasonalities = {item.seasonality for item in hot_items}
    # Should include 'hot' and 'all-weather' items, but no 'cold' items
    assert "cold" not in seasonalities
    assert all(item.seasonality in ("hot", "all-weather") for item in hot_items)


def test_closet_filter_cold_seasonality():
    closet = Closet()
    cold_items = closet.get_items_by_seasonality("cold")
    seasonalities = {item.seasonality for item in cold_items}
    # Should include 'cold' and 'all-weather' items, but no 'hot' items
    assert "hot" not in seasonalities
    assert all(item.seasonality in ("cold", "all-weather") for item in cold_items)


def test_closet_invalid_path_raises():
    with pytest.raises(FileNotFoundError):
        Closet(json_path="non_existent_file.json")
