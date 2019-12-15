from .exceptions import alttprException
from .http import http


async def smz3(
    settings=None,
    hash=None,
    baseurl='https://samus.link',
    username=None,
    password=None,
):
    """Generates, or retrieves, an ALttPR game.

    Keyword Arguments:
        settings {dict} -- Dictionary of settings to use for generating a game. (default: {None})
        hash {str} -- The 10 character string that identifies an already generated game. (default: {None})
        baseurl {str} -- URL of the ALTTPR Website to use. (default: {'https://alttpr.com'})
        username {str} -- A basic auth username (not typically needed) (default: {None})
        password {str} -- A basic auth password (not typically needed) (default: {None})

    Returns:
        [type] -- [description]
    """
    seed = smz3Class(settings, hash, baseurl, username, password)
    await seed._init()
    return seed


class smz3Class():
    def __init__(
        self,
        settings=None,
        hash=None,
        baseurl='https://samus.link',
        username=None,
        password=None,
    ):
        self.settings = settings
        self.hash = hash
        self.baseurl = baseurl
        self.username = username
        self.password = password

    async def _init(self):
        self.site = http(
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

