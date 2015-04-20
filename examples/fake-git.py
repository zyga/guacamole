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

"""A fake git-like command with Guacamole."""

from __future__ import absolute_import, print_function, unicode_literals

from guacamole import Command


class GitCommit(Command):

    """The 'git commit' command."""

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        print("fake git commit")

    def register_arguments(self, parser):
        """
        Guacamole method used by the argparse ingredient.

        :param parser:
            Argument parser (from :mod:`argparse`) specific to this command.
        """
        parser.add_argument(
            '-m', '--message', metavar='<msg>',
            help="Use given <msg> as the commit message")


class GitLog(Command):

    """The 'git log' command."""

    def invoked(self, ctx):
        """Method called when the command is invoked."""
        print("fake git log")

    def register_arguments(self, parser):
        """
        Guacamole method used by the argparse ingredient.

        :param parser:
            Argument parser (from :mod:`argparse`) specific to this command.
        """
        parser.add_argument(
            '--follow', action='store_true', help=(
                'Continue listing the history of a file beyond renames'
                ' (works only for a single file).'))


class Git(Command):

    """A fake git-like command."""

    sub_commands = (
        ('commit', GitCommit),
        ('log', GitLog)
    )


if __name__ == '__main__':
    Git().main()
