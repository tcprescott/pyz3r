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
    # iterate through subweights until fully resolved
    while True:
        subweight_name = get_random_option(
            {k: v['chance'] for (k, v) in weights.get('subweights', {}).items()})

        print(f"{subweight_name=}")

        if subweight_name is None:
            break

        subweights = weights.get('subweights', {}).get(subweight_name, {}).get('weights', {})
        subweights['subweights'] = subweights.get('subweights', {})
        weights = {**weights, **subweights}

    # customizer isn't used until its used
    customizer = False

    options = {}

    options["glitches"] = get_random_option(weights['glitches_required'])
    options["item_placement"] = get_random_option(weights['item_placement'])
    options["dungeon_items"] = get_random_option(weights['dungeon_items'])
    options["accessibility"] = get_random_option(weights['accessibility'])
    options["goals"] = get_random_option(weights['goals'])
    options["ganon_open"] = get_random_option(weights['ganon_open'])
    options["tower_open"] = get_random_option(weights['tower_open'])
    options["world_state"] = get_random_option(weights['world_state'])
    options["hints"] = get_random_option(weights['hints'])
    options["weapons"] = get_random_option(weights['weapons'])
    options["item_pool"] = get_random_option(weights['item_pool'])
    options["item_functionality"] = get_random_option(weights['item_functionality'])
    options["boss_shuffle"] = get_random_option(weights['boss_shuffle'])
    options["enemy_shuffle"] = get_random_option(weights['enemy_shuffle'])
    options["enemy_damage"] = get_random_option(weights['enemy_damage'])
    options["enemy_health"] = get_random_option(weights['enemy_health'])
    options["pot_shuffle"] = get_random_option(weights.get('pot_shuffle', 'off'))
    options["allow_quickswap"] = get_random_option(weights.get('allow_quickswap', False))
    options["pseudoboots"] = get_random_option(weights.get('pseudoboots', False))
    options['entrance_shuffle'] = get_random_option(weights['entrance_shuffle'])

    # only roll customizer stuff if entrance shuffle isn't on, and we have a customizer section
    if options['entrance_shuffle'] == "none" and weights.get('customizer', None):
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
            options['enemy_shuffle'] = 'none'
            options['enemy_damage'] = 'default'
            options['pot_shuffle'] = 'off'

        # set dungeon_items to standard if any region.wild* custom settings are present
        if any(key in ['region.wildKeys', 'region.wildBigKeys', 'region.wildCompasses', 'region.wildMaps'] for key in custom):
            options['dungeon_items'] = 'standard'

        if settings['custom'].get('region.wildKeys', False) or settings['custom'].get('region.wildBigKeys', False) or settings['custom'].get('region.wildCompasses', False) or settings['custom'].get('region.wildMaps', False):
            settings['custom']['rom.freeItemMenu'] = True
            settings['custom']['rom.freeItemText'] = True

        if settings['custom'].get('region.wildMaps', False) and 'rom.mapOnPickup' not in weights['customizer']['custom']:
            settings['custom']['rom.mapOnPickup'] = True

        if settings['custom'].get('region.wildCompasses', False) and 'rom.dungeonCount' not in weights['customizer']['custom']:
            settings['custom']['rom.dungeonCount'] = 'pickup'

        # set custom triforce hunt settings if TFH is the goal
        if options['goals'] == 'triforce-hunt':
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

            # settings = dict(mergedicts(options, weights['customizer']['timed-ohko'].get('forced_settings', {})))

        # fill in empty items in pool with FillItemPoolWith option, defaults to "Nothing"
        filler = weights.get('options', {}).get('FillItemPoolWith', 'Nothing')
        settings['custom']['item']['count'][filler] = settings['custom']['item']['count'].get(
            filler, 0) + max(0, 216 - sum(settings['custom']['item']['count'].values()))

        # deactivate a starting flute that's pre-activated, as it'll cause some really dumb rainstate scenarios
        if options["world_state"] == 'standard':
            settings['eq'] = [item if item != 'OcarinaActive' else 'OcarinaInactive' for item in settings.get('eq', {})]

        # fix a bad interaction between pedestal/dungeons goals and prize.crossWorld
        if options["goals"] in ['pedestal', 'dungeons']:
            settings['custom']['prize.crossWorld'] = True

    # If mc or mcs shuffle gets rolled, and its entrance, shift to either standard or full accordingly
    # mc and mcs are not supported by the entrance randomizer version currently used for v31.0.4.
    # If this changes, these statements will get removed.
    if options.get('entrances', 'none') != 'none':
        if options.get('dungeon_items', 'standard') == 'mc':
            options['dungeon_items'] = 'standard'
        elif options.get('dungeon_items', 'standard') == 'mcs':
            options['dungeon_items'] = 'full'

    # This if statement is dedicated to the survivors of http://www.speedrunslive.com/races/result/#!/264658
    # Play https://alttpr.com/en/h/30yAqZ99yV if you don't believe me. <3
    if options['weapons'] not in ['vanilla', 'assured'] and options['world_state'] == 'standard' and (
            options['enemy_shuffle'] != 'none'
            or options['enemy_damage'] != 'default'
            or options['enemy_health'] != 'default'):
        options['weapons'] = 'assured'

    # apply rules
    for rule in weights.get('rules', {}):
        conditions = rule.get('conditions', {})
        actions = rule.get('actions', {})

        # iterate through each condition
        match = True

        for condition in conditions:
            if condition.get('MatchType', 'exact') == 'exact':
                if options[condition['Key']] == condition['Value']:
                    continue
                else:
                    match = False

        if match:
            for key, value in actions.items():
                options[key] = get_random_option(value)

    settings["glitches"] = options["glitches"]
    settings["item_placement"] = options['item_placement']
    settings["dungeon_items"] = options['dungeon_items']
    settings["accessibility"] = options['accessibility']
    settings["goal"] = options['goals']
    settings["crystals"]["ganon"] = options['ganon_open']
    settings["crystals"]["tower"] = options['tower_open']
    settings["mode"] = options['world_state']
    settings["hints"] = options['hints']
    settings["weapons"] = options['weapons']
    settings["item"]["pool"] = options['item_pool']
    settings["item"]["functionality"] = options['item_functionality']
    settings["tournament"] = tournament
    settings["spoilers"] = spoilers
    settings["enemizer"]["boss_shuffle"] = options['boss_shuffle']
    settings["enemizer"]["enemy_shuffle"] = options['enemy_shuffle']
    settings["enemizer"]["enemy_damage"] = options['enemy_damage']
    settings["enemizer"]["enemy_health"] = options['enemy_health']
    settings["enemizer"]["pot_shuffle"] = options.get('pot_shuffle', 'off')
    settings["entrances"] = options['entrance_shuffle']
    settings["pseudoboots"] = options['pseudoboots']

    settings["allow_quickswap"] = get_random_option(weights.get('allow_quickswap', False))

    return settings, customizer


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
    if optset is None or optset == {}:
        return None
    try:
        return random.choices(population=[conv(key) for key in list(optset.keys())], weights=list(optset.values()))[0] if isinstance(optset, dict) else conv(optset)
    except TypeError as err:
        raise TypeError("There is a non-numeric value as a weight.") from err
