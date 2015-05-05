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

"""Tests for the cmdtree module."""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from guacamole.core import Bowl
from guacamole.ingredients.cmdtree import CommandTreeBuilder
from guacamole.recipes.cmd import Command


class _sub(Command):
    spices = ('mustard',)


class _cmd(Command):
    spices = ('salt', 'pepper')
    sub_commands = (('sub', _sub),)


class CommandTreeBuilderTests(unittest.TestCase):

    """Tests for the CommandTreeBuilder class."""

    def setUp(self):
        """Common initialization method."""
        self.bowl = Bowl([CommandTreeBuilder(_cmd())])
        self.bowl.eat()

    def test_build_command_tree(self):
        """check if a correct command tree is built."""
        cmd_obj = self.bowl.context.cmd_tree[1]
        sub_obj = self.bowl.context.cmd_tree[2][0][1]
        self.assertIsInstance(cmd_obj, _cmd)
        self.assertIsInstance(sub_obj, _sub)
        self.assertEqual(
            self.bowl.context.cmd_tree,
            (None, cmd_obj, (('sub', sub_obj, ()),)))

    def test_collect_spices(self):
        """check if spices are collected from top-level command only."""
        self.assertTrue(self.bowl.has_spice('salt'))
        self.assertTrue(self.bowl.has_spice('pepper'))
        self.assertFalse(self.bowl.has_spice('mustard'))
