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

"""Tests for the argparse module."""

from __future__ import absolute_import, print_function, unicode_literals

import contextlib
import io
import sys
import unittest

from guacamole.core import Bowl
from guacamole.ingredients.argparse import ParserIngredient
from guacamole.ingredients.cmdtree import cmd_tree_node
from guacamole.recipes.cmd import Command


class _sub(Command):
    pass


class _cmd(Command):
    sub_commands = (('sub', _sub),)


class ParserIngredientTests(unittest.TestCase):

    """Tests for the ParserIngredient class."""

    def setUp(self):
        """Common initialization method."""
        self.bowl = Bowl([ParserIngredient()])
        # The next two lines implement a correctly-behaving cmdtree ingredient
        self.bowl.context.cmd_tree = cmd_tree_node(
            None, _cmd(), (cmd_tree_node('sub', _sub(), ()),))
        self.bowl.context.cmd_toplevel = self.bowl.context.cmd_tree.cmd_obj

    def test_regression_4(self):
        """
        Regression test for issue #4.

        A command with sub commands that is called without arguments
        should behave the same way (complaining about missing command)
        on both python 3 and python 2.

        .. seealso: https://github.com/zyga/guacamole/issues/4
        """
        with self.assertRaises(SystemExit) as cm:
            # [] is the argument list as if called on command-line
            with discard_stderr():
                self.bowl.eat([])
        self.assertEqual(cm.exception.args, (2, ))
        self.bowl.eat(['sub'])
        self.assertEqual(self.bowl.context.args.sub_command, 'sub')


@contextlib.contextmanager
def redirect_stderr(new_target):
    """
    Context manager for redirecting sys.stderr.

    :param new_target:
        The object to replace sys.stderr with.

    This context manager re-implements a Python 3.5 feature under identical
    name. As in the original implementation, native system-level stderr is
    not affected.
    """
    old_stderr = sys.stderr
    try:
        sys.stderr = new_target
        yield
    finally:
        sys.stderr = old_stderr


@contextlib.contextmanager
def discard_stderr():
    """
    Context manager for discarding sys.stderr.

    This method simply opens ``/dev/null`` (posix) or ``NUL`` (windows) and
    uses :func:`redirect_stderr()` to send all stderr data there.

    This context manager infuences python code only, native system-level stderr
    is not affected.
    """
    if sys.platform == 'win32':
        devnul = 'NUL'
    else:
        devnul = '/dev/null'
    with open(devnul, 'wt') as stream:
        with redirect_stderr(stream):
            yield
