"""Super Metroid VARIA Randomizer API client."""

from typing import Optional, Dict, Any, Union
import logging
import asyncio
import json
import uuid

import aiohttp
from tenacity import RetryError, AsyncRetrying, stop_after_attempt, retry_if_exception_type

from .misc import mergedicts
from .exceptions import UnableToRetrieve, UnableToGenerate

logger = logging.getLogger(__name__)


class SuperMetroidVaria:
    """Client for the Super Metroid VARIA Randomizer API.
    
    Attributes:
        skills_preset: Name of the skills preset to use.
        settings_preset: Name of the settings preset to use.
        race: Whether to generate a race mode seed.
        baseurl: Base URL for the VARIA API.
        auth: Authentication credentials (if provided).
        settings_dict: Additional settings overrides.
        settings: Combined settings for generation.
        data: Game data returned from the API.
        guid: UUID for the generated seed.
    """
    
    def __init__(
        self,
        skills_preset: str,
        settings_preset: str,
        race: bool,
        baseurl: str,
        username: Optional[str],
        password: Optional[str],
        settings_dict: Optional[Dict[str, Any]],
    ) -> None:
        """Initialize the VARIA randomizer client.
        
        Args:
            skills_preset: Name of the skills preset.
            settings_preset: Name of the settings preset.
            race: Whether to generate a race mode seed.
            baseurl: Base URL for the API.
            username: Optional username for authentication.
            password: Optional password for authentication.
            settings_dict: Optional dictionary of additional settings.
        """
        self.skills_preset = skills_preset
        self.settings_preset = settings_preset
        self.baseurl = baseurl
        self.race = race
        self.username = username
        self.password = password
        self.auth: Optional[aiohttp.BasicAuth] = (
            aiohttp.BasicAuth(login=username, password=password) 
            if username and password else None
        )
        self.settings_dict = settings_dict
        self.settings: Optional[Dict[str, Any]] = None
        self.data: Optional[Union[Dict[str, Any], str]] = None
        self.guid: Optional[uuid.UUID] = None
        logger.debug(f"Initialized VARIA client with skills={skills_preset}, settings={settings_preset}")

    async def generate_game(self, raise_for_status: bool = True) -> Union[Dict[str, Any], str]:
        """Generate a VARIA randomizer seed via the API.
        
        Args:
            raise_for_status: Whether to raise an exception on HTTP errors.
            
        Returns:
            Dictionary or string containing the generated game data.
            
        Raises:
            The exception from the last failed attempt if all retries fail.
        """
        logger.info("Generating VARIA randomizer seed")
        try:
            async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    retry=retry_if_exception_type((
                        aiohttp.ClientResponseError, 
                        aiohttp.client_exceptions.ServerDisconnectedError
                    ))):
                with attempt:
                    logger.debug(f"Generation attempt {attempt.retry_state.attempt_number}/3")
                    async with aiohttp.request(
                            method='post',
                            url=f'{self.baseurl}/randomizerWebService',
                            data=self.settings,
                            auth=self.auth,
                            raise_for_status=raise_for_status) as resp:
                        try:
                            req = await resp.json(content_type='text/html')
                        except json.decoder.JSONDecodeError:
                            req = await resp.text()
                    logger.info("Successfully generated VARIA seed")
                    return req
        except RetryError as e:
            logger.error(f"Failed to generate VARIA seed after 3 attempts: {e}")
            raise e.last_attempt._exception from e

    @classmethod
    async def create(
        cls,
        skills_preset: str = 'regular',
        settings_preset: str = 'default',
        race: bool = False,
        baseurl: str = 'https://randommetroidsolver.pythonanywhere.com',
        username: Optional[str] = None,
        password: Optional[str] = None,
        settings_dict: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True,
    ) -> 'SuperMetroidVaria':
        """Create and generate a VARIA randomizer seed.
        
        Args:
            skills_preset: Skills preset name. Defaults to 'regular'.
            settings_preset: Settings preset name. Defaults to 'default'.
            race: Whether to generate a race mode seed. Defaults to False.
            baseurl: Base URL for the VARIA API.
            username: Optional username for authentication.
            password: Optional password for authentication.
            settings_dict: Optional additional settings.
            raise_for_status: Whether to raise exceptions on HTTP errors.
            
        Returns:
            An initialized SuperMetroidVaria instance with generated seed.
        """
        logger.info(f"Creating VARIA seed with skills={skills_preset}, settings={settings_preset}, race={race}")
        seed = cls(
            skills_preset=skills_preset,
            settings_preset=settings_preset,
            race=race,
            baseurl=baseurl,
            username=username,
            password=password,
            settings_dict=settings_dict,
        )

        seed.settings = await seed.get_settings()

        seed.data = await seed.generate_game(raise_for_status)
        if isinstance(seed.data, dict) and 'seedKey' in seed.data:
            seed.guid = uuid.UUID(hex=seed.data['seedKey'])
            logger.info(f"Created VARIA seed with GUID: {seed.guid}")

        return seed

    async def get_default_settings(self) -> Dict[str, Any]:
        """Get the default VARIA settings.
        
        Returns:
            Dictionary of default settings with backwards compatibility additions.
        """
        logger.debug("Fetching default VARIA settings")
        settings = await self.fetch_settings_preset("default")
        # these two settings may not be needed, but added for backwards compatibility
        settings['complexity'] = "advanced"
        settings['seed'] = "0"
        # this setting is missing in VARIA defaults
        settings['logic'] = "vanilla"
        return settings

    async def get_settings(self) -> Dict[str, Any]:
        """Build the complete settings dictionary for generation.
        
        Combines default settings, preset settings, custom settings, and skills.
        
        Returns:
            Dictionary of complete settings ready for API submission.
        """
        logger.debug("Building complete settings configuration")
        settings = await self.get_default_settings()
        
        if "default" != self.settings_preset:
            logger.debug(f"Applying settings preset: {self.settings_preset}")
            settings_preset_data = await self.fetch_settings_preset(self.settings_preset)
            settings = dict(mergedicts(settings, settings_preset_data))
        
        if self.settings_dict:
            logger.debug("Applying custom settings overrides")
            settings = dict(mergedicts(settings, self.settings_dict))

        logger.debug(f"Applying skills preset: {self.skills_preset}")
        skills_preset_data = await self.fetch_skills_preset(self.skills_preset)
        settings['paramsFileTarget'] = json.dumps(skills_preset_data)
        settings['preset'] = self.skills_preset
        settings['raceMode'] = "on" if self.race else "off"

        # convert any lists to comma-delimited strings and return
        result = {s: (','.join(v) if isinstance(v, list) else v) for (s, v) in settings.items()}
        logger.debug("Settings configuration complete")
        return result

    async def fetch_settings_preset(self, setting: str) -> Dict[str, Any]:
        """Fetch a settings preset from the VARIA API.

        Args:
            setting: Name of the settings preset to fetch.
            
        Returns:
            Dictionary of settings for the preset.
            
        Raises:
            UnableToRetrieve: If the preset doesn't exist or can't be retrieved.
        """
        logger.debug(f"Fetching settings preset: {setting}")
        data = {"randoPreset": setting, "origin": "extStats"}
        try:
            async with aiohttp.request(
                method='post', 
                url=f'{self.baseurl}/randoPresetWebService', 
                data=data, 
                auth=self.auth, 
                raise_for_status=True
            ) as resp:
                settings = await resp.json(content_type='text/html')
            logger.debug(f"Successfully fetched settings preset: {setting}")
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.status == 400:
                logger.error(f"Settings preset '{setting}' not found")
                raise UnableToRetrieve(f'Unable to retrieve settings preset "{setting}". It may not exist?') from e
            raise
        return settings

    async def fetch_skills_preset(self, skill: str) -> Dict[str, Any]:
        """Fetch a skills preset from the VARIA API.

        Args:
            skill: Name of the skills preset to fetch.
            
        Returns:
            Dictionary of skills settings for the preset.
            
        Raises:
            UnableToRetrieve: If the preset doesn't exist or can't be retrieved.
        """
        logger.debug(f"Fetching skills preset: {skill}")
        try:
            async with aiohttp.request(
                method='post', 
                url=f'{self.baseurl}/presetWebService', 
                data={"preset": skill}, 
                auth=self.auth, 
                raise_for_status=True
            ) as resp:
                settings = await resp.json(content_type='text/html')
            logger.debug(f"Successfully fetched skills preset: {skill}")
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.status == 400:
                logger.error(f"Skills preset '{skill}' not found")
                raise UnableToRetrieve(f'Unable to retrieve skill preset "{skill}". It may not exist?') from e
            raise
        return settings

    @property
    def url(self) -> str:
        """Get the URL for this VARIA seed.
        
        Returns:
            The full URL to access this seed on the VARIA website.
        """
        return f'{self.baseurl}/customizer/{str(self.guid)}'
