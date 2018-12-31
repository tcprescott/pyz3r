import requests
import json
import itertools
import hashlib
from time import sleep

class alttprException(Exception):
    pass

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
                    req_gen = requests.post(
                        url=self.baseurl + "/seed",
                        json=settings,
                        auth=self.auth
                    )
                elif randomizer == 'entrance':
                    req_gen = requests.post(
                        url=self.baseurl + "/entrance/seed",
                        json=settings,
                        auth=self.auth
                    )
                req_gen.raise_for_status()
                #override whatever hash was provided and instead use what was gen'd
                hash=json.loads(req_gen.text)['hash']
                sleep(3)

            req = requests.get(
                url=self.seed_baseurl + '/' + hash + '.json'
            )
            req.raise_for_status()
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


    def url(self):
        if not self.data:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.')

        return '{baseurl}/h/{hash}'.format(
            baseurl = self.baseurl,
            hash = self.data['hash']
        )


    def get_hash(self):
        if not self.data:
            raise alttprException('Please specify a seed or hash first to generate or retrieve a game.')

        return self.data['hash']


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


    def get_patch_heart_speed(self, speed=''):
        if speed == 'off':
            sbyte=0
        elif speed == 'half':
            sbyte=64
        elif speed == 'quarter':
            sbyte=128
        elif speed == 'double':
            sbyte=16
        else:
            sbyte=32 #vanilla speed
        patch = [{
            '1572915': [sbyte]
        }]
        return patch


    def get_patch_heart_color(self,color='red'):
        if color=='blue':
            byte=44
            file_byte=13
        elif color=='green':
            byte=60
            file_byte=25
        elif color=='yellow':
            byte=40
            file_byte=9
        else:
            byte=36
            file_byte=5
        patch = [
            {'457246': [byte]},
            {'457248': [byte]},
            {'457250': [byte]},
            {'457252': [byte]},
            {'457254': [byte]},
            {'457256': [byte]},
            {'457258': [byte]},
            {'457260': [byte]},
            {'457262': [byte]},
            {'457264': [byte]},
            {'415073': [file_byte]},
        ]
        return patch


    def patch(self, rom, patches):
        for patch in patches:
            offset = int(list(patch.keys())[0])
            patch_values = list(patch.values())[0]
            for idx, value in enumerate(patch_values):
                rom[offset+idx] = value
        return rom


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
        self.expand_rom(patchrom_array)

        # apply the base modifications
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.get_patch_base()
        )

        #apply the seed-specific changes
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.data['patch']
        )

        #apply the heart speed change
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.get_patch_heart_speed(heartspeed)
        )

        #apply the heart color change
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.get_patch_heart_color(heartcolor)
        )

        #apply the sprite
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.get_patch_sprite(name=spritename)
        )

        #apply the sprite
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.get_patch_music(music=music)
        )

        #calculate the SNES checksum and apply it to the ROM
        patchrom_array = self.patch(
            rom=patchrom_array,
            patches=self.checksum_patch(patchrom_array)
        )

        return patchrom_array

    def get_patch_sprite(self, name, spr=None):
        if spr==None:
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
            except UnboundLocalError:
                raise alttprException('Sprite \"{name}\" is not available.'.format(
                    name=name
                ))
            req_sprite.raise_for_status()
            spr = list(req_sprite.content)
        #Verify ZSPR by checking first four characters, SPR <> ZSPR!
        if spr[:4] == [90, 83, 80, 82]:
            #stolen from VT's code
            gfx_offset = spr[12] << 24 | spr[11] << 16 | spr[10] << 8 | spr[9]
            palette_offset = spr[18] << 24 | spr[17] << 16 | spr[16] << 8 | spr[15]
            patch = [
                {'524288': spr[gfx_offset:gfx_offset+28671]},
                {'905992': spr[palette_offset:palette_offset+120]},
                {'912885': spr[palette_offset+120:palette_offset+120+3]}
            ]
        #Else treat it like a SPR file instead
        else:
            patch = [
                {'524288': spr[0:28671]},
                {'905992': spr[28672:28791]},
                {
                    '912885': [
                        spr[28726],
                        spr[28727],
                        spr[28756],
                        spr[28757],
                    ]
                }
            ]
        return patch

    def get_patch_music(self, music=True):
        if music:
            return []
        else:
            patch = [
                {'851480': [0]},
                {'851649': [0]},
                {'851968': [0, 0]},
                {'852199': [196, 88]}
            ]
            return patch


    def read_rom(self, srcfilepath):
        expected_rom_sha256='794e040b02c7591b59ad8843b51e7c619b88f87cddc6083a8e7a4027b96a2271'
        sha256_hash = hashlib.sha256()
        with open(srcfilepath,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        if not sha256_hash.hexdigest() == expected_rom_sha256:
            raise alttprException('Expected checksum "{expected_rom_sha256}", got "{actual_checksum}" instead.  Verify the source ROM is an unheadered Japan 1.0 Link to the Past ROM.'.format(
                expected_rom_sha256=expected_rom_sha256,
                actual_checksum=sha256_hash.hexdigest()
            ))
        fr = open(srcfilepath,"rb")
        baserom_array = list(fr.read())
        fr.close()
        return baserom_array


    def write_rom(self, rom, dstfilepath):
        fw = open(dstfilepath,"wb")
        patchrom = bytes()
        for idx, chunk_array in enumerate(self._chunk(rom,256)):
            patchrom += bytes(chunk_array)
        fw.write(patchrom)
        fw.close


    def expand_rom(self, rom, newlenmb=None):
        if newlenmb:
            newlen = newlenmb * 1024 * 1024
        else:
            newlen = self.data['size'] * 1024 * 1024
        if len(rom) > newlen:
            raise alttprException('ROM is already larger than {bytes}'.format(
                bytes=newlen
            ))
        diff = len(rom) - newlen
        if diff > 0:
            rom[newlen] = 0
        else:
            rom.extend(itertools.repeat(0, -diff))
            rom.append(0)


    def _chunk(self, iterator, count):
        itr = iter(iterator)
        while True:
            yield tuple([next(itr) for i in range(count)])


    def checksum_patch(self, rom):
        sum_of_bytes = sum(rom[:32731]) + sum(rom[32736:])
        checksum = (sum_of_bytes + 510) & 65535
        inverse = checksum ^ 65535
        patch = [
            {
                '32732': [
                    inverse & 255,
                    inverse >> 8,
                    checksum & 255,
                    checksum >> 8,
                ]
            }
        ]
        return patch