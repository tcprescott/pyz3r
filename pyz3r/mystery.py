import copy
import random
from .customizer import get_starting_equipment, BASE_CUSTOMIZER_PAYLOAD

BASE_RANDOMIZER_PAYLOAD = {
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
    "hints": "off",
    "weapons": "randomized",
    "item": {
        "pool": "normal",
        "functionality": "normal"
    },
    "tournament": False,
    "spoilers": "on",
    "lang": "en",
    "enemizer": {
        "boss_shuffle": "none",
        "enemy_shuffle": "none",
        "enemy_damage": "default",
        "enemy_health": "default"
    }
}

def generate_random_settings(weights, tournament=True, spoilers="mystery"):
    entrances =  get_random_option(weights['entrance_shuffle'])

    if entrances == "none" and 'customizer' in weights:
        custom = {}
        eq = ['BossHeartContainer'] * 3

        if 'eq' in weights['customizer']:
            for key in weights['customizer']['eq'].keys():
                value = get_random_option(weights['customizer']['eq'][key])
                eq += get_starting_equipment(key=key, value=value)
            customizer = False if eq == ['BossHeartContainer'] * 3 else True

        if 'custom' in weights['customizer']:
            for key in weights['customizer']['custom'].keys():
                value = get_random_option(weights['customizer']['custom'][key])
                custom[key] = value
            customizer = True

    else:
        customizer = False

    if customizer:
        settings = copy.deepcopy(BASE_CUSTOMIZER_PAYLOAD)
    else:
        settings = copy.deepcopy(BASE_RANDOMIZER_PAYLOAD)
    
    settings["glitches"] = get_random_option(weights['glitches_required'])
    settings["item_placement"] = get_random_option(weights['item_placement'])
    settings["dungeon_items"] = get_random_option(weights['dungeon_items'])
    settings["accessibility"] = get_random_option(weights['accessibility'])
    settings["goal"] = get_random_option(weights['goals'])
    settings["crystals"]["ganon"] = get_random_option(weights['tower_open'])
    settings["crystals"]["tower"] = get_random_option(weights['ganon_open'])
    settings["mode"] = get_random_option(weights['world_state'])
    settings["hints"] = get_random_option(weights['hints'])
    settings["weapons"] = get_random_option(weights['weapons'])
    settings["item"]["pool"] = get_random_option(weights['item_pool'])
    settings["item"]["functionality"] = get_random_option(weights['item_functionality'])
    settings["tournament"] = tournament
    settings["spoilers"] = spoilers
    settings["enemizer"]["boss_shuffle"] = get_random_option(weights['boss_shuffle'])
    settings["enemizer"]["enemy_shuffle"] = get_random_option(weights['enemy_shuffle'])
    settings["enemizer"]["enemy_damage"] = get_random_option(weights['enemy_damage'])
    settings["enemizer"]["enemy_health"] = get_random_option(weights['enemy_health'])

    if customizer:
        settings['eq'] = eq

        settings['custom']['customPrizePacks'] = False
        for key, value in custom.items():
            settings["custom"][key] = value
        
        if settings['goal'] == 'triforce-hunt':
            min_difference = get_random_option(weights['customizer']['triforce-hunt'].get('min_difference', 0))
            try:
                goal_pieces = random.randint(weights['customizer']['triforce-hunt']['goal']['min'], weights['customizer']['triforce-hunt']['goal']['max'])
            except KeyError:
                goal_pieces = 20

            try:
                pool_pieces = random.randint(weights['customizer']['triforce-hunt']['pool']['min'], weights['customizer']['triforce-hunt']['pool']['max'])
            except KeyError:
                pool_pieces = 30
            
            if pool_pieces - goal_pieces < min_difference:
                pool_pieces = goal_pieces + min_difference

            pool_pieces = 100 if pool_pieces > 100 else pool_pieces
            goal_pieces = 100 if goal_pieces > 100 else goal_pieces

            settings['custom']['item.Goal.Required'] = goal_pieces
            settings['custom']['item']['count']['TriforcePiece'] = pool_pieces

    else:
        settings["entrances"] = entrances

    # This if statement is dedicated to the survivors of http://www.speedrunslive.com/races/result/#!/264658
    if settings['weapons'] not in ['vanilla', 'assured'] and settings['mode'] == 'standard' and (
            settings['enemizer']['enemy_shuffle'] != 'none'
            or settings['enemizer']['enemy_damage'] != 'default'
            or settings['enemizer']['enemy_health'] != 'default'):
        settings['weapons'] = 'assured'

    # Stop gap measure until swordless entrance with a hard+ item pool is fixed
    if settings.get('entrances', 'none') != 'none' and settings['item']['pool'] in ['hard', 'expert'] and settings['weapons'] == 'swordless':
        settings['weapons'] = 'randomized'

    return settings, customizer

def get_random_option(optset):
    return random.choices(population=list(optset.keys()), weights=list(optset.values()))[0] if isinstance(optset, dict) else optset
