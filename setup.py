import setuptools
from src.version import *

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="ScreenPinKit",
    version=VERSION,
    keywords="pyqt ScreenPinKit screenshot screen-paint",
    author="YaoXuanZhi",
    author_email="yaoxuanzhi@outlook.com",
    description="A mini screenshot and annotation tool that incorporates ideas from Snipaste, Excalidraw, ShareX, and others.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPLv3",
    url="https://github.com/YaoXuanZhi/ScreenPinKit",
    packages=setuptools.find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "scipy",
        "pillow<=9.4.0",
        "PyQt-Fluent-Widgets",
        "system_hotkey",
    ],
    extras_require = {
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    project_urls={
        'Documentation': 'https://github.com/YaoXuanZhi/ScreenPinKit/wiki',
        'Source Code': 'https://github.com/YaoXuanZhi/ScreenPinKit',
        'Bug Tracker': 'https://github.com/YaoXuanZhi/ScreenPinKit/issues',
    }
)
