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

"""Module that defines the logging ingredient."""

from __future__ import absolute_import, print_function, unicode_literals

import logging

from guacamole.core import Ingredient

_logger = logging.getLogger("guacamole")


class ANSIFormatter(logging.Formatter):

    """A log formatter that uses ANSI SGR codes for readability."""

    def __init__(self, context, fmt=None, datefmt=None):
        """
        Initialize the formatter.

        :param context:
            The guacamole context
        :param fmt:
            Format string for log messages
        :param datefmt:
            Format string for dates and time-stamps
        """
        super(ANSIFormatter, self).__init__(fmt, datefmt)
        self.context = context

    def format(self, record):
        """Overridden method that applies SGR codes to log messages."""
        # XXX: idea, colorize message arguments
        s = super(ANSIFormatter, self).format(record)
        if hasattr(self.context, 'ansi'):
            s = self.context.ansi(s, **self.get_sgr(record))
        return s

    def get_sgr(self, record):
        """
        Get the SGR attributes to set for given record.

        :param record:
            A logging.LogRecord object to inspect
        :returns:
            A dictionary (possibly empty) of SGR commands to apply. The keys
            and values are suitable as keyword arguments to
            :meth:`guacamole.ingredients.ansi.ANSIFormatter.__call__()`.
        """
        return self.LEVELNAME_TO_SGR.get(record.levelname, {})

    LEVELNAME_TO_SGR = {
        'DEBUG': {'dim': 1},
        'INFO': {'bold': 1},
        'WARNING': {'fg': 'bright_yellow', 'bg': 0x10},
        'ERROR': {'fg': 'bright_red', 'bg': 0x10},
        'CRITICAL': {'fg': 'bright_white', 'bg': 'bright_red'},
    }


class Logging(Ingredient):

    """
    Ingredient for enabling the python logging subsystem.

    This ingredient cooperates with the
    :class:`~guacamole.ingredients.argparse.ParserIngredient` ingredient and
    implements a pretty basic support for working with the python logging
    subsystem.

    Logging is enabled early, as soon as :meth:`added()` is called. Command
    line logging is adjusted immediately after the early command line handling
    is performed (so bulk of application code runs with logging subsystem fully
    configured).
    """

    def __init__(self):
        """Initialize the logging ingredient."""
        self._expose_argparse = False

    def added(self, context):
        """
        Configure generic application logging.

        This method just calls ``:meth:`configure_logging()`` which sets up
        everything else. This allows other components to use logging without
        triggering implicit configuration.
        """
        self._expose_argparse = context.bowl.has_spice("log:arguments")
        self.configure_logging(context)

    def build_early_parser(self, context):
        """
        Register logging arguments in the early argument parser.

        This method registers the arguments common to the logging module in the
        early argument parser. The same arguments are added to the regular
        parser later.
        """
        if self._expose_argparse:
            self._add_argparse_options(context.early_parser)

    def early_init(self, context):
        """
        Adjust the logging on the root logger.

        This method looks at the ``context.args.log_level`` and if it's defined
        it adjusts logging level on the root logger. This allows all
        applications to have a common method of accessing basic logging for
        debugging.
        """
        if self._expose_argparse:
            self.adjust_logging(context)

    def build_parser(self, context):
        """
        Register logging arguments in the argument parser.

        This method registers the arguments common to the logging module in the
        argument parser. They are added so that they show up in ``--help``.
        """
        if self._expose_argparse:
            self._add_argparse_options(context.parser)

    def _add_argparse_options(self, parser):
        group = parser.add_argument_group("Logging and debugging")
        # Add the --log-level argument
        group.add_argument(
            "-l", "--log-level", metavar="LEVEL",
            choices=(str('CRITICAL'), str('ERROR'), str('WARNING'),
                     str('INFO'), str('DEBUG')),
            help="set global log level to the specified value")
        # Add the --trace flag
        group.add_argument(
            "-T", "--trace",
            metavar="NAME",
            action="append",
            default=[],
            # TRANSLATORS: please keep DEBUG untranslated
            help=str("enable DEBUG messages on the specified logger "
                     "(can be used multiple times)"))

    def configure_logging(self, context):
        """
        Configure logging for the application.

        :param context:
            The guacamole context object.

        This method attaches a :py:class:logging.StreamHandler` with a
        subclass of :py:class:`logging.Formatter` to the root logger. The
        specific subclass is :class:`ANSIFormatter` and it adds basic ANSI
        formatting (colors and some styles) to logging messages so that they
        stand out from normal output.
        """
        fmt = "%(name)-12s: %(levelname)-8s %(message)s"
        formatter = ANSIFormatter(context, fmt)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    def adjust_logging(self, context):
        """
        Adjust logging configuration.

        :param context:
            The guacamole context object.

        This method uses the context and the results of early argument parsing
        to adjust the configuration of the logging subsystem. In practice the
        values passed to ``--log-level`` and ``--trace`` are applied.
        """
        if context.early_args.log_level:
            log_level = context.early_args.log_level
            logging.getLogger("").setLevel(log_level)
        for name in context.early_args.trace:
            logging.getLogger(name).setLevel(logging.DEBUG)
            _logger.info("Enabled tracing on logger %r", name)
