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

"""A simple program that uses logging."""

from __future__ import absolute_import, print_function, unicode_literals

import logging

from guacamole import Command


class Logger(Command):

    """Experiment with the logging subsystem."""

    #: Spices tell guacamole how to change some default behavior.
    # By default, the command-line interface to the logging subsystem is
    # disabled. Using the "log:arguments" spice enables it.
    spices = ['log:arguments']

    def invoked(self, ctx):
        """
        Guacamole method used by the command ingredient.

        :param ctx:
            The guacamole context object. Context provides access to all
            features of guacamole.
        :returns:
            The return code of the command. Guacamole translates ``None`` to a
            successful exit status (return code zero).
        """
        logging.debug("Some debugging message")
        print("Just a normal print!")
        logging.info("Some informational message")
        print("Just a normal print!")
        logging.warn("Some warning message")
        print("Just a normal print!")
        logging.error("Some error message")
        print("Just a normal print!")
        logging.critical("Some critical message")
        print("Just a normal print!")


if __name__ == '__main__':
    Logger().main()
