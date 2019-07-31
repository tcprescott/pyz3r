import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="pyz3r",
    version="3.1.0",
    author="Thomas Prescott",
    author_email="tcprescott@gmail.com",
    description="A python module for interacting with alttpr.com, such as generating new z3r games, and patching existing games.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tcprescott/pyz3r",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests','aiofiles','aiohttp'],
)