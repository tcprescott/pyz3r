from .exceptions import alttprException
from . import misc, spoiler
from . import http

async def alttpr(
    settings=None,
    hash_id=None,
    randomizer='item',
    customizer=False,
    baseurl='https://alttpr.com',
    seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
    username=None,
    password=None,
):
    seed = alttprClass(settings=settings, hash_id=hash_id, randomizer=randomizer, customizer=customizer,
                       baseurl=baseurl, seed_baseurl=seed_baseurl, username=username, password=password, festive=False)
    await seed._init()
    return seed

class alttprClass():
    def __init__(
        self,
        settings=None,
        hash_id=None,
        randomizer=None,
        customizer=False,
        baseurl='https://alttpr.com',
        seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
        username=None,
        password=None,
        festive=False
    ):
        self.settings = settings
        self.hash = hash_id
        self.seed_baseurl = seed_baseurl
        self.baseurl = baseurl
        self.seed_baseurl = seed_baseurl
        self.customizer = customizer
        self.username = username
        self.password = password
        self.festive = festive

    async def _init(self):
        self.site = http.site(
            site_baseurl=self.baseurl,
            patch_baseurl=self.seed_baseurl,
            username=self.username,
            password=self.password,
        )

        self.randomizer = 'alttpr'

        if self.customizer:
            endpoint = '/api/customizer'
        elif self.festive:
            endpoint = '/api/festive'
        else:
            endpoint = '/api/randomizer'

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

    @classmethod
    async def create(
        cls,
        settings=None,
        hash_id=None,
        randomizer='item',
        customizer=False,
        baseurl='https://alttpr.com',
        seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
        username=None,
        password=None,
    ):
        seed = cls(settings=settings, hash_id=hash_id, randomizer=randomizer, customizer=customizer,
                        baseurl=baseurl, seed_baseurl=seed_baseurl, username=username, password=password, festive=False)
        await seed._init()
        return seed

    async def randomizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        return await self.site.retrieve_json('/randomizer/settings')

    async def customizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        return await self.site.retrieve_json('/customizer/settings')

    async def find_daily_hash(self):
        daily = await http.request_generic(f'{self.baseurl}/api/daily', returntype='json')
        return daily['hash']

    @property
    def code(self):
        """An list of strings that represents the

        Raises:
            alttprException -- Raised if no game has been generated or retrieved.

        Returns:
            list -- List of strings depicting the code on the in-game file select screen.
        """
        if not self.data:
            raise alttprException(
                'Please specify a seed or hash first to generate or retrieve a game.')

        code_map = {
            0: 'Bow', 1: 'Boomerang', 2: 'Hookshot', 3: 'Bombs',
            4: 'Mushroom', 5: 'Magic Powder', 6: 'Ice Rod', 7: 'Pendant',
            8: 'Bombos', 9: 'Ether', 10: 'Quake', 11: 'Lamp',
            12: 'Hammer', 13: 'Shovel', 14: 'Flute', 15: 'Bugnet', 16: 'Book',
            17: 'Empty Bottle', 18: 'Green Potion', 19: 'Somaria', 20: 'Cape',
            21: 'Mirror', 22: 'Boots', 23: 'Gloves', 24: 'Flippers',
            25: 'Moon Pearl', 26: 'Shield', 27: 'Tunic', 28: 'Heart',
            29: 'Map', 30: 'Compass', 31: 'Big Key'
        }

        codebytes = misc.seek_patch_data(self.data['patch'], 1573397, 5)
        if len(codebytes) != 5:
            return ["Bow", "Boomerang", "Hookshot", "Bombs", "Mushroom"]
        else:
            p = list(map(lambda x: code_map[x], codebytes))
            return [p[0], p[1], p[2], p[3], p[4]]

    def get_formatted_spoiler(self, translate_dungeon_items=False):
        return spoiler.create_filtered_spoiler(self, translate_dungeon_items)
