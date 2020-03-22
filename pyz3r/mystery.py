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
    # customizer isn't used until its used
    customizer = False

    # we need to figure out if entrance shuffle is a thing, since that tells us if we should even bother with rolling customizer things
    entrances =  get_random_option(weights['entrance_shuffle'])

    # only roll customizer stuff if entrance shuffle isn't on, and we have a customizer section
    if entrances == "none" and 'customizer' in weights:
        custom = {}
        eq = []
        pool = {}

        if 'eq' in weights['customizer']:
            for key in weights['customizer']['eq'].keys():
                value = get_random_option(weights['customizer']['eq'][key])
                if value is not None:
                    eq += get_starting_equipment(key=key, value=value)
                    customizer = True

        if 'custom' in weights['customizer']:
            for key in weights['customizer']['custom'].keys():
                value = get_random_option(weights['customizer']['custom'][key])
                if value is not None:
                    custom[key] = value
                    customizer = True

        if 'pool' in weights['customizer']:
            for key in weights['customizer']['pool'].keys():
                value = get_random_option(weights['customizer']['pool'][key])
                if value is not None:
                    pool[key] = value
                    customizer = True

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
        # default to v31 prize packs
        settings['custom']['customPrizePacks'] = False

        # set custom settings that were rolled
        for key, value in custom.items():
            settings['custom'][key] = value

        # set custom item pool that was rolled
        for key, value in pool.items():
            settings['custom']['item']['count'][key] = value

        # apply custom starting equipment, and adjust the item pool accordingly
        if eq:
            # remove items from pool
            for item in eq:
                settings['custom']['item']['count'][item] = settings['custom']['item']['count'].get(item, 0) - 1 if settings['custom']['item']['count'].get(item, 0) > 0 else 0

            # re-add 3 heart containers as a baseline
            eq += ['BossHeartContainer'] * 3

            # update the eq section of the settings
            settings['eq'] = eq

        # if dark room navigation is enabled, then 
        # oh and yes item.require.Lamp is mixed around for whatever reason
        # False = dark room navigation isn't required
        if settings['custom'].get('item.require.Lamp', False):
            settings['enemizer']['enemy_shuffle'] = 'none'
            settings['enemizer']['enemy_damage'] = 'default'

        # set dungeon_items to standard if any region.wild* custom settings are present
        if any(key in ['region.wildKeys', 'region.wildBigKeys', 'region.wildCompasses', 'region.wildMaps'] for key in custom):
            settings['dungeon_items'] = 'standard'

        # set custom triforce hunt settings if TFH is the goal
        if settings['goal'] == 'triforce-hunt':
            min_difference = get_random_option(weights['customizer']['triforce-hunt'].get('min_difference', 0))
            try:
                goal_pieces = random.randint(weights['customizer']['triforce-hunt']['goal']['min'], weights['customizer']['triforce-hunt']['goal']['max'])
            except KeyError:
                goal_pieces = 20

            try:
                pool_pieces = random.randint(
                    weights['customizer']['triforce-hunt']['pool']['min'] if weights['customizer']['triforce-hunt']['pool']['min'] + min_difference > goal_pieces else goal_pieces + min_difference,
                    weights['customizer']['triforce-hunt']['pool']['max'],
                )
            except KeyError:
                pool_pieces = 30

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
    try:
        return random.choices(population=list(optset.keys()), weights=list(optset.values()))[0] if isinstance(optset, dict) else optset
    except TypeError as err:
        raise TypeError("There is a non-numeric value as a weight.") from err
