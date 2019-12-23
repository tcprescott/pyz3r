from .exceptions import alttprException
from . import patch, misc, spoiler
from .http import http


async def alttpr(
    settings=None,
    hash=None,
    randomizer='item',
    customizer=False,
    baseurl='https://alttpr.com',
    seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
    username=None,
    password=None,
):
    """Generates, or retrieves, an ALttPR game.

    Keyword Arguments:
        settings {dict} -- Dictionary of settings to use for generating a game. (default: {None})
        hash {str} -- The 10 character string that identifies an already generated game. (default: {None})
        randomizer {str} -- The randomizer to use for generating a game ('item' or 'entrance') (default: {'item'})
        baseurl {str} -- URL of the ALTTPR Website to use. (default: {'https://alttpr.com'})
        seed_baseurl {str} -- URL of the S3 bucket or web location that has already generated games. (default: {'https://s3.us-east-2.amazonaws.com/alttpr-patches'})
        username {str} -- A basic auth username (not typically needed) (default: {None})
        password {str} -- A basic auth password (not typically needed) (default: {None})

    Returns:
        [type] -- [description]
    """
    seed = alttprClass(settings=settings, hash=hash, randomizer=randomizer, customizer=customizer,
                       baseurl=baseurl, seed_baseurl=seed_baseurl, username=username, password=password, festive=False)
    await seed._init()
    return seed


class alttprClass():
    def __init__(
        self,
        settings=None,
        hash=None,
        randomizer=None,
        customizer=False,
        baseurl='https://alttpr.com',
        seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
        username=None,
        password=None,
        festive=False
    ):
        self.settings = settings
        self.hash = hash
        self.seed_baseurl = seed_baseurl
        self.baseurl = baseurl
        self.seed_baseurl = seed_baseurl
        self.customizer = customizer
        self.username = username
        self.password = password
        self.festive = festive

    async def _init(self):

        self.site = http(
            site_baseurl=self.baseurl,
            patch_baseurl=self.seed_baseurl,
            username=self.username,
            password=self.password,
        )

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
        import bs4

        text = await self.site.retrieve_url_raw_content(self.baseurl + '/daily', useauth=True)

        html = bs4.BeautifulSoup(text.decode('utf-8'), 'html5lib')
        return html.find('hashloader')['hash']

    async def code(self):
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
        baserom_settings = await self.site.retrieve_json("/base_rom/settings")
        req_patch = await self.site.retrieve_json(baserom_settings['base_file'])
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

        # expand the ROM to size requested in seed_data
        patchrom_array = patch.expand(
            patchrom_array, newlenmb=self.data['size'])

        # apply the base modifications
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=await self.get_patch_base()
        )

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
        sprites = await self.site.retrieve_json('/sprites')
        for sprite in sprites:
            if sprite['name'] == name:
                fileurl = sprite['file']
                break
        try:
            sprite = await self.site.retrieve_url_raw_content(fileurl, useauth=False)
        except BaseException:
            raise alttprException('Sprite \"{name}\" is not available.'.format(
                name=name
            ))
        spr = list(sprite)
        return spr

    def get_formatted_spoiler(self):
        return spoiler.create_filtered_spoiler(self)
