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
        'pydantic',
        'tox'
    ],
    python_requires='>=3.7',
    test_suite='tests',
    entry_points={},
    keywords='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
