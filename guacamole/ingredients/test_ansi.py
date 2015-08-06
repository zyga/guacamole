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

"""Tests for the ansi module."""

from __future__ import absolute_import, print_function, unicode_literals

import io
import sys
import unittest

if sys.version_info[:2] <= (3, 3):
    import mock
else:
    from unittest import mock

from guacamole.ingredients.ansi import ANSIFormatter


class ANSIFormatterTests(unittest.TestCase):

    """Tests for the ANSIFormatter class."""

    def test_flush_works(self):
        """check that aprint(..., flush=True) works okay."""
        # https://github.com/zyga/guacamole/issues/9
        # This should print to our stream
        stream = io.StringIO()
        fmt = ANSIFormatter(enabled=False)
        fmt.aprint("hello world", file=stream, flush=True)
        self.assertEqual(stream.getvalue(), "hello world\n")
        # This should print to sys.stdout
        with mock.patch('sys.stdout', spec_set=True) as mocked_stdout:
            fmt.aprint("goodbye world", file=None, flush=True)
            mocked_stdout.write.assert_has_calls([
                mock.call("goodbye world"),
                mock.call("\n"),
            ])
