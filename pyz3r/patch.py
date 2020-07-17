import bps.apply
import bps.io
import io

import itertools
from .exceptions import alttprException


def apply(rom, patches):
    """Applies a patch, which is a list of dictionaries

    Arguments:
        rom {list} -- A list of bytes depicting the ROM data to be patched.
        patches {list} -- A list of dictionaries that depict of set of patches to be applied to the ROM.

    Returns:
        list -- a list of bytes depicting the patched rom
    """
    for patch in patches:
        offset = int(list(patch.keys())[0])
        patch_values = list(patch.values())[0]
        for idx, value in enumerate(patch_values):
            rom[offset + idx] = value
    return rom

def apply_bps(rom, patches: bytes):
    """Applies a patch, which is a bps

    Arguments:
        rom {list} -- A list of bytes depicting the ROM data to be patched.
        patches {bytes} -- A series of bytes representing a bps patch

    returns:
        list -- a list of bytes depicting the patched rom
    """
    # create "files" for apply_to_files
    # although there is an apply_to_bytearrays it does not perform CRC
    # validation of input or output, apply_to_files does.
    patch_file = io.BytesIO(patches)
    source_file = io.BytesIO(bytes(rom))
    target_file = io.BytesIO()

    bps.apply.apply_to_files(patch_file, source_file, target_file)
    target_file.seek(0)
    return list(target_file.read())

def heart_speed(speed='half'):
    """Set the low-health warning beep interval.

    Keyword Arguments:
        speed {str} -- Chose the speed at which the low health warning beeps.
            Options are 'off', 'double', 'normal', 'half', and 'quarter'. (default: {'half'})

    Returns:
        list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
    """
    if speed is None:
        speed = 'normal'
    sbyte = {
        'off': 0,
        'double': 16,
        'normal': 32,
        'half': 64,
        'quarter': 128,
    }
    patch = [{
        '1572915': [sbyte[speed]]
    }]
    return patch

def heart_color(color='red'):
    """Set the color of the hearts on the player's HUD.

    Keyword Arguments:
        color {str} -- The heart color.  Options are 'red', 'blue', 'green', and 'yellow' (default: {'red'})

    Returns:
        list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
    """

    if color is None:
        color = 'red'
    cbyte = {
        'blue': [44, 13],
        'green': [60, 25],
        'yellow': [40, 9],
        'red': [36, 5],
    }
    byte = cbyte[color][0]
    file_byte = cbyte[color][1]
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

def music(music=True):
    """Enables, or disables, the in-game music.  Useful if you want to use an MSU-1 soundtrack instead.

    Keyword Arguments:
        music {bool} -- If true, music is enabled.  If false, the music id disabled. (default: {True})

    Returns:
        list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
    """

    return [{'1573402': [0 if music else 1]}]


def quickswap(quickswap=False):
    return [{'1572939': [1 if quickswap else 0]}]


def menu_speed(speed='normal'):
    if speed is None:
        speed = 'normal'
    sbyte = {
        'instant': 0xE8,
        'fast': 0x10,
        'normal': 0x08,
        'slow': 0x04
    }
    patch = [
        {'1572936': [sbyte[speed]]},
        {'449946': [0x20 if menu_speed == 'instant' else 0x11]},
        {'450346': [0x20 if menu_speed == 'instant' else 0x12]},
        {'450793': [0x20 if menu_speed == 'instant' else 0x12]}
        ]
    return patch

def sprite(spr):
    """Creates a patch for to replace Link's sprite with the contents of a XSPR or SPR file.

    Arguments:
        spr {list} -- a list of bytes that depicts a ZSPR or SPR file

    Returns:
        list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
    """

    if spr[:4] == [90, 83, 80, 82]:
        # stolen from VT's code
        gfx_offset = spr[12] << 24 | spr[11] << 16 | spr[10] << 8 | spr[9]
        palette_offset = spr[18] << 24 | spr[17] << 16 | spr[16] << 8 | spr[15]
        patch = [
            {'524288': spr[gfx_offset:gfx_offset + 28671]},
            {'905992': spr[palette_offset:palette_offset + 120]},
            {'912885': spr[palette_offset + 120:palette_offset + 120 + 3]}
        ]
    # Else treat it like a SPR file instead
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

def checksum(rom):
    """Writes a patch that fixes a ROM's checksum.  This should be the last patch applied to a ROM before it is written.

    Arguments:
        rom {list} -- a list of bytes depicitng the rom

    Returns:
            list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
    """

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

def expand(rom, newlenmb):
    """Expands the byte list of a ROM to the specified number of megabytes, filling in the new space with zeroes.

    Arguments:
        rom {list} -- a list of bytes depicitng the rom

    Keyword Arguments:
        newlenmb {int} -- The size of the ROM should be, in megabytes.

    Raises:
        alttprException -- Raised if the new length is shorter than the current size of the byte list.

    Returns:
        list -- a list of bytes depicitng the rom
    """

    newlen = int(newlenmb) * 1024 * 1024
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
    return rom
