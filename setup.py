import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="pyz3r",
    version="7.0.0",
    author="Thomas Prescott",
    author_email="tcprescott@gmail.com",
    description="A python module for interacting with the web API of various randomizers, such as https://alttpr.com or https://samus.link.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tcprescott/pyz3r",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        'aiofiles',
        'aiohttp',
        'python-bps-continued>=7',
        'slugid',
        'tenacity'
    ]
)
