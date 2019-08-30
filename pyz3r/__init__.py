"""
ALTTPR API Wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper for the ALTTPR.com API.
"""

__title__ = 'pyz3r'
__author__ = 'Thomas Prescott'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2018-2019 Thomas Prescott'
__version__ = '4.0.0'

from .alttpr import alttpr
from .rom import romfile

from .alttpr import alttpr as async_alttpr
from .rom import romfile as async_romfile
