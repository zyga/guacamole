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

"""Tests for various parts of the Logging ingredient."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import sys

# Pick the right testing tools
if sys.version_info[0:2] >= (3, 4):
    import unittest
    from unittest import mock
else:
    import unittest2 as unittest
    import mock

from guacamole.core import Bowl
from guacamole.core import Context
from guacamole.ingredients import log


class LoggingTests(unittest.TestCase):

    """Tests for the Logging ingredient."""

    def setUp(self):
        """Common setup code."""
        self.ingredient = log.Logging()
        self.context = Context()
        self.context.bowl = mock.Mock(name='bowl', spec_set=Bowl)
        self.context.early_parser = mock.Mock(
            name='early_parser', spec_set=argparse.ArgumentParser)
        self.context.parser = mock.Mock(
            name='parser', spec_set=argparse.ArgumentParser)
        self.context.early_args = mock.Mock(name='early_args')

    def test_added_configures_logging(self):
        """Calling Logging.added() calls configure_logging()."""
        with mock.patch.object(self.ingredient, 'configure_logging') as cl:
            self.ingredient.added(self.context)
        cl.assert_called_with(self.context)

    def test_added_consults_spices(self):
        """Calling Logging.added() checks for log:arguments spice."""
        with mock.patch.object(self.ingredient, 'configure_logging'):
            self.ingredient.added(self.context)
        self.context.bowl.has_spice.assert_called_once_with("log:arguments")
        self.ingredient._expose_argparse = self.context.bowl.has_spice()

    def test_build_early_parser__enabled(self):
        """Calling Logging.build_early_parser() adds the new option."""
        self.ingredient._expose_argparse = True
        self.ingredient.build_early_parser(self.context)
        self._test_logging_option_was_added(self.context.early_parser)

    def test_build_early_parser__disabled(self):
        """Calling Logging.build_early_parser() doesn't add the new option."""
        self.ingredient._expose_argparse = False
        self.ingredient.build_early_parser(self.context)
        self._test_logging_option_was_not_added(self.context.early_parser)

    def test_early_init__enabled(self):
        """Calling Logging.early_init() runs setLevel() on root logger."""
        self.ingredient._expose_argparse = True
        with mock.patch.object(self.ingredient, 'adjust_logging') as al:
            self.ingredient.early_init(self.context)
        al.assert_called_with(self.context)

    def test_early_init__disabled(self):
        """Calling Logging.early_init() doesn't do anything."""
        self.ingredient._expose_argparse = False
        with mock.patch.object(self.ingredient, 'adjust_logging') as al:
            self.ingredient.early_init(self.context)
        al.assert_not_called()

    def test_build_parser__enabled(self):
        """Calling Logging.build_parser() adds the new option."""
        self.ingredient._expose_argparse = True
        self.ingredient.build_parser(self.context)
        self._test_logging_option_was_added(self.context.parser)

    def test_build_parser__disabled(self):
        """Calling Logging.build_parser() adds the new option."""
        self.ingredient._expose_argparse = False
        self.ingredient.build_parser(self.context)
        self._test_logging_option_was_not_added(self.context.parser)

    def _test_logging_option_was_added(self, parser):
        parser.add_argument_group.assert_called_with(
            "Logging and debugging")
        group = parser.add_argument_group()
        group.add_argument.assert_has_calls([
            mock.call("-l", "--log-level", metavar="LEVEL",
                      choices=('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'),
                      help="set global log level to the specified value"),
        ])

    def _test_logging_option_was_not_added(self, parser):
        parser.add_argument_group.assert_not_called()
