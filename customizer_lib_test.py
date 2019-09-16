import json
from pyz3r import alttpr, romfile
from pyz3r.customizer import customizer

import asyncio

import config

async def generation_test():
    f = open('input/customizer-settings.json', "r")
    customizer_settings = json.loads(f.read())
    f.close()

    settings = customizer.convert2settings(customizer_settings, tournament=False)

    with open('outputs/actual_output.json', 'w+') as w:
        w.write(json.dumps(settings, indent=4))

    seed = await alttpr(
        customizer=True,
        baseurl=config.baseurl,
        seed_baseurl=config.seed_baseurl,
        username=config.username,
        password=config.password,
        settings=settings
    )

    print("Permalink: {url}".format(
        url = seed.url
    ))
    print("Hash: [{hash}]".format(
        hash = ' | '.join(await seed.code())
    ))

    # jpn10rom = await romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

    # patched_rom = await seed.create_patched_game(
    #     patchrom_array = jpn10rom,  
    #     heartspeed=None, #can be off, quarter, half, double or normal.
    #     heartcolor='red', #can be red, 
    #     spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
    #     music=False # true or false, defaults true
    #     )
    # await romfile.write(patched_rom, "outputs/patched_rom.sfc")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test())