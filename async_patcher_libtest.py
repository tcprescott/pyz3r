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
            baseurl=config.baseurl,
            seed_baseurl=config.seed_baseurl,
            username=config.username,
            password=config.password,
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
                "spoilers_ongen": True,
                "lang":"en",
                "enemizer": {
                    "boss_shuffle":"none",
                    "enemy_shuffle":"none",
                    "enemy_damage":"normal",
                    "enemy_health":"normal"
                }
            }
        )
    elif num==3:
        seed = await pyz3r.alttpr(
            baseurl=config.baseurl,
            seed_baseurl=config.seed_baseurl,
            username=config.username,
            password=config.password,
            hash='ObGbbxeGPL'
        )

    # print(json.dumps(await seed.customizer_settings(), indent=4))

    print("Permalink: {url}".format(
        url = seed.url
    ))
    print("Hash: [{hash}]".format(
        hash = ' | '.join(await seed.code())
    ))

    # print(seed.data['spoiler'])

    # jpn10rom = await pyz3r.async_romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

    # patched_rom = await seed.create_patched_game(
    #     patchrom_array = jpn10rom,  
    #     heartspeed=None, #can be off, quarter, half, double or normal.
    #     heartcolor='red', #can be red, 
    #     spritename='Negative Link', #can be any sprite listed at https://alttpr.com/sprites
    #     music=False # true or false, defaults true
    #     )
    # await pyz3r.async_romfile.write(patched_rom, "outputs/patched_rom.sfc")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test(3))