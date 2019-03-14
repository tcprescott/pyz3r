import pyz3r

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))

#generate a new game
seed = pyz3r.alttpr(
    randomizer='item', # optional, defaults to item
    settings={
        "difficulty": "hard",
        "enemizer": False,
        "logic": "NoGlitches",
        "mode": "inverted",
        "spoilers": False,
        "tournament": True,
        "variation": "key-sanity",
        "weapons": "uncle",
        "lang": "en"
    }
)
#generate an entrance shuffle game
# seed = pyz3r.alttpr(
#     randomizer='entrance',
#     settings={
#         "logic":"NoGlitches",
#         "difficulty":"normal",
#         "variation":"retro",
#         "mode":"open",
#         "goal":"ganon",
#         "shuffle":"restricted",
#         "tournament":True,
#         "spoilers":False,
#         "enemizer":False,
#         "lang":"en"
#     }
# )
# seed = pyz3r.alttpr(
#     randomizer='item',
#     hash='zDvxWLLEMa'
# )
# seed = pyz3r.alttpr()


print("Permalink: {url}".format(
    url = seed.url()
))
print("Hash: [{hash}]".format(
    hash = ' | '.join(seed.code())
))

print(seed.data['spoiler'])

base_rom = seed.read_rom("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
patched_rom = seed.create_patched_game(
    patchrom_array = base_rom,  
    heartspeed=None, #can be off, quarter, half, double or None.  None would default to normal speed.
    heartcolor='red', #can be red, 
    spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
    music=False # true or false, defaults true
    )
seed.write_rom(patched_rom, "outputs/patched_rom.sfc")
