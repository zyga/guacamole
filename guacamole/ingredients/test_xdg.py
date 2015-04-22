# encoding: utf-8
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

"""Tests for various parts of the XDG ingredient."""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from guacamole.core import Context
from guacamole.ingredients import xdg


class XDGBaseDirectorySpecTests(unittest.TestCase):

    """Tests for XDGBaseDirectorySpec."""

    def test_defaults_without_HOME(self):
        """Without HOME, all _HOME variables don't have defaults."""
        base_dirs = xdg.XDGBaseDirectorySpec({})
        self.assertIsNone(base_dirs.XDG_DATA_HOME)
        self.assertIsNone(base_dirs.XDG_CONFIG_HOME)
        self.assertIsNone(base_dirs.XDG_CACHE_HOME)
        self.assertEqual(
            base_dirs.XDG_DATA_DIRS, '/usr/local/share/:/usr/share/')
        self.assertEqual(base_dirs.XDG_CONFIG_DIRS, '/etc/xdg')
        self.assertIsNone(base_dirs.XDG_RUNTIME_DIR)

    def test_defaults_with_HOME(self):
        """With HOME, all _HOME variables have defaults."""
        base_dirs = xdg.XDGBaseDirectorySpec({'HOME': '/home/u'})
        self.assertEqual(base_dirs.XDG_DATA_HOME, '/home/u/.local/share')
        self.assertEqual(base_dirs.XDG_CONFIG_HOME, '/home/u/.config')
        self.assertEqual(base_dirs.XDG_CACHE_HOME, '/home/u/.cache')
        self.assertEqual(
            base_dirs.XDG_DATA_DIRS, '/usr/local/share/:/usr/share/')
        self.assertEqual(base_dirs.XDG_CONFIG_DIRS, '/etc/xdg')
        self.assertIsNone(base_dirs.XDG_RUNTIME_DIR)

    def test_defines_bypass_defaults(self):
        """Defining particular XDG_ variables makes bypasses defaults."""
        base_dirs = xdg.XDGBaseDirectorySpec({
            'HOME': '/home/u/',
            'XDG_DATA_HOME': '/home/u/custom/data',
            'XDG_CONFIG_HOME': '/home/u/custom/config',
            'XDG_CACHE_HOME': '/home/u/custom/cache',
            'XDG_DATA_DIRS': '/custom/data',
            'XDG_CONFIG_DIRS': '/custom/config',
            'XDG_RUNTIME_DIR': '/custom/runtime',
            })
        self.assertEqual(base_dirs.XDG_DATA_HOME, '/home/u/custom/data')
        self.assertEqual(base_dirs.XDG_CONFIG_HOME, '/home/u/custom/config')
        self.assertEqual(base_dirs.XDG_CACHE_HOME, '/home/u/custom/cache')
        self.assertEqual(base_dirs.XDG_DATA_DIRS, '/custom/data')
        self.assertEqual(base_dirs.XDG_CONFIG_DIRS, '/custom/config')
        self.assertEqual(base_dirs.XDG_RUNTIME_DIR, '/custom/runtime')


class XDGTests(unittest.TestCase):

    """Tests for XDG."""

    def setUp(self):
        """Common setup code."""
        self.ingredient = xdg.XDG()
        self.context = Context()

    def test_added(self):
        """Calling XDG.added() registers the ``xdg_base`` object"""
        self.ingredient.added(self.context)
        self.assertIsInstance(self.context.xdg_base, xdg.XDGBaseDirectorySpec)
