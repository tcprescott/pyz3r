import pyz3r

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
# seed = pyz3r.alttpr(settings=data)
seed = pyz3r.alttpr(hash='xry04EgKy5')

print("Permalink: {url}".format(
    url = seed.url()
))
print("Hash: [{hash}]".format(
    hash = ' | '.join(seed.get_code())
))
base_rom = seed.read_rom("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
patched_rom = seed.create_patched_game(
    base_rom,
    heartspeed=None,
    heartcolor='red'
    )
seed.write_rom(patched_rom, "outputs/patched_rom.sfc")
