from setuptools import setup, find_packages
from baleotp.version import __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="baleotp",
    version=__version__,
    author="Ali NabiPour",
    author_email="noyan.joun.89@gmail.com",
    description="Async client for sending OTPs via Bale API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ali-Nabi-Pour/baleotp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp",
        "logging"
    ],
)
