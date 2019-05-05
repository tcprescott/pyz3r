from .misc import misc
from .exceptions import alttprException

import hashlib

class romfile:
    def read(srcfilepath, verify_checksum=True):
        """Reads a ROM and converts it to a list of bytes, preparing it for patching.
        
        Arguments:
            srcfilepath {str} -- A path (either relative or absolute) to a file on the filesystem to be read.
            verify_checksum {bool} -- Verify the checksum of the file to ensure it is an unheadered ALTTPR Japan 1.0 ROM.
        
        Raises:
            alttprException -- Returns if the sha256 checksum does not match a ALTTPR Japan 1.0 ROM.
        
        Returns:
            list -- A list of bytes depicting the read ROM file.
        """
        with open(srcfilepath,"rb") as f:
            baserom_array = list(f.read())
        if verify_checksum:
            if len(baserom_array) == 1049088:
                baserom_array = baserom_array[512:]
            expected_rom_sha256='794e040b02c7591b59ad8843b51e7c619b88f87cddc6083a8e7a4027b96a2271'
            sha256_hash = hashlib.sha256()
            sha256_hash.update(bytes(baserom_array))
            if not sha256_hash.hexdigest() == expected_rom_sha256:
                raise alttprException('Expected checksum "{expected_rom_sha256}", got "{actual_checksum}" instead.  Verify the source ROM is an unheadered Japan 1.0 Link to the Past ROM.'.format(
                    expected_rom_sha256=expected_rom_sha256,
                    actual_checksum=sha256_hash.hexdigest()
                ))
        return baserom_array 

    def write(rom, dstfilepath):
        """Writes a list of bytes to a file on the filesystem.
        
        Arguments:
            rom {list} -- a list of bytes depicitng the rom
            dstfilepath {str} -- A path (either relative or absolute) to a file on the filesystem to be written.
        """

        fw = open(dstfilepath,"wb")
        patchrom = bytes()
        for idx, chunk_array in enumerate(misc.chunk(rom,256)):
            patchrom += bytes(chunk_array)
        fw.write(patchrom)
        fw.close

