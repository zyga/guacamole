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
Recipe for using guacamole to run commands.

This module contains sock recipes for guacamole. Stock recipes allow
application developers to use use simple-to-understand design patterns to get
predictable runtime behiavior.

Currently, guacamole ships with two such recipes, for creating simple commands
and for creating hierarhical command groups. They are captured by the
:class:`Command` and :class:`Group` classes respectively.
"""

from __future__ import absolute_import, print_function, unicode_literals

import gettext
import inspect
import logging

from guacamole.ingredients import ansi
from guacamole.ingredients import argparse
from guacamole.ingredients import cmdtree
from guacamole.ingredients import crash
from guacamole.recipes import Recipe


__all__ = (
    'Command',
    'CommandRecipe',
)


_logger = logging.getLogger('guacamole')


class Command(object):

    """
    A single-purpose command.

    Single purpose commands are the most commonly known tools in command line
    environments. Tools such as ``ls``, ``mkdir`` or ``vim`` all fall in this
    class. A command is essentially a named action that can be invoked from the
    terminal emulator or other command line environment specific to a given
    operating system.

    To create a new command simply create a custom class and override the
    :meth:`invoked()` method. Put all of your custom code there. If you want to
    interact with command line arguments then please also override the
    :meth:`register_arguments()` method.

    Have a look at example applications for details of how to do this. You can
    use them as a starting point for your own application as they are licensed
    very liberally.
    """

    def __repr__(self):
        """Get the debugging representation of a command."""
        return "<{}>".format(self.__class__.__name__)

    def invoked(self, context):
        """
        Callback called when the command gets invoked.

        :param context:
            The guacamole context object.
        :returns:
            The return value is returned by the executable. It should be an
            integer between 0 and 255. Other values are will likely won't work
            at all.

        The context argument can be used to access command line arguments and
        other information that guacamole provides.
        """
        if not self.get_sub_commands():
            _logger.warning(
                "Command %r doesn't override Command.invoked()", self)

    def register_arguments(self, parser):
        """
        Callback called to register command-specific arguments.

        :param parser:
            Argument parser (from :mod:`argparse`) specific to this command.
        """

    def get_app_vendor(self):
        """
        Get the name of the application vendor.

        The name should be a human readable name, like ``"Joe Developer"`` or
        ``"Big Corporation Ltd."``

        .. note::
            Application vendor name is looked up using the ``app_vendor``
            attribute.
        """
        try:
            return self.app_vendor
        except AttributeError:
            pass

    def get_app_name(self):
        """
        Get the name of the application.

        .. note::
            Application name is looked up using the ``app_name`` attribute.

        Application name differs from executable name. The executable might be
        called ``my-app`` or ``myapp`` while the application might be called
        ``My Application``.
        """
        try:
            return self.app_name
        except AttributeError:
            pass

    def get_app_id(self):
        """
        Get the identifier of the application.

        .. note::
            Application identifier is looked up using the ``app_id`` attribute.

        The syntax of a valid command identifier is ``REVERSE-DNS-NAME:ID``.
        For example, ``"com.example.product:command"``. This identifier must
        not contain characters that are hostile to the file systems. It's best
        to stick to ASCII characters and digits.

        On *Mac OS X* this will be used as a directory name rooted in
        ``~/Library/Preferences/``. On Linux and other freedesktop.org-based
        systems this will be used as directory name rooted in
        ``$XDG_CONFIG_HOME`` and ``$XDG_CACHE_HOME``. On Windows it will be
        used as a directory name rooted in the per-user ``AppData`` folder.

        .. note::
            If this method returns None then logging and configuration services
            are disabled. It is strongly recommended to implement this method
            and return a correct value as it enhances application behavior.
        """
        try:
            return self.app_id
        except AttributeError:
            pass

    def get_cmd_name(self):
        """
        Get the name of the application executable.

        .. note::
            If this method returns None then the executable name is guessed
            from ``sys.argv[0]``.
        """
        try:
            return self.name
        except AttributeError:
            pass

    def get_cmd_version(self):
        """
        Get the version reported by this executable.

        .. note::
            If this method returns None then the ``--version`` option
            is disabled.
        """
        try:
            return self.version
        except AttributeError:
            pass

    def get_cmd_usage(self):
        """
        Get the usage string associated with this command.

        :returns:
            ``self.usage``, if defined
        :returns:
            None, otherwise

        The usage string typically contains the list of available, abbreviated
        options, mandatory arguments and other arguments. Its purpose is to
        quickly inform the user on the basic syntax used by the command.

        It is perfectly fine not to customize this method as the default is to
        compute an appropriate usage string out of all the arguments.  Consider
        implementing this method in a customized way if your command has highly
        complicated syntax and you want to provide an alternative, more terse
        usage string instead.
        """
        try:
            return self.usage
        except AttributeError:
            pass

    def get_cmd_help(self):
        """
        Get the single-line help of this command.

        :returns:
            ``self.help``, if defined
        :returns:
            The first line of the docstring, without the trailing dot, if
            present.
        :returns:
            None, otherwise
        """
        try:
            return self.help
        except AttributeError:
            pass
        try:
            return get_localized_docstring(
                self, self.get_gettext_domain()
            ).splitlines()[0].rstrip('.').lower()
        except (AttributeError, IndexError, ValueError):
            pass

    def get_cmd_description(self):
        """
        Get the leading, multi-line description of this command.

        :returns:
            ``self.description``, if defined
        :returns:
            A substring of the class docstring between the first line (which
            is discarded) and the string ``@EPILOG@``, if present, or the end
            of the docstring, if any
        :returns:
            None, otherwise

        The description string will be displayed after the usage string but
        before any of the detailed argument descriptions.

        Please consider following good practice by keeping the description line
        short enough not to require scrolling but useful enough to provide
        additional information that cannot be inferred from the name of the
        command or other arguments. Stating the purpose of the command is
        highly recommended.
        """
        try:
            return self.description
        except AttributeError:
            pass
        try:
            return '\n'.join(
                get_localized_docstring(
                    self, self.get_gettext_domain()
                ).splitlines()[1:]
            ).split('@EPILOG@', 1)[0].strip()
        except (AttributeError, IndexError, ValueError):
            pass

    def get_cmd_epilog(self):
        """
        Get the trailing, multi-line description of this command.

        :returns:
            ``self.epilog``, if defined
        :returns:
            A substring of the class docstring between the string ``@EPILOG``
            and the end of the docstring, if defined
        :returns:
            None, otherwise

        The epilog is similar to the description string but it is instead
        printed after the section containing detailed descriptions of all of
        the command line arguments.

        Please consider following good practice by providing additional details
        about how the command can be used, perhaps an example or a reference to
        means of finding additional documentation.
        """
        try:
            return self.source.epilog
        except AttributeError:
            pass
        try:
            return '\n'.join(
                get_localized_docstring(
                    self, self.get_gettext_domain()
                ).splitlines()[1:]
            ).split('@EPILOG@', 1)[1].strip()
        except (AttributeError, IndexError, ValueError):
            pass

    def get_gettext_domain(self):
        """
        Get the gettext translation domain associated with this command.

        The value returned will be used to select translations to global calls
        to gettext() and ngettext() everywhere in python.

        .. note::
            If this method returns None then all i18n services are disabled.
        """
        try:
            return self.gettext_domain
        except AttributeError:
            pass

    def get_locale_dir(self):
        """
        Get the path of the gettext translation catalogs for this command.

        This value is used to bind the domain returned by
        :meth:`get_gettext_domain()` to a specific directory.

        .. note::
            If this method returns None then standard, system-wide locations
            are used (on compatibles systems). In practical terms, on Windows,
            you may need to use it to have access to localization data.
        """
        try:
            return self.locale_dir
        except AttributeError:
            pass

    def get_sub_commands(self):
        """
        Get a list of sub-commands of this command.

        :returns:
            ``self.sub_commands``, if defined. This is a sequence of pairs
            ``(name, cls)`` where ``name`` is the name of the sub command and
            ``cls`` is a command class (not an object). The ``name`` can be
            None if the command has a version of :meth:`get_cmd_name()` that
            returns an useful value.
        :returns:
            An empty tuple otherwise

        Applications can create hierarchical commands by defining the
        ``sub_commands`` attribute. Many developers are familiar with nested
        commands, for example ``git commit`` is a sub-command of the ``git``
        command. All commands can be nested this way.
        """
        try:
            return self.sub_commands
        except AttributeError:
            return ()

    def get_cmd_spices(self):
        """
        Get a list of spices requested by this command.

        Feature flags are a mechanism that allows application developers to
        control ingredients (switch them on or off) as well as to control how
        some ingredients behave.

        :returns:
            ``self.spices``, if defined. This should be a set of strings.  Each
            string represents as single flag. Ingredients should document the
            set of flags they understand and use.
        :returns:
            An empty set otherwise

        Some flags have a generic meaning, you can scope a flag to a given
        ingredient using the ``name:`` prefix where the name is the name of the
        ingredient.
        """
        try:
            spices = self.spices
        except AttributeError:
            spices = set()
        return spices

    def main(self, argv=None, exit=True):
        """
        Shortcut for running a command.

        See :meth:`guacamole.recipes.Recipe.main()` for details.
        """
        return CommandRecipe(self).main(argv, exit)


def get_localized_docstring(obj, domain):
    """Get a cleaned-up, localized copy of docstring of this class."""
    if obj.__class__.__doc__ is not None:
        return inspect.cleandoc(
            gettext.dgettext(domain, obj.__class__.__doc__))


class CommandRecipe(Recipe):

    """A recipe for using commands."""

    def __init__(self, command):
        """Initialize a recipe for working with a specific command."""
        self.command = command

    def get_ingredients(self):
        """Get a list of ingredients for guacamole."""
        return [
            ansi.ANSIIngredient(),
            cmdtree.CommandTreeBuilder(self.command),
            cmdtree.CommandTreeDispatcher(),
            argparse.AutocompleteIngredient(),
            argparse.ParserIngredient(),
            crash.VerboseCrashHandler(),
        ]
