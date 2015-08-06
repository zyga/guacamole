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
Guacamole -- command line applications that suck less.

Guacamole is a flexible, modular system for creating command line applications.
Guacamole comes with built-in support for writing command line applications
that integrate well with the running system. A short list of supported features
(ingredients) includes:

    - handling flat and hierarchical commands
    - hassle-free crash detection
    - hassle-free logging
    - internationalization and localization

The guacamole ingredient system allows for third party add-ons. Please read the
add-on developer guide for details.

.. note::
    Guacamole supports Python 2.7 and Python 3.2, 3.4 and 3.5. Other versions
    are not tested extensively. Versions earlier than 2.7 are not supported and
    won't be. Applications that still need to support the end-of-life Python
    2.x release series are encouraged to update to Python 2.7.

Lower-level classes can be found in the :mod:`guacamole.core` and
:mod:`guacamole.recipes` modules. Add-on developers should use those modules
exclusively. All other APIs are considered private.
"""

from __future__ import absolute_import, print_function

from guacamole.recipes.cmd import Command

__all__ = ('Command',)

__version__ = '0.9.2'
