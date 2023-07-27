import asyncio
import json
import uuid

import aiohttp
from tenacity import RetryError, AsyncRetrying, stop_after_attempt, retry_if_exception_type

from .misc import mergedicts
from .exceptions import UnableToRetrieve, UnableToGenerate


class SuperMetroidVaria():
    def __init__(
        self,
        skills_preset,
        settings_preset,
        race,
        baseurl,
        username,
        password,
        settings_dict,
    ):
        self.skills_preset = skills_preset
        self.settings_preset = settings_preset
        self.baseurl = baseurl
        self.race = race
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None
        self.settings_dict = settings_dict

    async def generate_game(self, raise_for_status=True):
        try:
            async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    retry=retry_if_exception_type((aiohttp.ClientResponseError, aiohttp.client_exceptions.ServerDisconnectedError))):
                with attempt:
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
                    return req
        except RetryError as e:
            raise e.last_attempt._exception from e

    @classmethod
    async def create(
        cls,
        skills_preset='regular',
        settings_preset='default',
        race=False,
        baseurl='https://randommetroidsolver.pythonanywhere.com',
        username=None,
        password=None,
        settings_dict=None,
        raise_for_status=True,
    ):
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
        if 'seedKey' in seed.data:
            seed.guid = uuid.UUID(hex=seed.data['seedKey'])

        return seed

    async def get_default_settings(self):
        settings = await self.fetch_settings_preset("default")
        # these two settings may not be needed, but added for backwards compatibility
        settings['complexity'] = "advanced"
        settings['seed'] = "0"
        # this setting is missing in VARIA defaults
        settings['logic'] = "vanilla"
        return settings

    async def get_settings(self):
        settings = await self.get_default_settings()
        if "default" != self.settings_preset:
            settings_preset_data = await self.fetch_settings_preset(self.settings_preset)
            settings = dict(mergedicts(settings, settings_preset_data))
        if self.settings_dict:
            settings = dict(mergedicts(settings, self.settings_dict))

        skills_preset_data = await self.fetch_skills_preset(self.skills_preset)
        settings['paramsFileTarget'] = json.dumps(skills_preset_data)
        settings['preset'] = self.skills_preset
        settings['raceMode'] = "on" if self.race else "off"

        # convert any lists to comma-deliminated strings and return
        return {s: (','.join(v) if isinstance(v, list) else v) for (s, v) in settings.items()}

    async def fetch_settings_preset(self, setting):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        data = {"randoPreset": setting, "origin": "extStats"}
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/randoPresetWebService', data=data, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve settings preset "{setting}".  It may not exist?') from e
            raise
        return settings

    async def fetch_skills_preset(self, skill):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/presetWebService', data={"preset": skill}, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve skill preset "{skill}".  It may not exist?') from e
            raise
        return settings

    @property
    def url(self):
        return f'{self.baseurl}/customizer/{str(self.guid)}'
