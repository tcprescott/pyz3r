from .exceptions import alttprException
from . import http


async def smz3(
    settings=None,
    hash_id=None,
    baseurl='https://samus.link',
    username=None,
    password=None,
):
    seed = smz3Class(settings, hash_id, baseurl, username, password)
    await seed._init()
    return seed


class smz3Class():
    def __init__(
        self,
        settings=None,
        hash_id=None,
        baseurl='https://samus.link',
        username=None,
        password=None,
    ):
        self.settings = settings
        self.hash = hash_id
        self.baseurl = baseurl
        self.username = username
        self.password = password

    async def _init(self):
        self.site = http.site(
            site_baseurl=self.baseurl,
            username=self.username,
            password=self.password,
        )

        endpoint = '/seed'

        if self.settings is None and self.hash is None:
            self.data = None
        else:
            if self.settings:
                self.data = await self.site.generate_game(endpoint, self.settings)
                self.hash = self.data['hash']
            else:
                self.data = await self.site.retrieve_game(self.hash)

            self.url = '{baseurl}/h/{hash}'.format(
                baseurl=self.baseurl,
                hash=self.hash
            )

    async def randomizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        return await self.site.retrieve_json('/randomizer/settings')

