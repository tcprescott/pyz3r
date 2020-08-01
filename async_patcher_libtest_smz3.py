import asyncio

from pyz3r.smvaria import SuperMetroidVaria

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))


async def generation_test():
    seed = await SuperMetroidVaria.create(
        skills_preset='regular',
        settings_preset='quite_random',
        baseurl='https://variabeta.pythonanywhere.com'
    )
    print(seed.url)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test())
