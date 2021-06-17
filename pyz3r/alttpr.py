from .exceptions import Pyz3rException, AlttprFailedToRetrieve, AlttprFailedToGenerate
from . import misc, spoiler
from .rom import Rom
import aiohttp
import logging
import tempfile
import os
from pathlib import Path

from pyz3r import rom

class alttpr():
    def __init__(
        self,
        settings=None,
        hash_id=None,
        baseurl='https://alttpr.com',
        endpoint='/api/randomizer',
        username=None,
        password=None,
    ):
        self.settings = settings
        self.hash = hash_id
        self.baseurl = baseurl
        self.endpoint = endpoint
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None
        self.http = aiohttp.ClientSession(raise_for_status=True)

    @classmethod
    async def create(
        cls,
        settings=None,
        hash_id=None,
        baseurl='https://alttpr.com',
        endpoint='/api/randomizer',
        username=None,
        password=None,
    ):
        seed = cls(settings=settings, hash_id=hash_id, baseurl=baseurl, endpoint=endpoint, username=username, password=password)

        if seed.settings is None and seed.hash is None:
            seed.data = None
            return

        if seed.settings:
            seed.data = await seed.generate_game()
            seed.hash = seed.data['hash']
        else:
            seed.data = await seed.retrieve_game()

        return seed

    async def generate_game(self):
        for i in range(0, 5):
            try:
                async with self.http.post(url=self.uri(self.endpoint), json=self.settings, auth=self.auth) as resp:
                    req = await resp.json()
            except aiohttp.client_exceptions.ServerDisconnectedError:
                logging.exception("Unable to generate game.")
                continue
            except aiohttp.ClientResponseError:
                logging.exception("Unable to generate game.")
                continue
            return req
        raise AlttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self):
        for i in range(0, 5):
            try:
                async with self.http.get(url=self.uri('/hash/' + self.hash), auth=self.auth) as resp:
                    patch = await resp.json(content_type="text/html")
            except aiohttp.ClientResponseError:
                logging.exception("Unable to retrieve game.")
                continue
            except aiohttp.client_exceptions.ServerDisconnectedError:
                logging.exception("Unable to retrieve game.")
                continue
            return patch
        raise AlttprFailedToRetrieve(
            f'failed to retrieve game {self.hash}, the game is likely not found')


    async def randomizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        async with self.http.get(url=self.baseurl + '/randomizer/settings', auth=self.auth) as resp:
            settings = await resp.json()
        return settings

    async def customizer_settings(self):
        """Returns a dictonary of valid settings, based on the randomizer in use (item or entrance).

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        async with self.http.get(url=self.baseurl + '/customizer/settings', auth=self.auth) as resp:
            settings = await resp.json()
        return settings

    async def find_daily_hash(self):
        async with self.http.get(url=f'{self.baseurl}/api/daily', auth=self.auth) as resp:
            daily = await resp.json()
        return daily['hash']

    @property
    def url(self):
        return f'{self.baseurl}/h/{self.hash}'

    @property
    def code(self):
        """An list of strings that represents the

        Raises:
            Pyz3rException -- Raised if no game has been generated or retrieved.

        Returns:
            list -- List of strings depicting the code on the in-game file select screen.
        """
        if not self.data:
            raise Pyz3rException('Please specify a seed or hash first to generate or retrieve a game.')

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
        Caches BPS files in the system's temp directory (/tmp/pyz3r/bps on *nix systems).

        Returns:
            bytes -- a bytes-like object representing a BPS patch
        """
        async with self.http.get(url=self.uri("/api/h/" + self.hash), auth=self.auth) as resp:
            seed_settings = await resp.json()

        cachedbpstmp = os.path.join(tempfile.gettempdir(), "pyz3r", "bps")
        cachedbpsfile = os.path.join(cachedbpstmp, f"{seed_settings['md5']}.bps")
        try:
            Path(cachedbpstmp).mkdir(parents=True, exist_ok=True)
            with open(cachedbpsfile, "rb") as f:
                req_patch = f.read()
        except (FileNotFoundError, PermissionError):
            async with self.http.get(url=self.baseurl + seed_settings['bpsLocation'], auth=self.auth) as resp:
                req_patch = await resp.read()

            try:
                with open(cachedbpsfile, "wb") as f:
                    f.write(req_patch)
            except PermissionError:
                logging.exception("Unable to cache BPS file.")

        return req_patch

    async def create_patched_game(
        self,
        input_filename,
        output_filename=None,
        heartspeed='half',
        heartcolor='red',
        quickswap=False,
        menu_speed='normal',
        spritename='Link',
        music=True) -> Rom:
        if not self.data:
            raise Pyz3rException('Please specify a seed or hash first to generate or retrieve a game.')

        self.rom = Rom()
        self.rom.read(input_filename)

        self.rom.apply_bps_patch(patch=await self.get_patch_base())

        # expand the ROM to size requested in seed_data
        if self.data['size'] > 2:
            self.rom.expand(newlenmb=self.data['size'])

        # apply the seed-specific changes
        self.rom.apply_dict_patches(patches=self.data['patch'])

        # apply the heart speed change
        self.rom.heart_speed(heartspeed)

        # apply the heart color change
        self.rom.heart_color(heartcolor)

        # apply menu speed
        self.rom.menu_speed(menu_speed)

        # apply quickswap
        self.rom.quickswap(quickswap)

        if spritename != "Link":
            # apply the sprite
            self.rom.sprite(zspr=await self.get_sprite(spritename))

        # apply the sprite
        self.rom.music(music=music)

        # calculate the SNES checksum and apply it to the ROM
        self.rom.checksum()

        if output_filename is not None:
            self.rom.write_to_file(output_filename)

        return self.rom

    async def get_sprite(self, name):
        """Retrieve the ZSPR file for the named sprite.

        Arguments:
            name {str} -- The name of the sprite, as listed at https://alttpr.com/en/sprite_preview

        Raises:
            Pyz3rException -- Raised if no game has been generated or retrieved.

        Returns:
            list -- a list of bytes depicting a SPR or ZSPR file
        """
        async with self.http.get(url=self.baseurl + '/sprites', auth=self.auth) as resp:
            sprites = await resp.json()
        try:
            spriteinfo = next(
                (sprite for sprite in sprites if sprite["name"] == name))
        except StopIteration:
            raise Pyz3rException(
                f"Sprite {name} does not exist on {self.base_url}.")
        try:
            async with self.http.get(url=spriteinfo["file"]) as resp:
                spritedata = await resp.read()
        except Exception as e:
            raise Pyz3rException(
                f'Sprite "{name}" could not be downloaded.') from e

        return bytearray(spritedata)

    def uri(self, url):
        return f'{self.baseurl}{url}'

    def get_formatted_spoiler(self, translate_dungeon_items=False):
        return spoiler.create_filtered_spoiler(self, translate_dungeon_items)
