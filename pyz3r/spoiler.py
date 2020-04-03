from collections import OrderedDict
from . import misc

# creates an enhanced spoiler dictionary for spoiler log races

translation = {
    'BigKeyP1':  'BigKeyP1-EasternPalace',
    'BigKeyP2':  'BigKeyP2-DesertPalace',
    'BigKeyP3':  'BigKeyP3-TowerOfHera',
    'BigKeyD1':  'BigKeyD1-PalaceOfDarkness',
    'BigKeyD2':  'BigKeyD2-SwampPalace',
    'BigKeyD3':  'BigKeyD3-SkullWoods',
    'BigKeyD4':  'BigKeyD4-ThievesTown',
    'BigKeyD5':  'BigKeyD5-IcePalace',
    'BigKeyD6':  'BigKeyD6-MiseryMire',
    'BigKeyD7':  'BigKeyD7-TurtleRock',
    'BigKeyA2':  'BigKeyA2-GanonsTower',
    'KeyH2':     'KeyH2-HyruleCastle',
    'KeyP2':     'KeyP2-DesertPalace',
    'KeyP3':     'KeyP3-TowerOfHera',
    'KeyA1':     'KeyA1-CastleTower',
    'KeyD1':     'KeyD1-PalaceOfDarkness',
    'KeyD2':     'KeyD2-SwampPalace',
    'KeyD3':     'KeyD3-SkullWoods',
    'KeyD4':     'KeyD4-ThievesTown',
    'KeyD5':     'KeyD5-IcePalace',
    'KeyD6':     'KeyD6-MiseryMire',
    'KeyD7':     'KeyD7-TurtleRock',
    'KeyA2':     'KeyA2-GanonsTower',
    'MapH2':     'MapH2-HyruleCastle',
    'MapP1':     'MapP1-EasternPalace',
    'MapP2':     'MapP2-DesertPalace',
    'MapP3':     'MapP3-TowerOfHera',
    'MapD1':     'MapD1-PalaceOfDarkness',
    'MapD2':     'MapD2-SwampPalace',
    'MapD3':     'MapD3-SkullWoods',
    'MapD4':     'MapD4-ThievesTown',
    'MapD5':     'MapD5-IcePalace',
    'MapD6':     'MapD6-MiseryMire',
    'MapD7':     'MapD7-TurtleRock',
    'MapA2':     'MapA2-GanonsTower',
    'CompassP1': 'CompassP1-EasternPalace',
    'CompassP2': 'CompassP2-DesertPalace',
    'CompassP3': 'CompassP3-TowerOfHera',
    'CompassD1': 'CompassD1-PalaceOfDarkness',
    'CompassD2': 'CompassD2-SwampPalace',
    'CompassD3': 'CompassD3-SkullWoods',
    'CompassD4': 'CompassD4-ThievesTown',
    'CompassD5': 'CompassD5-IcePalace',
    'CompassD6': 'CompassD6-MiseryMire',
    'CompassD7': 'CompassD7-TurtleRock',
    'CompassA2': 'CompassA2-GanonsTower',
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
            'Tower Of Hera',
            'Castle Tower',
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
                    if value in translation.keys():
                        sorteddict[section][key] = translation[value]
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
