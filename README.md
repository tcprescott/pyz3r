# pyz3r for Python 3.6, 3.7, and 3.8!
Pyz3r is an unofficial python abstraction library for interacting with the [alttpr.com](https://alttpr.com) API.

This allows developers to create applications that not only generate games on [alttpr.com](https://alttpr.com),
but also create the ROM as well using the patch data provided by the website.

## Installation
This module is available on PyPI.  It can be installed via pip:

`pip install pyz3r`

## Compatiblity
This library has been tested on both Linux (Centos 7) and Windows on Python 3.6.  Python 3.7 should also work, though it hasn't been as extensively tested.  An internet connection is required so it can communicate with alttpr.com.

## Disclaimer(s)
This is an unofficial tool.  Please do not submit bug reports on the official ALTTPR repository Github for issues that
are related to the use of this library!

If something is broken, please make sure it isn't related to this library before posting the bug report on the
alttp_vt_randomizer repository.  Feel free to post the bug here first if you're unsure.

Using this library to patch a ROM for racing may not be permitted.
Its best to check with an official before using it for racing.

Finally, this library may break when new versions of the Link to the Past Randomizer are released.  This version
was tested with v31, however it may cease to function in later releases.  If it does, please submit a Github issue!


## Usage
Basic usage is fairly simple.

First you'll need to either generate a new seed or use the hash of a previous seed to get a game.

### Initiating an Item Randomizer seed
The below example will generate an item randomizer game with a list of settings:
```python
import pyz3r

async def main():
    seed = await pyz3r.alttpr(
        settings={
            "glitches": "none",
            "item_placement": "advanced",
            "dungeon_items": "standard",
            "accessibility": "items",
            "goal": "ganon",
            "crystals": {
                "ganon": "random",
                "tower": "4"
            },
            "mode": "open",
            "entrances": "none",
            "hints": "on",
            "weapons": "randomized",
            "item": {
                "pool": "normal",
                "functionality": "normal"
            },
            "tournament": True,
            "spoilers": "off",
            "lang":"en",
            "enemizer": {
                "boss_shuffle":"none",
                "enemy_shuffle":"none",
                "enemy_damage":"default",
                "enemy_health":"default"
            }
        }
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

This will give you a list of item randomizer options as a dictionary:
```python
pyz3r.alttpr().settings()
```


### Loading an already generated game
If the game you want to work with has already been generated, you can load the hash like this:

```python
import pyz3r

async def main()
    seed = await pyz3r.alttpr(
        hash='zDvxWLLEMa'
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### Getting the code display and URL

This will return to you a list of strings with the "code" that appears on the file select screen.

```python
code = seed.code
print("Hash: [{hash}]".format(
    hash = ' | '.join(code)
))
```
Output:
`Hash: [Heart | Empty Bottle | Somaria | Ice Rod | Boots]`

You can also get the url quickly as well:

```python
url = seed.url
print("Permalink: {url}".format(
    url = url
))
```
Output:
`Permalink: https://alttpr.com/h/zDvxWLLEMa`


### Accessing seed data

You can access the seed's data via the `data` variable in the alttpr class.  The example below will print the dictionary that has the seed's spoiler data (if available).

```python
print(seed.data['spoiler'])
```

### Patching

This is the meat and potatoes of the library.  There are two ways, the easy and advanced way.

#### Easy patching

You'll first want to read your unmodified Japan 1.0 ROM of Link to the Past.  `read_rom()` will checksum the file to ensure its the correct ROM.

```python
base_rom = await pyz3r.rom.read("path/to/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
```

`base_rom` will be an array of integers representing the bytes of the original ROM.

You'll then want to use `create_patched_game` to apply all of the patches required to randomize and customize the ROM.
```python
patched_rom = await seed.create_patched_game(
    base_rom,  
    heartspeed='normal',
    heartcolor='red',
    spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
    music=False, # true or false, defaults true
    quickswap=False,
    menu_speed='normal'
)
```

Here you can customize the following:

0. `patchrom_array` - Required.  This is an array of bits that have your original Japan 1.0 ROM.  The `pyz3r.romfile.read()` function.
1. `heartspeed` - Optional. The low health beep speed.  Acceptable values are `'off'`, `'quarter'`, `'half'`, `'double'`, or `'normal'`.  Defaults is `'normal'`.
2. `heartcolor` - Optional. The color of your hearts.  Acceptable values are `'red'`, `'blue'`, `'green'`, or `'yellow'`.  Default is `'red'`.
3. `spritename` - Optional. The sprite to use.  Acceptable values are the `name` keys in the json file at https://alttpr.com/sprites.  Default is `'Link'`.
4. `music` - Optional. Whether music should play.  Acceptable values are `True` and `False`. `False` allows MSU-1 music to work correctly.  Default is `True`.
5. `quickswap` - Optional.  Enable quickswap.  Only works on non-tournament games or entrance shuffle.  Acceptable values are `True` and `False`.  Default is `False`.
6. `menu_speed` - Optional.  This is the menu speed setting.  Only works on non-tournament games.  Acceptable values are `instant`, `fast`, `normal`, `slow`.  Default is `normal`.

The result of `create_patched_game` is an array of integers representing the fully patched ROM.

Finally, you can write the ROM to a new file:
```python
pyz3r.romfile.write(patched_rom, "path/to/patched_rom.sfc")
```

#### Advanced patching
If you have a patched game, and just want to customize the already patched game, this library lets you do that too.

The following example will let you bring in an already patched game and let you customize the heart speed, heart color, sprite, and music.

```python
import pyz3r
from pyz3r.patch import patch

rom = pyz3r.romfile.read('path/to/rom.sfc',verify_checksum=False)

#apply the heart speed change
rom = patch.apply(
    rom=rom,
    patches=patch.heart_speed('half')
)

#apply the heart color change
rom = patch.apply(
    rom=rom,
    patches=patch.heart_color('blue')
)

#apply the sprite, retrieves a sprite from the alttpr website
rom = patch.apply(
    rom=rom,
    patches=patch.sprite(
        spr=pyz3r.alttpr().get_sprite('Negative Link')
    )
)

#apply the music
rom = patch.apply(
    rom=rom,
    patches=patch.music(True)
)

# apply menu speed
rom = patch.apply(
    rom=patchrom_array,
    patches=patch.menu_speed('normal')
)

# apply quickswap
rom = patch.apply(
    rom=patchrom_array,
    patches=patch.quickswap(False)
)

pyz3r.romfile.write(rom,'path/to/patched_rom.sfc')
```

### Using the customizer
The ALttPR website has a feature where a player may customize a game, including choosing starting equipment, item locations, game settings, drops and prizepack customization.  This library has a feature that allows you to generate games using the settings saved on alttpr.com's customizer.

To use it,  you'll want to read a `customizer-settings.json` file that was saved from alttpr.com, then use the provided function `customizer.convert2settings()` to convert the json file to something that can be be used for game generation.

`tournament` can be set to True to generate the game as a race rom.  This will cause the spoiler log to be unavailable,
along with scrambling the item table within the ROM.

```python
import json
import pyz3r

f = open('customizer-settings.json', "r")
customizer_settings = json.loads(f.read())
f.close()

seed = pyz3r.alttpr(
    settings=pyz3r.customizer.convert2settings(customizer_save=customizer_settings, tournament=False)
)
```

### Mystery seeds

Want to build your own mystery games without using SahasrahBot?  The pyz3r module now supports mystery games!

Just use the new `pyz3r.mystery.generate_random_settings()` function and pass in the weights you wish to use.  It'll output a dictionary can be fed into a into `pyz3r.alttpr()`.

```python
settings=pyz3r.mystery.generate_random_settings(
    weights={
        "glitches_required": {
            "none": 100,
            "overworld_glitches": 0,
            "major_glitches": 0,
            "no_logic": 0
        },
        "item_placement": {
            "basic": 25,
            "advanced": 75
        },
        "dungeon_items": {
            "standard": 60,
            "mc": 10,
            "mcs": 10,
            "full": 20
        },
        "accessibility": {
            "items": 60,
            "locations": 10,
            "none": 30
        },
        "goals": {
            "ganon": 40,
            "fast_ganon": 20,
            "dungeons": 10,
            "pedestal": 20,
            "triforce-hunt": 10
        },
        "tower_open": {
            "0": 5,
            "1": 5,
            "2": 5,
            "3": 5,
            "4": 5,
            "5": 5,
            "6": 5,
            "7": 50,
            "random": 15
        },
        "ganon_open": {
            "0": 5,
            "1": 5,
            "2": 5,
            "3": 5,
            "4": 5,
            "5": 5,
            "6": 5,
            "7": 50,
            "random": 15
        },
        "world_state": {
            "standard": 35,
            "open": 35,
            "inverted": 20,
            "retro": 10
        },
        "entrance_shuffle": {
            "none": 60,
            "simple": 7,
            "restricted": 10,
            "full": 10,
            "crossed": 10,
            "insanity": 2
        },
        "boss_shuffle": {
            "none": 60,
            "simple": 10,
            "full": 10,
            "random": 20
        },
        "enemy_shuffle": {
            "none": 60,
            "shuffled": 20,
            "random": 20
        },
        "hints": {
            "on": 50,
            "off": 50
        },
        "weapons": {
            "randomized": 40,
            "assured": 40,
            "vanilla": 15,
            "swordless": 5
        },
        "item_pool": {
            "normal": 80,
            "hard": 15,
            "expert": 5,
            "crowd_control": 0
        },
        "item_functionality": {
            "normal": 80,
            "hard": 15,
            "expert": 5
        },
        "enemy_damage": {
            "default": 80,
            "shuffled": 10,
            "random": 10
        },
        "enemy_health": {
            "default": 80,
            "easy": 5,
            "hard": 10,
            "expert": 5
        }
    }
)

seed = await pyz3r.alttpr(settings=settings)
print(seed.url)
```

### Getting a formatted spoiler log

If a game is generated where spoilers is set to `on` or `generate`, you may retrieve an Ordered Dictionary of the spoiler log with QOL enhancements used during the spoiler tournament.

```python
spoiler = seed.get_formatted_spoiler()
```

 You may then write this to whatever you see fit.

### Generating a Super Metroid + A Link to the Past Combo Randomizer

```python
from pyz3r.sm import sm

seed = await sm(
    settings={
        "smlogic": "normal",
        "goal": "defeatboth",
        "swordlocation": "randomized",
        "morphlocation": "randomized",
        "seed": "",
        "race": "true",
        "gamemode": "normal",
        "players": "1"
    },
    randomizer='smz3',
)
print(seed.url)
print(seed.code)
```

### Generating a Super Metroid Varia randomizer game

Only generating, not retrieving, SM Varia randomizer games is supported at this time.  ROM patching is also not supported.

Usage is pretty simple.

```python
from pyz3r.smvaria import SuperMetroidVaria
seed = await SuperMetroidVaria.create(
    skills_preset='regular',
    settings_preset='default'
)
print(seed.url)
```

## To do

0. Add a feature to verify a settings dictionary before attempting to generate a game.  This may become the default behavior, with the ability to override it.  This could also just be a separate function that could be invoked as well.
1. Improve logging.  Right now this library does zero logging on its own, which should be fixed.
2. Add unit tests.

## Credits and shoutouts

0. Veetorp, Karkat, ChristosOwen, Smallhacker, and Dessyreqt for making an incredible randomizer.
1. This work is dedicated to my father.  May he rest in peace.
2. Jaysee87 for his input into specific functionality, and suggesting asyncio support for usage with discord bots.

Github for alttp_vt_randomizer: https://github.com/sporchia/alttp_vt_randomizer
Super Metroid + A Link to the Past Combo Randomizer: https://github.com/tewtal/SMZ3Randomizer
Super Metroid VARIA Randomizer: https://github.com/theonlydude/RandomMetroidSolver

For a "real"-world usage of this library, check out SahasrahBot at https://github.com/tcprescott/sahasrahbot
