#!/usr/bin/env python3
"""Setup script for HTMLArk."""

import re
from setuptools import setup

# Extract version number from source code
with open('htmlark.py', 'r') as f:
    source_code = f.read()
    version_regex = re.compile(r'''^\s*__version__\s*=\s*['"](\d.*)['"]''', re.MULTILINE)
    project_version = version_regex.search(source_code).group(1)

with open('README.rst', 'r') as f:
    readme_text = f.read()

setup(
    name="HTMLArk",
    version=project_version,
    description="Pack a webpage including support files into a single HTML file.",
    long_description=readme_text,
    url="https://github.com/BitLooter/htmlark",
    author="David Powell",
    author_email="BitLooter@users.noreply.github.com",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    keywords="development html webpage css javascript",
    py_modules=['htmlark'],
    install_requires=['beautifulsoup4'],
    extras_require={
        'parsers': ['lxml', 'html5lib'],
        'http': ['requests'],
    },
    entry_points={
        'console_scripts': [
            'htmlark = htmlark:_main_wrapper',
        ]
    }
)
