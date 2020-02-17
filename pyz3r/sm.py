from . import http
import slugid
import uuid


async def sm(
    settings=None,
    slug_id=None,
    guid_id=None,
    baseurl='https://beta.samus.link',
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

    async def _init(self):
        self.site = http.site(
            site_baseurl=self.baseurl,
            username=self.username,
            password=self.password,
        )

        if self.settings:
            endpoint = f'/api/randomizers/{self.randomizer}/generate'
            self.data = await self.site.generate_game(endpoint, self.settings)
            self.guid = uuid.UUID(hex=self.data['guid'])
            self.slug_id = slugid.encode(self.guid)
        elif self.slug_id:
            self.guid = slugid.decode(self.slug_id)
            self.data = await http.request_generic(
                url=f'{self.baseurl}/api/seed/{self.guid.hex}',
                method='get',
                returntype='json'
            )
        elif self.guid_id:
            self.guid = uuid.UUID(hex=self.guid_id)
            self.slug_id = slugid.encode(self.guid)
            self.data = await http.request_generic(
                url=f'{self.baseurl}/api/seed/{self.guid.hex}',
                method='get',
                returntype='json'
            )
        else:
            self.data = None
            self.slug_id = None
            self.guid = None

        self.url = f'{self.baseurl}/seed/{self.slug_id}'

    async def randomizer_settings(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        return await http.request_generic(
            url=f'/api/randomizers/{self.randomizer}',
            method='get',
            returntype='json'
        )

