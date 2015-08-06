#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of Guacamole.
#
# Copyright 2012-2015 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# Guacamole is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3,
# as published by the Free Software Foundation.
#
# Guacamole is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Guacamole.  If not, see <http://www.gnu.org/licenses/>.
"""setup for guacamole."""

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='guacamole',
    version='0.9',
    description='Guacamole is an command line tool library for Python',
    long_description=readme + '\n\n' + history,
    author='Zygmunt Krynicki',
    author_email='me@zygoon.pl',
    url='https://github.com/zyga/guacamole',
    packages=['guacamole', 'guacamole.ingredients', 'guacamole.recipes'],
    package_dir={'guacamole': 'guacamole'},
    include_package_data=True,
    license="LGPLv3",
    zip_safe=True,
    keywords='argparse cli tool command sub-command subcommand',
    tests_require=([
        # XXX: we don't depend on funcsigs but apparently mocks does without
        # properly declaring it. When I run ./setup.py test on Python 2.7 I get
        # an import error on mock, failing to import funcsigs. Oddly enough
        # explicitly installing mock installs funcsigs.
        #
        # If this doesn't happen later, feel free to remove funcsigs.
        'funcsigs',
        'mock',
        'unittest2' if sys.version_info[0] == 2 else 'unittest2py3k',
    ] if sys.version_info[:2] <= (3, 3) else None),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        ('License :: OSI Approved :: GNU Lesser General Public License v3'
         ' (LGPLv3)'),
        'Natural Language :: English',
        'Natural Language :: Polish',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='guacamole',
)
