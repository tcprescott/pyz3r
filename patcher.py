import requests
import json
import itertools
import time

start_time = time.time()

def get_hash(patches):
    seek = '1573395'
    for patch in patches:
        if seek in patch:
            return '{p[0]} | {p[1]} | {p[2]} | {p[3]} | {p[4]}'.format(
                p=list(map(lambda x: code_map[x], patch[seek][2:])))

def patch_rom(rom, patches):
    for patch in patches:
        offset = int(list(patch.keys())[0])
        for idx, value in enumerate(list(patch.values())[0]):
            assign(rom, offset+idx, int(value))
    return rom

def assign(lst, idx, value, fill=0):
    diff = len(lst) - idx
    if diff > 0:
        lst[idx] = value
    else:
        lst.extend(itertools.repeat(fill, -diff))
        lst.append(value)

def chunk(iterator, count):
    itr = iter(iterator)
    while True:
        yield tuple([next(itr) for i in range(count)])

data = {
        "difficulty": "hard",
        "enemizer": False,
        "logic": "NoGlitches",
        "mode": "open",
        "spoilers": False,
        "tournament": True,
        "variation": "key-sanity",
        "weapons": "uncle",
        "lang": "en"
    }
# data = '{"logic":"NoGlitches","difficulty":"normal","variation":"timed-ohko","mode":"open","goal":"triforce-hunt","weapons":"uncle","tournament":false,"spoilers":false,"enemizer":false,"lang":"en"}'

# req = requests.post(
#     url="https://alttpr.com/seed",
#     json=data
# )
req = requests.get(
    url='https://s3.us-east-2.amazonaws.com/alttpr-patches/xry04EgKy5.json'
)
seed_data = json.loads(req.text)
print(seed_data)

def get_base_patch():
    req = requests.get(
        url='https://alttpr.com/base_rom/settings'
    )
    base_file = json.loads(req.text)['base_file']
    req_patch = requests.get(
        url='https://alttpr.com/' + base_file
    )
    return json.loads(req_patch.text)

def get_heart_speed_patch(speed='default'):
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

def get_heart_color_patch(color='red'):
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
        {
            '457246': [byte]
        },
        {
            '457248': [byte]
        },
        {
            '457250': [byte]
        },
        {
            '457252': [byte]
        },
        {
            '457254': [byte]
        },
        {
            '457256': [byte]
        },
        {
            '457258': [byte]
        },
        {
            '457260': [byte]
        },
        {
            '457262': [byte]
        },
        {
            '457264': [byte]
        },
        {
            '415073': [file_byte]
        },
    ]
    return patch

def get_checksum_patch(rom):
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


code_map = {
    0: 'Bow',
    1: 'Boomerang',
    2: 'Hookshot',
    3: 'Bombs',
    4: 'Mushroom',
    5: 'Magic Powder',
    6: 'Ice Rod',
    7: 'Pendant',
    8: 'Bombos',
    9: 'Ether',
    10: 'Quake',
    11: 'Lamp',
    12: 'Hammer',
    13: 'Shovel',
    14: 'Flute',
    15: 'Bugnet',
    16: 'Book',
    17: 'Empty Bottle',
    18: 'Green Potion',
    19: 'Somaria',
    20: 'Cape',
    21: 'Mirror',
    22: 'Boots',
    23: 'Gloves',
    24: 'Flippers',
    25: 'Moon Pearl',
    26: 'Shield',
    27: 'Tunic',
    28: 'Heart',
    29: 'Map',
    30: 'Compass',
    31: 'Big Key'
}

print("Permalink: https://alttpr.com/h/{hash}".format(
    hash = seed_data['hash']
))

fr = open("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc","rb")
baserom = fr.read()
baserom_array = list(baserom)
fr.close

fw = open("outputs/patched_rom.sfc","wb")
patchrom_array = baserom_array
patchrom_array = patch_rom(patchrom_array,get_base_patch())
patchrom_array = patch_rom(patchrom_array,seed_data['patch'])
patchrom_array = patch_rom(patchrom_array,get_heart_speed_patch('default'))
patchrom_array = patch_rom(patchrom_array,get_heart_color_patch('red'))
assign(patchrom_array,2097151,0) #this will expand the ROM to 2MB
print("--- %s seconds ---" % (time.time() - start_time))
patchrom_array = patch_rom(patchrom_array,get_checksum_patch(patchrom_array))
print("--- %s seconds ---" % (time.time() - start_time))
patchrom = bytes()
for idx, chunk_array in enumerate(chunk(baserom_array,256)):
    patchrom += bytes(chunk_array)
fw.write(patchrom)
fw.close

print(get_hash(seed_data['patch']))
print("--- %s seconds ---" % (time.time() - start_time))