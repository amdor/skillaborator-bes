#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'src', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='skillaborator-bes',
    version=get_version(),
    description='Skill evaluator backend service',
    long_description='',
    author='Zsolt Deak',
    url='https://github.com/amdor/skillaborator-bes',
    scripts=[],
    packages=find_packages(exclude=['tests*']),
    package_data={},
    include_package_data=False,
    install_requires=[],
    license="The MIT License (MIT)",
    classifiers=[
        'Development Status :: 2 - Work in progress',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8.1',
    ]
)