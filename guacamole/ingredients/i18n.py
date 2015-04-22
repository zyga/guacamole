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

"""Ingredient for enabling localization and internationalization."""

from __future__ import absolute_import, print_function, unicode_literals

import gettext
import logging

from guacamole.core import Ingredient


_logger = logging.getLogger("guacamole")


class GettextIngredient(Ingredient):

    """Ingredient for enabling localization and internationalization."""

    def added(self, context):
        """
        Ingredient method called before anything else.

        Here this method just walks the tree of commands, as setup by the
        ``CommandTreeIngredient`` and initializes the gettext domain for each
        one. The top-most command also becomes the default (domainless)
        translation domain.
        """
        cmd_name, cmd_obj, sub_cmds = context.cmd_tree
        _initialize_i18n(cmd_name, cmd_obj, sub_cmds)


def _initialize_i18n(cmd_name, cmd_obj, sub_cmds, domains_seen=None):
    if domains_seen is None:
        domains_seen = set()
        top_level = True
    else:
        top_level = False
    domain = cmd_obj.get_gettext_domain()
    if domain is not None and domain not in domains_seen:
        domains_seen.add(domain)
        if top_level:
            _logger.debug("textdomain(%r)", domain)
            gettext.textdomain(domain)
        locale_dir = cmd_obj.get_locale_dir()
        if locale_dir is not None:
            _logger.debug("bindtextdomain(%r, %r)", domain, locale_dir)
            gettext.bindtextdomain(domain, locale_dir)
    for subcmd_name, subcmd_obj, subsub_cmds in sub_cmds:
        _initialize_i18n(subcmd_name, subcmd_obj, subsub_cmds, domains_seen)
