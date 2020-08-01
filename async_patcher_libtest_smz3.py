import asyncio
from pyz3r.smvaria import SuperMetroidVaria

async def gen():
    seed = await SuperMetroidVaria.create(
        skills_preset='regular',
        settings_preset='default'
    )
    print(seed.url)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generation_test())
