# filepath: setup.py
from setuptools import setup, find_packages

setup(
    name='osfm',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'win10toast',
        'plyer' # or whatever dependencies you have
    ],
    entry_points={
        'console_scripts': [
            'osfm = osfm.__main__:main',
        ],
    },
)