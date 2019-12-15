import random

def generate_random_settings(weights, tournament=True, spoilers="mystery"):
    settings={
        "glitches": get_random_option(weights['glitches_required']),
        "item_placement": get_random_option(weights['item_placement']),
        "dungeon_items": get_random_option(weights['dungeon_items']),
        "accessibility": get_random_option(weights['accessibility']),
        "goal": get_random_option(weights['goals']),
        "crystals": {
            "ganon": get_random_option(weights['tower_open']),
            "tower": get_random_option(weights['ganon_open']),
        },
        "mode": get_random_option(weights['world_state']),
        "entrances": get_random_option(weights['entrance_shuffle']),
        "hints": get_random_option(weights['hints']),
        "weapons": get_random_option(weights['weapons']),
        "item": {
            "pool": get_random_option(weights['item_pool']),
            "functionality": get_random_option(weights['item_functionality']),
        },
        "tournament": tournament,
        "spoilers": spoilers,
        "lang": "en",
        "enemizer": {
            "boss_shuffle": get_random_option(weights['boss_shuffle']),
            "enemy_shuffle": get_random_option(weights['enemy_shuffle']),
            "enemy_damage": get_random_option(weights['enemy_damage']),
            "enemy_health": get_random_option(weights['enemy_health']),
        }
    }

    # This if statement is dedicated to the survivors of http://www.speedrunslive.com/races/result/#!/264658
    if settings['weapons'] not in ['vanilla','assured'] and settings['mode'] == 'standard' and (
            settings['enemizer']['enemy_shuffle'] != 'none'
            or settings['enemizer']['enemy_damage'] != 'default'
            or settings['enemizer']['enemy_health'] != 'default'):
        settings['weapons'] = 'assured'

    return settings

def get_random_option(optset):
    return random.choices(population=list(optset.keys()),weights=list(optset.values()))[0]