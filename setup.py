#!/usr/bin/env python

"""
Setup script for building the Art Data Extract macOS application.
"""
from setuptools import setup
import sys

# Data files to include
DATA_FILES = [
    ('', ['icon.png', 'screenshot.png', 'LICENSE', 'README.md', 'requirements.txt', 
          'run.command', 'install.command', 'imessage_pdf_extract.py', 'imessage_pdf_extract_gui.py',
          'pdf_extractor.py', 'messages_sync_app.py'])
]

# Special handling for Python 3.13 which has removed Sequence from collections
if sys.version_info >= (3, 10):
    # For Python 3.10+, use collections.abc for Sequence
    APP = ['messages_sync_app.py']
else:
    # For older Python versions, original configuration
    APP = ['messages_sync_app.py']

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.png',
    'packages': ['tkinter'],
    'excludes': ['matplotlib', 'numpy', 'pandas', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
                'scipy', 'setuptools', 'numpydoc', 'pytz', 'sphinx', 'sphinx_rtd_theme',
                'jupyter_client', 'jupyter_core', 'notebook', 'ipykernel', 'ipython',
                'ipython_genutils', 'ipywidgets', 'nbconvert', 'nbformat', 'pygments'],
    'plist': {
        'CFBundleName': 'Art Data Extract',
        'CFBundleDisplayName': 'Art Data Extract',
        'CFBundleGetInfoString': 'Extract PDFs from iMessage conversations',
        'CFBundleIdentifier': 'com.keoles.artdataextract',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2023-2024 Spencer Keoleian. All Rights Reserved.',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
    },
}

setup(
    name='Art Data Extract',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    author='Spencer Keoleian',
    author_email='spencer.keoleian@gmail.com',
    description='A tool to extract PDFs from iMessage conversations',
    version='1.0.0',
) 