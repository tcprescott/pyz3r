"""Tests for pyz3r.rom module."""

import pytest
import tempfile
import os
from pyz3r.rom import Rom
from pyz3r.exceptions import Pyz3rException


class TestRomBasic:
    """Test basic Rom operations."""

    def test_rom_write_byte(self):
        """Test writing a single byte to ROM."""
        # Create a temporary ROM file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            # Write a minimal ROM (2MB)
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            rom.write_byte(0x100, 0xFF)
            assert rom.rom[0x100] == 0xFF
        finally:
            os.unlink(temp_path)

    def test_rom_write_bytes(self):
        """Test writing multiple bytes to ROM."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            rom.write_bytes(0x100, [0x01, 0x02, 0x03])
            assert rom.rom[0x100] == 0x01
            assert rom.rom[0x101] == 0x02
            assert rom.rom[0x102] == 0x03
        finally:
            os.unlink(temp_path)

    def test_rom_write_to_file(self):
        """Test writing ROM to a file."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        output_path = temp_path + '.out'
        try:
            rom = Rom(temp_path)
            rom.write_byte(0x100, 0xAB)
            rom.write_to_file(output_path)
            
            # Verify the output file
            with open(output_path, 'rb') as f:
                data = f.read()
                assert data[0x100] == 0xAB
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_rom_expand_too_small(self):
        """Test expanding ROM when already larger than target."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (4 * 1024 * 1024))  # 4MB ROM
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            with pytest.raises(Pyz3rException):
                rom.expand(2)  # Try to expand to 2MB (smaller than current)
        finally:
            os.unlink(temp_path)


class TestRomVersion:
    """Test ROM version detection."""

    def test_rom_version_default(self):
        """Test ROM version detection for versioned ROM."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            # Create a ROM with version info
            rom_data = bytearray(2 * 1024 * 1024)
            # Set version bytes at 0x7FE2-0x7FE3 to version 4
            rom_data[0x7FE2] = 0x04
            rom_data[0x7FE3] = 0x00
            f.write(rom_data)
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            assert rom.rom_version == 4
        finally:
            os.unlink(temp_path)

    def test_rom_version_unversioned(self):
        """Test ROM version detection for unversioned ROM."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            # Create a ROM with 0xFFFF at version bytes (unversioned)
            rom_data = bytearray(2 * 1024 * 1024)
            rom_data[0x7FE2] = 0xFF
            rom_data[0x7FE3] = 0xFF
            f.write(rom_data)
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            assert rom.rom_version == 0
        finally:
            os.unlink(temp_path)


class TestRomSettings:
    """Test ROM setting methods."""

    def test_heart_speed_settings(self):
        """Test heart speed setting values."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            
            rom.heart_speed('off')
            assert rom.rom[0x180033] == 0
            
            rom.heart_speed('double')
            assert rom.rom[0x180033] == 16
            
            rom.heart_speed('normal')
            assert rom.rom[0x180033] == 32
            
            rom.heart_speed('half')
            assert rom.rom[0x180033] == 64
            
            rom.heart_speed('quarter')
            assert rom.rom[0x180033] == 128
        finally:
            os.unlink(temp_path)

    def test_music_setting(self):
        """Test music enable/disable."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            
            rom.music(True)
            assert rom.rom[0x18021a] == 0x00
            
            rom.music(False)
            assert rom.rom[0x18021a] == 0x01
        finally:
            os.unlink(temp_path)

    def test_quickswap_setting(self):
        """Test quickswap enable/disable."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            
            rom.quickswap(False)
            assert rom.rom[0x18004b] == 0x00
            
            rom.quickswap(True)
            assert rom.rom[0x18004b] == 0x01
        finally:
            os.unlink(temp_path)

    def test_menu_speed_settings(self):
        """Test menu speed setting values."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.sfc') as f:
            f.write(b'\x00' * (2 * 1024 * 1024))
            temp_path = f.name

        try:
            rom = Rom(temp_path)
            
            rom.menu_speed('instant')
            assert rom.rom[0x180048] == 0xE8
            
            rom.menu_speed('fast')
            assert rom.rom[0x180048] == 0x10
            
            rom.menu_speed('normal')
            assert rom.rom[0x180048] == 0x08
            
            rom.menu_speed('slow')
            assert rom.rom[0x180048] == 0x04
        finally:
            os.unlink(temp_path)
