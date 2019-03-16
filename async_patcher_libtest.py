import pyz3r
import asyncio

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))

async def generation_test(num):
    #generate a new game
    if num==1:
        seed = await pyz3r.async_alttpr(
            randomizer='item', # optional, defaults to item
            settings={
                "difficulty": "hard",
                "enemizer": False,
                "logic": "NoGlitches",
                "mode": "open",
                "spoilers": False,
                "tournament": True,
                "variation": "key-sanity",
                "weapons": "uncle",
                "lang": "en"
            }
        )
    #generate an entrance shuffle game
    elif num==2:
        seed = await pyz3r.async_alttpr(
            randomizer='entrance',
            settings={
                "logic":"NoGlitches",
                "difficulty":"normal",
                "variation":"retro",
                "mode":"open",
                "goal":"ganon",
                "shuffle":"restricted",
                "tournament":True,
                "spoilers":False,
                "enemizer":{
                    "bosses":"off",
                    "pot_shuffle":False,
                    "enemy_damage":"off",
                    "palette_shuffle":False,
                    "enemy_health":0,
                    "enemy":False
                },
                "lang":"en"
            }
        )
    elif num==3:
        seed = await pyz3r.async_alttpr(
            randomizer='item',
            hash='zDvxWLLEMa'
        )


    print("Permalink: {url}".format(
        url = seed.url
    ))
    print("Hash: [{hash}]".format(
        hash = ' | '.join(await seed.code())
    ))

    print(seed.data['spoiler'])

    jpn10rom = await pyz3r.async_romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

    patched_rom = await seed.create_patched_game(
        patchrom_array = jpn10rom,  
        heartspeed=None, #can be off, quarter, half, double or normal.
        heartcolor='red', #can be red, 
        spritename='Negative Link', #can be any sprite listed at https://alttpr.com/sprites
        music=False # true or false, defaults true
        )
    await pyz3r.async_romfile.write(patched_rom, "outputs/patched_rom.sfc")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test(2))