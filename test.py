import asyncio

import pyz3r


async def main():
    seed = await pyz3r.alttpr.create(
        hash_id = '7myk6wwgvQ'
    )

    await seed.create_patched_game(
        input_filename="input/japan1.0.sfc",
        output_filename="outputs/patched_rom.sfc",
        heartspeed='normal',
        heartcolor='red',
        spritename='Rainbow Link', #can be any sprite listed at https://alttpr.com/sprites
        music=False, # true or false, defaults true
        quickswap=False,
        menu_speed='normal'
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
