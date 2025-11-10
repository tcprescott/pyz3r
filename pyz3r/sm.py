"""Super Metroid and SM/ALTTPR Combo Randomizer API client."""

from typing import Optional, Dict, Any
import logging
import slugid
import uuid
import asyncio
import aiohttp

from . import exceptions

logger = logging.getLogger(__name__)


async def sm(
    settings: Optional[Dict[str, Any]] = None,
    slug_id: Optional[str] = None,
    guid_id: Optional[str] = None,
    baseurl: str = 'https://samus.link',
    randomizer: str = 'sm',
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> 'smClass':
    """Create a Super Metroid randomizer seed (async factory function).
    
    Args:
        settings: Dictionary of game generation settings.
        slug_id: Existing seed's slug ID to retrieve.
        guid_id: Existing seed's GUID to retrieve.
        baseurl: Base URL for the randomizer API. Defaults to 'https://samus.link'.
        randomizer: Randomizer type ('sm' or 'smz3'). Defaults to 'sm'.
        username: Optional username for authentication.
        password: Optional password for authentication.
        
    Returns:
        An initialized smClass instance.
    """
    logger.debug(f"Creating SM seed with randomizer={randomizer}")
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


class smClass:
    """Client for Super Metroid and SM/ALTTPR combo randomizer APIs.
    
    Attributes:
        settings: Game generation settings.
        slug_id: Short encoded ID for the seed.
        guid: UUID for the seed.
        baseurl: Base URL for the API.
        randomizer: Type of randomizer ('sm' or 'smz3').
        data: Game data from the API.
        auth: Authentication credentials (if provided).
    """
    
    def __init__(
        self,
        settings: Optional[Dict[str, Any]],
        slug_id: Optional[str],
        guid_id: Optional[str],
        baseurl: str,
        randomizer: str,
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """Initialize the SM randomizer client.
        
        Args:
            settings: Game generation settings.
            slug_id: Existing seed's slug ID.
            guid_id: Existing seed's GUID.
            baseurl: Base URL for the API.
            randomizer: Randomizer type.
            username: Optional username for authentication.
            password: Optional password for authentication.
        """
        self.settings = settings
        self.slug_id = slug_id
        self.guid_id = guid_id
        self.baseurl = baseurl
        self.randomizer = randomizer
        self.username = username
        self.password = password
        self.auth: Optional[aiohttp.BasicAuth] = (
            aiohttp.BasicAuth(login=username, password=password) 
            if username and password else None
        )
        self.data: Optional[Dict[str, Any]] = None
        self.guid: Optional[uuid.UUID] = None
        self.endpoint: Optional[str] = None
        logger.debug(f"Initialized SM client with baseurl={baseurl}, randomizer={randomizer}")

    async def _init(self) -> None:
        """Internal initialization to generate or retrieve game data."""
        if self.settings:
            logger.info("Generating new SM game")
            self.endpoint = f'/api/randomizers/{self.randomizer}/generate'
            self.data = await self.generate_game()
            self.guid = uuid.UUID(hex=self.data['guid'])
            self.slug_id = slugid.encode(self.guid)
            logger.info(f"Generated game with slug_id: {self.slug_id}")
        elif self.slug_id:
            logger.info(f"Retrieving SM game by slug_id: {self.slug_id}")
            self.guid = slugid.decode(self.slug_id)
            self.data = await self.retrieve_game()
        elif self.guid_id:
            logger.info(f"Retrieving SM game by guid: {self.guid_id}")
            self.guid = uuid.UUID(hex=self.guid_id)
            self.slug_id = slugid.encode(self.guid)
            self.data = await self.retrieve_game()
        else:
            logger.debug("No settings or IDs provided, seed not initialized")
            self.data = None
            self.slug_id = None
            self.guid = None

    async def generate_game(self) -> Dict[str, Any]:
        """Generate a new game via the API.
        
        Returns:
            Dictionary containing the generated game data.
            
        Raises:
            AlttprFailedToGenerate: If generation fails after 5 retries.
        """
        for attempt in range(1, 6):
            try:
                logger.debug(f"Game generation attempt {attempt}/5")
                async with aiohttp.request(
                    method='post', 
                    url=self.baseurl + self.endpoint, 
                    json=self.settings, 
                    auth=self.auth
                ) as resp:
                    req = await resp.json()
                logger.info(f"Game generated successfully on attempt {attempt}")
                return req
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                logger.warning(f"Generation attempt {attempt}/5 failed with disconnect: {e}")
                continue
        
        logger.error("Failed to generate game after 5 attempts")
        raise exceptions.AlttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self) -> Dict[str, Any]:
        """Retrieve game data from the API.
        
        Returns:
            Dictionary containing the game data.
            
        Raises:
            AlttprFailedToRetrieve: If retrieval fails after 5 retries.
        """
        for attempt in range(1, 6):
            try:
                logger.debug(f"Game retrieval attempt {attempt}/5 for guid: {self.guid.hex}")
                async with aiohttp.request(
                    method='get', 
                    url=f'{self.baseurl}/api/seed/{self.guid.hex}'
                ) as resp:
                    patch = await resp.json()
                logger.info(f"Game retrieved successfully on attempt {attempt}")
                return patch
            except aiohttp.ClientResponseError as e:
                logger.warning(f"Retrieval attempt {attempt}/5 failed with HTTP error: {e}")
                await asyncio.sleep(5)
                continue
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                logger.warning(f"Retrieval attempt {attempt}/5 failed with disconnect: {e}")
                continue
        
        logger.error(f"Failed to retrieve game {self.slug_id} after 5 attempts")
        raise exceptions.AlttprFailedToRetrieve(
            f'failed to retrieve game {self.slug_id}, the game is likely not found')

    @classmethod
    async def create(
        cls,
        settings: Optional[Dict[str, Any]] = None,
        slug_id: Optional[str] = None,
        guid_id: Optional[str] = None,
        baseurl: str = 'https://samus.link',
        randomizer: str = 'sm',
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> 'smClass':
        """Create and initialize an SM randomizer seed (alternative async factory).
        
        Args:
            settings: Game generation settings.
            slug_id: Existing seed's slug ID.
            guid_id: Existing seed's GUID.
            baseurl: Base URL for the API.
            randomizer: Randomizer type ('sm' or 'smz3').
            username: Optional username for authentication.
            password: Optional password for authentication.
            
        Returns:
            An initialized smClass instance.
        """
        logger.debug(f"Creating SM seed via classmethod with randomizer={randomizer}")
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

    async def randomizer_settings(self) -> Dict[str, Any]:
        """Get valid randomizer settings from the API.

        Returns:
            Dictionary of valid settings that can be used.
        """
        logger.debug("Fetching randomizer settings")
        async with aiohttp.request(
            method='get', 
            url=f'{self.baseurl}/api/randomizers/{self.randomizer}'
        ) as resp:
            settings = await resp.json()
        logger.debug("Successfully fetched randomizer settings")
        return settings

    @property
    def url(self) -> str:
        """Get the permalink URL for this seed.
        
        Returns:
            The full URL to access this seed.
        """
        if self.data and self.data.get('mode', 'normal') == 'multiworld':
            return f'{self.baseurl}/multiworld/{self.slug_id}'
        return f'{self.baseurl}/seed/{self.slug_id}'

    @property
    def code(self) -> str:
        """Get the hash code for this seed.
        
        Returns:
            The seed's hash code.
        """
        return self.data['hash']
