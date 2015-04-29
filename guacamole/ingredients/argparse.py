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

"""
Ingredients for using arparse for parsing command line arguments.

This module contains two ingredients. The main one is the
:class:`ParserIngredient`. It is responsible for handling all of the command
line parsing and command argument registration. It is a part of the recipe
for the command class. Note that command dispatch is not handled by this
ingredient (see :class:`~guacamole.ingredients.cmdtree.CommandTreeIngredient`).

The second ingredient is :class:`AutocompleteIngredient` which relies on the
third-party argcomplete module to add support for automatic command line
completion to supported shells (bash).
"""

from __future__ import absolute_import, print_function, unicode_literals

import argparse

from guacamole.core import Ingredient
from guacamole.recipes import RecipeError
# from guacamole._argparse import LegacyHelpFormatter


class ParserIngredient(Ingredient):

    """
    Ingredient for using argparse to parse command line arguments.

    This ingredient uses the following Ingredient methods:

     - ``build_early_parser()``
     - ``preparse()``
     - ``build_parser()``
     - ``parse()``

    The main parser is constructed in, unsurprisingly, the
    :meth:`build_parser()` method and stored in the context as ``parser``.
    Other ingredients can be added *after* the ``ParserIngredient`` and can
    extend the available arguments (on the root parser) by using standard
    argparse APIs such as ``parser.add_argument()`` or
    ``parser.add_argument_group()``. This parser is used to handle all of
    command line in the :meth:`parse()` method.

    While most users won't concern themselves with this design decision, there
    is also a second parser, called the *early parser*, that is used to
    *pre-parse* the command line arguments. This can be used as a way
    to optimize subsequent actions as, perhaps, knowing which commands are
    going to be invoked there will be no need to instantiate and prepare *all*
    of the commands in the command tree.

    Currently this feature is not used. To take advantage of this knowledge you
    can look at the ``context.early_args`` object which contains the result of
    parsing the command line with the *early parser*. The early parser is a
    simple parser consisting of ``--help``, ``--version`` (if applicable) and
    *rest*. The *rest* argument can be used as a hint as to what is coming next
    (e.g. if it matches a name of a command we know to exist)

    After parsing is done the results of parsing the command line are stored in
    the ``context.args`` attribute. This is commonly accessed by individual
    commands from their ``invoke()`` methods.
    """

    def build_early_parser(self, context):
        """
        Create the early argument parser.

        This method creates the early argparse argument parser. The early
        parser doesn't know about any of the sub-commands so it can be used
        much earlier during the start-up process (before commands
        are loaded and initialized).
        """
        context.early_parser = self._create_early_parser(context)

    def preparse(self, context):
        """
        Parse a portion of command line arguments with the early parser.

        This method relies on ``context.argv`` and ``context.early_parser``
        and produces ``context.early_args``.

        The ``context.early_args`` object is the return value from argparse.
        It is the dict/object like namespace object.
        """
        context.early_args, unused = (
            context.early_parser.parse_known_args(context.argv))

    def build_parser(self, context):
        """
        Create the final argument parser.

        This method creates the non-early (full) argparse argument parser.
        Unlike the early counterpart it is expected to have knowledge of
        the full command tree.

        This method relies on ``context.cmd_tree`` and produces
        ``context.parser``. Other ingredients can interact with the parser
        up until :meth:`parse()` is called.
        """
        context.parser, context.max_level = self._create_parser(context)

    def parse(self, context):
        """
        Parse command line arguments.

        This method relies on ``context.argv`` and ``context.early_parser``
        and produces ``context.args``. Note that ``.argv`` is modified by
        :meth:`preparse()` so it actually has _less_ things in it.

        The ``context.args`` object is the return value from argparse.
        It is the dict/object like namespace object.
        """
        context.args = context.parser.parse_args(context.argv)

    def _create_parser(self, context):
        cmd_name, cmd_obj, cmd_subcmds = context.cmd_tree
        parser = argparse.ArgumentParser(
            prog=cmd_name, **self._get_parser_kwargs(cmd_obj))
        parser.add_argument("-h", "--help", action="help")
        self._maybe_add_version(parser, cmd_obj)
        max_level = self._add_command_to_parser(
            parser, cmd_name, cmd_obj, cmd_subcmds)
        return parser, max_level

    def _create_early_parser(self, context):
        early_parser = argparse.ArgumentParser(add_help=False)
        early_parser.add_argument(
            "rest", nargs="...", help=argparse.SUPPRESS)
        early_parser.add_argument(
            "-h", "--help", action="store_const", const=None)
        cmd_name, cmd_obj, cmd_subcmds = context.cmd_tree
        version = cmd_obj.get_cmd_version()
        if version is not None:
            early_parser.add_argument(
                "--version", action="store_const", const=None)
        return early_parser

    def _maybe_add_version(self, parser, command):
        version = command.get_cmd_version()
        if version is not None:
            # NOTE: help= is provided explicitly as argparse doesn't wrap
            # everything with _() correctly (depending on version)
            parser.add_argument(
                "--version", action="version", version=version,
                help="show program's version number and exit")

    def _get_parser_kwargs(self, command):
        return {
            'usage': command.get_cmd_usage(),
            'description': command.get_cmd_description(),
            'epilog': command.get_cmd_epilog(),
            'add_help': False,
            # formatter_class=LegacyHelpFormatter,
        }

    def _add_command_to_parser(
            self, parser, cmd_name, cmd_obj, cmd_subcmds, level=0
    ):
        # Register this command
        cmd_obj.register_arguments(parser)
        parser.set_defaults(**{'command{}'.format(level): cmd_obj})
        # Register sub-commands of this command (recursively)
        if not cmd_subcmds:
            return level
        subparsers = parser.add_subparsers(
            help="sub-command to pick")
        max_level = level
        for subcmd_name, subcmd_obj, subcmd_cmds in cmd_subcmds:
            sub_parser = subparsers.add_parser(
                subcmd_name, help=subcmd_obj.get_cmd_help(),
                **self._get_parser_kwargs(subcmd_obj))
            sub_parser.add_argument("-h", "--help", action="help")
            max_level = max(
                max_level, self._add_command_to_parser(
                    sub_parser, subcmd_name, subcmd_obj, subcmd_cmds,
                    level + 1))
        return max_level


class AutocompleteIngredient(Ingredient):

    """
    Ingredient for adding shell auto-completion.

    .. warning::
        This component is not widely tested due to difficulty of providing
        actual integration. It might be totally broken.

    .. note::
        To effectively get tab completion you need to have the ``argcomplete``
        package installed. In addition, a per-command initialization command
        has to be created and sourced by the shell. Look at argcomplete
        documentation for details.
    """

    def parse(self, context):
        """
        Optionally trigger argument completion in the invoking shell.

        This method is called to see if bash argument completion is requested
        and to honor the request, if needed. This causes the process to exit
        (early) without giving other ingredients a chance to initialize or shut
        down.

        Due to the way argcomple works, no other ingredient can print()
        anything to stdout prior to this point.
        """
        try:
            import argcomplete
        except ImportError:
            return
        try:
            parser = context.parser
        except AttributeError:
            raise RecipeError(
                """
                The context doesn't have the parser attribute.

                The auto-complete ingredient depends on having a parser object
                to generate completion data for she shell.  In a typical
                application this requires that the AutocompleteIngredient and
                ParserIngredient are present and that the auto-complete
                ingredient precedes the parser.
                """)
        else:
            argcomplete.autocomplete(parser)
