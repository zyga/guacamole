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

"""Ingredient for color transformations."""

from __future__ import absolute_import, print_function, unicode_literals

import array
import gettext

from guacamole.core import Ingredient

_ = gettext.gettext
_string_types = (str, type(""))


class TerminalPalette(object):

    """
    Palette of a particular terminal emulator.

    Various terminal emulators render the set of 256 palette-based colors
    differently. In order to implement color transformations each of those
    palette entries must be resolvable to an RGB triplet.
    """

    def __init__(self, palette, slug, name):
        """
        Initialize a new terminal palette.

        :param palette:
            A tuple of 256 triplets ``(r, g, b)`` where each component is
            an integer in ``range(256)``
        :param slug:
            A short name of the palette. This will be visible on command line
        :param name:
            A human-readable name of the palette. This will be visible in
            certain parts of the user interface.
        """
        if len(palette) != 256:
            raise ValueError("The palette needs to have 256 entries")
        self.palette = palette
        self.slug = slug
        self.name = name

    def __str__(self):
        """Get the name of the terminal emulator palette."""
        return self.name

    def __repr__(self):
        """Get the debugging representation of a terminal emulator palette."""
        return "<{0} {1}>".format(self.__class__.__name__, self.slug)

    def resolve(self, color):
        """
        Resolve a symbolic or indexed color to an ``(r, g, b)`` triplet.

        :param color:
            One of the well-known string color names:
                'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan',
                'white', 'bright_black', 'bright_red', 'bright_green',
                'bright_yellow', 'bright_blue', 'bright_magenta',
                'bright_cyan', 'bright_white',
            Or an integer in range(256) that corresponds to the indexed
            palette entry.
            Or an ``(r, g, b)`` triplet.
        :returns:
            An ``(r, g, b)`` triplet that corresponds to the given color.
        :raises ValueError:
            If the color format is unrecognized
        """
        if isinstance(color, _string_types):
            color_index = self._sgr_color_to_palette_index(color)
            return self.palette[color_index]
        elif isinstance(color, int):
            try:
                return self.palette[color]
            except IndexError:
                raise ValueError("indexed colors are defined in range(256)")
        elif isinstance(color, tuple):
            return color
        else:
            raise ValueError(
                "Unsupported color representation: {!r}".format(color))

    #: Tuple of color names that correspond to the srg_{fg,bg}_$color codes.
    # Those can be used to map named color into a palette entry. Various
    # terminal emulators implement different palettes. The palette can be used
    # to map the symbolic colors (e.g., "red") to an (r, g, b) triplet.
    _color_names = (
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
        'bright_black', 'bright_red', 'bright_green', 'bright_yellow',
        'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white',
    )
    assert len(_color_names) == 16

    @classmethod
    def _sgr_color_to_palette_index(cls, color):
        try:
            return cls._color_names.index(color)
        except IndexError:
            raise ValueError("incorrect color: {!r}".format(color))

#: A palette with (r, g, b) triplets (using 0-255 integer range) for each
# of the symbolic color names.
# This palette was sampled on Ubuntu 15.04 (text mode). Note that only
# "bold/bright" variant of the bright colors are available.
LinuxConsolePalette = TerminalPalette((
    # Basic colors
    (0x00, 0x00, 0x00),  # 0x00 - black
    (0xaa, 0x00, 0x00),  # 0x01 - red
    (0x00, 0xaa, 0x00),  # 0x02 - green
    (0xaa, 0x55, 0x00),  # 0x03 - yellow
    (0x00, 0x00, 0xaa),  # 0x04 - blue
    (0xaa, 0x00, 0xaa),  # 0x05 - magenta
    (0x00, 0xaa, 0xaa),  # 0x06 - cyan
    (0xaa, 0xaa, 0xaa),  # 0x07 - white
    # Bright colors
    (0x55, 0x55, 0x55),  # 0x08 - bright black
    (0xff, 0x55, 0x55),  # 0x09 - bright red
    (0x55, 0xff, 0x55),  # 0x0A - bright green
    (0xff, 0xff, 0x55),  # 0x0B - bright yellow
    (0x55, 0x55, 0xff),  # 0x0C - bright blue
    (0xff, 0x55, 0xff),  # 0x0D - bright magenta
    (0x55, 0xff, 0xff),  # 0x0E - bright cyan
    (0xff, 0xff, 0xff),  # 0x0F - bright white
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
    (0xaa, 0xaa, 0xaa),  # (rest)
), "linux-console", _("Linux Console"))

#: Palette sampled on Ubuntu 15.04 using Gnome Terminal with "custom"
# color scheme (default for Ubuntu).
GnomeTerminalUbuntu1504Palette = TerminalPalette((
    # Basic colors
    (0x2e, 0x34, 0x36),  # 0x00 - black
    (0xcc, 0x00, 0x00),  # 0x01 - red
    (0x4e, 0x9a, 0x06),  # 0x02 - green
    (0xc4, 0xa0, 0x00),  # 0x03 - yellow
    (0x34, 0x65, 0xa4),  # 0x04 - blue
    (0x75, 0x50, 0x7b),  # 0x05 - magenta
    (0x06, 0x98, 0x9a),  # 0x06 - cyan
    (0xd3, 0xd7, 0xcf),  # 0x07 - white
    # Bright colors
    (0x55, 0x57, 0x53),  # 0x08 - bright black
    (0xef, 0x29, 0x29),  # 0x09 - bright red
    (0x8a, 0xe2, 0x34),  # 0x0A - bright green
    (0xfc, 0xe9, 0x4f),  # 0x0B - bright yellow
    (0x72, 0x9f, 0xcf),  # 0x0C - bright blue
    (0xad, 0x7f, 0xa8),  # 0x0D - bright magenta
    (0x34, 0xe2, 0xe2),  # 0x0E - bright cyan
    (0xee, 0xee, 0xec),  # 0x0F - bright white
    #: 6 * 6 * 6 RGB colors
    (0x00, 0x00, 0x00),  # 0x10
    (0x00, 0x00, 0x5f),  # 0x11
    (0x00, 0x00, 0x87),  # 0x12
    (0x00, 0x00, 0xaf),  # 0x13
    (0x00, 0x00, 0xd7),  # 0x14
    (0x00, 0x00, 0xff),  # 0x15
    (0x00, 0x5f, 0x00),  # 0x16
    (0x00, 0x5f, 0x5f),  # 0x17
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0x00),
    #: 24 gray-scale colors
    (0x08, 0x08, 0x08),  # 0xE8
    (0x12, 0x12, 0x12),  # 0xE9
    (0x1c, 0x1c, 0x1c),  # 0xEA
    (0x26, 0x26, 0x26),  # 0xEB
    (0x30, 0x30, 0x30),  # 0xEC
    (0x3a, 0x3a, 0x3a),  # 0xED
    (0x44, 0x44, 0x44),  # 0xEE
    (0x4e, 0x4e, 0x4e),  # 0xEF
    (0x58, 0x58, 0x58),  # 0xF0
    (0x62, 0x62, 0x62),  # 0xF1
    (0x6c, 0x6c, 0x6c),  # 0xF2
    (0x76, 0x76, 0x76),  # 0xF3
    (0x80, 0x80, 0x80),  # 0xF4
    (0x8a, 0x8a, 0x8a),  # 0xF5
    (0x94, 0x94, 0x94),  # 0xF6
    (0x9e, 0x9e, 0x9e),  # 0xF7
    (0xa8, 0xa8, 0xa8),  # 0xF8
    (0xb2, 0xb2, 0xb2),  # 0xF9
    (0xbc, 0xbc, 0xbc),  # 0xFA
    (0xc6, 0xc6, 0xc6),  # 0xFB
    (0xd0, 0xd0, 0xd0),  # 0xFC
    (0xda, 0xda, 0xda),  # 0xFD
    (0xe4, 0xe4, 0xe4),  # 0xFE
    (0xee, 0xee, 0xee),  # 0xFF
), "gnome-terminal-ubuntu-15.04-default",
    _("Gnome Terminal on Ubuntu 15.04 (default)"))

# TODO: putty palette
# TODO: osx palette


class AccessibilityEmulator(object):

    """
    An accessibility emulator for color-blind user experience.

    This class can emulate various kinds of color blindness. The particular
    color transformation matrix is stored in the emulator. Any (r, g, b) color
    can be transformed to the resulting approximation of how a given class of
    color-blind people would perceive that color.

    The way this works is by associating three coefficients for each of (r, g,
    b) values. The resulting color is then mixed with each basic colors in
    different quantities.

    The resulting colors are computed according to this formula::

        red = red_c.r * red + green_c.green * green + blue_c.blue * blue
        (similar for green and blue)

    For example a non-color-blind person would have the following
    coefficients::

        red_c = (1, 0, 0)
        green_c = (0, 1, 0)
        blue_c = (0, 0, 1)

    This simply results in an identity transformation of the original color (no
    change occurs). A person affected by protanopia would see different colors,
    those can be emulated with this set of coefficients::

        red_c =(0.56667, 0.43333, 0)
        green_c = (0.55833, 0.44167, 0)
        blue_c = (0, 0.24167, 0.75833)

    Here the effective red color would be a 56% mixture of input red and 43% of
    input green. The effective green would be a similar mixture of 55% red and
    44% green.  Lastly, the effective blue would be a 24% mixture of green and
    75% blue.
    """

    def __init__(self, matrix, slug, name):
        """
        Initialize a new accessibility emulator with a given matrix and name.

        :param matrix:
            Any sequence of 9 floating point values. They are distributed to
            the coefficients according to this pattern: ``(red_red, red_green,
            red_blue, green_red, green_green, green_blue, blue_red, blue_green,
            blue_blue)`` Each coefficient must be a number between zero and
            one. Coefficients from each basic color should add up to one.
        :param name:
            A human-readable name of the accessibility emulator.
        """
        matrix = array.array(str('f'), matrix)
        if len(matrix) != 9:
            raise ValueError("matrix must have 9 elements")
        if any(0 > factor > 1 for factor in matrix):
            raise ValueError("all factors must be in range 0..1")
        self.matrix = matrix
        self.name = name
        self.slug = slug

    def __str__(self):
        """Get the name of the accessibility emulator."""
        return self.name

    def __repr__(self):
        """Get the debugging representation of an accessibility emulator."""
        return "<{0} {1}>".format(self.__class__.__name__, self.slug)

    def transform(self, r, g, b):
        """Transform the input color according to the matrix."""
        m = self.matrix
        tr = m[0 * 3 + 0] * r + m[0 * 3 + 1] * g + m[0 * 3 + 2] * b
        tg = m[1 * 3 + 0] * r + m[1 * 3 + 1] * g + m[1 * 3 + 2] * b
        tb = m[2 * 3 + 0] * r + m[2 * 3 + 1] * g + m[2 * 3 + 2] * b
        ro, go, bo = int(min(255, tr)), int(min(255, tg)), int(min(255, tb))
        return ro, go, bo


Normal = AccessibilityEmulator(
    [1, 0, 0,
     0, 1, 0,
     0, 0, 1],
    "normal", _("Normal"))
GrayScale1 = AccessibilityEmulator(
    [0.3, 0.59, 0.11,
     0.3, 0.59, 0.11,
     0.3, 0.59, 0.11],
    "gray-scale-intensity", _("Gray scale (intensity)"))
GrayScale2 = AccessibilityEmulator(
    [0.3333, 0.3333, 0.3333,
     0.3333, 0.3333, 0.3333,
     0.3333, 0.3333, 0.3333],
    "gray-scale-average", _("Gray scale (average)"))
Protanopia = AccessibilityEmulator(
    [0.56667, 0.43333, 0,
     0.55833, 0.44167, 0,
     0, 0.24167, 0.75833],
    "protanopia", _("Protanopia"))
Protanomaly = AccessibilityEmulator(
    [0.81667, 0.18333, 0,
     0.33333, 0.66667, 0,
     0, 0.125, 0.875],
    "protanomaly", _("Protanomaly"))
Deuteranopia = AccessibilityEmulator(
    [0.625, 0.375, 0,
     0.70, 0.3, 0,
     0, 0.30, 0.70],
    "deuteranopia", _("Deuteranopia"))
Deuteranomaly = AccessibilityEmulator(
    [0.80, 0.20, 0,
     0.25833, 0.74167, 0,
     0, 0.14167, 0.85833],
    "deuteranomaly", _("Deuteranomaly"))
Tritanopia = AccessibilityEmulator(
    [0.95, 0.5, 0,
     0, 0.43333, 0.56667,
     0, 0.475, 0.525],
    "tritanopia", _("Tritanopia"))
Tritanomaly = AccessibilityEmulator(
    [0.96667, 0.3333, 0,
     0, 0.73333, 0.26667,
     0, 0.18333, 0.81667],
    "tritanomaly", _("Tritanomaly"))
Achromatopsia = AccessibilityEmulator(
    [0.299, 0.587, 0.114,
     0.299, 0.587, 0.114,
     0.299, 0.587, 0.114],
    "achromatopsia", _("Achromatopsia"))
Achromatomaly = AccessibilityEmulator(
    [0.618, 0.32, 0.62,
     0.163, 0.775, 0.62,
     0.163, 0.320, 0.516],
    "achromatomaly", _("Achromatomaly"))


class ColorController(object):

    """
    Controller for all the color usage inside Guacamole.

    The controller acts as a global color interpreter inside any Guacamole
    application. By default it is disabled. In this mode, any color used by the
    application is directly used without change.

    The controller can be enabled by toggling the :attr:`active` attribute. In
    that mode, the :meth:`transform()` performs two operations, first of all,
    all symbolic and indexed colors are replaced by their RGB counterparts.
    Then, each of the colors is further modified according to the active
    accessibility emulator used.

    This operation requires that the palette and accessibility emulators are
    set using :meth:`emulator` and :meth:`palette` respectively.

    Unfortunately each terminal emulator uses different palette and Guacamole
    can only try to catch up with the commonly used palettes.

    You can use the method :meth:`get_available_palettes()` to learn about all
    available palettes.  Similarly you can use
    :meth:`get_available_emulators()` to discover all accessibility emulators.
    Each of the returned objects has a human-readable name attribute that can
    be used for user interface. If you application chooses to provide one.
    """

    def __init__(self):
        """Initialize a new color controller."""
        self._active = False
        self._palette = None
        self._emulator = None

    @property
    def active(self):
        """Flag indicating if the color controller is active."""
        return self._active

    @active.setter
    def active(self, value):
        """Set the activity flag."""
        self._active = bool(value)

    @property
    def palette(self):
        """The currently enabled terminal emulator palette."""
        return self._palette

    @palette.setter
    def palette(self, value):
        """
        Set the terminal emulator palette.

        :param value:
            The slug of the terminal emulator palette or any
            :class:`TerminalPalette` object.
        :raises ValueError:
            If the supplied value is not a well-known palette slug.
        :raises TypeError:
            If the supplied value unsupported.
        """
        if isinstance(value, str):
            for palette in self.get_available_palettes():
                if palette.slug == value:
                    self._palette = palette
                    break
            else:
                raise ValueError("Unknown palette: {!r}".format(value))
        elif isinstance(value, TerminalPalette):
            self._palette = value
        else:
            raise TypeError("value must be a palette or palette slug")

    @property
    def emulator(self):
        """The currently configured accessibility emulator."""
        return self._emulator

    @emulator.setter
    def emulator(self, value):
        """
        Set the accessibility emulator.

        :param value:
            The slug of the accessibility emulator or any
            :class:`AccessibilityEmulator` emulator object.
        :raises ValueError:
            If the supplied value is not a well-known palette slug.
        :raises TypeError:
            If the supplied value unsupported.
        """
        if isinstance(value, str):
            for emulator in self.get_available_emulators():
                if emulator.slug == value:
                    self._emulator = emulator
                    break
            else:
                raise ValueError("Unknown emulator: {!r}".format(value))
        elif isinstance(value, AccessibilityEmulator):
            self._emulator = value
        else:
            raise TypeError("value must be an emulator or emulator slug")

    def adjust(self, color):
        """
        Adjust the given color according to configured paremeters.

        :param color:
            Any color understood by guacamole ANSI ingredient.
        :returns:
            The tuple ``(r, g, b)`` where each item is an integer
            in range 0..255.
        :raises ValueError:
            if the color specification is incorrect

        This method can be used by anyone operating with colors. Most notably,
        it is used by the ansi ingredient for color rendering to the terminal
        emulator. This method can adjust (change) any of the colors before it
        is displayed on the terminal.

        .. note::
            This method depends on the active flag, pre-configured terminal
            palette and pre-configured accessibility emulator.
        """
        if color is None:
            return
        if not self._active:
            return color
        if self._palette is None:
            return color
        r, g, b = self._palette.resolve(color)
        if self._emulator is None:
            return r, g, b
        return self._emulator.transform(r, g, b)

    @staticmethod
    def get_available_palettes():
        """
        Discover all available terminal emulator color palettes.

        :returns:
            A tuple containing all supported terminal palettes.
        """
        return (
            LinuxConsolePalette,
            GnomeTerminalUbuntu1504Palette,
        )

    @staticmethod
    def get_available_emulators():
        """
        Discover all available accessibility emulators.

        :returns:
            A tuple containing all supported accessibility emulators.
        """
        return (
            Normal,
            GrayScale1,
            GrayScale2,
            Protanopia,
            Protanomaly,
            Deuteranopia,
            Deuteranomaly,
            Tritanopia,
            Tritanomaly,
            Achromatopsia,
            Achromatomaly,
        )


class ColorIngredient(Ingredient):

    """Ingredient that exposes control over the color subsystem."""

    def __init__(self):
        """Initialize the color ingredient."""
        self.color_ctrl = ColorController()

    def added(self, context):
        """
        Register the color controller in the guacamole execution context.

        This method inserts the color controller as the ``color_ctrl``
        attribute of the execution context. The ``color:arguments`` spice is
        inspected to see if command-line interface specific to the color
        controller should be enabled.
        """
        context.color_ctrl = self.color_ctrl
        self._expose_argparse = context.bowl.has_spice("color:arguments")

    def build_parser(self, context):
        """
        Register color controller arguments in the argument parser.

        This method registers the arguments common to the color module in the
        argument parser. They are added so that they show up in ``--help``.
        """
        if self._expose_argparse:
            self._add_argparse_options(context.parser)

    def late_init(self, context):
        """
        Configure the color controller according to the command-line options.

        This method applies the options selected on command line to the color
        controller.  This includes the active flag, the terminal emulator
        palette and the accessibility emulator.
        """
        if self._expose_argparse:
            if context.args.enable_color_controller:
                self.color_ctrl.active = True
            if context.args.palette:
                self.color_ctrl.palette = context.args.palette
            if context.args.emulator:
                self.color_ctrl.emulator = context.args.emulator

    def _add_argparse_options(self, parser):
        group = parser.add_argument_group("Color control")
        group.add_argument(
            '--enable-color-controller', action='store_true',
            help="enable the color controller")
        # Add the --palette argument
        group.add_argument(
            "--palette", metavar="PALETTE",
            choices=[str(palette.slug) for palette in
                     self.color_ctrl.get_available_palettes()],
            help="translate symbolic colors using selected palette")
        # Add the --emulator argument
        group.add_argument(
            "--emulator", metavar="EMULATOR",
            choices=[str(emulator.slug) for emulator in
                     self.color_ctrl.get_available_emulators()],
            help="emulate selected variant of color-blindness")
