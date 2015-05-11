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

"""Ingredient for reacting to application crashes."""

from __future__ import absolute_import, print_function, unicode_literals

import traceback

from guacamole.core import Ingredient


class VerboseCrashHandler(Ingredient):

    """
    Ingredient for reacting to crashes with a traceback.

    You can add this ingredient into your recipe to react to application
    crashes. It will simply print the exception, as stored in
    ``context.exc_type``, ``context.exc_value`` and ``context.traceback`` and
    raise SystemExit(1).
    """

    def dispatch_failed(self, context):
        """Print the unhandled exception and exit the application."""
        traceback.print_exception(
            context.exc_type, context.exc_value, context.traceback)
        raise SystemExit(1)
