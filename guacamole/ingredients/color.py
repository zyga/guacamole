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

import argparse
import array
import gettext
import math

from guacamole.core import Ingredient

_ = gettext.gettext
_string_types = (str, type(""))


class ColorPalette(object):

    """
    A palette that contains named colors.

    Each color can be defined in up to three variants:

        - RGB color
        - 256-indexed color
        - 8-indexed color

    The first variant is only useful on modern terminal emulators on Linux.
    Guacamole can automatically compute the indexed color for many other
    terminal emulators. For best (and controllable) effects, application author
    should supply a palette that supports at least the fist two color styles.

    If your application is expected to work in a Windows environment, or the
    Linux console then please also supply the third value.
    """

    PREFER_TRUECOLOR, PREFER_INDEXED_256, PREFER_INDEXED_8 = range(3)

    def __init__(self, **palette):
        """
        Initialize a new palette.

        :param palette:
            A dictionary with color definitions (see below).
        :raises ValueError:
            If the palette is malformed.

        For a discussion of how to define palette entries see
        :meth:`add_colors()` below. The initializer uses it for everything.
        """
        self._palette_rgb = {}
        self._palette_i256 = {}
        self._palette_i8 = {}
        self.add_colors(**palette)

    def add_colors(self, **palette):
        """
        Add new colors to the palette.

        :param palette:
            A dictionary with color definitions (see below).
        :raises ValueError:
            If the palette is malformed.

        The following definition formats are supported:

        An integer in ``range(8)``:
            The most widely supported color definition applicable to any
            environment. The value maps to the eight well-known ANSI colors:
                black=0, red=1, green=2, yellow=3, blue=4, magenta=5, cyan=6,
                white=7.
        An integer in ``range(256):
            A more modern color applicable to nearly all Linux environments an
            OS X. This mode is not supported on Windows. Distinct values have
            the following meanings:
                - range(8): same as the earlier definition
                - range(8, 16): bright versions of earlier colors
                - range(16, 256-24): 6 * 6 * 6 RGB values
                - range(256-24, 25): 24 gray-scale values
        A three-element tuple (r, g, b) with each component in range(256):
            The most modern, true color definition. This version is only
            supported on the most modern Linux terminal emulators. In Ubuntu
            terms this is supported since, at least, Ubuntu 14.04.
        A tuple of any of those:
            This allows the designer to offer many variants of the same color
            name that adapts correctly to the environment. This can be commonly
            used to define both indexed and RGB color values.
        """
        for name in palette:
            name = str(name)
            data = palette[name]
            if isinstance(data, int) and data in range(256):
                self._palette_i256[name] = data
                if isinstance(data, int) and data < 8:
                    self._palette_i8[name] = data
            elif isinstance(data, tuple) and len(data) == 3:
                self._palette_rgb[name] = data
            elif isinstance(data, tuple):
                for sub_data in data:
                    if isinstance(sub_data, int) and sub_data in range(256):
                        self._palette_i256[name] = sub_data
                        if isinstance(sub_data, int) and sub_data < 8:
                            self._palette_i8[name] = sub_data
                    elif isinstance(sub_data, tuple) and len(sub_data) == 3:
                        self._palette_rgb[name] = sub_data
                    else:
                        raise ValueError("invalid color: {}".format(name))
            else:
                raise ValueError("invalid color: {}".format(name))

    def resolve(self, color, prefer=PREFER_TRUECOLOR):
        """
        Resolve a guacamole color definition.

        :param color:
            A named color (which is resolved according to the rules below).  Or
            an integer in range(256) that corresponds to the indexed palette
            entry. Or an ``(r, g, b)`` triplet.
        :param prefer:
            Preferred color type. This can be ``PREFER_TRUECOLOR``,
            ``PREFER_INDEXED_256`` or ``PREFER_INDEXED_8``. See below for
            details.
        :returns:
            The resolved color. See below.
        :raises ValueError:
            If the color format is unrecognized
        """
        if isinstance(color, _string_types):
            if prefer == self.PREFER_TRUECOLOR:
                try:
                    return self._palette_rgb[color]
                except KeyError:
                    pass
                try:
                    return self._palette_i256[color]
                except KeyError:
                    pass
                try:
                    return self._palette_i8[color]
                except KeyError:
                    pass
            elif prefer == self.PREFER_INDEXED_256:
                try:
                    return self._palette_i256[color]
                except KeyError:
                    pass
                try:
                    return self._palette_i8[color]
                except KeyError:
                    pass
            elif prefer == self.PREFER_INDEXED_8:
                try:
                    return self._palette_i8[color]
                except KeyError:
                    pass
            raise LookupError("unknown named color: {!r}".format(color))
        elif isinstance(color, int):
            if color not in range(256):
                raise ValueError("indexed colors are defined in range(256)")
            return color
        elif isinstance(color, tuple):
            return color
        else:
            raise ValueError(
                "Unsupported color representation: {!r}".format(color))


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
            An integer in range(256) that corresponds to the indexed palette
            entry.  Or an ``(r, g, b)`` triplet.
        :returns:
            An ``(r, g, b)`` triplet that corresponds to the given color.
        :raises ValueError:
            If the color format is unrecognized.
        :raises ValueError:
            When a color name is used. Please use a :class:`ColorPalette` to
            resolve it before continuing with the terminal palette.
        """
        if isinstance(color, _string_types):
            raise ValueError("color names are not supported"
                             ", please use the palette to resolve them")
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

    def resolve_fast(self, color):
        """
        Resolve a symbolic or indexed color to an ``(r, g, b)`` triplet.

        :param color:
            An integer in range(256) that corresponds to the indexed palette
            entry.  Or an ``(r, g, b)`` triplet.
        :returns:
            An ``(r, g, b)`` triplet that corresponds to the given color.
        :raises ValueError:
            If the color format is unrecognized.
        :raises ValueError:
            When a color name is used. Please use a :class:`ColorPalette` to
            resolve it before continuing with the terminal palette.
        """
        try:
            return self.palette[color]
        except IndexError:
            raise ValueError("indexed colors are defined in range(256)")


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
) + ((0xaa, 0xaa, 0xaa),) * (256 - 16),  # (all of the rest is plain)
    "linux-console", _("Linux Console"))

_rgb6 = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)

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
) + tuple(
    (_rgb6[r], _rgb6[g], _rgb6[b])
    for r in range(6)
    for g in range(6)
    for b in range(6)
    #: 24 gray-scale colors
) + tuple(
    (shade * 0x0A + 0x08,) * 3
    for shade in range(24)
), "gnome-terminal-ubuntu-15.04-default",
    _("Gnome Terminal on Ubuntu 15.04 (default)"))


#: Palette sampled on Ubuntu 15.04 using xterm
XTermPalette = TerminalPalette((
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
) + tuple(
    (_rgb6[r], _rgb6[g], _rgb6[b])
    for r in range(6)
    for g in range(6)
    for b in range(6)
    #: 24 gray-scale colors
) + tuple(
    (shade * 0x0A + 0x08,) * 3
    for shade in range(24)
), "xterm-256color",
    _("X Terminal Emulator"))

# TODO: putty palette

#: Palette sampled on Mac OS X 10.10 (yosemite) Apple Terminal
AppleTerminalOSX1010Palette = TerminalPalette((
    # Basic colors
    (0x00, 0x00, 0x00),  # 0x00 - black
    (0x99, 0x00, 0x00),  # 0x01 - red
    (0x1a, 0x50, 0x06),  # 0x02 - green
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
) + tuple(
    (_rgb6[r], _rgb6[g], _rgb6[b])
    for r in range(6)
    for g in range(6)
    for b in range(6)
    #: 24 gray-scale colors
) + tuple(
    (shade * 0x0A + 0x08,) * 3
    for shade in range(24)
), "apple-terminal-osx-10.10-default",
    _("Apple Terminal on OS X 10.10 (default)"))


class AccessibilityEmulator(object):

    """
    An accessibility emulator for color-blind user experience.

    This class can emulate various kinds of color blindness. The particular
    color transformation matrix is stored in the emulator. Any ``(r, g, b)``
    color can be transformed to the resulting approximation of how a given
    class of color-blind people would perceive that color.

    The way this works is by associating three coefficients for each of
    ``(r, g, b)`` values. The resulting color is then mixed with each basic
    colors in different quantities.

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

        red_c = (0.56667, 0.43333, 0)
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
        # TODO: optimize this code
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


class ColorMixerBase(object):

    """
    A filter for color post-processing.

    This class is essentially a function mapping colors to colors. It can be
    used to implement the RGB-to-indexed downmixing that is required on many
    terminal emulators.

    :attr slug:
        The non-translatable identifier of this mixer.
    :attr name:
        A human-readable name of the accessibility emulator.
    :attr preferred_mode:
        The preferred named color resolution mode. This is either
        ColorPalette.PREFER_TRUECOLOR, ColorPalette.PREFER_INDEXED_256 or
        ColorPalette.PREFER_INDEXED_8.
    """

    def __str__(self):
        """Get the name of a color mixer."""
        return self.name

    def __repr__(self):
        """Get the debugging representation of a color mixer."""
        return "<{0} {1}>".format(self.__class__.__name__, self.slug)

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.
        """
        raise NotImplementedError


# NOTE: The ColorController has a fast path for the pass-through case. It is
# best not to actually use the PassthruColorMixer

class TrueColorMixer(ColorMixerBase):

    """
    True Color mixer.

    This color mixer simply returns the r, g, b data without reinterpretation.

    This mixer uses PREFER_TRUECOLOR colors from the named color palette so
    that applications can have full fidelity in expressing the desired color.
    """

    name = _("24bit RGB (TrueColor)")
    slug = 'truecolor'
    preferred_mode = ColorPalette.PREFER_TRUECOLOR
    needs_palette = False

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.

        .. note::
            This implementation always returns ``(r, g, b)`` unchanged.
        """
        return (r, g, b)


class FastIndexed256ColorMixer(ColorMixerBase):

    """
    Fast mixer that reduces true color to one of 246 indexed values.

    This mixer produces sub-optimal results because it ignores the real
    terminal emulator palette and simply assumes a given arrangement of colors.
    The mixer has two code paths, one is optimized for grayscale colors, the
    other for saturated colors.

    The grayscale path is used when all of the color channels have the same
    value. In that mode, the mixer uses one of the 24 linear grayscale values
    as the output.

    Int the saturated color path the mixer uses one of the 216 available RGB
    colors from the 6*6*6 color cube. It operates by dividing each channel by
    256/6.0 which is 42.(6), clamping that to range(6) then re-mapping the
    result to the 6*6*6 color cube.

    It has the advantage of not requiring any lookup tables and producing
    colors quickly but the perception is somewhat suboptimal.

    This mixer uses PREFER_INDEXED_256 colors from the named color palette so
    that applications can avoid the inaccurate conversion if they provide a
    hand-picked indexed color variant for each named color.
    """

    name = _("Indexed 256 color palette (fast transform)")
    slug = 'fast-indexed-256'
    preferred_mode = ColorPalette.PREFER_INDEXED_256
    needs_palette = False

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.

        .. note::
            This implementation always returns an indexed color.
        """
        # To avoid coloring grayscale colors, include a special case
        # grayscale path if all the components are of the same magnitude.
        if r == g == b:
            # NOTE: 0xE8 is the offset of the 24 grayscale bar in the ANSI
            # indexed color palette.
            color = 0xE8 + int(r / (256.0 / 24))
            assert color in range(0xE8, 0x100)
            return color
        else:
            f = 256 / 6.0
            r /= f
            g /= f
            b /= f
            r = int(r)
            g = int(g)
            b = int(b)
            r = max(0, min(r, 5))
            g = max(0, min(g, 5))
            b = max(0, min(b, 5))
            # NOTE: 0x10 is the offset of the 6 * 6 * 6 color cube in the ANSI
            # indexed color palette.
            assert r in range(6)
            assert g in range(6)
            assert b in range(6)
            assert r * 36 + g * 6 + b in range(216)
            color = 0x10 + r * 36 + g * 6 + b
            assert color in range(0x10, 0xE8)
            return color


class FastIndexed8ColorMixer(ColorMixerBase):

    """
    Mixer that reduces true color to one of 8 classic indexed values.

    This mixer produces rather terrible results simply because of the bare
    minimum combination of available output colors. It can be used to
    downconvert a full-color application to DOS or Linux Console environment.
    It is strongly recommended that applications use optimized, hand-picked
    colors however, as otherwise the application may be a colorful, perhaps
    unreadable mess.

    It operates by reducing the bit depth of each color channel to one.

    This mixer uses PREFER_INDEXED_8 colors so that applications can take
    advantage of optimized, low-color palette entries for named colors.
    """

    name = _("Indexed 8 color palette (fast transform)")
    slug = 'fast-indexed-8'
    preferred_mode = ColorPalette.PREFER_INDEXED_8
    needs_palette = False

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.

        .. note::
            This implementation always returns an indexed color.
        """
        color = ((r >> 7) << 2) | ((g >> 7)) << 1 | (b >> 7)
        assert color in range(8)
        return color


class AccurateIndexed256ColorMixer(ColorMixerBase):

    """
    Accurate mixer that reduces true color to one of 256 indexed values.

    This mixer produces pretty good results as it considers each of the 256
    palette entries. It is significantly slower than its cousin
    :class:`FastIndexed256ColorMixer` so depending on the application you may
    not want to use it.

    It operates by looking for minimal distance between the input color and
    each of the colors of the terminal emulator palette. Unlike other mixers it
    does take advantage of the terminal palette to improve accuracy of the
    conversion. This means that the resulting color is may be different from
    one system to another but the perceived color should be the same.

    This mixer uses PREFER_INDEXED_256 colors from the named color palette so
    that applications can avoid the costly conversion if they provide a
    hand-picked indexed color variant for each named color.
    """

    name = _("Indexed 256 color palette (accurate transform)")
    slug = 'accurate-indexed-256'
    preferred_mode = ColorPalette.PREFER_INDEXED_256
    needs_palette = True

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.

        .. note::
            This implementation always returns an indexed color.
        """
        min_distance = 1000
        min_distance_idx = 0
        for idx, (r2, g2, b2) in enumerate(terminal_palette):
            distance = math.sqrt((r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2)
            if distance == 0:
                return idx
            elif distance < min_distance:
                min_distance = distance
                min_distance_idx = idx
        assert min_distance_idx in range(0x100)
        return min_distance_idx


class AccurateIndexed8ColorMixer(ColorMixerBase):

    """
    Mixer that reduces true color to one of 8 classic indexed values.

    This mixer produces rather terrible results simply because of the bare
    minimum combination of available output colors. It can be used to
    downconvert a full-color application to DOS or Linux Console environment.
    It is strongly recommended that applications use optimized, hand-picked
    colors however, as otherwise the application may be a colorful, perhaps
    unreadable mess.

    It operates by looking for minimal distance between the input color and
    each of the eight colors of the terminal emulator palette. To avoid
    creating unexpected colors, it has a special case when all of the base
    components have the same magnitude. In that mode it will simply output
    black or white, depending on the threshold.

    This mixer uses PREFER_INDEXED_8 colors so that applications can take
    advantage of optimized, low-color palette entries for named colors.
    """

    name = _("Indexed 8 color palette (accurate transform)")
    slug = 'accurate-indexed-8'
    preferred_mode = ColorPalette.PREFER_INDEXED_8
    needs_palette = False

    def mix(self, r, g, b, terminal_palette):
        """
        Optionally downmix the input color to an indexed color.

        :param r:
            The red component. It is always an integer in ``range(256)``.
        :param g:
            The blue component. It is always an integer in ``range(256)``.
        :param b:
            The green component. It is always an integer in ``range(256)``.
        :param terminal_palette:
            An array / tuple of exactly 256 entries. Each entry maps to a
            3-tuple ``(r, g, b)`` that describes the actual color used by the
            terminal emulator to render the corresponding indexed color.
        :returns:
            The downmixed color. It can be the either the ``(r, g, b)`` input
            color or a new integer in ``range(256)`` that corresponds to the
            input color.

        .. note::
            This implementation always returns an indexed color.
        """
        color = ((r >> 7) << 2) | ((g >> 7)) << 1 | (b >> 7)
        assert color in range(8)
        return color
        # To avoid coloring grayscale colors, include a special case
        # (black/white) exit path if all the components are of the same
        # magnitude.
        if r == g == b:
            return 7 if r > 127 else 0
        min_distance = 1000
        min_distance_idx = 0
        for idx, (r2, g2, b2) in enumerate(terminal_palette[:8]):
            distance = math.sqrt((r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2)
            if distance == 0:
                return idx
            elif distance < min_distance:
                min_distance = distance
                min_distance_idx = idx
        assert min_distance_idx in range(0x100)
        return min_distance_idx


def get_intensity(r, g, b):
    """
    Get the gray level intensity of the given rgb triplet.

    :param rgb:
        A tuple ``(r, g, b)`` where each component is an integer in
        ``range(256)``.
    :returns:
        An integer in ``range(256)`` which represents the intensity
        (brightness) of the input color.
    """
    return int(0.3 * r + 0.59 * g + 0.11 * b)


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
    set using :meth:`accessibility_emulator` and :meth:`terminal_palette`
    respectively.

    Unfortunately each terminal emulator uses different palette and Guacamole
    can only try to catch up with the commonly used palettes.

    You can use the method :meth:`get_available_terminal_palettes()` to learn
    about all available palettes.  Similarly you can use
    :meth:`get_available_accessibility_emulators()` to discover all
    accessibility emulators.  Each of the returned objects has a human-readable
    name attribute that can be used for user interface. If you application
    chooses to provide one.
    """

    # Color rendering mode
    MODE_RGB, MODE_INDEXED = range(2)

    def __init__(self):
        """Initialize a new color controller."""
        self._active = False
        self._color_palette = ColorPalette()
        self._terminal_palette = None
        self._color_mixer = None
        self._accessibility_emulator = None
        # Basic ANSI colors
        self.add_colors(
            black=0, red=1, green=2, yellow=3, blue=4, magenta=5, cyan=6,
            white=7)
        # Extended ANSI colors.
        # NOTE: each color is provided twice, the second entry is for the
        # smaller 8-entry palette. Here they map just exactly back to the
        # non-bright variants listed above. This is done so that applications
        # can use all the bright variants in a portable manner and the
        # application will still behave correctly in low-color environments
        # (DOS or Linux Console)
        self.add_colors(
            bright_black=(8, 0), bright_red=(9, 1), bright_green=(10, 2),
            bright_yellow=(11, 3), bright_blue=(12, 4), bright_magenta=(13, 5),
            bright_cyan=(14, 6), bright_white=(15, 7))

    @property
    def active(self):
        """Flag indicating if the color controller is active."""
        return self._active

    @active.setter
    def active(self, value):
        """Set the activity flag."""
        self._active = bool(value)

    @property
    def terminal_palette(self):
        """The currently enabled terminal emulator palette."""
        return self._terminal_palette

    @terminal_palette.setter
    def terminal_palette(self, value):
        """
        Set the terminal emulator palette.

        :param value:
            The slug of a well-known color palette or any
            :class:`TerminalPalette` object, the object ``None`` or the string
            ``"none"``.
        :raises ValueError:
            If the supplied value is not a well-known palette slug.
        :raises TypeError:
            If the supplied value unsupported.
        """
        if isinstance(value, _string_types):
            if value == 'none':
                self._terminal_palette = None
                return
            for palette in self.get_available_terminal_palettes():
                if palette.slug == value:
                    self._terminal_palette = palette
                    break
            else:
                raise ValueError("Unknown palette: {!r}".format(value))
        elif isinstance(value, TerminalPalette):
            self._terminal_palette = value
        else:
            raise TypeError("value must be a palette or palette slug")

    @property
    def color_mixer(self):
        """The currently configured color mixer."""
        return self._color_mixer

    @color_mixer.setter
    def color_mixer(self, value):
        """
        Set the color mixer.

        :param value:
            The slug of a well-known color mixer or any :class:`ColorMixerBase`
            mixer object, the object ``None`` or the string ``"none"``.
        :raises ValueError:
            If the supplied value is not a well-known color mixer slug.
        :raises TypeError:
            If the supplied value unsupported.
        """
        if isinstance(value, _string_types):
            if value == 'none':
                self._color_mixer = None
                return
            for mixer in self.get_available_color_mixers():
                if mixer.slug == value:
                    self._color_mixer = mixer
                    break
            else:
                raise ValueError("Unknown mixer: {!r}".format(value))
        elif isinstance(value, ColorMixerBase):
            self._color_mixer = value
        else:
            raise TypeError("value must be a color mixer or color mixer slug")

    @property
    def accessibility_emulator(self):
        """The currently configured accessibility emulator."""
        return self._accessibility_emulator

    @accessibility_emulator.setter
    def accessibility_emulator(self, value):
        """
        Set the accessibility emulator.

        :param value:
            The slug of a well-known accessibility emulator or any
            :class:`AccessibilityEmulator` emulator object, the object ``None``
            or the string ``"none"``.
        :raises ValueError:
            If the supplied value is not a well-known accessibility emulator
            slug.
        :raises TypeError:
            If the supplied value unsupported.
        """
        if isinstance(value, _string_types):
            if value == 'none':
                self._accessibility_emulator = None
                return
            for emulator in self.get_available_accessibility_emulators():
                if emulator.slug == value:
                    self._accessibility_emulator = emulator
                    break
            else:
                raise ValueError("Unknown emulator: {!r}".format(value))
        elif isinstance(value, AccessibilityEmulator):
            self._accessibility_emulator = value
        else:
            raise TypeError("value must be an emulator or emulator slug")

    def add_colors(self, **palette):
        """
        Register additional named colors.

        :param palette:
            A dictionary with color definitions.
        :raises ValueError:
            If the palette is malformed.

        For a discussion of this method, see :meth:`ColorPalette.add_colors()`.
        """
        self._color_palette.add_colors(**palette)

    def transform(self, color):
        """
        Transform the given color according to configured parameters.

        :param color:
            Any color understood by guacamole ANSI ingredient.
        :returns:
            A new color, as understood by the rest of guacamole. This might be
            a tuple ``(r, g, b)`` where each item is an integer in range
            ``0..255``. It might also be an indexed ``0..255`` color.
        :raises ValueError:
            if the color specification is incorrect

        This method can be used by anyone operating with colors. Most notably,
        it is used by the ``ansi`` ingredient for color rendering to the
        terminal emulator. This method can adjust (change) any of the colors
        before it is displayed on the terminal.

        .. note::
            This method depends on the active flag, pre-configured terminal
            palette, pre-configured accessibility emulator and the
            pre-configured color mixer.

        .. note::
            Even if the color controller is disabled it will resolve named
            colors from the palette.
        """
        if color is None:
            return
        # Do a palette color-name lookup unconditionally so that named colors
        # can be resolved successfully even if the color controller is
        # otherwise disabled.
        #
        # When no mixer is set, the code will prefer indexed-256 mode as it is
        # the safest choice.
        if self._color_mixer is not None:
            preferred_mode = self._color_mixer.preferred_mode
        else:
            preferred_mode = ColorPalette.PREFER_INDEXED_256
        if isinstance(color, _string_types):
            color = self._color_palette.resolve(color, preferred_mode)
        # If the color controller is not enabled just return the color without
        # further transformations.
        if not self._active:
            return color
        # If we don't have a terminal emulator palette or a color mixer then no
        # further work should be done, just return an indexed value as-is.
        if self._terminal_palette is None or self._color_mixer is None:
            return color
        # If the color is an indexed color number from the 8 or 256 entry
        # palette then use the terminal emulator palette to reconstruct the
        # (r, g, b) color.
        if isinstance(color, int):
            r, g, b = self._terminal_palette.resolve_fast(color)
        elif isinstance(color, tuple):
            r, g, b = color
        else:
            raise ValueError(
                "Unsupported color representation: {!r}".format(color))
        # Allow the emulator to change the color, if one is enabled.
        if self._accessibility_emulator is not None:
            r, g, b = self._accessibility_emulator.transform(r, g, b)
        # Use the mixer to output the final color
        return self._color_mixer.mix(r, g, b, self._terminal_palette.palette)

    @staticmethod
    def get_available_terminal_palettes():
        """
        Discover all available terminal emulator color palettes.

        :returns:
            A tuple containing all supported terminal palettes.
        """
        return (
            LinuxConsolePalette,
            XTermPalette,
            GnomeTerminalUbuntu1504Palette,
            AppleTerminalOSX1010Palette,
        )

    @staticmethod
    def get_available_accessibility_emulators():
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

    @staticmethod
    def get_available_color_mixers():
        """
        Discover all available color mixers.

        :returns:
            A tuple containing all supported color mixers.
        """
        return (
            TrueColorMixer(),
            FastIndexed256ColorMixer(),
            FastIndexed8ColorMixer(),
            AccurateIndexed256ColorMixer(),
            AccurateIndexed8ColorMixer(),
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
        self._enable_by_default = context.bowl.has_spice("color:enable")

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
        if self._enable_by_default:
            context.color_ctrl.active = True
            context.color_ctrl.color_mixer = 'fast-indexed-256'
            context.color_ctrl.terminal_palette = 'xterm-256color'
        if self._expose_argparse:
            if context.args.enable_color_controller is True:
                self.color_ctrl.active = True
            elif context.args.enable_color_controller is False:
                self.color_ctrl.active = False
            if context.args.terminal_palette:
                self.color_ctrl.terminal_palette = (
                    context.args.terminal_palette)
            if context.args.accessibility_emulator:
                self.color_ctrl.accessibility_emulator = (
                    context.args.accessibility_emulator)
            if context.args.color_mixer:
                self.color_ctrl.color_mixer = context.args.color_mixer

    def _add_argparse_options(self, parser):
        group = parser.add_argument_group("Color control")
        # Add the --enable-color-controller and --disable-color-controller
        # arguments. One of those is hidden depending on the presence or
        # absence of the 'color:enable' spice.
        group.add_argument(
            '--enable-color-controller', action='store_true',
            default=None, help=(
                argparse.SUPPRESS if self._enable_by_default
                else _("enable the color controller")))
        group.add_argument(
            '--disable-color-controller', action='store_false',
            dest='enable_color_controller', help=(
                argparse.SUPPRESS if not self._enable_by_default
                else _("disable the color controller")))
        # Add the --terminal-palette argument
        group.add_argument(
            "--terminal-palette", metavar=_("TERMINAL-PALETTE"),
            choices=[str('none')] + [
                str(palette.slug) for palette in
                self.color_ctrl.get_available_terminal_palettes()],
            help="translate indexed colors using selected terminal palette")
        # Add the --color-mixer argument
        group.add_argument(
            "--color-mixer", metavar=_("COLOR-MIXER"),
            choices=[str('none')] + [
                str(mixer.slug) for mixer in
                self.color_ctrl.get_available_color_mixers()],
            help="use the specific color mixer")
        # Add the --accessibility-emulator argument
        group.add_argument(
            "--accessibility-emulator", metavar=_("ACCESSIBILITY-EMULATOR"),
            choices=[str('none')] + [
                str(emulator.slug) for emulator in
                self.color_ctrl.get_available_accessibility_emulators()],
            help="emulate selected variant of color-blindness")
