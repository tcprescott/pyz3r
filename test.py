import asyncio

import pyz3r


async def main():
    seed = await pyz3r.alttpr(
        hash_id = 'bYMNVZOKM0'
        # settings={
        #     "glitches": "none",
        #     "item_placement": "advanced",
        #     "dungeon_items": "standard",
        #     "accessibility": "items",
        #     "goal": "ganon",
        #     "crystals": {
        #         "ganon": "random",
        #         "tower": "4"
        #     },
        #     "mode": "open",
        #     "entrances": "none",
        #     "hints": "on",
        #     "weapons": "randomized",
        #     "item": {
        #         "pool": "normal",
        #         "functionality": "normal"
        #     },
        #     "tournament": True,
        #     "spoilers": "off",
        #     "lang":"en",
        #     "enemizer": {
        #         "boss_shuffle":"none",
        #         "enemy_shuffle":"none",
        #         "enemy_damage":"default",
        #         "enemy_health":"default"
        #     }
        # }
    )

    base_rom = await pyz3r.rom.read("input/japan1.0.sfc")
    patched_rom = await seed.create_patched_game(
        base_rom,  
        heartspeed='normal',
        heartcolor='red',
        spritename='Rainbow Link', #can be any sprite listed at https://alttpr.com/sprites
        music=False, # true or false, defaults true
        quickswap=False,
        menu_speed='normal'
    )
    await pyz3r.rom.write(patched_rom,'outputs/patched_rom.sfc')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
