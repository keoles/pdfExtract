#!/usr/bin/env python3

"""
Setup script for building the Art Data Extract macOS application.
"""
from setuptools import setup

APP = ['src/gui/messages_sync_app.py']
DATA_FILES = [
    'resources/icon.png',
    'resources/screenshot.png',
    'LICENSE',
    'README.md',
    'requirements.txt',
    'src/core/imessage_pdf_extract.py',
    'src/gui/imessage_pdf_extract_gui.py',
    'src/core/pdf_extractor.py'
]

OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter'],
    'includes': ['os', 'sys', 'subprocess', 'tkinter', 'sqlite3', 'datetime', 'time', 're', 'json', 'pathlib'],
    'iconfile': 'resources/icon.png',
    'plist': {
        'CFBundleName': 'Art Data Extract',
        'CFBundleDisplayName': 'Art Data Extract',
        'CFBundleGetInfoString': 'Extract PDFs from iMessage',
        'CFBundleIdentifier': 'com.keoles.artdataextract',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2023, All Rights Reserved',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14'
    }
}

setup(
    app=APP,
    name='Art Data Extract',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 