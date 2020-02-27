#!/usr/bin/env python
# encoding: utf-8

import codecs
import re
from os.path import dirname, join
from setuptools import setup, find_packages


def find_version(*path_parts):
    """
    Get current blockchain backend src version.

    :param tuple path_parts: path parts for version module.
    :return str: blockchain backend version.
    """
    version = read(*path_parts)
    match = re.search(r'^__version__ = ["\'](?P<version>[^"\']*)["\']', version, re.M)
    if not match.group('version'):
        msg = 'Unable to find module version.'
        raise RuntimeError(msg)
    return str(match.group('version'))


def read(*path_parts):
    """
    Get version module.

    :param tuple path_parts: path parts for version module.
    :return obj: module with version.
    """
    base_dir = dirname(__file__)
    file_path = join(base_dir, *path_parts)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='blockchain',
    version=find_version('src', '__init__.py'),
    description='Blockchain and cryptocurrency application',
    author='Sergio de Diego',
    author_email='sergiodediego@outlook.com',
    url='https://github.com/sdediego/blockchain',
    license='MIT',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.cfg']},
    install_requires=[
        'aiounittest',
        'asynctest',
        'cryptography',
        'fastapi',
        'pydantic',
        'requests',
        'tox',
        'uvicorn',
        'websockets'
    ],
    python_requires='>=3.7',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'run = src.bin.www',
        ],
    },
    keywords='api asynchronous backend blockchain client consensus cryptocurrency '
             'cryptography fastapi mining network nodes peer-to-peer proof-of-work '
             'python socket-server transactions transactions-pool wallet websocket',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Fastapi',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
