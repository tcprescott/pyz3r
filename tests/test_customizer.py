"""Tests for pyz3r.customizer module."""

import pytest
from pyz3r.customizer import convert2settings, get_starting_equipment, BASE_CUSTOMIZER_PAYLOAD


class TestConvert2Settings:
    """Test the convert2settings function."""

    def test_convert_basic_settings(self):
        """Test converting basic customizer settings."""
        customizer_save = {
            'randomizer.glitches_required': 'none',
            'randomizer.accessibility': 'items',
            'randomizer.goal': 'ganon',
        }
        result = convert2settings(customizer_save)
        assert result['glitches'] == 'none'
        assert result['accessibility'] == 'items'
        assert result['goal'] == 'ganon'
        assert result['tournament'] == False

    def test_convert_with_tournament(self):
        """Test converting with tournament flag."""
        customizer_save = {}
        result = convert2settings(customizer_save, tournament=True)
        assert result['tournament'] == True

    def test_convert_with_spoilers(self):
        """Test converting with spoilers setting."""
        customizer_save = {}
        result = convert2settings(customizer_save, spoilers='on')
        assert result['spoilers'] == 'on'

    def test_convert_spoilers_ongen_deprecated(self):
        """Test deprecated spoilers_ongen parameter."""
        customizer_save = {}
        result = convert2settings(customizer_save, spoilers_ongen=True)
        assert result['spoilers'] == 'generate'

    def test_convert_dungeon_items(self):
        """Test converting dungeon items settings."""
        customizer_save = {
            'randomizer.dungeon_items': 'mcs',
        }
        result = convert2settings(customizer_save)
        assert result['dungeon_items'] == 'mcs'

    def test_convert_world_state(self):
        """Test converting world state (mode) settings."""
        customizer_save = {
            'randomizer.world_state': 'inverted',
        }
        result = convert2settings(customizer_save)
        assert result['mode'] == 'inverted'

    def test_convert_crystals(self):
        """Test converting crystal requirements."""
        customizer_save = {
            'randomizer.tower_open': '4',
            'randomizer.ganon_open': '7',
        }
        result = convert2settings(customizer_save)
        assert result['crystals']['tower'] == '4'
        assert result['crystals']['ganon'] == '7'

    def test_convert_item_pool_and_functionality(self):
        """Test converting item pool and functionality."""
        customizer_save = {
            'randomizer.item_pool': 'hard',
            'randomizer.item_functionality': 'expert',
        }
        result = convert2settings(customizer_save)
        assert result['item']['pool'] == 'hard'
        assert result['item']['functionality'] == 'expert'

    def test_convert_enemizer_settings(self):
        """Test converting enemizer settings."""
        customizer_save = {
            'randomizer.boss_shuffle': 'simple',
            'randomizer.enemy_shuffle': 'shuffled',
            'randomizer.enemy_damage': 'random',
            'randomizer.enemy_health': 'hard',
        }
        result = convert2settings(customizer_save)
        assert result['enemizer']['boss_shuffle'] == 'simple'
        assert result['enemizer']['enemy_shuffle'] == 'shuffled'
        assert result['enemizer']['enemy_damage'] == 'random'
        assert result['enemizer']['enemy_health'] == 'hard'

    def test_convert_with_custom_drops(self):
        """Test converting custom drop settings."""
        customizer_save = {
            'vt.custom.drops': {
                'Heart': 10,
                'RupeeGreen': 5
            }
        }
        result = convert2settings(customizer_save)
        # Check that custom.drop.count exists and has the values
        # Note: The base payload already has default drop counts, so values are overridden
        assert 'custom' in result
        assert 'drop' in result['custom']
        # The customizer saves override values in the drop count
        assert 'Heart' in result['custom']['drop']['count']
        assert 'RupeeGreen' in result['custom']['drop']['count']

    def test_convert_preserves_base_payload(self):
        """Test that conversion preserves base customizer payload structure."""
        customizer_save = {}
        result = convert2settings(customizer_save)
        
        # Check that key structure from BASE_CUSTOMIZER_PAYLOAD is preserved
        assert 'glitches' in result
        assert 'item_placement' in result
        assert 'dungeon_items' in result
        assert 'crystals' in result
        assert 'custom' in result


class TestGetStartingEquipment:
    """Test the get_starting_equipment function."""

    def test_bottle_equipment(self):
        """Test converting bottle starting equipment."""
        # Empty bottle
        result = get_starting_equipment('Bottle1', 1)
        assert result == ['Bottle']
        
        # Bottle with red potion
        result = get_starting_equipment('Bottle2', 2)
        assert result == ['BottleWithRedPotion']
        
        # Bottle with green potion
        result = get_starting_equipment('Bottle3', 3)
        assert result == ['BottleWithGreenPotion']
        
        # Bottle with blue potion
        result = get_starting_equipment('Bottle4', 4)
        assert result == ['BottleWithBluePotion']

    def test_progressive_bow(self):
        """Test converting progressive bow equipment."""
        result = get_starting_equipment('ProgressiveBow', 2)
        assert result == ['Bow']
        
        result = get_starting_equipment('ProgressiveBow', 3)
        assert result == ['BowAndSilverArrows']

    def test_boomerang_equipment(self):
        """Test converting boomerang equipment."""
        result = get_starting_equipment('Boomerang', 1)
        assert result == ['Boomerang']
        
        result = get_starting_equipment('Boomerang', 2)
        assert result == ['RedBoomerang']
        
        result = get_starting_equipment('Boomerang', 3)
        assert result == ['Boomerang', 'RedBoomerang']

    def test_ocarina_equipment(self):
        """Test converting ocarina equipment."""
        result = get_starting_equipment('Ocarina', 1)
        assert result == ['OcarinaInactive']
        
        result = get_starting_equipment('Ocarina', 2)
        assert result == ['OcarinaActive']

    def test_rupees_equipment(self):
        """Test converting rupees to equipment items."""
        # 305 rupees = 1x300 + 1x5
        result = get_starting_equipment('Rupees', '305')
        assert 'ThreeHundredRupees' in result
        assert 'FiveRupees' in result
        assert len([x for x in result if x == 'ThreeHundredRupees']) == 1
        
        # 157 rupees = 1x100 + 1x50 + 1x5 + 2x1
        result = get_starting_equipment('Rupees', '157')
        assert 'OneHundredRupees' in result
        assert 'FiftyRupees' in result

    def test_generic_equipment(self):
        """Test converting generic equipment with count."""
        result = get_starting_equipment('Hammer', 1)
        assert result == ['Hammer']
        
        # Multiple items
        result = get_starting_equipment('BossHeartContainer', 3)
        assert result == ['BossHeartContainer', 'BossHeartContainer', 'BossHeartContainer']
        assert len(result) == 3

    def test_zero_count(self):
        """Test equipment with zero count."""
        result = get_starting_equipment('Lamp', 0)
        assert result == []
