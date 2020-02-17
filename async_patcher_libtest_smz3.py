import asyncio

import pyz3r

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))


async def generation_test():
    # seed = await pyz3r.sm(
    #     randomizer='sm',
    #     settings={
    #         "logic": "Tournament",
    #         "goal": "defeatmb",
    #         "placement": "split",
    #         "seed": "",
    #         "race": "true",
    #         "gamemode": "normal"
    #     }
    # )
    # seed = await pyz3r.sm(
    #     randomizer='smz3',
    #     settings={
    #         "logic": "Hard",
    #         "goal": "defeatboth",
    #         "seed": "",
    #         "race": "true",
    #         "gamemode": "normal"
    #     }
    # )
    seed = await pyz3r.sm(
        guid_id='74a221fcff63453e8afe05a3d68c0f68'
    )
    # preset = 'hard'
    # seed = await pyz3r.smz3(
    #     settings={
    #         'logic': 'NoMajorGlitches',
    #         'sm_logic': 'Casual' if preset == 'normal' else 'Tournament',
    #         'difficulty': 'normal',
    #         'variation': 'combo',
    #         'mode': 'open',
    #         'goal': 'ganon',
    #         'weapons': '',
    #         'morph': 'randomized',  # or vanilla
    #         'heart_speed': 'half',
    #         'sram_trace': 'false',
    #         'menu_speed': 'normal',
    #         'debug': False,
    #         'tournament': True  # or False
    #     }
    # )


    print(f"Permalink: {seed.url}")
    print(f'Guid: {seed.guid.hex}')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test())
