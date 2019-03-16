from .exceptions import alttprException
from .rom import patch, romfile

import warnings

import requests
import json

class alttpr():
    def __init__(
            self,
            settings=None,
            hash=None,
            randomizer='item',
            baseurl='https://alttpr.com',
            seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches',
            username='',
            password='',
        ):
        self.baseurl = baseurl
        self.seed_baseurl = seed_baseurl
        self.randomizer = randomizer

        if not username==None:
            self.auth = (username,password)
        else:
            self.auth = None

        if randomizer not in ['item','entrance']:
            raise alttprException("randomizer must be \"item\" or \"entrance\"")

        if settings == None and hash==None:
            self.data=None
        else:
            if settings:
                if randomizer == 'item':
                    url = self.baseurl + "/seed"
                elif randomizer == 'entrance':
                    url=self.baseurl + "/entrance/seed"
                for i in range(0,5):
                    try:
                        req_gen = requests.post(
                            url=url,
                            json=settings,
                            auth=self.auth
                        )
                    except requests.exceptions.ConnectionError:
                        continue
                    if not req_gen.status_code == requests.codes.ok:
                        continue
                    break
                
                req_gen.raise_for_status()
                #override whatever hash was provided and instead use what was gen'd
                hash=json.loads(req_gen.text)['hash']

            self.hash = hash
            self.url = '{baseurl}/h/{hash}'.format(
                baseurl = self.baseurl,
                hash = hash
            )

            req = requests.get(
                url=self.seed_baseurl + '/' + hash + '.json'
            )
            if not req.status_code == requests.codes.ok:
                req2 = requests.get(
                    url=self.baseurl + '/hash/' + hash
                )
                req2.raise_for_status()
                self.data = json.loads(req2.text)
            else:
                self.data = json.loads(req.text)


    def settings(self):
        if self.randomizer == 'item':
            req = requests.get(
                url=self.baseurl + "/randomizer/settings",
                auth=self.auth
            )
        elif self.randomizer == 'entrance':
            req = requests.get(
                url=self.baseurl + "/entrance/randomizer/settings",
                auth=self.auth
            )
        req.raise_for_status()
        return json.loads(req.text)


    def code(self):
        if not self.data:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.')
        
        code_map = {
            0: 'Bow', 1: 'Boomerang', 2: 'Hookshot', 3: 'Bombs',
            4: 'Mushroom',  5: 'Magic Powder', 6: 'Ice Rod', 7: 'Pendant',
            8: 'Bombos', 9: 'Ether', 10: 'Quake', 11: 'Lamp',
            12: 'Hammer', 13: 'Shovel', 14: 'Flute', 15: 'Bugnet', 16: 'Book',
            17: 'Empty Bottle', 18: 'Green Potion', 19: 'Somaria', 20: 'Cape',
            21: 'Mirror', 22: 'Boots', 23: 'Gloves', 24: 'Flippers',
            25: 'Moon Pearl', 26: 'Shield', 27: 'Tunic', 28: 'Heart',
            29: 'Map', 30: 'Compass', 31: 'Big Key'
        }

        for patch in self.data['patch']:
            seek = '1573395'
            if seek in patch:
                p=list(map(lambda x: code_map[x], patch[seek][2:]))
                return [p[0], p[1], p[2], p[3], p[4]]

    def get_patch_base(self):
        req = requests.get(
            url=self.baseurl + "/base_rom/settings",
            auth=self.auth
        )
        req.raise_for_status()
        base_file = json.loads(req.text)['base_file']
        req_patch = requests.get(
            url=self.baseurl + base_file,
            auth=self.auth
        )
        req_patch.raise_for_status()
        return json.loads(req_patch.text)

    def create_patched_game(
            self,
            patchrom_array,
            heartspeed='half',
            heartcolor='red',
            spritename='Link',
            music=True
        ):
        if not self.data:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.')

        #expand the ROM to size requested in seed_data
        patchrom_array = patch.expand(patchrom_array, newlenmb=self.data['size'])

        # apply the base modifications
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=self.get_patch_base()
        )

        #apply the seed-specific changes
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=self.data['patch']
        )

        #apply the heart speed change
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.heart_speed(heartspeed)
        )

        #apply the heart color change
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.heart_color(heartcolor)
        )

        #apply the sprite
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.sprite(
                spr=self.get_sprite(spritename)
            )
        )

        #apply the sprite
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.music(music=music)
        )

        #calculate the SNES checksum and apply it to the ROM
        patchrom_array = patch.apply(
            rom=patchrom_array,
            patches=patch.checksum(patchrom_array)
        )

        return patchrom_array

    def get_sprite(self, name):
        req = requests.get(
            url=self.baseurl + '/sprites',
            auth=self.auth
        )
        req.raise_for_status()
        sprites = json.loads(req.text)
        for sprite in sprites:
            if sprite['name'] == name:
                fileurl = sprite['file']
                break
        try:
            req_sprite = requests.get(
                url=fileurl
            )
            req_sprite.raise_for_status()
        except alttprException:
            raise alttprException('Sprite \"{name}\" is not available.'.format(
                name=name
            ))
        req_sprite.raise_for_status()
        spr = list(req_sprite.content)
        return spr

    # leave these here for backwards compatibility, we'll eventually remove these
    def read_rom(self, srcfilepath):
        warnings.warn('This has been deprecated.  Use pyz3r.romfile.read() instead.', DeprecationWarning)
        return romfile.read(srcfilepath)

    def write_rom(self, rom, dstfilepath):
        warnings.warn('This has been deprecated.  Use pyz3r.romfile.write() instead.', DeprecationWarning)
        return romfile.write(rom, dstfilepath)

    def get_hash(self):
        warnings.warn('This has been deprecated.  Use pyz3r.alttpr().hash instead.', DeprecationWarning)
        if not self.data:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.', DeprecationWarning)

        return self.data['hash']

    def url(self):
        warnings.warn('This has been deprecated.  Use pyz3r.alttpr().hash instead.', DeprecationWarning)
        if not self.url:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.')

        return self.url