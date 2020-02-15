from collections import OrderedDict
from . import misc

# creates an enhanced spoiler dictionary for spoiler log races

translation_map = {
    'BigKeyP1':  'EasternPalace_BigKey',
    'BigKeyP2':  'DesertPalace_BigKey',
    'BigKeyP3':  'TowerOfHera_BigKey',
    'BigKeyD1':  'PalaceOfDarkness_BigKey',
    'BigKeyD2':  'SwampPalace_BigKey',
    'BigKeyD3':  'SkullWoods_BigKey',
    'BigKeyD4':  'ThievesTown_BigKey',
    'BigKeyD5':  'IcePalace_BigKey',
    'BigKeyD6':  'MiseryMire_BigKey',
    'BigKeyD7':  'TurtleRock_BigKey',
    'BigKeyA2':  'GanonsTower_BigKey',
    'KeyH2':     'HyruleCastle_SmallKey',
    'KeyP2':     'DesertPalace_SmallKey',
    'KeyP3':     'TowerOfHera_SmallKey',
    'KeyA1':     'CastleTower_SmallKey',
    'KeyD1':     'PalaceOfDarkness_SmallKey',
    'KeyD2':     'SwampPalace_SmallKey',
    'KeyD3':     'SkullWoods_SmallKey',
    'KeyD4':     'ThievesTown_SmallKey',
    'KeyD5':     'IcePalace_SmallKey',
    'KeyD6':     'MiseryMire_SmallKey',
    'KeyD7':     'TurtleRock_SmallKey',
    'KeyA2':     'GanonsTower_SmallKey',
    'MapH2':     'HyruleCastle_Map',
    'MapP1':     'EasternPalace_Map',
    'MapP2':     'DesertPalace_Map',
    'MapP3':     'TowerOfHera_Map',
    'MapD1':     'PalaceOfDarkness_Map',
    'MapD2':     'SwampPalace_Map',
    'MapD3':     'SkullWoods_Map',
    'MapD4':     'ThievesTown_Map',
    'MapD5':     'IcePalace_Map',
    'MapD6':     'MiseryMire_Map',
    'MapD7':     'TurtleRock_Map',
    'MapA2':     'GanonsTower_Map',
    'CompassP1': 'EasternPalace_Compass',
    'CompassP2': 'DesertPalace_Compass',
    'CompassP3': 'TowerOfHera_Compass',
    'CompassD1': 'PalaceOfDarkness_Compass',
    'CompassD2': 'SwampPalace_Compass',
    'CompassD3': 'SkullWoods_Compass',
    'CompassD4': 'ThievesTown_Compass',
    'CompassD5': 'IcePalace_Compass',
    'CompassD6': 'MiseryMire_Compass',
    'CompassD7': 'TurtleRock_Compass',
    'CompassA2': 'GanonsTower_Compass',
}

def create_filtered_spoiler(seed, translate_dungeon_items=False):
    if not seed.data['spoiler']['meta'].get('spoilers') in ['on', 'generate']:
        return None

    spoiler = seed.data['spoiler']

    sorteddict = OrderedDict()

    if spoiler['meta'].get('shuffle', 'none') == 'none':
        sectionlist = [
            'Special',
            'Hyrule Castle',
            'Eastern Palace',
            'Desert Palace',
            'Castle Tower',
            'Tower Of Hera',
            'Dark Palace',
            'Swamp Palace',
            'Skull Woods',
            'Thieves Town',
            'Ice Palace',
            'Misery Mire',
            'Turtle Rock',
            'Ganons Tower',
            'Light World',
            'Death Mountain',
            'Dark World'
        ]
        prizemap = [
            ['Eastern Palace', 'Eastern Palace - Prize:1'],
            ['Desert Palace', 'Desert Palace - Prize:1'],
            ['Tower Of Hera', 'Tower of Hera - Prize:1'],
            ['Dark Palace', 'Palace of Darkness - Prize:1'],
            ['Swamp Palace', 'Swamp Palace - Prize:1'],
            ['Skull Woods', 'Skull Woods - Prize:1'],
            ['Thieves Town', 'Thieves\' Town - Prize:1'],
            ['Ice Palace', 'Ice Palace - Prize:1'],
            ['Misery Mire', 'Misery Mire - Prize:1'],
            ['Turtle Rock', 'Turtle Rock - Prize:1'],
        ]
    else:
        sectionlist = [
            'Special',
            'Hyrule Castle',
            'Eastern Palace',
            'Desert Palace',
            'Tower of Hera',
            'Agahnims Tower',
            'Palace of Darkness',
            'Swamp Palace',
            'Skull Woods',
            'Thieves Town',
            'Ice Palace',
            'Misery Mire',
            'Turtle Rock',
            'Ganons Tower',
            'Caves',
            'Light World',
            'Dark World'
        ]
        prizemap = [
            ['Eastern Palace', 'Eastern Palace - Prize'],
            ['Desert Palace', 'Desert Palace - Prize'],
            ['Tower of Hera', 'Tower of Hera - Prize'],
            ['Palace of Darkness', 'Palace of Darkness - Prize'],
            ['Swamp Palace', 'Swamp Palace - Prize'],
            ['Skull Woods', 'Skull Woods - Prize'],
            ['Thieves Town', 'Thieves\' Town - Prize'],
            ['Ice Palace', 'Ice Palace - Prize'],
            ['Misery Mire', 'Misery Mire - Prize'],
            ['Turtle Rock', 'Turtle Rock - Prize'],
        ]

    sorteddict['Prizes'] = {}
    for dungeon, prize in prizemap:
        try:
            sorteddict['Prizes'][dungeon] = spoiler[dungeon][prize].replace(
                ':1', '')
        except KeyError:
            continue

    for section in sectionlist:
        try:
            sorteddict[section] = mw_filter(spoiler[section])
            if translate_dungeon_items:
                for key, value in sorteddict[section].items():
                    if value in translation_map.keys():
                        sorteddict[section][key] = translation_map[value]
        except KeyError:
            continue

    drops = get_seed_prizepacks(seed.data)
    sorteddict['Drops'] = {}
    sorteddict['Drops']['PullTree'] = drops['PullTree']
    sorteddict['Drops']['RupeeCrab'] = {}
    sorteddict['Drops']['RupeeCrab']['Main'] = drops['RupeeCrab']['Main']
    sorteddict['Drops']['RupeeCrab']['Final'] = drops['RupeeCrab']['Final']
    sorteddict['Drops']['Stun'] = drops['Stun']
    sorteddict['Drops']['FishSave'] = drops['FishSave']

    sorteddict['Special']['DiggingGameDigs'] = misc.seek_patch_data(
        seed.data['patch'], 982421, 1)[0]

    if spoiler['meta'].get('mode', 'open') == 'retro':
        sorteddict['Shops'] = spoiler['Shops']

    if not spoiler['meta'].get('enemizer.boss_shuffle', 'none') == 'none':
        sorteddict['Bosses'] = mw_filter(spoiler['Bosses'])

    if not spoiler['meta'].get('shuffle', 'none') == 'none':
        sorteddict['Entrances'] = spoiler['Entrances']

    sorteddict['meta'] = spoiler['meta']
    sorteddict['meta']['hash'] = seed.hash
    sorteddict['meta']['permalink'] = seed.url

    for dungeon, prize in prizemap:
        del sorteddict[dungeon][prize.replace(':1', '')]

    return sorteddict


def get_seed_prizepacks(data):
    d = {}
    d['PullTree'] = {}
    d['RupeeCrab'] = {}

    stun_offset = '227731'
    pulltree_offset = '981972'
    rupeecrap_main_offset = '207304'
    rupeecrab_final_offset = '207300'
    fishsave_offset = '950988'

    for patch in data['patch']:
        if stun_offset in patch:
            d['Stun'] = get_sprite_droppable(patch[stun_offset][0])
        if pulltree_offset in patch:
            d['PullTree']['Tier1'] = get_sprite_droppable(
                patch[pulltree_offset][0])
            d['PullTree']['Tier2'] = get_sprite_droppable(
                patch[pulltree_offset][1])
            d['PullTree']['Tier3'] = get_sprite_droppable(
                patch[pulltree_offset][2])
        if rupeecrap_main_offset in patch:
            d['RupeeCrab']['Main'] = get_sprite_droppable(
                patch[rupeecrap_main_offset][0])
        if rupeecrab_final_offset in patch:
            d['RupeeCrab']['Final'] = get_sprite_droppable(
                patch[rupeecrab_final_offset][0])
        if fishsave_offset in patch:
            d['FishSave'] = get_sprite_droppable(patch[fishsave_offset][0])

    return d


def get_sprite_droppable(i):
    spritemap = {
        121: "Bee", 178: "BeeGood", 216: "Heart",
        217: "RupeeGreen", 218: "RupeeBlue", 219: "RupeeRed",
        220: "BombRefill1", 221: "BombRefill4", 222: "BombRefill8",
        223: "MagicRefillSmall", 224: "MagicRefillFull",
        225: "ArrowRefill5", 226: "ArrowRefill10",
        227: "Fairy",
    }
    try:
        return spritemap[i]
    except KeyError:
        return 'ERR: UNKNOWN'


def mw_filter(dict):
    sorteddict = {}
    for key, item in dict.items():
        sorteddict[key.replace(':1', '')] = dict[key].replace(':1', '')
    return sorteddict
