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

"""Hello World with Guacamole."""

from __future__ import absolute_import, print_function, unicode_literals

from guacamole import Command


class TerminalInfo(Command):

    """Display terminal information."""

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        print("Terminal:", ctx.terminal)
        print("Terminal version:", ctx.terminal.version)
        if any(status == 2 for status in ctx.terminal.features.values()):
            print("Supported features:")
        for feature, status in ctx.terminal.features.items():
            if status == 2:
                print(" -", feature)
        if any(status == 1 for status in ctx.terminal.features.values()):
            print("Configurable features:")
        for feature, status in sorted(ctx.terminal.features.items()):
            if status == 1:
                print(" -", feature)
        if any(status == 0 for status in ctx.terminal.features.values()):
            print("Unsupported features:")
        for feature, status in sorted(ctx.terminal.features.items()):
            if status == 0:
                print(" -", feature)


class TerminalFeatureCheck(Command):

    """Verify that terminal features are detected correctly."""

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        print('=' * 60)
        print("Terminal Feature Check Matrix".center(60))
        print('=' * 60)
        if ctx.terminal.version is not None:
            print("Detected Terminal: {}, version {}".format(
                ctx.terminal, ctx.terminal.version))
        else:
            print("Detected Terminal: {}".format(ctx.terminal))
        print()
        print("Please VISUALLY inspect the rendering of all the lines below")
        print('-' * 60)
        # x = 1 + max(len(feature.name) for feature in ctx.terminal.features)
        fmt_0 = " - {feature:30}: {sample1} == {sample2}"
        fmt_1 = " - {feature:30}: {sample1} either {sample2} or {sample3}"
        fmt_2 = " - {feature:30}: {sample1} != {sample2}"
        sample1 = 'SAMPLE-A'
        sample2 = 'SAMPLE-B'
        sample3 = 'SAMPLE-C'
        for status_only in range(3):
            if status_only == 0:
                if any(status == 0 for status in ctx.terminal.features.values()):
                    print("The following features are NOT SUPPORTED")
            elif status_only == 1:
                if any(status == 1 for status in ctx.terminal.features.values()):
                    print("The following features are CONFIGURABLE")
            elif status_only == 2:
                if any(status == 2 for status in ctx.terminal.features.values()):
                    print("The following features are SUPPORTED")
            for feature, status in sorted(ctx.terminal.features.items()):
                if status != status_only:
                    continue
                if status == 0:  # unsupported
                    ctx.aprint(fmt_0.format(
                        feature=feature.name, sample1=sample1,
                        sample2=ctx.ansi(sample2, **feature.test_sgr)))
                elif status == 1:  # configurable
                    ctx.aprint(fmt_1.format(
                        feature=feature.name, sample1=sample1,
                        sample2=ctx.ansi(sample2, **feature.test_sgr),
                        sample3=sample3))
                elif status == 2:  # supported
                    ctx.aprint(fmt_2.format(
                        feature=feature.name, sample1=sample1,
                        sample2=ctx.ansi(sample2, **feature.test_sgr)))
        print('-' * 60)
        ctx.aprint("If you see a discrepancy, please report a bug")
        ctx.aprint("Make sure to include the screen-shot of the output")


class Terminal(Command):

    """Terminal detection and feature matrix."""

    sub_commands = (
        ('info', TerminalInfo),
        ('check', TerminalFeatureCheck),
    )

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        # Disable the color controller so that nothing is emulated
        ctx.color_ctrl.active = False


if __name__ == '__main__':
    Terminal().main()
