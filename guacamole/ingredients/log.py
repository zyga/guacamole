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

"""Ingredient for enabling the python logging subsystem."""

from __future__ import absolute_import, print_function, unicode_literals

import logging

from guacamole.core import Ingredient


class LoggingIngredient(Ingredient):

    """Ingredient for enabling the python logging subsystem."""

    def added(self, context):
        """
        Ingredient method called before anything else.

        This method just calls ``logging.basicConfig()`` with no arguments.
        """
        logging.basicConfig()
