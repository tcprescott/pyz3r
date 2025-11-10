"""Tests for pyz3r.misc module."""

import pytest
from pyz3r import misc


class TestChunkFunction:
    """Test the chunk utility function."""

    def test_chunk_basic(self):
        """Test basic chunking of an iterator."""
        data = [1, 2, 3, 4, 5, 6]
        result = list(misc.chunk(iter(data), 2))
        assert result == [(1, 2), (3, 4), (5, 6)]

    def test_chunk_uneven(self):
        """Test chunking with uneven division."""
        data = [1, 2, 3, 4, 5]
        result = list(misc.chunk(iter(data), 2))
        assert result == [(1, 2), (3, 4)]

    def test_chunk_size_one(self):
        """Test chunking with size 1."""
        data = [1, 2, 3]
        result = list(misc.chunk(iter(data), 1))
        assert result == [(1,), (2,), (3,)]

    def test_chunk_empty(self):
        """Test chunking an empty iterator."""
        data = []
        result = list(misc.chunk(iter(data), 2))
        assert result == []


class TestSeekPatchData:
    """Test the seek_patch_data function."""

    def test_seek_patch_data_exact_offset(self):
        """Test seeking patch data at exact offset."""
        patches = [
            {"50": [9, 9, 9]},  # Add a patch before to make bisect work properly
            {"100": [1, 2, 3, 4, 5]},
            {"200": [6, 7, 8, 9, 10]}
        ]
        result = misc.seek_patch_data(patches, 100, 3)
        assert result == [1, 2, 3]

    def test_seek_patch_data_slice(self):
        """Test seeking patch data with slice from middle of a patch."""
        patches = [
            {"100": [1, 2, 3, 4, 5, 6, 7, 8]},
            {"200": [9, 9, 9]}  # Add another patch after
        ]
        result = misc.seek_patch_data(patches, 102, 3)
        assert result == [3, 4, 5]

    def test_seek_patch_data_not_found(self):
        """Test seeking patch data at non-existent offset."""
        patches = [{"100": [1, 2, 3]}]
        with pytest.raises(ValueError):
            misc.seek_patch_data(patches, 50, 2)


class TestConvertRandomizerSettings:
    """Test the convert_randomizer_settings function."""

    def test_convert_basic_settings(self):
        """Test converting basic randomizer settings."""
        web_dict = {
            "glitches_required": "none",
            "item_placement": "advanced",
            "goal": "ganon",
            "world_state": "open"
        }
        result = misc.convert_randomizer_settings(web_dict)
        assert result["glitches"] == "none"
        assert result["item_placement"] == "advanced"
        assert result["goal"] == "ganon"
        assert result["mode"] == "open"

    def test_convert_with_crystals(self):
        """Test converting settings with crystal requirements."""
        web_dict = {
            "ganon_open": "7",
            "tower_open": "4"
        }
        result = misc.convert_randomizer_settings(web_dict)
        assert result["crystals"]["ganon"] == "7"
        assert result["crystals"]["tower"] == "4"


class TestMergeDicts:
    """Test the mergedicts function."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = dict(misc.mergedicts(dict1, dict2))
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        dict1 = {"a": {"x": 1, "y": 2}, "b": 3}
        dict2 = {"a": {"y": 5, "z": 6}, "c": 7}
        result = dict(misc.mergedicts(dict1, dict2))
        assert result["a"]["x"] == 1
        assert result["a"]["y"] == 5
        assert result["a"]["z"] == 6
        assert result["b"] == 3
        assert result["c"] == 7

    def test_merge_empty_dicts(self):
        """Test merging with empty dictionaries."""
        dict1 = {"a": 1}
        dict2 = {}
        result = dict(misc.mergedicts(dict1, dict2))
        assert result == {"a": 1}

    def test_merge_override_non_dict(self):
        """Test that non-dict values override."""
        dict1 = {"a": {"x": 1}}
        dict2 = {"a": "string"}
        result = dict(misc.mergedicts(dict1, dict2))
        assert result == {"a": "string"}
