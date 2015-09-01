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

"""Ingredients for terminal identification and capability detection."""


from __future__ import absolute_import, print_function, unicode_literals

import gettext
import os
import sys

from guacamole.core import Ingredient

_ = gettext.gettext

__all__ = ('TerminalIngredient',)

_string_types = (type(""), str)


class TerminalFeature(object):

    """Information about a particular terminal emulator feature."""

    def __init__(self, slug, name, test_sgr):
        self.slug = slug
        self.name = name
        if test_sgr is None:
            test_sgr = {}
        self.test_sgr = test_sgr

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.slug)

    def __eq__(self, other):
        if isinstance(other, TerminalFeature):
            return self.slug == other.slug
        elif isinstance(other, _string_types):
            return self.slug == other
        else:
            return False

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.slug)


ANSI_COLOR_BG_INDEXED_8 = TerminalFeature(
    'ansi-color-bg-indexed-8', _("8 background colors"), {'bg': -3})
ANSI_COLOR_BG_INDEXED_16 = TerminalFeature(
    'ansi-color-bg-indexed-16', _("16 background colors"), {'bg': -11})
ANSI_COLOR_BG_INDEXED_256 = TerminalFeature(
    'ansi-color-bg-indexed-256', _("256 background colors"), {'bg': 0x1C})
ANSI_COLOR_BG_RGB = TerminalFeature(
    'ansi-color-bg-rgb', _("16M background colors"), {
        'bg': (0x00, 0x7f, 0x00)})
ANSI_COLOR_FG_DIM = TerminalFeature(
    'ansi-color-fg-dim', _("dim foreground color"), {'dim': 1})
ANSI_COLOR_FG_INDEXED_8 = TerminalFeature(
    'ansi-color-fg-indexed-8', _("8 foreground colors"), {'fg': -3})
ANSI_COLOR_FG_INDEXED_16 = TerminalFeature(
    'ansi-color-fg-indexed-16', _("16 foreground colors"), {'fg': -11})
ANSI_COLOR_FG_INDEXED_256 = TerminalFeature(
    'ansi-color-fg-indexed-256', _("256 foreground colors"), {'fg': 0x1C})
ANSI_COLOR_FG_RGB = TerminalFeature(
    'ansi-color-fg-rgb', _("16M foreground colors"), {
        'fg': (0x00, 0x7f, 0x00)})
ANSI_COLOR_REVERSE = TerminalFeature(
    'ansi-color-reverse', _("reversed colors"), {'reverse': 1})
ANSI_FONT_BOLD = TerminalFeature(
    'ansi-font-bold', _("bold font face"), {'bold': 1})
ANSI_FONT_ITALIC = TerminalFeature(
    'ansi-font-italic', _("italic font face"), {'italic': 1})
ANSI_TEXT_BLINK_FAST = TerminalFeature(
    'ansi-text-blink-fast', _("fast-blinking text"), {'blink_fast': 1})
ANSI_TEXT_BLINK_SLOW = TerminalFeature(
    'ansi-text-blink-slow', _("slow-blinking text"), {'blink_slow': 1})
ANSI_TEXT_CONCEALED = TerminalFeature(
    'ansi-text-concealed', _("concealed text"), {'concealed': 1})
ANSI_TEXT_CROSSED = TerminalFeature(
    'ansi-text-crossed', _("crossed text"), {'crossed': 1})
ANSI_TEXT_UNDERLINE = TerminalFeature(
    'ansi-text-underline', _("underlined text"), {'underline': 1})


_all_features = (
    ANSI_COLOR_BG_INDEXED_16,
    ANSI_COLOR_BG_INDEXED_256,
    ANSI_COLOR_BG_INDEXED_8,
    ANSI_COLOR_BG_RGB,
    ANSI_COLOR_FG_DIM,
    ANSI_COLOR_FG_INDEXED_16,
    ANSI_COLOR_FG_INDEXED_256,
    ANSI_COLOR_FG_INDEXED_8,
    ANSI_COLOR_FG_RGB,
    ANSI_COLOR_REVERSE,
    ANSI_FONT_BOLD,
    ANSI_FONT_ITALIC,
    ANSI_TEXT_BLINK_FAST,
    ANSI_TEXT_BLINK_SLOW,
    ANSI_TEXT_CONCEALED,
    ANSI_TEXT_CROSSED,
    ANSI_TEXT_UNDERLINE,
)


class Terminal(object):

    """
    A terminal (emulator).

    Terminal object exposes the following information about the terminal
    emulator program that a guacamole-based application is running on.

    :attr name:
        Name of the terminal emulator program
    :attr version:
        Version of the terminal emulator program. This property is rarely
        available.
    :attr features:
        A mapping from features (TerminalFeature) to support status. The
        support status may be one of the three values: ``UNSUPPORTED``,
        ``SUPPORTED`` or ``CONFIGURABLE``.
    """

    def __init__(self, name, version, features):
        self.name = name
        self.version = version
        self.features = features

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{} name:{!r} version:{!r} features:{!r}>'.format(
            self.__class__.__name__, self.name, self.version, self.features)


UNSUPPORTED = 0
CONFIGURABLE = 1
SUPPORTED = 2


def guess_terminal():
    name = None
    version = None
    features = {feature: UNSUPPORTED for feature in _all_features}
    if sys.platform == 'win32':
        name = 'cmd.exe'
        # cmd.exe supports 8 foreground and background colors
        features[ANSI_COLOR_FG_INDEXED_8] = SUPPORTED
        features[ANSI_COLOR_BG_INDEXED_8] = SUPPORTED
    elif sys.platform == 'darwin' and (sys.stdout.isatty() or
                                       sys.stderr.isatty()):
        # TERM = os.getenv("TERM")
        name = os.getenv("TERM_PROGRAM")
        version = os.getenv("TERM_PROGRAM_VERSION")
        if name == 'Apple_Terminal':
            features[ANSI_TEXT_BLINK_SLOW] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_16] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_256] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_8] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_16] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_256] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_8] = SUPPORTED
            features[ANSI_TEXT_CONCEALED] = SUPPORTED
            features[ANSI_COLOR_REVERSE] = SUPPORTED
            features[ANSI_TEXT_UNDERLINE] = SUPPORTED
            # Depending on the theme italic text might not display
            # correctly. Some of the themes use a font with just the
            # monospace variant but without the italics variant.
            features[ANSI_FONT_ITALIC] = CONFIGURABLE
            # Bold-face fonts support is a configurable property of each
            # theme. I don't know what the defaults are though.
            features[ANSI_FONT_BOLD] = CONFIGURABLE
        elif name == 'iTerm.app':
            # NOTE: This covers both iTerm and iTerm 2
            features[ANSI_TEXT_BLINK_SLOW] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_16] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_256] = SUPPORTED
            features[ANSI_COLOR_FG_INDEXED_8] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_16] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_256] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_8] = SUPPORTED
            features[ANSI_COLOR_REVERSE] = SUPPORTED
            features[ANSI_TEXT_UNDERLINE] = SUPPORTED
            # Depending on the theme italic text might not display
            # correctly. Some of the themes use a font with just the
            # monospace variant but without the italics variant.
            features[ANSI_FONT_ITALIC] = CONFIGURABLE
            # Bold-face fonts support is a configurable property of each
            # theme. I don't know what the defaults are though.
            features[ANSI_FONT_BOLD] = CONFIGURABLE
    else:
        term = os.getenv('TERM')
        if term == 'linux':
            name = 'Linux Console'
            features[ANSI_COLOR_FG_INDEXED_8] = SUPPORTED
            features[ANSI_COLOR_BG_INDEXED_8] = SUPPORTED
            features[ANSI_COLOR_REVERSE] = SUPPORTED
            # XXX: All of those are "supported" by rendering a different color
            features[ANSI_TEXT_BLINK_SLOW] = SUPPORTED
            features[ANSI_FONT_BOLD] = SUPPORTED
            features[ANSI_COLOR_FG_DIM] = SUPPORTED
            features[ANSI_FONT_ITALIC] = SUPPORTED
            features[ANSI_TEXT_UNDERLINE] = SUPPORTED
        else:
            name = 'Unknown'
    return Terminal(name, version, features)


class TerminalIngredient(Ingredient):

    """Ingredient for working with the terminal emulator."""

    def added(self, context):
        """Ingredient method called before anything else."""
        context.terminal = guess_terminal()
