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

"""Ingredients for using ANSI command sequences."""

from __future__ import absolute_import, print_function, unicode_literals

import sys

from guacamole.core import Ingredient


class ANSI(object):

    """
    Numerous ANSI constants.

    .. seealso::

        Original specification in the `Standard ECMA 48
        <http://www.ecma-international.org/publications/
        files/ECMA-ST/Ecma-048.pdf>`_, page 61 (75th page of
        the PDF).

        Wikipedia article about `ANSI escape code
        <http://en.wikipedia.org/wiki/ANSI_escape_code>`_.

    .. attribute:: cmd_erase_display
        Command for erasing the whole display

    .. attribute:: cmd_erase_line
        Command for erasing the current line

    .. attribute:: cmd_sgr_reset_all:
        Command for resetting all SGR attributes

    .. attribute:: sgr_reset_all:
        SGR code for resetting all attributes

    .. attribute:: sgr_bold:

        Causes text to be rendered with bold face font or, alternatively,
        to be rendered with bright color variant. This code is widely
        supported on Linux. It is not supported on Windows.

    .. attribute:: sgr_bright:
        Alternate spelling of :attr:`sgr_bold`.

    .. attribute:: sgr_faint:
        SGR code that activates faint color subset

    .. attribute:: srg_dim:
        Alternate spelling of ``sgr_faint``

    .. attribute:: srg_italic:
        SGR code that activates italic font face

    .. attribute:: sgr_underline:
        SGR code that activates underline mode

    .. attribute:: sgr_blink_slow:
        SGR code that activates slow blinking of characters

    .. attribute:: sgr_blink_fast:
        SGR code that activates fast blinking of characters

    .. attribute:: sgr_reverse:
        SGR code that activates reverse-video mode

    .. attribute:: sgr_double_underline:
        SGR code that activates double-underline mode
    """

    cmd_erase_display = '\033[2J'
    cmd_erase_line = '\033[K'
    cmd_sgr_reset_all = '\033[0m'

    @staticmethod
    def cmd_sgr(sgr_list):
        """Get a SGR (Set Graphics Rendition) code."""
        return '\033[{}m'.format(';'.join(sgr_list))

    # SGR 0-9: text attribute control

    sgr_reset_all = '0'
    sgr_bold = '1'
    sgr_bright = '1'
    sgr_faint = sgr_dim = '2'
    sgr_italic = '3'
    sgr_underline = '4'
    sgr_blink_slow = '5'
    sgr_blink_fast = '6'
    sgr_reverse = '7'
    sgr_concealed = '8'
    sgr_crossed = '9'

    # SGR 10-20: font set control (not implemented)

    sgr_font_default = '10'
    sgr_font_alt1 = '11'
    sgr_font_alt2 = '12'
    sgr_font_alt3 = '13'
    sgr_font_alt4 = '14'
    sgr_font_alt5 = '15'
    sgr_font_alt6 = '16'
    sgr_font_alt7 = '17'
    sgr_font_alt8 = '18'
    sgr_font_alt9 = '19'
    sgr_font_fraktur = '20'

    # SGR 21-29: text attribute control (cont.)

    sgr_double_underline = '21'
    sgr_normal = '22'  # undo sgr_bold and sgr_dim
    sgr_not_italic = '23'  # also undoes Fraktur
    sgr_not_underline = '24'
    sgr_steady = '25'  # undo sgr_blink_{slow,fast}
    # 26 - reserved for proportional spacing
    sgr_positive = '27'  # undo sgr_reverse
    sgr_reveal = '28'  # undo sgr_concealed
    sgr_not_crossed = '29'  # undo sgr_crossed

    # SGR 30-39: foreground color control

    sgr_fg_black = '30'
    sgr_fg_red = '31'
    sgr_fg_green = '32'
    sgr_fg_yellow = '33'
    sgr_fg_blue = '34'
    sgr_fg_magenta = '35'
    sgr_fg_cyan = '36'
    sgr_fg_white = '37'

    @staticmethod
    def sgr_fg_rgb(r, g, b):
        """Get SGR (Set Graphics Rendition) foreground RGB color."""
        return '38;2;{};{};{}'.format(r, g, b)

    @staticmethod
    def sgr_fg_indexed(i):
        """Get SGR (Set Graphics Rendition) foreground indexed color."""
        return '38;5;{}'.format(i)

    sgr_fg_default = '39'

    # SGR 40-49: background color control

    sgr_bg_black = '40'
    sgr_bg_red = '41'
    sgr_bg_green = '42'
    sgr_bg_yellow = '43'
    sgr_bg_blue = '44'
    sgr_bg_magenta = '45'
    sgr_bg_cyan = '46'
    sgr_bg_white = '47'

    @staticmethod
    def sgr_bg_rgb(r, g, b):
        """Get SGR (Set Graphics Rendition) background RGB color."""
        return '48;2;{};{};{}'.format(r, g, b)

    @staticmethod
    def sgr_bg_indexed(i):
        """Get SGR (Set Graphics Rendition) background indexed color."""
        return '48;5;{}'.format(i)

    sgr_bg_default = '49'

    # SGR 90-97: high-intensity foreground color control

    sgr_fg_bright_black = '90'
    sgr_fg_bright_red = '91'
    sgr_fg_bright_green = '92'
    sgr_fg_bright_yellow = '93'
    sgr_fg_bright_blue = '94'
    sgr_fg_bright_magenta = '95'
    sgr_fg_bright_cyan = '96'
    sgr_fg_bright_white = '97'

    # SGR 100-107: high-intensity background color control

    sgr_bg_bright_black = '100'
    sgr_bg_bright_red = '101'
    sgr_bg_bright_green = '102'
    sgr_bg_bright_yellow = '103'
    sgr_bg_bright_blue = '104'
    sgr_bg_bright_magenta = '105'
    sgr_bg_bright_cyan = '106'
    sgr_bg_bright_white = '107'


def ansi_cmd(cmd, *args):
    """Get ANSI command code by name."""
    try:
        obj = getattr(ANSI, str('cmd_{}'.format(cmd)))
    except AttributeError:
        raise ValueError(
            "incorrect command: {!r}".format(cmd))
    if isinstance(obj, type("")):
        return obj
    else:
        return obj(*args)


class _Visible:

    black = str('white')
    red = str('black')
    green = str('black')
    yellow = str('black')
    blue = str('black')
    magenta = str('black')
    cyan = str('black')
    white = str('black')

    bright_black = str('bright_white')
    bright_red = str('bright_black')
    bright_green = str('bright_black')
    bright_yellow = str('bright_black')
    bright_blue = str('bright_black')
    bright_magenta = str('bright_black')
    bright_cyan = str('bright_black')
    bright_white = str('bright_black')

    default = str('default')


def get_visible_color(color):
    """Get the visible counter-color."""
    if isinstance(color, (str, type(""))):
        try:
            return getattr(_Visible, str('{}'.format(color)))
        except AttributeError:
            raise ValueError("incorrect color: {!r}".format(color))
    elif isinstance(color, tuple):
        return (0x80 ^ color[0], 0x80 ^ color[1], 0x80 ^ color[2])
    elif isinstance(color, int):
        if 0 <= color <= 0x07:
            index = color
            return 0xFF if index == 0 else 0xE8
        elif 0x08 <= color <= 0x0F:
            index = color - 0x08
            return 0xFF if index == 0 else 0xE8
        elif 0x10 <= color <= 0xE7:
            index = color - 0x10
            if 0 <= index % 36 < 18:
                return 0xFF
            else:
                return 0x10
        elif 0xE8 <= color <= 0xFF:
            index = color - 0x0E8
            return 0xFF if 0 <= index < 12 else 0xE8
    else:
        raise ValueError("incorrect color: {!r}".format(color))


def get_intensity(r, g, b):
    """Get the gray level intensity of the given rgb triplet."""
    return int(round(255 * (0.3 * r + 0.59 * g + 0.11 * b)))


def ansi_sgr(text, fg=None, bg=None, style=None, reset=True, **sgr):
    """
    Apply desired SGR commands to given text.

    :param text:
        Text or anything convertible to text
    :param fg:
        (optional) Foreground color. Choose one of
        ``black``, ``red``, ``green``, ``yellow``, ``blue``, ``magenta``
        ``cyan`` or ``white``. Note that the ``bright`` *SGR* impacts
        effective color in most implementations.

    """
    # Ensure that text is really a string
    text = str(text)
    # NOTE: SGR stands for "set graphics rendition"
    sgr_list = []  # List of SGR codes
    # Load SGR code associated with desired foreground color
    if isinstance(fg, (str, type(""))):
        try:
            sgr_code = getattr(ANSI, str('sgr_fg_{}'.format(fg)))
        except AttributeError:
            raise ValueError("incorrect foreground color: {!r}".format(fg))
        else:
            sgr_list.append(sgr_code)
    elif isinstance(fg, tuple):
        sgr_code = ANSI.sgr_fg_rgb(*fg)
        sgr_list.append(sgr_code)
    elif isinstance(fg, int):
        sgr_code = ANSI.sgr_fg_indexed(fg)
        sgr_list.append(sgr_code)
    elif fg is None:
        pass
    else:
        raise ValueError("incorrect foreground color: {!r}".format(fg))
    # Load SGR code associated with desired background color
    if isinstance(bg, (str, type(""))):
        try:
            sgr_code = getattr(ANSI, str('sgr_bg_{}'.format(bg)))
        except AttributeError:
            raise ValueError("incorrect background color: {!r}".format(bg))
        else:
            sgr_list.append(sgr_code)
    elif isinstance(bg, tuple):
        sgr_code = ANSI.sgr_bg_rgb(*bg)
        sgr_list.append(sgr_code)
    elif isinstance(bg, int):
        sgr_code = ANSI.sgr_bg_indexed(bg)
        sgr_list.append(sgr_code)
    elif bg is None:
        pass
    else:
        raise ValueError("incorrect background color: {!r}".format(bg))
    # Load single SGR code for "style"
    if style is not None:
        try:
            sgr_code = getattr(ANSI, str('sgr_{}'.format(style)))
        except AttributeError:
            raise ValueError("incorrect text style: {!r}".format(style))
        else:
            sgr_list.append(sgr_code)
    # Load additional SGR codes (custom)
    for name, active in sgr.items():
        try:
            sgr_code = getattr(ANSI, str('sgr_{}'.format(name)))
        except AttributeError:
            raise ValueError("incorrect custom SGR code: {!r}".format(name))
        else:
            if active:
                sgr_list.append(sgr_code)
    # Combine everything into one sequence
    if reset:
        return ANSI.cmd_sgr(sgr_list) + text + ANSI.cmd_sgr_reset_all
    else:
        return ANSI.cmd_sgr(sgr_list) + text


class ANSIFormatter(object):

    """
    Formatter for ANSI Set Graphics Rendition codes.

    An instance of this class is inserted into the context object as `ansi`.
    Using the fact that `ANSIFormatter` is callable one can easily add
    ANSI control sequences for foreground and background color as well as text
    attributes.
    """

    def __init__(self, enabled=None):
        """
        Initialize an ANSI Formatter.

        :param enabled:
            A tri-state that controls the formatter.  If `enabled` is True or
            False then the obvious meaning is assumed. If `enabled` is None
            then the effective value is computed using ``sys.stdout.isatty()``.
        """
        if enabled is None:
            enabled = sys.stdout.isatty()
        self._enabled = enabled

    @property
    def is_enabled(self):
        """
        Flag indicating if text style is enabled.

        This property is useful to let applications customize their
        behavior if they know color support is desired and enabled.
        """
        return self._enabled

    def cmd(self, cmd, *args):
        """Get an ANSI control sequence, if the formatter is enabled."""
        if self._enabled:
            return ansi_cmd(cmd, *args)
        else:
            return ''

    def __call__(self, text, fg=None, bg=None, style=None, reset=True, **sgr):
        """
        Format given text with ANSI control codes.

        If the formatter is enabled this is a pass-through to
        :func:`ansi_sgr()`. Otherwise this is a no-op that returns ``text``.
        """
        if fg == 'auto' and bg is not None:
            fg = get_visible_color(bg)
        elif bg == 'auto' and fg is not None:
            bg = get_visible_color(fg)
        if self._enabled:
            return ansi_sgr(text, fg, bg, style, reset, **sgr)
        else:
            return text

    available_colors = (
        str('black'), str('red'), str('green'), str('blue'), str('magenta'),
        str('cyan'), str('white'))

    available_bright_colors = (
        str('bright_black'), str('bright_red'), str('bright_green'),
        str('bright_blue'), str('bright_magenta'), str('bright_cyan'),
        str('bright_white'))

    available_styles = (
        None, 'bold', 'dim', 'italic', 'underline', 'blink_slow', 'blink_fast',
        'reverse', 'concealed', 'crossed'
    )

    def _aprint2(self, *values, **kwargs):
        """
        ANSI formatting-aware print().

        This method is a version of print() (function) that understands
        additional ansi control parameters.

        :param value:
            The values to print, same as with ``print()``
        :param sep:
            Separator between values, same as with ``print()``
        :param end:
            Terminator of the line, same as with ``print()``
        :param file:
            File to print to, same as with ``print()``
        :param flush:
            Flag that controls stream flush behavior, same as with ``print()``
        :param fg:
            Foreground color, same as with :meth:`__call__()`.
        :param bg:
            Background color, same as with :meth:`__call__()`.
        :param style:
            Text style, same as with :meth:`__call__()`.
        :param reset:
            Flag that controls if ANSI attributes are reset at the end, same as
            with :meth:`__call__()`.
        :param sgr:
            Additonal (custom) Set Graphics Rendition directives, same as with
            :meth:`__call__()`.

        .. note::
            This implementation is intended for Python 2
        """
        sep = kwargs.pop(str('sep'), ' ')
        end = kwargs.pop(str('end'), '\n')
        file = kwargs.pop(str('file'), None) or sys.stdout
        flush = kwargs.pop(str('flush'), False)
        fg = kwargs.pop(str('fg'), None)
        bg = kwargs.pop(str('bg'), None)
        style = kwargs.pop(str('style'), None)
        reset = kwargs.pop(str('reset'), True)
        sgr = kwargs
        text = sep.join(str(value) for value in values)
        text = self(text, fg, bg, style, reset, **sgr)
        print(text, end=end, file=file)
        if flush:
            file.flush()

    def _aprint3(self, *values, **kwargs):
        """
        ANSI formatting-aware print().

        This method is a version of print() (function) that understands
        additional ansi control parameters.

        :param value:
            The values to print, same as with ``print()``
        :param sep:
            Separator between values, same as with ``print()``
        :param end:
            Terminator of the line, same as with ``print()``
        :param file:
            File to print to, same as with ``print()``
        :param flush:
            Flag that controls stream flush behavior, same as with ``print()``
        :param fg:
            Foreground color, same as with :meth:`__call__()`.
        :param bg:
            Background color, same as with :meth:`__call__()`.
        :param style:
            Text style, same as with :meth:`__call__()`.
        :param reset:
            Flag that controls if ANSI attributes are reset at the end, same as
            with :meth:`__call__()`.
        :param sgr:
            Additonal (custom) Set Graphics Rendition directives, same as with
            :meth:`__call__()`.

        .. note::
            This implementation only works on Python 3
        """
        sep = kwargs.pop('sep', ' ')
        end = kwargs.pop('end', '\n')
        file = kwargs.pop('file', None) or sys.stdout
        flush = kwargs.pop('flush', False)
        fg = kwargs.pop('fg', None)
        bg = kwargs.pop('bg', None)
        style = kwargs.pop('style', None)
        reset = kwargs.pop('reset', True)
        sgr = kwargs
        text = sep.join(str(value) for value in values)
        text = self(text, fg, bg, style, reset, **sgr)
        print(text, end=end, file=file)
        # NOTE: Don't use print(..., flush=flush) as that doesn't work on
        # Python 3.2. This was https://github.com/zyga/guacamole/issues/9
        if flush:
            file.flush()

    if sys.version_info[0] == 2:
        aprint = _aprint2
    else:
        aprint = _aprint3


class ANSIIngredient(Ingredient):

    """Ingredient for colorizing output."""

    def __init__(self, enable=None):
        """
        Initialize the ANSI ingredient.

        :param enable:
            Tri-state flag that controls if the embedded ANSI formatter
            should be enabled. See :meth:`ANSI.__init__()`.
        """
        if sys.platform == 'win32':
            try:
                import colorama
            except ImportError:
                enable = False
            else:
                colorama.init()
        self._enable = enable

    def added(self, context):
        """Ingredient method called before anything else."""
        context.ansi = ANSIFormatter(self._enable)
        context.aprint = context.ansi.aprint
