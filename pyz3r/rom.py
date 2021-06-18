import io
import itertools

import bps.apply

from .exceptions import Pyz3rException


class Rom(object):
    def __init__(self, input_filename):
        self.read(input_filename)

    def read(self, filename: str):
        with open(filename, "rb") as f:
            self.rom = bytearray(f.read())

    def write_to_file(self, path: str):
        with open(path, "wb") as f:
            f.write(self.rom)

    def apply_bps_patch(self, patch: bytes):
        """Applies a patch, which is a bps

        Arguments:
            patch {bytes} -- A series of bytes representing a bps patch
        """
        # create "files" for apply_to_files
        # although there is an apply_to_bytearrays it does not perform CRC
        # validation of input or output, apply_to_files does.
        patch_file = io.BytesIO(patch)
        source_file = io.BytesIO(bytes(self.rom))
        target_file = io.BytesIO()

        bps.apply.apply_to_files(patch_file, source_file, target_file)
        target_file.seek(0)
        self.rom = bytearray(target_file.read())

    def apply_dict_patches(self, patches: list):
        """Applies a patch, which is a list of dictionaries

        Arguments:
            patches {list} -- A list of dictionaries that depict of set of patches to be applied to the ROM.
        """
        for patch in patches:
            offset = int(list(patch.keys())[0])
            values = list(patch.values())[0]
            self.write_bytes(offset, values)

    def write_byte(self, offset, value):
        self.rom[offset] = value

    def write_bytes(self, offset, values):
        for idx, value in enumerate(values):
            self.write_byte(offset + idx, value)

    def heart_speed(self, speed='half'):
        """Set the low-health warning beep interval.

        Keyword Arguments:
            speed {str} -- Chose the speed at which the low health warning beeps.
                Options are 'off', 'double', 'normal', 'half', and 'quarter'. (default: {'half'})
        """
        sbyte = {
            'off': 0,
            'double': 16,
            'normal': 32,
            'half': 64,
            'quarter': 128,
        }
        self.write_byte(0x180033, sbyte[speed])

    def heart_color(self, color='red'):
        """Set the color of the hearts on the player's HUD.

        Keyword Arguments:
            color {str} -- The heart color.  Options are 'red', 'blue', 'green', and 'yellow' (default: {'red'})
        """

        cbyte = {
            'blue': [44, 13],
            'green': [60, 25],
            'yellow': [40, 9],
            'red': [36, 5],
        }

        byte = cbyte[color][0]
        file_byte = cbyte[color][1]

        self.write_byte(0x6fa1e, byte)
        self.write_byte(0x6fa20, byte)
        self.write_byte(0x6fa22, byte)
        self.write_byte(0x6fa24, byte)
        self.write_byte(0x6fa26, byte)
        self.write_byte(0x6fa28, byte)
        self.write_byte(0x6fa2a, byte)
        self.write_byte(0x6fa2c, byte)
        self.write_byte(0x6fa2e, byte)
        self.write_byte(0x6fa30, byte)
        self.write_byte(0x65561, file_byte)

    def music(self, music=True):
        """Enables, or disables, the in-game music.  Useful if you want to use an MSU-1 soundtrack instead.

        Keyword Arguments:
            music {bool} -- If true, music is enabled.  If false, the music id disabled. (default: {True})

        Returns:
            list -- a list of dictionaries indicating which ROM address offsets to write and what to write to them
        """

        self.write_byte(0x18021a, 0x00 if music else 0x01)

    def quickswap(self, quickswap=False):
        self.write_byte(0x18004b, 0x01 if quickswap else 0x00)

    def reduce_flashing(self, enable=False):
        self.write_byte(0x18017f, 0x01 if enable else 0x00)

    def menu_speed(self, speed='normal'):
        sbyte = {
            'instant': 0xE8,
            'fast': 0x10,
            'normal': 0x08,
            'slow': 0x04
        }
        self.write_byte(0x180048, sbyte[speed])
        self.write_byte(0x6dd9a, 0x20 if speed == 'instant' else 0x11)
        self.write_byte(0x6df2a, 0x20 if speed == 'instant' else 0x12)
        self.write_byte(0x6e0e9, 0x20 if speed == 'instant' else 0x12)

    def sprite(self, zspr):
        """Creates a patch for to replace Link's sprite with the contents of a ZSPR file.

        Arguments:
            spr {list} -- a bytes-like object of a ZSPR file
        """

        # stolen from VT's code
        gfx_offset = zspr[12] << 24 | zspr[11] << 16 | zspr[10] << 8 | zspr[9]
        palette_offset = zspr[18] << 24 | zspr[17] << 16 | zspr[16] << 8 | zspr[15]

        if self.rom[0x118000] == 0x02 and self.rom[0x118001] == 0x37 and self.rom[0x11801E] == 0x02 and self.rom[0x11801F] == 0x37:
            # skip past unicode title and author
            metadata_index = 0x1D
            junk = 2
            while metadata_index < gfx_offset and junk > 0:
                if zspr[metadata_index + 1] == 0 and zspr[metadata_index] == 0:
                    junk = junk - 1

                metadata_index = metadata_index + 2

            sprite_author_short = ""

            while metadata_index < gfx_offset and zspr[metadata_index] != 0x00:
                char = chr(zspr[metadata_index])
                sprite_author_short += char
                metadata_index = metadata_index + 1

            sprite_author_map = {
                " ": (0x9F, 0x9F), "0": (0x53, 0x79), "1": (0x54, 0x7A),
                "2": (0x55, 0x7B), "3": (0x56, 0x7C), "4": (0x57, 0x7D),
                "5": (0x58, 0x7E), "6": (0x59, 0x7F), "7": (0x5A, 0x80),
                "8": (0x5B, 0x81), "9": (0x5C, 0x82), "A": (0x5D, 0x83),
                "B": (0x5E, 0x84), "C": (0x5F, 0x85), "D": (0x60, 0x86),
                "E": (0x61, 0x87), "F": (0x62, 0x88), "G": (0x63, 0x89),
                "H": (0x64, 0x8A), "I": (0x65, 0x8B), "J": (0x66, 0x8C),
                "K": (0x67, 0x8D), "L": (0x68, 0x8E), "M": (0x69, 0x8F),
                "N": (0x6A, 0x90), "O": (0x6B, 0x91), "P": (0x6C, 0x92),
                "Q": (0x6D, 0x93), "R": (0x6E, 0x94), "S": (0x6F, 0x95),
                "T": (0x70, 0x96), "U": (0x71, 0x97), "V": (0x72, 0x98),
                "W": (0x73, 0x99), "X": (0x74, 0x9A), "Y": (0x75, 0x9B),
                "Z": (0x76, 0x9C), "'": (0x77, 0x9d), ".": (0xA0, 0xC0),
                "/": (0xA2, 0xC2), ":": (0xA3, 0xC3), "_": (0xA6, 0xC6)
            }

            sprite_author_short = sprite_author_short[:28].center(28, ' ').upper()
            sprite_author_bytes = [sprite_author_map[a] if a in sprite_author_map else (0x9F, 0x9F) for a in sprite_author_short]

            for idx, (upper, lower) in enumerate(sprite_author_bytes):
                self.write_byte(0x118002 + idx, upper)
                self.write_byte(0x118020 + idx, lower)

        self.write_bytes(0x80000, zspr[gfx_offset:gfx_offset + 28671])
        self.write_bytes(0xDD308, zspr[palette_offset:palette_offset + 120])
        self.write_bytes(0xDEDF5, zspr[palette_offset + 120:palette_offset + 120 + 4])

    def checksum(self):
        """Writes a patch that fixes a ROM's checksum.  This should be the last patch applied to a ROM before it is written.
        """

        sum_of_bytes = sum(self.rom[:32731]) + sum(self.rom[32736:])
        checksum = (sum_of_bytes + 510) & 65535
        inverse = checksum ^ 65535
        self.write_bytes(0x7fdc, [
            inverse & 255,
            inverse >> 8,
            checksum & 255,
            checksum >> 8,
        ])

    def expand(self, newlenmb):
        """Expands the byte list of a ROM to the specified number of megabytes, filling in the new space with zeroes.

        Arguments:
            rom {list} -- a list of bytes depicitng the rom

        Keyword Arguments:
            newlenmb {int} -- The size of the ROM should be, in megabytes.

        Raises:
            Pyz3rException -- Raised if the new length is shorter than the current size of the byte list.

        Returns:
            list -- a list of bytes depicitng the rom
        """

        newlen = int(newlenmb) * 1024 * 1024
        if len(self.rom) > newlen:
            raise Pyz3rException(f'ROM is already larger than {newlen}')
        diff = len(self.rom) - newlen
        if diff > 0:
            self.rom[newlen] = 0
        else:
            self.rom.extend(itertools.repeat(0, -diff))
            self.rom.append(0)
