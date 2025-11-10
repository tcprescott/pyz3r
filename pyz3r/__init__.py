"""
ALTTPR API Wrapper
~~~~~~~~~~~~~~~~~~~
A Python library for interacting with the ALTTPR.com API and other randomizer APIs.

This module provides a clean, type-safe interface for:
- Generating and retrieving ALTTPR (A Link to the Past Randomizer) seeds
- Creating patched ROM files with customizations
- Working with Super Metroid randomizers
- Generating mystery seeds with weighted settings
"""

__title__ = 'pyz3r'
__author__ = 'Thomas Prescott'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2018-2024 Thomas Prescott'
__version__ = '7.0.0'

from pyz3r.alttpr import ALTTPR
from pyz3r.sm import sm, smClass
from pyz3r.smvaria import SuperMetroidVaria
from pyz3r.rom import Rom
from pyz3r import mystery, customizer, rom, exceptions

__all__ = [
    'ALTTPR',
    'sm',
    'smClass',
    'SuperMetroidVaria',
    'Rom',
    'mystery',
    'customizer',
    'rom',
    'exceptions',
]
