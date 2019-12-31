import asyncio

import pyz3r

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))


async def generation_test():
    preset = 'hard'
    seed = await pyz3r.smz3(
        settings={
            'logic': 'NoMajorGlitches',
            'sm_logic': 'Casual' if preset == 'normal' else 'Tournament',
            'difficulty': 'normal',
            'variation': 'combo',
            'mode': 'open',
            'goal': 'ganon',
            'weapons': '',
            'morph': 'randomized',  # or vanilla
            'heart_speed': 'half',
            'sram_trace': 'false',
            'menu_speed': 'normal',
            'debug': False,
            'tournament': True  # or False
        }
    )

    print("Permalink: {url}".format(
        url=seed.url
    ))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test())
