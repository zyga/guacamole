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

"""Working with XDG Base Directory Specification with Guacamole."""

from __future__ import absolute_import, print_function, unicode_literals

import os

from guacamole import Command


class XDGPeek(Command):

    """
    A trivial XDG directory inspection tool.

    Tool for inspecting the XDG Base Directory Specification directories.

    @EPILOG@

    This tool computes the effective value and inspects each of the directories
    specified by the XDG specification. Color-coding is used, if possible, to
    convey the status of each directory.
    """

    _xdg_dirs = (
        'XDG_DATA_HOME',
        'XDG_CONFIG_HOME',
        'XDG_CACHE_HOME',
        'XDG_RUNTIME_DIR')
    _xdg_dir_lists = (
        'XDG_DATA_DIRS',
        'XDG_CONFIG_DIRS')

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        ctx.aprint("XDG Base Directory Specification Directories",
                   fg='bright_magenta')
        if ctx.ansi.is_enabled:
            ctx.aprint("Legend: ", bold=1, end='')
            ctx.aprint("not specified", fg='bright_black', bg='auto', end='')
            ctx.aprint(', ', end='')
            ctx.aprint("does not exist", fg='default', bg='auto', end='')
            ctx.aprint(', ', end='')
            ctx.aprint("not a directory", fg='bright_red', bg='auto', end='')
            ctx.aprint(', ', end='')
            ctx.aprint("not writable", fg='bright_yellow', bg='auto', end='')
            ctx.aprint(', ', end='')
            ctx.aprint("writable", fg='bright_green', bg='auto')
        # NOTE: the code below is written defensively to work in all kinds
        # of environments, including Windows which won't get any of the XDG
        # directories.
        for name in self._xdg_dirs:
            dirname = getattr(ctx.xdg_base, name)
            ctx.aprint('{}={}'.format(
                ctx.ansi(name, bold=1),
                ctx.ansi(dirname, fg=_dir_color(dirname), bg='auto')))
        for name in self._xdg_dir_lists:
            dirlist = getattr(ctx.xdg_base, name)
            if dirlist is None:
                ctx.aprint("{}={}".format(
                    ctx.ansi(name, bold=1),
                    ctx.ansi(dirlist, fg='bright_black', bg='auto')))
            else:
                ctx.aprint('{}={}'.format(
                    ctx.ansi(name, bold=1),
                    ':'.join(
                        ctx.ansi(dirname, fg=_dir_color(dirname), bg='auto')
                        for dirname in dirlist.split(':'))))


def _dir_color(dirname):
    if dirname is None:
        return "bright_black"
    if not os.path.exists(dirname):
        return "default"
    if not os.path.isdir(dirname):
        return "bright_red"
    if not os.access(dirname, os.R_OK | os.W_OK | os.X_OK):
        return "bright_yellow"
    return "bright_green"


if __name__ == '__main__':
    XDGPeek().main()
