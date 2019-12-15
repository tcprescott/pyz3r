import pyz3r
import asyncio
import json

import config

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))

async def generation_test(num):
    #generate a new game
    if num==1:
        seed = await pyz3r.alttpr(
            settings={
                "glitches": "none",
                "item_placement": "advanced",
                "dungeon_items": "standard",
                "accessibility": "items",
                "goal": "ganon",
                "crystals": {
                    "ganon": "random",
                    "tower": "4"
                },
                "mode": "open",
                "entrances": "none",
                "hints": "on",
                "weapons": "randomized",
                "item": {
                    "pool": "normal",
                    "functionality": "normal"
                },
                "tournament": True,
                "spoilers": "off",
                "lang":"en",
                "enemizer": {
                    "boss_shuffle":"none",
                    "enemy_shuffle":"none",
                    "enemy_damage":"default",
                    "enemy_health":"default"
                }
            }
        )
    elif num==2:
        website = await pyz3r.alttpr()
        dailyhash = await website.find_daily_hash()
        seed = await pyz3r.alttpr(hash=dailyhash)
    elif num==3:
        seed = await pyz3r.alttpr(
            hash='NYMrE8VG9d'
        )
    elif num==4:
        # generating a mystery game
        seed = await pyz3r.alttpr(
            settings=pyz3r.mystery.generate_random_settings(
                weights={
                    "glitches_required": {
                        "none": 100,
                        "overworld_glitches": 0,
                        "major_glitches": 0,
                        "no_logic": 0
                    },
                    "item_placement": {
                        "basic": 25,
                        "advanced": 75
                    },
                    "dungeon_items": {
                        "standard": 60,
                        "mc": 10,
                        "mcs": 10,
                        "full": 20
                    },
                    "accessibility": {
                        "items": 60,
                        "locations": 10,
                        "none": 30
                    },
                    "goals": {
                        "ganon": 40,
                        "fast_ganon": 20,
                        "dungeons": 10,
                        "pedestal": 20,
                        "triforce-hunt": 10
                    },
                    "tower_open": {
                        "0": 5,
                        "1": 5,
                        "2": 5,
                        "3": 5,
                        "4": 5,
                        "5": 5,
                        "6": 5,
                        "7": 50,
                        "random": 15
                    },
                    "ganon_open": {
                        "0": 5,
                        "1": 5,
                        "2": 5,
                        "3": 5,
                        "4": 5,
                        "5": 5,
                        "6": 5,
                        "7": 50,
                        "random": 15
                    },
                    "world_state": {
                        "standard": 35,
                        "open": 35,
                        "inverted": 20,
                        "retro": 10
                    },
                    "entrance_shuffle": {
                        "none": 60,
                        "simple": 7,
                        "restricted": 10,
                        "full": 10,
                        "crossed": 10,
                        "insanity": 2
                    },
                    "boss_shuffle": {
                        "none": 60,
                        "simple": 10,
                        "full": 10,
                        "random": 20
                    },
                    "enemy_shuffle": {
                        "none": 60,
                        "shuffled": 20,
                        "random": 20
                    },
                    "hints": {
                        "on": 50,
                        "off": 50
                    },
                    "weapons": {
                        "randomized": 40,
                        "assured": 40,
                        "vanilla": 15,
                        "swordless": 5
                    },
                    "item_pool": {
                        "normal": 80,
                        "hard": 15,
                        "expert": 5,
                        "crowd_control": 0
                    },
                    "item_functionality": {
                        "normal": 80,
                        "hard": 15,
                        "expert": 5
                    },
                    "enemy_damage": {
                        "default": 80,
                        "shuffled": 10,
                        "random": 10
                    },
                    "enemy_health": {
                        "default": 80,
                        "easy": 5,
                        "hard": 10,
                        "expert": 5
                    }
                }
            )
        )

    # print(json.dumps(await seed.customizer_settings(), indent=4))

    print("Permalink: {url}".format(
        url = seed.url
    ))
    print("Hash: [{hash}]".format(
        hash = ' | '.join(await seed.code())
    ))

    print(json.dumps(seed.get_formatted_spoiler()))

    # print(seed.data['spoiler'])

    jpn10rom = await pyz3r.rom.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

    patched_rom = await seed.create_patched_game(
        patchrom_array = jpn10rom,
        heartspeed='double', #can be off, quarter, half, double or normal.
        heartcolor='yellow', #can be red, 
        spritename='Cadence', #can be any sprite listed at https://alttpr.com/sprites
        music=True, # true or false, defaults true
        menu_speed="instant",
        quickswap=True
    )
    await pyz3r.rom.write(patched_rom, "outputs/patched_rom.sfc")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test(1))