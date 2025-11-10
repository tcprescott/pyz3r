"""Tests for pyz3r.mystery module."""

import pytest
from pyz3r.mystery import (
    generate_random_settings,
    get_random_option,
    conv,
    randval,
    BASE_RANDOMIZER_PAYLOAD
)


class TestConvFunction:
    """Test the conv (convert) function."""

    def test_conv_integer_string(self):
        """Test converting integer strings."""
        assert conv("123") == 123
        assert conv("0") == 0
        assert conv("-5") == -5

    def test_conv_boolean_strings(self):
        """Test converting boolean strings."""
        assert conv("true") is True
        assert conv("True") is True
        assert conv("TRUE") is True
        assert conv("false") is False
        assert conv("False") is False
        assert conv("FALSE") is False

    def test_conv_non_convertible_string(self):
        """Test strings that can't be converted."""
        assert conv("hello") == "hello"
        assert conv("12.5") == "12.5"

    def test_conv_non_string(self):
        """Test non-string values."""
        assert conv(123) == 123
        assert conv(True) is True
        assert conv(None) is None


class TestRandvalFunction:
    """Test the randval function."""

    def test_randval_with_range(self):
        """Test randval with a range list."""
        # Test that result is within range
        for _ in range(10):
            result = randval([10, 20])
            assert 10 <= result <= 20

    def test_randval_with_single_value(self):
        """Test randval with a single value."""
        assert randval(42) == 42
        assert randval(0) == 0


class TestGetRandomOption:
    """Test the get_random_option function."""

    def test_get_random_option_with_dict(self):
        """Test selecting from weighted dictionary."""
        options = {"a": 100, "b": 0, "c": 0}
        result = get_random_option(options)
        assert result == "a"

    def test_get_random_option_with_single_value(self):
        """Test with a single value (not a dict)."""
        result = get_random_option("fixed_value")
        assert result == "fixed_value"

    def test_get_random_option_with_none(self):
        """Test with None input."""
        result = get_random_option(None)
        assert result is None

    def test_get_random_option_with_empty_dict(self):
        """Test with empty dictionary."""
        result = get_random_option({})
        assert result is None

    def test_get_random_option_converts_keys(self):
        """Test that keys are converted using conv()."""
        options = {"true": 100, "false": 0}
        result = get_random_option(options)
        assert result is True

    def test_get_random_option_non_numeric_weights_raises(self):
        """Test that non-numeric weights raise TypeError."""
        options = {"a": "not_a_number"}
        with pytest.raises(TypeError, match="non-numeric value"):
            get_random_option(options)


class TestGenerateRandomSettings:
    """Test the generate_random_settings function."""

    def test_generate_basic_settings(self):
        """Test generating basic random settings."""
        weights = {
            'glitches_required': {'none': 100},
            'item_placement': {'advanced': 100},
            'dungeon_items': {'standard': 100},
            'accessibility': {'items': 100},
            'goals': {'ganon': 100},
            'ganon_open': {'7': 100},
            'tower_open': {'7': 100},
            'world_state': {'open': 100},
            'entrance_shuffle': {'none': 100},
            'boss_shuffle': {'none': 100},
            'enemy_shuffle': {'none': 100},
            'hints': {'on': 100},
            'weapons': {'randomized': 100},
            'item_pool': {'normal': 100},
            'item_functionality': {'normal': 100},
            'enemy_damage': {'default': 100},
            'enemy_health': {'default': 100},
        }
        
        settings, customizer = generate_random_settings(weights, tournament=True)
        
        assert isinstance(settings, dict)
        assert isinstance(customizer, bool)
        assert settings['glitches'] == 'none'
        assert settings['goal'] == 'ganon'
        assert settings['tournament'] is True

    def test_generate_with_customizer(self):
        """Test generating settings with customizer enabled."""
        weights = {
            'glitches_required': {'none': 100},
            'item_placement': {'advanced': 100},
            'dungeon_items': {'standard': 100},
            'accessibility': {'items': 100},
            'goals': {'ganon': 100},
            'ganon_open': {'7': 100},
            'tower_open': {'7': 100},
            'world_state': {'open': 100},
            'entrance_shuffle': {'none': 100},
            'boss_shuffle': {'none': 100},
            'enemy_shuffle': {'none': 100},
            'hints': {'on': 100},
            'weapons': {'randomized': 100},
            'item_pool': {'normal': 100},
            'item_functionality': {'normal': 100},
            'enemy_damage': {'default': 100},
            'enemy_health': {'default': 100},
            'customizer': {
                'eq': {
                    'Bottle1': {1: 100}
                }
            }
        }
        
        settings, customizer = generate_random_settings(weights, tournament=False)
        
        assert customizer is True
        assert 'custom' in settings
        assert 'eq' in settings

    def test_generate_tournament_flag(self):
        """Test tournament flag is properly set."""
        weights = {
            'glitches_required': {'none': 100},
            'item_placement': {'advanced': 100},
            'dungeon_items': {'standard': 100},
            'accessibility': {'items': 100},
            'goals': {'ganon': 100},
            'ganon_open': {'7': 100},
            'tower_open': {'7': 100},
            'world_state': {'open': 100},
            'entrance_shuffle': {'none': 100},
            'boss_shuffle': {'none': 100},
            'enemy_shuffle': {'none': 100},
            'hints': {'on': 100},
            'weapons': {'randomized': 100},
            'item_pool': {'normal': 100},
            'item_functionality': {'normal': 100},
            'enemy_damage': {'default': 100},
            'enemy_health': {'default': 100},
        }
        
        settings_true, _ = generate_random_settings(weights, tournament=True)
        assert settings_true['tournament'] is True
        
        settings_false, _ = generate_random_settings(weights, tournament=False)
        assert settings_false['tournament'] is False

    def test_generate_spoilers_setting(self):
        """Test spoilers setting is properly set."""
        weights = {
            'glitches_required': {'none': 100},
            'item_placement': {'advanced': 100},
            'dungeon_items': {'standard': 100},
            'accessibility': {'items': 100},
            'goals': {'ganon': 100},
            'ganon_open': {'7': 100},
            'tower_open': {'7': 100},
            'world_state': {'open': 100},
            'entrance_shuffle': {'none': 100},
            'boss_shuffle': {'none': 100},
            'enemy_shuffle': {'none': 100},
            'hints': {'on': 100},
            'weapons': {'randomized': 100},
            'item_pool': {'normal': 100},
            'item_functionality': {'normal': 100},
            'enemy_damage': {'default': 100},
            'enemy_health': {'default': 100},
        }
        
        settings, _ = generate_random_settings(weights, spoilers='on')
        assert settings['spoilers'] == 'on'


class TestBaseRandomizerPayload:
    """Test the BASE_RANDOMIZER_PAYLOAD constant."""

    def test_base_payload_structure(self):
        """Test that base payload has expected structure."""
        assert 'glitches' in BASE_RANDOMIZER_PAYLOAD
        assert 'item_placement' in BASE_RANDOMIZER_PAYLOAD
        assert 'dungeon_items' in BASE_RANDOMIZER_PAYLOAD
        assert 'crystals' in BASE_RANDOMIZER_PAYLOAD
        assert 'item' in BASE_RANDOMIZER_PAYLOAD
        assert 'enemizer' in BASE_RANDOMIZER_PAYLOAD

    def test_base_payload_defaults(self):
        """Test base payload default values."""
        assert BASE_RANDOMIZER_PAYLOAD['glitches'] == 'none'
        assert BASE_RANDOMIZER_PAYLOAD['mode'] == 'open'
        assert BASE_RANDOMIZER_PAYLOAD['tournament'] is False
