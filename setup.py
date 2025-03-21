"""
Setup script for building the iMessage PDF Extractor app bundle.
"""
from setuptools import setup
import py2app
import os
import sys

APP = ['messages_sync_app.py']
DATA_FILES = ['icon.png']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.png',
    'plist': {
        'CFBundleName': 'iMessage Sync',
        'CFBundleDisplayName': 'iMessage Sync',
        'CFBundleGetInfoString': 'Guide for syncing your iMessages',
        'CFBundleIdentifier': 'com.imessagesync.app',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHumanReadableCopyright': 'Created with love'
    },
    'packages': ['tkinter'],
    'includes': ['subprocess', 'threading', 'os', 'json', 'datetime']
}

setup(
    name='iMessage Sync',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['pillow'],
    author='iMessage Sync Team',
    description='A simple app to guide iMessage syncing'
) 