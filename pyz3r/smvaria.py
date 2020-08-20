import asyncio
import copy
import json
import uuid

import aiohttp
from tenacity import RetryError, AsyncRetrying, stop_after_attempt, retry_if_exception_type

from .misc import mergedicts
from .exceptions import UnableToRetrieve, UnableToGenerate

SETTINGS_DEFAULT = {
    "complexity": "advanced",
    "seed": "0",
    "preset": "regular",
    "raceMode": "off",
    "areaLayout": "off",
    "lightAreaRandomization": "off",
    "removeEscapeEnemies": "off",
    "layoutPatches": "on",
    "variaTweaks": "on",
    "gravityBehaviour": "Balanced",
    "nerfedCharge": "off",
    "itemsounds": "on",
    "elevators_doors_speed": "on",
    "spinjumprestart": "off",
    "rando_speed": "off",
    "animals": "off",
    "No_Music": "off",
    "random_music": "off",
    "maxDifficulty": "hardcore",
    "Infinite_Space_Jump": "off",
    "refill_before_save": "off",
    "missileQty": '3',
    "superQty": "2",
    "powerBombQty": "1",
    "minorQty": "100",
    "suitsRestriction": "on",
    "funCombat": "off",
    "funMovement": "off",
    "funSuits": "off",
    "hideItems": "off",
    "strictMinors": "off",
    "areaRandomization": "off",
    "bossRandomization": "off",
    "escapeRando": "off",
    "majorsSplit": "Full",
    "startLocation": "Landing Site",
    "energyQty": "vanilla",
    "morphPlacement": "early",
    "progressionDifficulty": "normal",
    "progressionSpeed": "medium",
    "startLocationMultiSelect": [
        'Ceres',
        'Landing Site',
        'Gauntlet Top',
        'Green Brinstar Elevator',
        'Big Pink,Etecoons Supers',
        'Wrecked Ship Main',
        'Firefleas Top',
        'Business Center',
        'Bubble Mountain',
        'Mama Turtle',
        'Watering Hole',
        'Aqueduct',
        'Red Brinstar Elevator',
        'Golden Four'
    ],
    "majorsSplitMultiSelect": [
        'Full',
        'Major',
        'Chozo'
    ],
    "progressionDifficultyMultiSelect": [
        'easier',
        'normal',
        'harder'
    ],
    "progressionSpeedMultiSelect": [
        'slowest',
        'slow',
        'medium',
        'fast',
        'fastest',
        'basic',
        'VARIAble',
        'speedrun'
    ],
    "morphPlacementMultiSelect": [
        'early',
        'late',
        'normal'
    ],
    "energyQtyMultiSelect": [
        'ultra sparse',
        'sparse',
        'medium',
        'vanilla'
    ],
}


class SuperMetroidVaria():
    def __init__(
        self,
        skills_preset,
        settings_preset,
        race,
        baseurl,
        username,
        password,
    ):
        self.skills_preset = skills_preset
        self.settings_preset = settings_preset
        self.baseurl = baseurl
        self.race = race
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None

    async def generate_game(self):
        try:
            async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(5),
                    retry=retry_if_exception_type((aiohttp.ClientResponseError, aiohttp.client_exceptions.ServerDisconnectedError))):
                with attempt:
                    async with aiohttp.request(
                            method='post',
                            url=f'{self.baseurl}/randomizerWebService',
                            data=self.settings,
                            auth=self.auth,
                            raise_for_status=True) as resp:
                        req = await resp.json(content_type='text/html')
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
    ):
        seed = cls(
            skills_preset=skills_preset,
            settings_preset=settings_preset,
            race=race,
            baseurl=baseurl,
            username=username,
            password=password
        )

        seed.settings = await seed.get_settings()

        seed.data = await seed.generate_game()
        seed.guid = uuid.UUID(hex=seed.data['seedKey'])

        return seed

    async def get_settings(self):
        skills_preset_data = await self.fetch_skills_preset()
        settings_preset_data = await self.fetch_settings_preset()

        settings = copy.deepcopy(SETTINGS_DEFAULT)
        settings = dict(mergedicts(settings, settings_preset_data))
        settings['preset'] = self.skills_preset
        settings['raceMode'] = "on" if self.race else "off"
        settings['paramsFileTarget'] = json.dumps(skills_preset_data)

        # convert any lists to comma-deliminated strings and return
        return {s: (','.join(v) if isinstance(v, list) else v) for (s, v) in settings.items()}

    async def fetch_settings_preset(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        data = {"randoPreset": self.settings_preset, "origin": "extStats"}
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/randoPresetWebService', data=data, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve settings preset "{self.settings_preset}".  It may not exist?') from e
            raise
        return settings

    async def fetch_skills_preset(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/presetWebService', data={"preset": self.skills_preset}, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve skill preset "{self.skills_preset}".  It may not exist?') from e
            raise
        return settings

    @property
    def url(self):
        return f'{self.baseurl}/customizer/{str(self.guid)}'
