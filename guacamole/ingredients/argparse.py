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

"""Ingredient for using arparse for parsing command line arguments."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse

from guacamole.core import Ingredient
from guacamole.recipes import RecipeError
# from guacamole._argparse import LegacyHelpFormatter


class ParserIngredient(Ingredient):

    """Ingredient for using argparse to parse command line arguments."""

    def preparse(self, context):
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
        context.early_args = early_parser.parse_args(context.argv)

    def early_init(self, context):
        cmd_name, cmd_obj, cmd_subcmds = context.cmd_tree
        parser = argparse.ArgumentParser(
            prog=cmd_name, **self._get_parser_kwargs(cmd_obj))
        parser.add_argument("-h", "--help", action="help")
        self._maybe_add_version(parser, cmd_obj)
        context.max_level = self._add_command_to_parser(
            parser, cmd_name, cmd_obj, cmd_subcmds)
        context.parser = parser

    def parse(self, context):
        context.args = context.parser.parse_args(context.argv)

    def dispatch(self, context):
        assert context.max_level >= 0
        for level in range(context.max_level + 1):
            try:
                command = getattr(context.args, 'command{}'.format(level))
            except AttributeError:
                break
            else:
                retval = command.invoked(context)
                if retval is None:
                    continue
        return retval

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

    """Ingredient for adding shell auto-completion."""

    def parse(self, context):
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
