"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_alttpr_settings():
    """Provide sample ALTTPR settings for testing."""
    return {
        "glitches": "none",
        "item_placement": "advanced",
        "dungeon_items": "standard",
        "accessibility": "items",
        "goal": "ganon",
        "crystals": {
            "ganon": "7",
            "tower": "7"
        },
        "mode": "open",
        "entrances": "none",
        "hints": "on",
        "weapons": "randomized",
        "item": {
            "pool": "normal",
            "functionality": "normal"
        },
        "tournament": False,
        "spoilers": "off",
        "lang": "en",
        "enemizer": {
            "boss_shuffle": "none",
            "enemy_shuffle": "none",
            "enemy_damage": "default",
            "enemy_health": "default"
        }
    }


@pytest.fixture
def sample_customizer_save():
    """Provide sample customizer save data for testing."""
    return {
        'randomizer.glitches_required': 'none',
        'randomizer.accessibility': 'items',
        'randomizer.goal': 'ganon',
        'randomizer.tower_open': '7',
        'randomizer.ganon_open': '7',
        'randomizer.dungeon_items': 'standard',
        'randomizer.item_placement': 'advanced',
        'randomizer.world_state': 'open',
        'randomizer.hints': 'on',
        'randomizer.weapons': 'randomized',
        'randomizer.item_pool': 'normal',
        'randomizer.item_functionality': 'normal',
    }
