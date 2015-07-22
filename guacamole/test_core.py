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

"""Tests for guacamole core."""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

from guacamole.core import Bowl
from guacamole.core import DeveloperError


class TestBowl(unittest.TestCase):

    """Tests for the Bowl class."""

    def setUp(self):
        """Common initialization code."""
        self.bowl = Bowl([])

    def test_spices(self):
        """Bowl.add_spice() and Bowl.has_spice() work as expected."""
        self.assertFalse(self.bowl.has_spice("salt"))
        self.bowl.add_spice('salt')
        self.assertTrue(self.bowl.has_spice("salt"))



class DeveloperErrorTests(unittest.TestCase):

    class test_friendly_advice(self):
        self.assertEqual(
            str(DevelopeError("Use the force Luke!", 0x0001),
            "Developer Error: 0x0001 Use the force Luke!\n"
            "\n"
            "This is a 'DeveloperError', we didn't mean to cause confusion\n"
            "we tried to make the APIs as clear as possible but we've failed\n"
            "We've assumed you'll do something else, the assumption didn't\n"
            "hold so we're here now.\n"
            "\n"
            "You can google for soltuions this isssue: "
        )
