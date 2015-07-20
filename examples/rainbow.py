#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015, Canonical Ltd.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""A colorful ANSI color demonstration with Guacamole."""

from __future__ import absolute_import, print_function, unicode_literals

import os

from guacamole import Command


class ANSIDemo(Command):

    """Demonstration of ANSI SGR codes."""

    spices = ["color:arguments"]

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        if not ctx.ansi.is_enabled:
            print("You need color support to use this demo")
        else:
            if ctx.args.clear:
                print(ctx.ansi.cmd('erase_display'))
            if ctx.args.fg_color:
                self._demo_fg_color(ctx)
            if ctx.args.bg_color:
                self._demo_bg_color(ctx)
            if ctx.args.bg_indexed:
                self._demo_bg_indexed(ctx)
            if ctx.args.rainbow:
                self._demo_rgb(ctx)
            if ctx.args.style:
                self._demo_style(ctx)

    def register_arguments(self, parser):
        parser.add_argument(
            '--no-clear', action='store_false', dest='clear', default=True)
        parser.add_argument(
            '--no-fg-color', action='store_false', dest='fg_color',
            default=True)
        parser.add_argument(
            '--no-bg-color', action='store_false', dest='bg_color',
            default=True)
        parser.add_argument(
            '--no-bg-indexed', action='store_false', dest='bg_indexed',
            default=True)
        parser.add_argument(
            '--no-rainbow', action='store_false', dest='rainbow', default=True)
        parser.add_argument(
            '--no-style', action='store_false', dest='style', default=True)
        parser.add_argument(
            '--no-headers', action='store_false', dest='headers', default=True)

    def _demo_fg_color(self, ctx):
        if os.getenv('TERM') == 'linux':
            marker = 'x'
        else:
            marker = '\u25AE'
        if ctx.args.headers:
            self._header("Foreground Color", ctx)
            self._sub_header("Regular Set", ctx)
        # Regular
        print(*[ctx.ansi(marker * (len(color) + 2), fg=color, bg='auto')
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' {} '.format(color.upper()), fg=color, bg='auto')
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(marker * (len(color) + 2), fg=color, bg='auto')
                for color in ctx.ansi.available_colors])
        # Bright (via extensions)
        if ctx.args.headers:
            self._sub_header("Bright Set (using extended codes)", ctx)
        print(*[ctx.ansi(marker * (len(color) + 2),
                         fg='bright_{}'.format(color), bg='auto')
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' {} '.format(color.upper()),
                         fg='bright_{}'.format(color), bg='auto')
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(marker * (len(color) + 2),
                         fg='bright_{}'.format(color), bg='auto')
                for color in ctx.ansi.available_colors])
        if ctx.args.headers:
            self._sub_header("Bright Set (using bold)", ctx)
        print(*[ctx.ansi(marker * (len(color) + 2), fg=color, bg='auto', bold=1)
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' {} '.format(color.upper()), fg=color, bg='auto', bold=1)
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(marker * (len(color) + 2), fg=color, bg='auto', bold=1)
                for color in ctx.ansi.available_colors])

    def _demo_bg_color(self, ctx):
        if ctx.args.headers:
            self._header("Background Color", ctx)
            self._sub_header("Regular and Bright Background Sets", ctx)
        # Regular
        print(*[ctx.ansi(' ' * (len(color) + 2), bg=color)
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' {} '.format(color.upper()), fg='auto', bg=color)
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' ' * (len(color) + 2), bg=color)
                for color in ctx.ansi.available_colors])
        # Bright
        print(*[ctx.ansi(' ' * (len(color) + 2), bg='bright_{}'.format(color))
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' {} '.format(color.upper()),
                         fg='auto', bg='bright_{}'.format(color))
                for color in ctx.ansi.available_colors])
        print(*[ctx.ansi(' ' * (len(color) + 2), bg='bright_{}'.format(color))
                for color in ctx.ansi.available_colors])

    def _demo_bg_indexed(self, ctx):
        if ctx.args.headers:
            self._header("Indexed 8-bit Background Color", ctx)
            self._sub_header("Regular and Bright Color Subsets", ctx)
        print(*(
            [ctx.ansi(' ' * 4, bg=i) for i in range(0x00, 0x07 + 1)]
            + [ctx.ansi(' ' * 4, bg=i) for i in range(0x08, 0x0F + 1)]))
        print(*(
            [ctx.ansi('{:02X}'.format(i).center(4), fg='auto', bg=i)
             for i in range(0x00, 0x07 + 1)]
            + [ctx.ansi('{:02X}'.format(i).center(4), fg='auto', bg=i)
               for i in range(0x08, 0x0F + 1)]))
        print(*(
            [ctx.ansi(' ' * 4, bg=i) for i in range(0x00, 0x07 + 1)]
            + [ctx.ansi(' ' * 4, bg=i) for i in range(0x08, 0x0F + 1)]))
        if ctx.args.headers:
            self._sub_header("6 * 6 * 6 RGB color subset", ctx)
        for y in range(6 * 3):
            print(*(
                [' ' * 5]
                + [ctx.ansi('{:02X}'.format(i).center(4), fg='auto', bg=i)
                   for i in range(0x10 + 6 * y, 0x10 + 6 * y + 6)]
                + [' ' * 6]
                + [ctx.ansi('{:02X}'.format(i).center(4), fg='auto', bg=i)
                    for i in range(0x7c + 6 * y, 0x7c + 6 * y + 6)]))
        if ctx.args.headers:
            self._sub_header("24 grayscale colors", ctx)
        print(
            '    ', *[ctx.ansi(' ' * 6, bg=i)
                      for i in range(0xE8, 0xF3 + 1)], sep='')
        print(
            '    ', *[ctx.ansi('{:02X}'.format(i).center(6), fg='auto', bg=i)
                      for i in range(0xE8, 0xF3 + 1)], sep='')
        print(
            '    ', *[ctx.ansi(' ' * 6, bg=i)
                      for i in range(0xE8, 0xF3 + 1)], sep='')
        print(
            '    ', *[ctx.ansi(' ' * 6, bg=i)
                      for i in range(0xF4, 0xFF + 1)], sep='')
        print(
            '    ', *[ctx.ansi('{:02X}'.format(i).center(6), fg='auto', bg=i)
                      for i in range(0xF4, 0xFF + 1)], sep='')
        print(
            '    ', *[ctx.ansi(' ' * 6, bg=i)
                      for i in range(0xF4, 0xFF + 1)], sep='')

    def _demo_rgb(self, ctx):
        if ctx.args.headers:
            self._header("24 bit RGB Color", ctx)
            self._sub_header(
                "The bar below only displays 80 unique colors", ctx)
        cols = 80
        for y in range(3):
            print(*[ctx.ansi(' ', fg='auto', bg=hsv(360.0 / cols * i, 1, 1))
                    for i in range(cols)], sep='')

    def _demo_style(self, ctx):
        if ctx.args.headers:
            self._header("Text style", ctx)
        styles = ctx.ansi.available_styles
        print(*[ctx.ansi(style, style=style) for style in styles])

    def _header(self, text, ctx):
        print(
            ctx.ansi(' ' * (40 - len(text) // 2), bg=0xE2),
            ctx.ansi(text, fg=0x10, bg=0xE2),
            ctx.ansi(' ' * (40 - len(text) // 2), bg=0xE2),
            sep='')

    def _sub_header(self, text, ctx):
        print(
            ctx.ansi(text, fg=0xFF, bg=0x10),
            ctx.ansi(' ' * (80 - len(text)), bg=0x10),
            sep='')


def hsv(h, s, v):
    """Convert HSV (hue, saturation, value) to RGB."""
    if 360 < h < 0:
        raise ValueError("h out of range: {}".format(h))
    if 1 < s < 0:
        raise ValueError("s out of range: {}".format(h))
    if 1 < v < 0:
        raise ValueError("v out of range: {}".format(h))
    c = v * s  # chroma
    h1 = h / 60
    x = c * (1 - abs(h1 % 2 - 1))
    if 0 <= h1 < 1:
        r1, g1, b1 = (c, x, 0)
    elif 1 <= h1 < 2:
        r1, g1, b1 = (x, c, 0)
    elif 2 <= h1 < 3:
        r1, g1, b1 = (0, c, x)
    elif 3 <= h1 < 4:
        r1, g1, b1 = (0, x, c)
    elif 4 <= h1 < 5:
        r1, g1, b1 = (x, 0, c)
    elif 5 <= h1 < 6:
        r1, g1, b1 = (c, 0, x)
    m = v - c
    r, g, b = r1 + m, g1 + m, b1 + m
    return int(r * 255), int(g * 255), int(b * 255)


if __name__ == '__main__':
    ANSIDemo().main()
