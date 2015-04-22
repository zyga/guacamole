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

"""Ingredient for arranging commands into a tree structure."""

from __future__ import absolute_import, print_function, unicode_literals

from guacamole.core import Ingredient


class CommandTreeIngredient(Ingredient):

    """
    Ingredient for arranging commands into a tree of instances.

    Since commands and sub-commands are specified as classes there has to be an
    ingredient that instantiates them and resolves all the naming ambiguities.
    This is it.

    This component acts early, in its :meth:`added()` method. It must be placed
    before the ``argparse`` component in the recipe.
    """

    def __init__(self, command):
        """Initialize the ingredient with a given top-level command."""
        self.command = command

    def added(self, context):
        """
        Ingredient method called before anything else.

        Here this method just builds the full command tree and stores it inside
        the context as the ``cmd_tree`` attribute. The structure of the tree is
        explained by the :func:`build_cmd_tree()` function.
        """
        context.cmd_tree = build_cmd_tree(self.command)


def build_cmd_tree(cmd_cls, cmd_name=None):
    """
    Build a tree of commands.

    :param cmd_cls:
        The Command class or object to start with.
    :param cmd_name:
        Hard-coded name of the command (can be None for auto-detection)
    :returns:
        A tree structure represented as tuple ``(cmd_obj, cmd_name, children)``
        Where ``cmd_obj`` is a Command instance, cmd_name is its name, if any
        (it might be None) and ``children`` is a tuple of identical tuples.

    Note that command name auto-detection relies on
    :meth:`guacamole.recipes.cmd.Command.get_cmd_name()`.

    Let's look at a simple git-like example, the ``example_cmd`` class provides
    a predicable repr method that doesn't care about object identity (which we
    don't care about in this example)::

        >>> from guacamole import Command
        >>>
        >>> class example_cmd(Command):
        >>>     def __repr__(self):
        >>>     return '<{}>'.format(self.__class__.__name__)
        >>>
        >>> class git_log(example_cmd):
        >>>     pass
        >>>
        >>> class git_stash_list(example_cmd):
        >>>     pass
        >>>
        >>> class git_stash(example_cmd):
        >>>     sub_commands = (('list', git_stash_list),)
        >>>
        >>> class git(example_cmd):
        >>>     sub_commands = (('log', git_log),
        >>>                     ('stash', git_stash))
        >>>
        >>> build_cmd_tree(git)
        (None, '<git>', (
            ('log', <git_log>, ()),
            ('stash', <git_stash>, (
                ('list', <git_stash_list>, ()),),),),)
    """
    if isinstance(cmd_cls, type):
        cmd_obj = cmd_cls()
    else:
        cmd_obj = cmd_cls
    if cmd_name is None:
        cmd_name = cmd_obj.get_cmd_name()
    return (cmd_name, cmd_obj, tuple([
        build_cmd_tree(subcmd_cls, subcmd_name)
        for subcmd_name, subcmd_cls in cmd_obj.get_sub_commands()]))
