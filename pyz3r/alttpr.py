"""ALTTPR (A Link to the Past Randomizer) API client."""

from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import aiohttp
import logging
import tempfile
import os

from .exceptions import Pyz3rException, AlttprFailedToRetrieve, AlttprFailedToGenerate
from . import misc, spoiler
from .rom import Rom

logger = logging.getLogger(__name__)


class ALTTPR:
    """Client for interacting with the ALTTPR (A Link to the Past Randomizer) API.
    
    This class provides methods to generate and retrieve randomized games from
    the ALTTPR website, as well as create patched ROM files.
    
    Attributes:
        data: The game data returned from the API.
        hash: The unique hash identifier for the game.
        settings: The settings used to generate the game.
        baseurl: The base URL for the ALTTPR API.
        auth: Authentication credentials for the API (if provided).
        rom: The ROM object after patching (if created).
    """
    
    def __init__(
        self,
        baseurl: str = 'https://alttpr.com',
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Initialize an ALTTPR client.
        
        Args:
            baseurl: The base URL for the ALTTPR API. Defaults to 'https://alttpr.com'.
            username: Optional username for API authentication.
            password: Optional password for API authentication.
        """
        self.data: Optional[Dict[str, Any]] = None
        self.hash_id: Optional[str] = None
        self.hash: Optional[str] = None
        self.settings: Optional[Dict[str, Any]] = None
        self.baseurl: str = baseurl
        self.auth: Optional[aiohttp.BasicAuth] = (
            aiohttp.BasicAuth(login=username, password=password) 
            if username and password else None
        )
        self.rom: Optional[Rom] = None
        logger.debug(f"Initialized ALTTPR client with baseurl={baseurl}")

    @classmethod
    async def generate(
        cls, 
        settings: Dict[str, Any], 
        endpoint: str = '/api/randomizer', 
        **kwargs: Any
    ) -> 'ALTTPR':
        """Generate a new randomized game with the specified settings.
        
        Args:
            settings: Dictionary of game generation settings.
            endpoint: API endpoint for game generation. Defaults to '/api/randomizer'.
            **kwargs: Additional arguments passed to the ALTTPR constructor.
            
        Returns:
            An ALTTPR instance with the generated game data.
            
        Raises:
            AlttprFailedToGenerate: If game generation fails after retries.
        """
        logger.info("Generating new ALTTPR game")
        logger.debug(f"Settings: {settings}")
        seed = cls(**kwargs)

        seed.data = await seed.generate_game(settings, endpoint)
        seed.hash = seed.data['hash']
        
        logger.info(f"Successfully generated game with hash: {seed.hash}")
        return seed

    @classmethod
    async def retrieve(cls, hash_id: str, **kwargs: Any) -> 'ALTTPR':
        """Retrieve an existing game by its hash ID.
        
        Args:
            hash_id: The unique hash identifier for the game.
            **kwargs: Additional arguments passed to the ALTTPR constructor.
            
        Returns:
            An ALTTPR instance with the retrieved game data.
            
        Raises:
            AlttprFailedToRetrieve: If the game cannot be retrieved.
        """
        logger.info(f"Retrieving ALTTPR game with hash: {hash_id}")
        seed = cls(**kwargs)

        seed.hash = hash_id
        seed.data = await seed.retrieve_game(hash_id)
        
        logger.info(f"Successfully retrieved game: {hash_id}")
        return seed

    async def generate_game(self, settings: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """Generate a game via the API.
        
        Args:
            settings: Dictionary of game generation settings.
            endpoint: API endpoint for game generation.
            
        Returns:
            Dictionary containing the generated game data.
            
        Raises:
            AlttprFailedToGenerate: If generation fails after 5 retries.
        """
        self.settings = settings
        for attempt in range(1, 6):
            try:
                logger.debug(f"Game generation attempt {attempt}/5 to {self.uri(endpoint)}")
                async with aiohttp.request(
                    method='post', 
                    url=self.uri(endpoint), 
                    json=settings, 
                    auth=self.auth, 
                    raise_for_status=True
                ) as resp:
                    req = await resp.json()
                self.data = req
                logger.info(f"Game generated successfully on attempt {attempt}")
                return req
            except (aiohttp.client_exceptions.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                logger.warning(f"Game generation attempt {attempt}/5 failed: {e}")

        logger.error("Failed to generate game after 5 attempts")
        raise AlttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self, hash_id: str) -> Dict[str, Any]:
        """Retrieve game data from the API by hash ID.
        
        Args:
            hash_id: The unique hash identifier for the game.
            
        Returns:
            Dictionary containing the game data.
            
        Raises:
            AlttprFailedToRetrieve: If retrieval fails after 5 retries.
        """
        for attempt in range(1, 6):
            try:
                logger.debug(f"Game retrieval attempt {attempt}/5 for hash: {hash_id}")
                async with aiohttp.request(
                    method='get', 
                    url=self.uri('/hash/' + hash_id), 
                    auth=self.auth, 
                    raise_for_status=True
                ) as resp:
                    req = await resp.json(content_type="text/html")
                self.data = req
                logger.info(f"Game retrieved successfully on attempt {attempt}")
                return req
            except aiohttp.ClientResponseError as e:
                logger.warning(f"Game retrieval attempt {attempt}/5 failed with HTTP error: {e}")
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                logger.warning(f"Game retrieval attempt {attempt}/5 failed with disconnect: {e}")
        
        logger.error(f"Failed to retrieve game {hash_id} after 5 attempts")
        raise AlttprFailedToRetrieve(
            f'failed to retrieve game {hash_id}, the game is likely not found.')


    async def randomizer_settings(self) -> Dict[str, Any]:
        """Get valid randomizer settings from the API.

        Returns:
            Dictionary of valid settings that can be used for game generation.
        """
        logger.debug("Fetching randomizer settings from API")
        async with aiohttp.request(
            method='get', 
            url=self.baseurl + '/randomizer/settings', 
            auth=self.auth, 
            raise_for_status=True
        ) as resp:
            settings = await resp.json()
        logger.debug("Successfully fetched randomizer settings")
        return settings

    async def customizer_settings(self) -> Dict[str, Any]:
        """Get valid customizer settings from the API.

        Returns:
            Dictionary of valid customizer settings that can be used.
        """
        logger.debug("Fetching customizer settings from API")
        async with aiohttp.request(
            method='get', 
            url=self.baseurl + '/customizer/settings', 
            auth=self.auth, 
            raise_for_status=True
        ) as resp:
            settings = await resp.json()
        logger.debug("Successfully fetched customizer settings")
        return settings

    async def find_daily_hash(self) -> str:
        """Get the hash for today's daily challenge.
        
        Returns:
            The hash string for today's daily seed.
        """
        logger.debug("Fetching daily challenge hash")
        async with aiohttp.request(
            method='get', 
            url=f'{self.baseurl}/api/daily', 
            auth=self.auth, 
            raise_for_status=True
        ) as resp:
            daily = await resp.json()
        logger.info(f"Daily hash retrieved: {daily['hash']}")
        return daily['hash']

    @property
    def url(self) -> str:
        """Get the permalink URL for this game.
        
        Returns:
            The full URL to access this game on the ALTTPR website.
        """
        return f'{self.baseurl}/h/{self.hash}'

    @property
    def code(self) -> List[str]:
        """Get the item code displayed on the file select screen.

        Returns:
            List of strings representing the five items shown on the file select screen.
            
        Raises:
            Pyz3rException: If no game has been generated or retrieved yet.
        """
        if not self.data:
            logger.error("Attempted to get code before game was generated/retrieved")
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
            logger.warning("Could not extract code bytes, using default")
            return ["Bow", "Boomerang", "Hookshot", "Bombs", "Mushroom"]
        else:
            p = list(map(lambda x: code_map[x], codebytes))
            code = [p[0], p[1], p[2], p[3], p[4]]
            logger.debug(f"Extracted code: {code}")
            return code

    async def get_patch_base(self) -> bytes:
        """Get the base BPS patch from the website.
        
        This is the first set of patches that must be applied to the ROM.
        BPS files are cached in the system's temp directory (/tmp/pyz3r/bps on *nix systems).

        Returns:
            Bytes object representing the BPS patch.
        """
        logger.debug(f"Fetching patch base for hash: {self.hash}")
        async with aiohttp.request(
            method='get', 
            url=self.uri("/api/h/" + self.hash), 
            auth=self.auth, 
            raise_for_status=True
        ) as resp:
            seed_settings = await resp.json()

        cachedbpstmp = os.path.join(tempfile.gettempdir(), "pyz3r", "bps")
        cachedbpsfile = os.path.join(cachedbpstmp, f"{seed_settings['md5']}.bps")
        
        try:
            Path(cachedbpstmp).mkdir(parents=True, exist_ok=True)
            with open(cachedbpsfile, "rb") as f:
                req_patch = f.read()
            logger.info(f"Loaded BPS patch from cache: {cachedbpsfile}")
        except (FileNotFoundError, PermissionError) as e:
            logger.debug(f"Cache miss or permission error: {e}, downloading BPS patch")
            async with aiohttp.request(
                method='get', 
                url=self.baseurl + seed_settings['bpsLocation'], 
                auth=self.auth, 
                raise_for_status=True
            ) as resp:
                req_patch = await resp.read()

            try:
                with open(cachedbpsfile, "wb") as f:
                    f.write(req_patch)
                logger.info(f"Cached BPS patch to: {cachedbpsfile}")
            except PermissionError:
                logger.warning("Unable to cache BPS file due to permission error")

        return req_patch

    async def create_patched_game(
        self,
        input_filename: str,
        output_filename: Optional[str] = None,
        heartspeed: str = 'half',
        heartcolor: str = 'red',
        quickswap: bool = False,
        menu_speed: str = 'normal',
        spritename: str = 'Link',
        music: bool = True,
        msu1_resume: bool = True
    ) -> Rom:
        """Create a patched ROM file with customizations.
        
        Args:
            input_filename: Path to the base Japan 1.0 ROM file.
            output_filename: Optional path to write the patched ROM to.
            heartspeed: Low health beep speed ('off', 'quarter', 'half', 'normal', 'double').
            heartcolor: Heart color on HUD ('red', 'blue', 'green', 'yellow').
            quickswap: Enable quickswap functionality.
            menu_speed: Menu speed ('instant', 'fast', 'normal', 'slow').
            spritename: Name of sprite to use (from alttpr.com/sprites).
            music: Enable in-game music (disable for MSU-1).
            msu1_resume: Enable MSU-1 resume feature.
            
        Returns:
            The patched Rom object.
            
        Raises:
            Pyz3rException: If no game has been generated or retrieved yet.
        """
        if not self.data:
            logger.error("Attempted to create patched game before generating/retrieving")
            raise Pyz3rException('Please specify a seed or hash first to generate or retrieve a game.')

        logger.info(f"Creating patched game from {input_filename}")
        self.rom = Rom(input_filename)

        logger.debug("Applying base BPS patch")
        self.rom.apply_bps_patch(patch=await self.get_patch_base())

        # expand the ROM to size requested in seed_data
        if self.data['size'] > 2:
            logger.debug(f"Expanding ROM to {self.data['size']}MB")
            self.rom.expand(newlenmb=self.data['size'])

        # apply the seed-specific changes
        logger.debug("Applying seed-specific patches")
        self.rom.apply_dict_patches(patches=self.data['patch'])

        # apply the heart speed change
        logger.debug(f"Setting heart speed to {heartspeed}")
        self.rom.heart_speed(heartspeed)

        # apply the heart color change
        logger.debug(f"Setting heart color to {heartcolor}")
        self.rom.heart_color(heartcolor)

        # apply menu speed
        logger.debug(f"Setting menu speed to {menu_speed}")
        self.rom.menu_speed(menu_speed)

        # apply quickswap
        logger.debug(f"Setting quickswap to {quickswap}")
        self.rom.quickswap(quickswap)

        if not spritename == "Link":
            # apply the sprite
            logger.info(f"Applying sprite: {spritename}")
            self.rom.sprite(zspr=await self.get_sprite(spritename))

        # apply music options
        logger.debug(f"Setting music={music}, msu1_resume={msu1_resume}")
        self.rom.music(music=music)
        self.rom.msu1_resume(enable=msu1_resume)

        # calculate the SNES checksum and apply it to the ROM
        logger.debug("Calculating and applying ROM checksum")
        self.rom.checksum()

        if output_filename is not None:
            logger.info(f"Writing patched ROM to {output_filename}")
            self.rom.write_to_file(output_filename)

        logger.info("Successfully created patched game")
        return self.rom

    async def get_sprite(self, name: str) -> bytearray:
        """Retrieve the ZSPR file for a named sprite.

        Args:
            name: The name of the sprite, as listed at https://alttpr.com/en/sprite_preview.

        Returns:
            Bytearray containing the SPR or ZSPR file data.
            
        Raises:
            Pyz3rException: If the sprite doesn't exist or can't be downloaded.
        """
        logger.debug(f"Fetching sprite list to find sprite: {name}")
        async with aiohttp.request(
            method='get', 
            url=self.baseurl + '/sprites', 
            auth=self.auth, 
            raise_for_status=True
        ) as resp:
            sprites = await resp.json()
        
        try:
            spriteinfo = next(
                (sprite for sprite in sprites if sprite["name"] == name))
        except StopIteration:
            logger.error(f"Sprite '{name}' not found on {self.baseurl}")
            raise Pyz3rException(
                f"Sprite {name} does not exist on {self.baseurl}.")
        
        try:
            logger.debug(f"Downloading sprite from {spriteinfo['file']}")
            async with aiohttp.request(
                method='get', 
                url=spriteinfo["file"], 
                raise_for_status=True
            ) as resp:
                spritedata = await resp.read()
            logger.info(f"Successfully downloaded sprite: {name}")
        except Exception as e:
            logger.error(f"Failed to download sprite '{name}': {e}")
            raise Pyz3rException(
                f'Sprite "{name}" could not be downloaded.') from e

        return bytearray(spritedata)

    def uri(self, url: str) -> str:
        """Construct a full URI from a relative URL path.
        
        Args:
            url: Relative URL path.
            
        Returns:
            Full URI combining baseurl and the path.
        """
        return f'{self.baseurl}{url}'

    def get_formatted_spoiler(self, translate_dungeon_items: bool = False) -> Optional[Dict[str, Any]]:
        """Get a formatted and filtered spoiler log.
        
        Args:
            translate_dungeon_items: Whether to translate dungeon item names.
            
        Returns:
            Ordered dictionary of the formatted spoiler log, or None if spoilers are disabled.
        """
        logger.debug("Creating formatted spoiler log")
        return spoiler.create_filtered_spoiler(self, translate_dungeon_items)
