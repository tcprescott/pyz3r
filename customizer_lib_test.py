import json
from pyz3r import alttpr, romfile
from pyz3r.customizer import customizer

f = open('input/impossible.json', "r")
customizer_settings = json.loads(f.read())
f.close()

seed = alttpr(
    randomizer='item',
    settings=customizer.convert2settings(customizer_settings, tournament=False)
)

print("Permalink: {url}".format(
    url = seed.url
))
print("Hash: [{hash}]".format(
    hash = ' | '.join(seed.code())
))

# jpn10rom = romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

# patched_rom = seed.create_patched_game(
#     patchrom_array = jpn10rom,  
#     heartspeed=None, #can be off, quarter, half, double or normal.
#     heartcolor='red', #can be red, 
#     spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
#     music=False # true or false, defaults true
#     )
# romfile.write(patched_rom, "outputs/patched_rom.sfc")