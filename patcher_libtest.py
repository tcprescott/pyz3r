import pyz3r

# get settings without generating a game
# print(pyz3r.alttpr(randomizer='entrance').settings())

# print(pyz3r.alttpr(randomizer='item').get_patch_sprite(name='Eggplant'))

#generate a new game
# seed = pyz3r.alttpr(
#     baseurl='http://localhost:8000',
#     seed_baseurl=None,
#     settings={
#         "glitches": "none",
#         "item_placement": "advanced",
#         "dungeon_items": "standard",
#         "accessibility": "items",
#         "goal": "ganon",
#         "crystals": {
#             "ganon": "7",
#             "tower": "4"
#         },
#         "mode": "open",
#         "entrances": "none",
#         "hints": "on",
#         "weapons": "randomized",
#         "item": {
#             "pool": "normal",
#             "functionality": "normal"
#         },
#         "tournament": True,
#         "spoilers": False,
#         "lang":"en",
#         "enemizer": {
#             "boss_shuffle":"none",
#             "enemy_shuffle":"none",
#             "enemy_damage":"normal",
#             "enemy_health":"normal"
#         }
#     }
# )

seed = pyz3r.alttpr(
    baseurl='http://localhost:8000',
    seed_baseurl=None,
    hash='aO4v56yqwQ'
)
# seed = pyz3r.alttpr()


print("Permalink: {url}".format(
    url = seed.url
))
print("Hash: [{hash}]".format(
    hash = ' | '.join(seed.code())
))

# print(seed.data['spoiler'])

jpn10rom = pyz3r.romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")

patched_rom = seed.create_patched_game(
    patchrom_array = jpn10rom,  
    heartspeed='half', #can be off, quarter, half, double or normal.
    heartcolor='red', #can be red, 
    spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
    music=True # true or false, defaults true
    )
pyz3r.romfile.write(patched_rom, "outputs/patched_rom.sfc")
