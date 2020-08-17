import copy
import random
from .customizer import get_starting_equipment, BASE_CUSTOMIZER_PAYLOAD
from .misc import mergedicts

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
        "enemy_health": "default",
        "pot_shuffle": "off"
    },
    "allow_quickswap": False
}


def generate_random_settings(weights, tournament=True, spoilers="mystery"):
    # customizer isn't used until its used
    customizer = False

    # we need to figure out if entrance shuffle is a thing, since that tells us if we should even bother with rolling customizer things
    entrances = get_random_option(weights['entrance_shuffle'])

    # only roll customizer stuff if entrance shuffle isn't on, and we have a customizer section
    if entrances == "none" and 'customizer' in weights:
        custom = {}
        eq = []
        pool = {}

        if 'eq' in weights['customizer']:
            for key in weights['customizer']['eq'].keys():
                value = get_random_option(weights['customizer']['eq'][key])
                if value:
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
    settings["crystals"]["ganon"] = get_random_option(weights['ganon_open'])
    settings["crystals"]["tower"] = get_random_option(weights['tower_open'])
    settings["mode"] = get_random_option(weights['world_state'])
    settings["hints"] = get_random_option(weights['hints'])
    settings["weapons"] = get_random_option(weights['weapons'])
    settings["item"]["pool"] = get_random_option(weights['item_pool'])
    settings["item"]["functionality"] = get_random_option(
        weights['item_functionality'])
    settings["tournament"] = tournament
    settings["spoilers"] = spoilers
    settings["enemizer"]["boss_shuffle"] = get_random_option(
        weights['boss_shuffle'])
    settings["enemizer"]["enemy_shuffle"] = get_random_option(
        weights['enemy_shuffle'])
    settings["enemizer"]["enemy_damage"] = get_random_option(
        weights['enemy_damage'])
    settings["enemizer"]["enemy_health"] = get_random_option(
        weights['enemy_health'])
    settings["enemizer"]["pot_shuffle"] = get_random_option(
        weights.get('pot_shuffle', 'off'))

    settings["allow_quickswap"] = get_random_option(
        weights.get('allow_quickswap', False))

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

                # remove flute if starting with activated flute
                # remove bottles as well
                # TODO: This code is terrible, it should be its own function
                if item == 'OcarinaActive':
                    item = 'OcarinaInactive'
                if item in ['Bottle', 'BottleWithRedPotion', 'BottleWithGreenPotion', 'BottleWithBluePotion', 'BottleWithBee', 'BottleWithGoldBee', 'BottleWithFairy']:
                    item = 'BottleWithRandom'

                settings['custom']['item']['count'][item] = settings['custom']['item']['count'].get(
                    item, 0) - 1 if settings['custom']['item']['count'].get(item, 0) > 0 else 0

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
            settings['enemizer']['pot_shuffle'] = 'off'

        # set dungeon_items to standard if any region.wild* custom settings are present
        if any(key in ['region.wildKeys', 'region.wildBigKeys', 'region.wildCompasses', 'region.wildMaps'] for key in custom):
            settings['dungeon_items'] = 'standard'

        # set custom triforce hunt settings if TFH is the goal
        if settings['goal'] == 'triforce-hunt':
            if 'triforce-hunt' in weights['customizer']:
                min_difference = get_random_option(
                    weights['customizer']['triforce-hunt'].get('min_difference', 0))
                try:
                    goal_pieces = randval(
                        weights['customizer']['triforce-hunt']['goal'])
                except KeyError:
                    goal_pieces = 20

                try:
                    if isinstance(weights['customizer']['triforce-hunt']['pool'], list):
                        if weights['customizer']['triforce-hunt']['pool'][0] + min_difference < goal_pieces:
                            weights['customizer']['triforce-hunt']['pool'][0] = goal_pieces + \
                                min_difference
                    pool_pieces = randval(
                        weights['customizer']['triforce-hunt']['pool'])

                    # a final catchall
                    if pool_pieces < goal_pieces + min_difference:
                        pool_pieces = goal_pieces + min_difference
                except KeyError:
                    pool_pieces = 30
            else:
                goal_pieces = 20
                pool_pieces = 30

            settings['custom']['item.Goal.Required'] = goal_pieces
            settings['custom']['item']['count']['TriforcePiece'] = pool_pieces

        if settings['custom'].get('rom.timerMode', 'off') == 'countdown-ohko':
            if 'timed-ohko' in weights['customizer']:
                for clock in weights['customizer']['timed-ohko'].get('clock', {}):
                    settings['custom'][f'item.value.{clock}'] = randval(
                        weights['customizer']['timed-ohko']['clock'][clock].get(
                            'value', 0)
                    )
                    settings['custom']['item']['count'][clock] = randval(
                        weights['customizer']['timed-ohko']['clock'][clock].get(
                            'pool', 0)
                    )

                settings['custom']['rom.timerStart'] = randval(
                    weights['customizer']['timed-ohko'].get('timerStart', 0)
                )

            settings = dict(mergedicts(
                settings, weights['customizer']['timed-ohko'].get('forced_settings', {})))

        # fill in empty items in pool with FillItemPoolWith option, defaults to "Nothing"
        filler = weights.get('options', {}).get('FillItemPoolWith', 'Nothing')
        settings['custom']['item']['count'][filler] = settings['custom']['item']['count'].get(
            filler, 0) + max(0, 216 - sum(settings['custom']['item']['count'].values()))

    else:
        settings["entrances"] = entrances

    # If mc or mcs shuffle gets rolled, and its entrance, shift to either standard or full accordingly
    # mc and mcs are not supported by the entrance randomizer version currently used for v31.0.4.
    # If this changes, these statements will get removed.
    if settings.get('entrances', 'none') != 'none':
        if settings.get('dungeon_items', 'standard') == 'mc':
            settings['dungeon_items'] = 'standard'
        elif settings.get('dungeon_items', 'standard') == 'mcs':
            settings['dungeon_items'] = 'full'

    # This if statement is dedicated to the survivors of http://www.speedrunslive.com/races/result/#!/264658
    if settings['weapons'] not in ['vanilla', 'assured'] and settings['mode'] == 'standard' and (
            settings['enemizer']['enemy_shuffle'] != 'none'
            or settings['enemizer']['enemy_damage'] != 'default'
            or settings['enemizer']['enemy_health'] != 'default'):
        settings['weapons'] = 'assured'

    # deactivate a starting flute that's pre-activated, as it'll cause some really dumb rainstate scenarios
    if settings["mode"] == 'standard':
        settings['eq'] = [item if item !=
                          'OcarinaActive' else 'OcarinaInactive' for item in settings.get('eq', {})]

    # fix a bad interaction between pedestal/dungeons goals and prize.crossWorld
    if settings["goal"] in ['pedestal','dungeons']:
        settings['custom']['prize.crossWorld'] = True

    return settings, customizer

# fix weights where strings are provided as keys, this fixes issues with injesting json as a weightset


def conv(string):
    # first try to convert it to a integer

    if isinstance(string, str):
        try:
            return int(string)
        except ValueError:
            pass

        if string.lower() == "true":
            return True
        if string.lower() == "false":
            return False

    return string


def randval(optset):
    if isinstance(optset, list):
        return random.randint(optset[0], optset[1])
    else:
        return optset


def get_random_option(optset):
    try:
        return random.choices(population=[conv(key) for key in list(optset.keys())], weights=list(optset.values()))[0] if isinstance(optset, dict) else conv(optset)
    except TypeError as err:
        raise TypeError("There is a non-numeric value as a weight.") from err
