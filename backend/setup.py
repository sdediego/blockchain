#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages


setup(
    name='blockchain',
    version='0.1.0',
    description='Blockchain and cryptocurrency application',
    author='Sergio de Diego',
    author_email='sergiodediego@outlook.com',
    url='https://github.com/sdediego/blockchain',
    license='MIT',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    package_data={'': ['*.txt']},
    install_requires=[],
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
