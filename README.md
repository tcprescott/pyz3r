# pyz3r for Python 3.6!
Pyz3r is an unofficial python abstraction library for interacting with the [alttpr.com](https://alttpr.com) API.

This allows developers to create applications that not only generate games on [alttpr.com](https://alttpr.com),
but also create the ROM as well using the patch data provided by the website.

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
    randomizer='item',
    hash='zDvxWLLEMa'
)
```

The `randomizer` argument will no longer be required once randomizer-type discovery is added.
For now you'll need to specify `item` (default) or `entrance`.

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
url = seed.url()
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
base_rom = seed.read_rom("path/to/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc")
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

0. `patchrom_array` - Required.  This is an array of bits that have your original Japan 1.0 ROM.  The `read_rom` function in the `pyz3r.alttpr()` class will create this for you.
1. `heartspeed` - Optional. The low health beep speed.  Acceptable values are `'off'`, `'quarter'`, `'half'`, `'double'`, or `'normal'`.  Defaults is `'normal'`.
2. `heartcolor` - Optional. The color of your hearts.  Acceptable values are `'red'`, `'blue'`, `'green'`, or `'yellow'`.  Default is `'red'`.
3. `spritename` - Optional. The sprite to use.  Acceptable values are the `name` keys in the json file at https://alttpr.com/sprites.  Default is `'Link'`.
4. `music` - Optional. Whether music should play.  Acceptable values are `True` and `False`. `False` allows MSU-1 music to work correctly.  Default is `True`.

The result of `create_patched_game` is an array of integers representing the fully patched ROM.

Finally, you can write the ROM to a new file:
```python
seed.write_rom(patched_rom, "path/to/patched_rom.sfc")
```

#### Advanced patching

Check out the `read_rom`, `write_rom`, and `create_patched_game` in the [library's init file](src/pyz3r/__init__.py) to see how you can stitch together the patch generator commands.  Maybe I'll write more documentation on these functions at a later time.

## To do

Right now Quickswap and Menu Speed options are not available.
If they were, the behavior of this library would be for them **not** to function on race seeds.
I figure few people use these features, so they won't be in the intial release of pyz3r.

When bringing in an already-generated game, automatically detect if its an item randomizer or entrance shuffle seed.

## Credits and shoutouts

0. Veetorp, Karkat, ChristosOwen, Smallhacker, and Dessyreqt for making an incredible randomizer.
1. The mods at the ALTTPR discord (https://discord.gg/alttprandomizer) for their hard work for the community.
2. This work is dedicated to my father.  May he rest in peace.

Github for alttp_vt_randomizer: https://github.com/sporchia/alttp_vt_randomizer