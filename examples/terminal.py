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
        print("Terminal information")
        print("    id: {!r}".format(ctx.terminal.slug))
        print("    name: {}".format(ctx.terminal.name))
        print("    version: {}".format(ctx.terminal.version))
        print("    preset: {}".format(ctx.terminal.preset))
        self._show_feature_list("Unsupported features",
                                ctx.terminal.unsupported_features)
        self._show_feature_list("Broken features",
                                ctx.terminal.broken_features)
        self._show_feature_list("Configurable features",
                                ctx.terminal.configurable_features)
        self._show_feature_list("Supported features",
                                ctx.terminal.supported_features)
        self._show_feature_list("Features of unknown status:",
                                ctx.terminal.unknown_features)

    @staticmethod
    def _show_feature_list(caption, feature_list):
        if feature_list:
            print(caption)
        for feature in feature_list:
            print(" - {0.slug:27} ({0.name})".format(feature))


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
        sample1 = 'SAMPLE-A'
        sample2 = 'SAMPLE-B'
        sample3 = 'SAMPLE-C'
        if ctx.terminal.unsupported_features:
            fmt = " - {feature.slug:27}: {sample1} == {sample2}"
            print("The following features are UNSUPPORTED")
            for feature in ctx.terminal.unsupported_features:
                ctx.aprint(fmt.format(
                    feature=feature, sample1=sample1,
                    sample2=ctx.ansi(sample2, **feature.test_sgr)))
        if ctx.terminal.broken_features:
            fmt = " - {feature.slug:27}: {sample1} unexpectedly {sample2}"
            print("The following features are BROKEN")
            for feature in ctx.terminal.broken_features:
                ctx.aprint(fmt.format(
                    feature=feature, sample1=sample1,
                    sample2=ctx.ansi(sample2, **feature.test_sgr)))
        if ctx.terminal.configurable_features:
            fmt = " - {feature.slug:27}: {sample1} either {sample2} or {sample3}"
            print("The following features are CONFIGURABLE")
            for feature in ctx.terminal.configurable_features:
                ctx.aprint(fmt.format(
                    feature=feature, sample1=sample1, sample3=sample3,
                    sample2=ctx.ansi(sample2, **feature.test_sgr)))
        if ctx.terminal.supported_features:
            fmt = " - {feature.slug:27}: {sample1} != {sample2}"
            print("The following features are SUPPORTED")
            for feature in ctx.terminal.supported_features:
                ctx.aprint(fmt.format(
                    feature=feature, sample1=sample1,
                    sample2=ctx.ansi(sample2, **feature.test_sgr)))
        if ctx.terminal.unknown_features:
            fmt = " - {feature.slug:27}: {sample1} either {sample2} or {sample3}"
            print("The following features are of UNKNOWN status")
            for feature in ctx.terminal.unknown_features:
                ctx.aprint(fmt.format(
                    feature=feature, sample1=sample1, sample3=sample3,
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
        # ctx.color_ctrl.active = False
        ctx.ansi.active = True

if __name__ == '__main__':
    Terminal().main()
