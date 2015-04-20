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

"""Synthesized set of i18n-strings from argparse in python 3.3."""

from gettext import gettext as _
from gettext import ngettext


_('usage: ')
_("show program's version number and exit")
_('unknown parser %(parser_name)r (choices: %(choices)s)')
_('argument "-" with mode %r')
_("can't open '%s': %s")
_('cannot merge actions - two groups are named %r')
_("'required' is an invalid argument for positionals")
_('invalid option string %(option)r: '
  'must start with a character %(prefix_chars)r')
_('dest= is required for options like %r')
_('invalid conflict_resolution value: %r')
ngettext('conflicting option string: %s',
         'conflicting option strings: %s', 0)
_('mutually exclusive arguments must be optional')
_('positional arguments')
_('optional arguments')
_('show this help message and exit')
_('cannot have multiple subparser arguments')
_('unrecognized arguments: %s')
_('not allowed with argument %s')
_('ignored explicit argument %r')
_('ignored explicit argument %r')
_('the following arguments are required: %s')
_('one of the arguments %s is required')
_('expected one argument')
_('expected at most one argument')
_('expected at least one argument'),
ngettext('expected %s argument',
         'expected %s arguments', 0)
_('ambiguous option: %(option)s could match %(matches)s')
_('unexpected option string: %s')
_('%r is not callable')
_('invalid %(type)s value: %(value)r')
_('invalid choice: %(value)r (choose from %(choices)s)')
_('%(prog)s: error: %(message)s\n')
