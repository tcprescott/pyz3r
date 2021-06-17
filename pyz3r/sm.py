import slugid
import uuid
import asyncio
import aiohttp
from . import exceptions

async def sm(
    settings=None,
    slug_id=None,
    guid_id=None,
    baseurl='https://samus.link',
    randomizer='sm',
    username=None,
    password=None,
):
    seed = smClass(
        settings=settings,
        slug_id=slug_id,
        guid_id=guid_id,
        baseurl=baseurl,
        randomizer=randomizer,
        username=username,
        password=password
    )
    await seed._init()
    return seed


class smClass():
    def __init__(
        self,
        settings,
        slug_id,
        guid_id,
        baseurl,
        randomizer,
        username,
        password,
    ):
        self.settings = settings
        self.slug_id = slug_id
        self.guid_id = guid_id
        self.baseurl = baseurl
        self.randomizer = randomizer
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(
            login=username, password=password) if username and password else None

    async def _init(self):
        if self.settings:
            self.endpoint = f'/api/randomizers/{self.randomizer}/generate'
            self.data = await self.generate_game()
            self.guid = uuid.UUID(hex=self.data['guid'])
            self.slug_id = slugid.encode(self.guid)
        elif self.slug_id:
            self.guid = slugid.decode(self.slug_id)
            self.data = await self.retrieve_game()
        elif self.guid_id:
            self.guid = uuid.UUID(hex=self.guid_id)
            self.slug_id = slugid.encode(self.guid)
            self.data = await self.retrieve_game()
        else:
            self.data = None
            self.slug_id = None
            self.guid = None

    async def generate_game(self):
        for i in range(0, 5):
            try:
                async with aiohttp.request(method='post', url=self.baseurl + self.endpoint, json=self.settings, auth=self.auth) as resp:
                    req = await resp.json()
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            # except aiohttp.ClientResponseError:
            #     continue
            return req
        raise exceptions.AlttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self):
        for i in range(0, 5):
            try:
                async with aiohttp.request(method='get', url=f'{self.baseurl}/api/seed/{self.guid.hex}') as resp:
                    patch = await resp.json()
            except aiohttp.ClientResponseError:
                await asyncio.sleep(5)
                continue
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            return patch
        raise exceptions.AlttprFailedToRetrieve(
            f'failed to retrieve game {self.slug_id}, the game is likely not found')

    @classmethod
    async def create(
        cls,
        settings=None,
        slug_id=None,
        guid_id=None,
        baseurl='https://samus.link',
        randomizer='sm',
        username=None,
        password=None,
    ):
        seed = cls(
            settings=settings,
            slug_id=slug_id,
            guid_id=guid_id,
            baseurl=baseurl,
            randomizer=randomizer,
            username=username,
            password=password
        )
        await seed._init()
        return seed

    async def randomizer_settings(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        async with aiohttp.request(method='get', url=f'{self.base_url}/api/randomizers/{self.randomizer}') as resp:
            settings = await resp.json()
        return settings

    @property
    def url(self):
        if self.data.get('mode', 'normal') == 'multiworld':
            return f'{self.baseurl}/multiworld/{self.slug_id}'
        return f'{self.baseurl}/seed/{self.slug_id}'

    @property
    def code(self):
        return self.data['hash']
