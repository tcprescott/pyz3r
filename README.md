# pyz3r for Python 3.6/3.7!
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
was tested with v30, however it may cease to function in later releases.  If it does, please submit a Github issue!


## Usage
Basic usage is fairly simple.

First you'll need to either generate a new seed or use the hash of a previous seed to get a game.

### Initiating an Item Randomizer seed
The below example will generate an item randomizer game with a list of settings:
```python
import pyz3r

seed = pyz3r.alttpr(
    randomizer='item', # optional, defaults to item
    settings={
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
)
```

This will give you a list of item randomizer options as a dictionary:
```python
pyz3r.alttpr(randomizer='item').settings()
```

### Intiating an Entrance Shuffle seed
This will generate an entrance shuffle game:
```python
import pyz3r

seed = pyz3r.alttpr(
    randomizer='entrance',
    settings={
        "logic":"NoGlitches",
        "difficulty":"normal",
        "variation":"retro",
        "mode":"open",
        "goal":"ganon",
        "shuffle":"restricted",
        "tournament":True,
        "spoilers":False,
        "enemizer":False,
        "lang":"en"
    }
)
```

This will give you a list of item randomizer options as a dictionary:
```python
pyz3r.alttpr(randomizer='entrance').settings()
```

### Loading an already generated game
If the game you want to work with has already been generated, you can load the hash like this:

```python
seed = pyz3r.alttpr(
    hash='zDvxWLLEMa'
)
```

### Getting the code display and URL

This will return to you a list of strings with the "code" that appears on the file select screen.

```python
code = seed.code()
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
base_rom = pyz3r.romfile.read("path/to/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
```

`base_rom` will be an array of integers representing the bytes of the original ROM.

You'll then want to use `create_patched_game` to apply all of the patches required to randomize and customize the ROM.
```python
patched_rom = seed.create_patched_game(
    base_rom,  
    heartspeed='normal',
    heartcolor='red',
    spritename='Link', #can be any sprite listed at https://alttpr.com/sprites
    music=False # true or false, defaults true
)
```

Here you can customize the following:

0. `patchrom_array` - Required.  This is an array of bits that have your original Japan 1.0 ROM.  The `pyz3r.romfile.read()` function.
1. `heartspeed` - Optional. The low health beep speed.  Acceptable values are `'off'`, `'quarter'`, `'half'`, `'double'`, or `'normal'`.  Defaults is `'normal'`.
2. `heartcolor` - Optional. The color of your hearts.  Acceptable values are `'red'`, `'blue'`, `'green'`, or `'yellow'`.  Default is `'red'`.
3. `spritename` - Optional. The sprite to use.  Acceptable values are the `name` keys in the json file at https://alttpr.com/sprites.  Default is `'Link'`.
4. `music` - Optional. Whether music should play.  Acceptable values are `True` and `False`. `False` allows MSU-1 music to work correctly.  Default is `True`.

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
from pyz3r.customizer import customizer

f = open('customizer-settings.json', "r")
customizer_settings = json.loads(f.read())
f.close()

seed = pyz3r.alttpr(
    randomizer='item',
    settings=customizer.convert2settings(customizer_save=customizer_settings, tournament=False)
)
```

As of v30, the customizer only works with the item randomizer.  There may be unexpected results if you try this with the entrance randomizer.

### Async Support
This library can also be used using asyncio (via the aiofiles and aiohttp library), which may be useful for bots that use asyncio (such as discord.py).  The syntax is very similar, with a two notable differences.

```python
import pyz3r
import asyncio

async def test_retrieve_game():
    seed = await pyz3r.alttpr(
        hash='zDvxWLLEMa'
    )

    print("Permalink: {url}".format(
        url = seed.url
    ))
    print("Hash: [{hash}]".format(
        hash = ' | '.join(await seed.code())
    ))

    print(seed.data['spoiler'])

    jpn10rom = await pyz3r.romfile.read("base_rom/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
    patched_rom = await seed.create_patched_game(
        patchrom_array = jpn10rom,  
        heartspeed=None, #can be off, quarter, half, double or normal.
        heartcolor='red', #can be red, 
        spritename='Negative Link', #can be any sprite listed at https://alttpr.com/sprites
        music=False # true or false, defaults true
        )
    await pyz3r.romfile.write(patched_rom, "outputs/patched_rom.sfc")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_retrieve_game())
```

The most notable changes are using asyncio's await syntax and using `pyz3r.alttpr()` and `pyz3r.romfile` instead.

## To do

0. Add a feature to verify a settings dictionary before attempting to generate a game.  This may become the default behavior, with the ability to override it.  This could also just be a separate function that could be invoked as well.
1. Right now Quickswap and Menu Speed options are not available. If they were, the behavior of this library would be for them **not** to function on race seeds.  I figure few people use these features, so they won't be in the initial release of pyz3r.
2. Add a shortcut for pulling the data for the daily game.  This would likely have to be scraped since it doesn't appear to be any API endpoint for this.
3. Improve logging.  Right now this library does zero logging on its own, which should be fixed.
4. Add unit tests.

## Credits and shoutouts

0. Veetorp, Karkat, ChristosOwen, Smallhacker, and Dessyreqt for making an incredible randomizer.
1. The mods at the ALTTPR discord (https://discord.gg/alttprandomizer).
2. This work is dedicated to my father.  May he rest in peace.
3. Jaysee87 for his input into specific functionality, and suggesting asyncio support for usage with discord bots.

Github for alttp_vt_randomizer: https://github.com/sporchia/alttp_vt_randomizer