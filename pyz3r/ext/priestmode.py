###
# Originaly created by Hycutype
###


# Priestmode
# Triforce is in sanctuary chest, goal is to beat enemized escape
# quickswap is allowed
# thieves are killable
# the sewers key may be in the uncle passage
#
# bombs are guaranteed as drops in case the randomized weapon cannot kill the
# boomerang chest guard or the keyrat (gibdo or minihelmasaur)
#   * prize packs 4 & 7 are unmodified; they each have an 8bomb drop
#   * the second prize of all other packs is replaced with a 4bomb drop
#   * the _secondary_ crab prize is a 4bomb drop

# technical:
# goal is triforce-hunt, suggested by Synack
# prize packs are manually shuffled. Synack confirmed this is necessary with
#   custom packs
# it's smallkey shuffle, with every key besides the sewers key manually
#   placed. I guessed this would be least problematic for the customizer
# key in link's house shouldn't be possible, because once you collect the
#   uncle item you can't get back

# observations:
# I was worried the extra bombs would be too much, but it's possible they are
# actually inadequate; we'll see with more plays. I am tempted to mess with
# the item pool more, or do more manual placments to give a more even
# distribution across seeds in a batch (e.g. the uncle weapon, weighting for
# weapons that haven't been placed in earlier seeds)
import json
import random
# import urllib.request as request
# from threading import Thread
from copy import deepcopy
from math import factorial
from pyz3r.alttpr import alttprClass as alttpr

ORIG_SETTINGS = {
    "allow_quickswap": True,
    "glitches": "none",
    "item_placement": "advanced",
    "dungeon_items": "standard",
    "accessibility": "none",
    "goal": "triforce-hunt",
    "crystals": {
        "ganon": "7",
        "tower": "7"
    },
    "mode": "standard",
    "hints": "off",
    "weapons": "randomized",
    "item": {
        "pool": "normal",
        "functionality": "normal"
    },
    "tournament": True,
    "spoilers": "off",
    "lang": "en",
    "enemizer": {
        "boss_shuffle": "none",
        "enemy_shuffle": "shuffled",
        "enemy_damage": "default",
        "enemy_health": "default"
    },
    "name": "kiss-priest",
    "notes": "The Triforce is in sanc chest. THE KEY MAY BE IN THE UNCLE CHEST\n\nBombs are guaranteed as drops in case the uncle weapon can't kill the boomerang chest guard or keyrat. Packs 4 & 7 are unmodified (8-bombs). The second prize of all others is replaced with a 4-bomb. The second crab drop is a 4-bomb",
    "l": {
        "U2FuY3R1YXJ5OjE=": "Triforce:1",
        "RGVzZXJ0IFBhbGFjZSAtIFRvcmNoOjE=": "KeyP2:1",
        "VG93ZXIgb2YgSGVyYSAtIEJhc2VtZW50IENhZ2U6MQ==": "KeyP3:1",
        "Q2FzdGxlIFRvd2VyIC0gUm9vbSAwMzox": "KeyA1:1",
        "Q2FzdGxlIFRvd2VyIC0gRGFyayBNYXplOjE=": "KeyA1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gU2hvb3RlciBSb29tOjE=": "KeyD1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gVGhlIEFyZW5hIC0gTGVkZ2U6MQ==": "KeyD1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gVGhlIEFyZW5hIC0gQnJpZGdlOjE=": "KeyD1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gU3RhbGZvcyBCYXNlbWVudDox": "KeyD1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gRGFyayBCYXNlbWVudCAtIExlZnQ6MQ==": "KeyD1:1",
        "UGFsYWNlIG9mIERhcmtuZXNzIC0gRGFyayBCYXNlbWVudCAtIFJpZ2h0OjE=": "KeyD1:1",
        "U3dhbXAgUGFsYWNlIC0gRW50cmFuY2U6MQ==": "KeyD2:1",
        "U2t1bGwgV29vZHMgLSBCcmlkZ2UgUm9vbTox": "KeyD3:1",
        "U2t1bGwgV29vZHMgLSBQb3QgUHJpc29uOjE=": "KeyD3:1",
        "U2t1bGwgV29vZHMgLSBQaW5iYWxsIFJvb206MQ==": "KeyD3:1",
        "VGhpZXZlcycgVG93biAtIEFtYnVzaCBDaGVzdDox": "KeyD4:1",
        "SWNlIFBhbGFjZSAtIEZyZWV6b3IgQ2hlc3Q6MQ==": "KeyD5:1",
        "SWNlIFBhbGFjZSAtIEljZWQgVCBSb29tOjE=": "KeyD5:1",
        "TWlzZXJ5IE1pcmUgLSBNYWluIExvYmJ5OjE=": "KeyD6:1",
        "TWlzZXJ5IE1pcmUgLSBCcmlkZ2UgQ2hlc3Q6MQ==": "KeyD6:1",
        "TWlzZXJ5IE1pcmUgLSBTcGlrZSBDaGVzdDox": "KeyD6:1",
        "VHVydGxlIFJvY2sgLSBDaGFpbiBDaG9tcHM6MQ==": "KeyD7:1",
        "VHVydGxlIFJvY2sgLSBSb2xsZXIgUm9vbSAtIExlZnQ6MQ==": "KeyD7:1",
        "VHVydGxlIFJvY2sgLSBSb2xsZXIgUm9vbSAtIFJpZ2h0OjE=": "KeyD7:1",
        "VHVydGxlIFJvY2sgLSBCaWcgQ2hlc3Q6MQ==": "KeyD7:1",
        "R2Fub24ncyBUb3dlciAtIEJvYidzIFRvcmNoOjE=": "KeyA2:1",
        "R2Fub24ncyBUb3dlciAtIERNcyBSb29tIC0gVG9wIExlZnQ6MQ==": "KeyA2:1",
        "R2Fub24ncyBUb3dlciAtIERNcyBSb29tIC0gVG9wIFJpZ2h0OjE=": "KeyA2:1",
        "R2Fub24ncyBUb3dlciAtIERNcyBSb29tIC0gQm90dG9tIExlZnQ6MQ==": "KeyA2:1"
    },
    "eq": ["BossHeartContainer", "BossHeartContainer", "BossHeartContainer"],
    "drops": {
        "0": ["Heart", "BombRefill4", "Heart", "Heart", "RupeeGreen", "Heart", "Heart", "RupeeGreen"],
        "1": ["RupeeBlue", "BombRefill4", "RupeeBlue", "RupeeRed", "RupeeBlue", "RupeeGreen", "RupeeBlue", "RupeeBlue"],
        "2": ["MagicRefillFull", "BombRefill4", "MagicRefillSmall", "RupeeBlue", "MagicRefillFull", "MagicRefillSmall", "Heart", "MagicRefillSmall"],
        "3": ["BombRefill1", "BombRefill1", "BombRefill1", "BombRefill4", "BombRefill1", "BombRefill1", "BombRefill8", "BombRefill1"],
        "4": ["ArrowRefill5", "BombRefill4", "ArrowRefill5", "ArrowRefill10", "ArrowRefill5", "Heart", "ArrowRefill5", "ArrowRefill10"],
        "5": ["MagicRefillSmall", "BombRefill4", "Heart", "ArrowRefill5", "MagicRefillSmall", "BombRefill1", "RupeeGreen", "Heart"],
        "6": ["Heart", "Fairy", "MagicRefillFull", "RupeeRed", "BombRefill8", "Heart", "RupeeRed", "ArrowRefill10"],
        "pull": ["RupeeGreen", "RupeeGreen", "RupeeGreen"],
        "crab": ["auto_fill", "BombRefill4"],
        "stun": ["auto_fill"],
        "fish": ["RupeeGreen"]
    },
    "custom": {
        "item.Goal.Required": "",
        "item.require.Lamp": False,
        "item.value.BlueClock": "",
        "item.value.GreenClock": "",
        "item.value.RedClock": "",
        "item.value.Rupoor": "",
        "prize.crossWorld": True,
        "prize.shuffleCrystals": True,
        "prize.shufflePendants": True,
        "region.bossNormalLocation": True,
        "region.wildBigKeys": False,
        "region.wildCompasses": False,
        "region.wildKeys": True,
        "region.wildMaps": False,
        "rom.dungeonCount": "off",
        "rom.freeItemMenu": False,
        "rom.freeItemText": False,
        "rom.mapOnPickup": False,
        "rom.timerMode": "off",
        "rom.timerStart": "",
        "rom.rupeeBow": False,
        "rom.genericKeys": False,
        "rom.logicMode": "NoGlitches",
        "spoil.BootsLocation": False,
        "canBootsClip": False,
        "canBunnyRevive": False,
        "canBunnySurf": False,
        "canDungeonRevive": False,
        "canFakeFlipper": False,
        "canMirrorClip": False,
        "canMirrorWrap": False,
        "canOneFrameClipOW": False,
        "canOneFrameClipUW": False,
        "canOWYBA": False,
        "canSuperBunny": False,
        "canSuperSpeed": False,
        "canWaterWalk": False,
        "item": {
            "count": {
                "BottleWithRandom": 4,
                "Nothing": 0,
                "L1Sword": 0,
                "L1SwordAndShield": 0,
                "MasterSword": 0,
                "L3Sword": 0,
                "L4Sword": 0,
                "BlueShield": 0,
                "RedShield": 0,
                "MirrorShield": 0,
                "FireRod": 1,
                "IceRod": 1,
                "Hammer": 1,
                "Hookshot": 1,
                "Bow": 0,
                "Boomerang": 1,
                "Powder": 1,
                "Bombos": 1,
                "Ether": 1,
                "Quake": 1,
                "Lamp": 1,
                "Shovel": 1,
                "OcarinaInactive": 1,
                "CaneOfSomaria": 1,
                "Bottle": 0,
                "PieceOfHeart": 24,
                "CaneOfByrna": 1,
                "Cape": 1,
                "MagicMirror": 1,
                "PowerGlove": 0,
                "TitansMitt": 0,
                "BookOfMudora": 1,
                "Flippers": 1,
                "MoonPearl": 1,
                "BugCatchingNet": 1,
                "BlueMail": 0,
                "RedMail": 0,
                "Bomb": 0,
                "ThreeBombs": 16,
                "Mushroom": 1,
                "RedBoomerang": 1,

                "BottleWithGreenPotion": 0,
                "BottleWithBluePotion": 0,
                "TenBombs": 1,
                "OneRupee": 2,
                "FiveRupees": 4,
                "TwentyRupees": 27,
                "BowAndArrows": 0,
                "BowAndSilverArrows": 0,
                "BottleWithBee": 0,
                "BottleWithFairy": 0,
                "BossHeartContainer": 10,
                "HeartContainer": 1,
                "OneHundredRupees": 1,
                "FiftyRupees": 7,
                "Heart": 0,
                "Arrow": 1,
                "TenArrows": 12,
                "SmallMagic": 0,
                "ThreeHundredRupees": 5,
                "BottleWithGoldBee": 0,
                "OcarinaActive": 0,
                "PegasusBoots": 1,
                "BombUpgrade5": 0,
                "BombUpgrade10": 0,
                "ArrowUpgrade5": 0,
                "ArrowUpgrade10": 0,
                "HalfMagic": 1,
                "QuarterMagic": 0,
                "SilverArrowUpgrade": 0,
                "Rupoor": 0,
                "RedClock": 0,
                "BlueClock": 0,
                "GreenClock": 0,
                "ProgressiveSword": 4,
                "ProgressiveShield": 3,
                "ProgressiveArmor": 2,
                "ProgressiveGlove": 2,
                "ProgressiveBow": 2,
                "Triforce": 0,
                "TriforcePiece": 0,
                "MapA2": 1,
                "MapD7": 1,
                "MapD4": 1,
                "MapP3": 1,
                "MapD5": 1,
                "MapD3": 1,
                "MapD6": 1,
                "MapD1": 1,
                "MapD2": 1,
                "MapA1": 0,
                "MapP2": 1,
                "MapP1": 1,
                "MapH1": 0,
                "MapH2": 1,
                "CompassA2": 1,
                "CompassD7": 1,
                "CompassD4": 1,
                "CompassP3": 1,
                "CompassD5": 1,
                "CompassD3": 1,
                "CompassD6": 1,
                "CompassD1": 1,
                "CompassD2": 1,
                "CompassA1": 0,
                "CompassP2": 1,
                "CompassP1": 1,
                "CompassH1": 0,
                "CompassH2": 0,
                "BigKeyA2": 1,
                "BigKeyD7": 1,
                "BigKeyD4": 1,
                "BigKeyP3": 1,
                "BigKeyD5": 1,
                "BigKeyD3": 1,
                "BigKeyD6": 1,
                "BigKeyD1": 1,
                "BigKeyD2": 1,
                "BigKeyA1": 0,
                "BigKeyP2": 1,
                "BigKeyP1": 1,
                "BigKeyH1": 0,
                "BigKeyH2": 0,
                "KeyH2": 1,
                "KeyH1": 0,
                "KeyP1": 0,
                "KeyP2": 0,
                "KeyA1": 0,
                "KeyD2": 0,
                "KeyD1": 0,
                "KeyD6": 0,
                "KeyD3": 0,
                "KeyD5": 0,
                "KeyP3": 0,
                "KeyD4": 0,
                "KeyD7": 0,
                "KeyA2": 0
            }
        },
        "drop": {
            "count": {
                "Bee": 0,
                "BeeGood": 0,
                "Heart": 13,
                "RupeeGreen": 9,
                "RupeeBlue": 7,
                "RupeeRed": 6,
                "BombRefill1": 7,
                "BombRefill4": 1,
                "BombRefill8": 2,
                "MagicRefillSmall": 6,
                "MagicRefillFull": 3,
                "ArrowRefill5": 5,
                "ArrowRefill10": 3,
                "Fairy": 1
            }
        }
    }
}

UNCLE_LOCATION = "TGluaydzIFVuY2xlOjE="


async def create_priestmode(count, genclass=alttpr):
    name = 'kiss-priest-' + batch_code() + '-{:0>2d}'
    settings_lists = [None]*count
    uncle = uncle_weapons(count)

    for i in range(count):
        settings = deepcopy(ORIG_SETTINGS)
        randomize_drops(settings)
        settings["name"] = name.format(i+1)
        settings["l"][UNCLE_LOCATION] = uncle[i]
        settings["custom"]["item"]["count"][uncle[i]] -= 1
        settings_lists[i] = settings

    for i in range(count * 2 // 3, count):
        settings_lists[i]["custom"]["item"]["count"]["BossHeartContainer"] -= 6
        settings_lists[i]["custom"]["item"]["count"]["ProgressiveArmor"] -= 1
        settings_lists[i]["custom"]["item"]["count"]["ProgressiveSword"] -= 2
        settings_lists[i]["custom"]["item"]["count"]["PieceOfHeart"] += 9

    seeds = []
    for i, s in enumerate(settings_lists):
        seed = await genclass.create(settings=settings_lists[i], customizer=True)
        seeds.append(seed)

    return seeds

# TODO will return garbage on batch sizes > 24
# XXX ^ doesn't actually do that and I haven't look at it

# TODO reconsider how I was doing sword weights


def uncle_weapons(count):
    sword = "ProgressiveSword"
    weapons = [sword, "ProgressiveBow", "FireRod", "Hammer",
               "CaneOfByrna", "CaneOfSomaria", "TenBombs"]

    # sword_weights = [82951, 15651, 1329, 67, 2]
    # sword_weights = {count:sword_weights[count] for count in range(len(sword_weights))}
    # sword_count = select_weighted_key(sword_weights)

    weights = {weapons[i]: 8 for i in range(len(weapons))}
    weights[sword] = 1

    uncle = []
    for _ in range(count):
        w = select_weighted_key(weights)
        weights[w] //= 2
        uncle.append(w)

    # make the potential sword more likely earlier, I think
    uncle.reverse()

    return uncle


def select_weighted_key(d):
    total = sum(d.values())

    i = random.randrange(total)
    for key, weight in d.items():
        if i <= weight:
            return key
        i -= weight


def randomize_drops(settings):
    drops = settings["custom"]["drop"]["count"]
    total_drops = sum(drops.values())

    def random_drop():
        item = select_weighted_key(drops)
        drops[item] -= 1
        return item

    settings["drops"]["crab"][0] = random_drop()
    settings["drops"]["stun"][0] = random_drop()

    packs = [value for key, value in settings["drops"].items()
             if key in map(str, range(6))]
    random.shuffle(packs)

    # ensure an 8bomb in the gibdo pack in case of double gibdos
    if "BombRefill4" == packs[2][1]:
        packs[2][1] = "BombRefill8"

    for i in range(6):
        settings["drops"][str(i)] = packs[i]


def batch_code():
    def rand_char():
        return chr(random.randint(ord('A'), ord('Z')))

    return ''.join([rand_char() for _ in range(3)])
