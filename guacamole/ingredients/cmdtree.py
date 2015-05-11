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

import collections
import logging
import types

from guacamole.core import Ingredient


_logger = logging.getLogger("guacamole")

#: A named tuple for representing the hierarchy of commands.
#
# The ``cmd_obj`` field is an instance of a Command class.
# The ``cmd_name`` field is the effective name of the command.
# The ``children`` field is a tuple of cmd_tree_node tuples.
cmd_tree_node = collections.namedtuple(
    'cmd_tree_node', 'cmd_name cmd_obj children')


class CommandTreeBuilder(Ingredient):

    """
    Ingredient for arranging commands into a tree of instances.

    Since commands and sub-commands are specified as classes there has to be an
    ingredient that instantiates them and resolves all the naming ambiguities.
    Here it is.

    This component acts early, in its :meth:`added()` method.
    """

    def __init__(self, command):
        """
        Initialize the ingredient with a given top-level command.

        :param command:
            The command that is the top of a commad hierarchy.
        """
        self.command = command

    def added(self, context):
        """
        Ingredient method called before anything else.

        Here this method just builds the full command tree and stores it inside
        the context as the ``cmd_tree`` attribute. The structure of the tree is
        explained by the :func:`build_cmd_tree()` function.
        """
        context.cmd_tree = self._build_cmd_tree(self.command)
        context.cmd_toplevel = context.cmd_tree.cmd_obj
        # Collect spices from the top-level command
        for spice in context.cmd_toplevel.get_cmd_spices():
            context.bowl.add_spice(spice)

    def _build_cmd_tree(self, cmd_cls, cmd_name=None):
        """
        Build a tree of commands.

        :param cmd_cls:
            The Command class or object to start with.
        :param cmd_name:
            Hard-coded name of the command (can be None for auto-detection)
        :returns:
            A tree structure represented as tuple
                ``(cmd_obj, cmd_name, children)``
            Where ``cmd_obj`` is a Command instance, cmd_name is its name, if
            any (it might be None) and ``children`` is a tuple of identical
            tuples.

        Note that command name auto-detection relies on
        :meth:`guacamole.recipes.cmd.Command.get_cmd_name()`.

        Let's look at a simple git-like example::

            >>> from guacamole import Command

            >>> class git_log(Command):
            >>>     pass

            >>> class git_stash_list(Command):
            >>>     pass

            >>> class git_stash(Command):
            >>>     sub_commands = (('list', git_stash_list),)

            >>> class git(Command):
            >>>     sub_commands = (('log', git_log),
            >>>                     ('stash', git_stash))

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
        return cmd_tree_node(cmd_name, cmd_obj, tuple([
            self._build_cmd_tree(subcmd_cls, subcmd_name)
            for subcmd_name, subcmd_cls in cmd_obj.get_sub_commands()]))


class CommandTreeDispatcher(Ingredient):

    """
    Ingredient for dispatching commands hierarchically.

    This ingredient builds on the :class:`CommandTreeBuilder` ingredient. It
    implements the :meth:`dispatch()` method that recurses from the top (root)
    of the command tree down to the appropriate leaf, calling the invoke()
    method of each command.

    The process stops on the first command that returns a value other than
    None, raises an exception or until a leaf command is reached. THe ability
    to return early allows commands to perform some sanity checks or short-
    circuit execution that is hard to express using standard parser APIs.

    Lastly, a command can return a generator, this is treated as a sign that
    the generator implements a context-manager-like API. In this case the
    generator is called exactly twice and can be used to manage resources
    during the lifetime of all sub-commands.
    """

    def dispatch(self, context):
        """Dispatch execution to the invoke() method of selected commands."""
        return self._dispatch(context, 0)

    def _dispatch(self, context, level):
        # Find the command we're about to execute.
        try:
            command = getattr(context.args, 'command{}'.format(level))
        except AttributeError:
            return
        else:
            from guacamole.recipes.cmd import Command
            assert isinstance(command, Command)
        # Invoke the command we found, if any.
        _logger.debug("Invoking command %r", command)
        retval = command.invoked(context)
        # Interpret the return value to know what to do next
        if isinstance(retval, types.GeneratorType):
            # Generators are invoked "around" sub-commands.
            # This allows them to use context managers and prepare
            # the execution environment for sub-commands reliably.
            _logger.debug("Command %r uses generator-based invoke. "
                          "Invoking sub-commands (if any)", command)
            return self._dispatch_generator(context, level, retval, command)
        elif retval is None:
            # None is simply ignored and execution continues until a leaf
            # command is reached or until ...
            _logger.debug("Command %r returned None from invoke. "
                          "Invoking sub-commands (if any)", command)
            return self._dispatch_None(context, level, retval, command)
        else:
            # ... or until a non-None result is produced.
            _logger.debug("Command %r returned code %s, returning",
                          command, retval)
            return self._dispatch_other(context, level, retval, command)

    def _dispatch_generator(self, context, level, retval, command):
        # Generators are dispatched with two next() calls.
        # The first one is just there to start executing the code and reach
        # the (first and only) yield statement.
        next(retval)
        # Next, we dispatch the next sub-command.
        try:
            return self._dispatch(context, level + 1)
        finally:
            # Lastly, and this is done in a finally block to ensure it happens
            # in spite of exceptions being thrown. We call the generator again.
            try:
                next(retval)
            except StopIteration:
                pass
            else:
                _logger.error(
                    "BUG in %s.invoke(). "
                    "Each generator-based invoke() MUST use exactly "
                    "one yield statement.", command.__class__.__name__)

    def _dispatch_None(self, context, level, retval, command):
        return self._dispatch(context, level + 1)

    def _dispatch_other(self, context, level, retval, command):
        return retval
