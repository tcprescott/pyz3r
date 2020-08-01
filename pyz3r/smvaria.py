import uuid
import asyncio
import aiohttp
import copy
import json
from .misc import mergedicts

SETTINGS_DEFAULT = {
    "complexity": "advanced",
    "seed": "0",
    "preset": "regular",
    "raceMode": "off",
    "areaLayout": "off",
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
    "progressionSpeed": "medium"
}

class SuperMetroidVaria():
    def __init__(
        self,
        skills_preset,
        settings_preset,
        baseurl,
        username,
        password,
    ):
        self.skills_preset = skills_preset
        self.settings_preset = settings_preset
        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None

    async def generate_game(self):
        for i in range(0, 5):
            try:
                async with aiohttp.request(method='post', url=self.baseurl + self.endpoint, data=self.settings, auth=self.auth) as resp:
                    print(await resp.text())
                    req = await resp.json(content_type='text/html')
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            # except aiohttp.ClientResponseError:
            #     continue
            return req
        raise exceptions.alttprFailedToGenerate('failed to generate game')

    @classmethod
    async def create(
        cls,
        skills_preset='regular',
        settings_preset='default',
        baseurl='https://randommetroidsolver.pythonanywhere.com',
        username=None,
        password=None,
    ):
        seed = cls(
            skills_preset=skills_preset,
            settings_preset=settings_preset,
            baseurl=baseurl,
            username=username,
            password=password
        )

        seed.endpoint = f'/randomizerWebService'

        settings_preset_data = await seed.fetch_settings_preset()
        skills_preset_data = await seed.fetch_skills_preset()

        seed.settings = copy.deepcopy(SETTINGS_DEFAULT)
        seed.settings = dict(mergedicts(seed.settings, settings_preset_data))
        seed.settings['preset'] = skills_preset
        seed.settings['paramsFileTarget'] = json.dumps(skills_preset_data)

        seed.settings['energyQtyMultiSelect'] = 'sparse,medium,vanilla'
        # seed.settings['morphPlacementMultiSelect'] = ['early','late','normal']
        # seed.settings['progressionDifficultyMultiSelect'] = ['easier','normal','harder']
        # seed.settings['progressionSpeedMultiSelect'] = ['slowest','slow','medium','fast','fastest','basic','VARIAble','speedrun']

        seed.data = await seed.generate_game()
        seed.guid = uuid.UUID(hex=seed.data['seedKey'])

        return seed

    async def fetch_settings_preset(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        data = { "randoPreset": self.settings_preset, "origin": "extStats" }
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/randoPresetWebService', data=data, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            raise
        return settings

    async def fetch_skills_preset(self):
        """Returns a dictonary of valid settings.

        Returns:
            dict -- dictonary of valid settings that can be used
        """
        async with aiohttp.request(method='post', url=f'{self.baseurl}/presetWebService', data={"preset": self.skills_preset}, auth=self.auth, raise_for_status=True) as resp:
            settings = await resp.json(content_type='text/html')
        return settings

    @property
    def url(self):
        return f'{self.baseurl}/customizer/{str(self.guid)}'
