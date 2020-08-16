from .exceptions import alttprException, alttprFailedToRetrieve, alttprFailedToGenerate
from . import misc, spoiler, patch
import aiohttp

# Use the "create" class method instead of this.  This is here for backwards compatibility and will be deprecated.


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
        self.customizer = customizer
        self.auth = aiohttp.BasicAuth(
            login=username, password=password) if username and password else None
        self.festive = festive

    async def _init(self):
        self.randomizer = 'alttpr'

        if self.customizer:
            self.endpoint = '/api/customizer'
        elif self.festive:
            self.endpoint = '/api/festive'
        else:
            self.endpoint = '/api/randomizer'

        if self.settings is None and self.hash is None:
            self.data = None
        else:
            if self.settings:
                self.data = await self.generate_game()
                self.hash = self.data['hash']
            else:
                self.data = await self.retrieve_game()

    async def generate_game(self):
        for i in range(0, 5):
            try:
                async with aiohttp.request(method='post', url=self.baseurl + self.endpoint, json=self.settings, auth=self.auth, raise_for_status=True) as resp:
                    req = await resp.json(content_type='text/html')
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            except aiohttp.ClientResponseError:
                continue
            return req
        raise alttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self):
        for i in range(0, 5):
            try:
                if self.seed_baseurl is not None:
                    async with aiohttp.request(method='get', url=self.seed_baseurl + '/' + self.hash + '.json') as resp:
                        patch = await resp.json()
                else:
                    async with aiohttp.request(method='get', url=self.baseurl + '/hash/' + self.hash, auth=self.auth, raise_for_status=True) as resp:
                        patch = await resp.json(content_type='text/html')
            except aiohttp.ClientResponseError:
                async with aiohttp.request(method='get', url=self.baseurl + '/hash/' + self.hash, auth=self.auth, raise_for_status=True) as resp:
                    patch = await resp.json(content_type='text/html')
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            return patch
        raise alttprFailedToRetrieve(
            f'failed to retrieve game {self.hash}, the game is likely not found')

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
        async with aiohttp.request(method='get', url=self.baseurl + '/randomizer/settings', auth=self.auth, raise_for_status=True) as resp:
            settings = await resp.json()
        return settings

    async def customizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        async with aiohttp.request(method='get', url=self.baseurl + '/customizer/settings', auth=self.auth, raise_for_status=True) as resp:
            settings = await resp.json()
        return settings

    async def find_daily_hash(self):
        async with aiohttp.request(method='get', url=f'{self.baseurl}/api/daily', auth=self.auth, raise_for_status=True) as resp:
            daily = await resp.json()
        return daily['hash']

    @property
    def url(self):
        return f'{self.baseurl}/h/{self.hash}'

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

    async def get_patch_base(self):
        """Gets the base_rom from the website.  This is the first set of patches that must be applied to the ROM.

        Returns:
            list -- a list of dictionaries that represent a rom patch
        """
        async with aiohttp.request(method='get', url=self.baseurl + '/base_rom/settings', auth=self.auth, raise_for_status=True) as resp:
            baserom_settings = await resp.json()
        async with aiohttp.request(method='get', url=self.baseurl + baserom_settings['base_file'], auth=self.auth, raise_for_status=True) as resp:
            req_patch = await resp.read()
        return req_patch

    async def create_patched_game(
        self,
        patchrom_array,
        heartspeed='half',
        heartcolor='red',
        quickswap=False,
        menu_speed='normal',
        spritename='Link',
        music=True
    ):
        """Creates a list of bytes depicting a fully patched A Link to the Past Randomizer rom.

        Arguments:
            patchrom_array {list} -- a list of dictionaries that represent a Japan 1.0 ROM of A Link to the Past.

        Keyword Arguments:
            heartspeed {str} -- Chose the speed at which the low health warning beeps.
                Options are 'off', 'double', 'normal', 'half', and 'quarter'. (default: {'half'})
            color {str} -- The heart color.  Options are 'red', 'blue', 'green', and 'yellow' (default: {'red'})
            spritename {str} -- The name of the sprite, as shown on https://alttpr.com/en/sprite_preview (default: {'Link'})
            music {bool} -- If true, music is enabled.  If false, the music id disabled. (default: {True})

        Raises:
            alttprException -- Raised if no game has been generated or retrieved.

        Returns:
            list -- a list of bytes depecting a fully patched ALTTPR game
        """
        if not self.data:
            raise alttprException(
                'Please specify a seed or hash first to generate or retrieve a game.')

        # apply the base modifications
        patchrom_array = patch.apply_bps(
            rom=patchrom_array,
            patches=await self.get_patch_base()
        )

        # expand the ROM to size requested in seed_data
        patchrom_array = patch.expand(
            patchrom_array, newlenmb=self.data['size'])

        # apply the seed-specific changes
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=self.data['patch']
        )

        # apply the heart speed change
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.heart_speed(heartspeed)
        )

        # apply the heart color change
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.heart_color(heartcolor)
        )

        # apply menu speed
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.menu_speed(menu_speed)
        )

        # apply quickswap
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.quickswap(quickswap)
        )

        # apply the sprite
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.sprite(
                spr=await self.get_sprite(spritename)
            )
        )

        # apply the sprite
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.music(music=music)
        )

        # calculate the SNES checksum and apply it to the ROM
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.checksum(patchrom_array)
        )

        return patchrom_array

    async def get_sprite(self, name):
        """Retrieve the ZSPR file for the named sprite.

        Arguments:
            name {str} -- The name of the sprite, as listed at https://alttpr.com/en/sprite_preview

        Raises:
            alttprException -- Raised if no game has been generated or retrieved.

        Returns:
            list -- a list of bytes depicting a SPR or ZSPR file
        """
        async with aiohttp.request(method='get', url=self.baseurl + '/sprites', auth=self.auth, raise_for_status=True) as resp:
            sprites = await resp.json()
        try:
            spriteinfo = next(
                (sprite for sprite in sprites if sprite["name"] == name))
        except StopIteration:
            raise alttprException(
                f"Sprite {name} does not exist on {self.base_url}.")
        try:
            async with aiohttp.request(method='get', url=spriteinfo["file"], raise_for_status=True) as resp:
                spritedata = await resp.read()
        except Exception as e:
            raise alttprException(
                f'Sprite "{name}" could not be downloaded.') from e
        spr = list(spritedata)
        return spr

    def get_formatted_spoiler(self, translate_dungeon_items=False):
        return spoiler.create_filtered_spoiler(self, translate_dungeon_items)
