#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['apistar>=0.5']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="Ryan Anguiano",
    author_email='ryan.anguiano@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Contrib packages to add on to API Star.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='apistar contrib',
    name='apistar-contrib',
    packages=find_packages(include=['apistar_contrib']),
    python_requires='>=3.5',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ryananguiano/apistar-contrib',
    version='0.0.4',
    zip_safe=False,
)
