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

"""
Ingredient for working with XDG Base Directory Specification.

See: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
"""

from __future__ import absolute_import, print_function, unicode_literals

import os

from guacamole.core import Ingredient


class XDGBaseDirectorySpec(object):

    """
    Implementation of the XDG Base Directory Specification.

    This class implements version 0.7 of the specification.

    The XDG Base Directory Specification is based on the following concepts:

     - There is a single base directory relative to which user-specific data
       files should be written. This directory is defined by the environment
       variable $XDG_DATA_HOME.
     - There is a single base directory relative to which user-specific
       configuration files should be written. This directory is defined by
       the environment variable $XDG_CONFIG_HOME.
     - There is a set of preference ordered base directories relative to which
       data files should be searched. This set of directories is defined by
       the environment variable $XDG_DATA_DIRS.
     - There is a set of preference ordered base directories relative to which
       configuration files should be searched. This set of directories is
       defined by the environment variable $XDG_CONFIG_DIRS.
     - There is a single base directory relative to which user-specific non-
       essential (cached) data should be written. This directory is defined by
       the environment variable $XDG_CACHE_HOME.
     - There is a single base directory relative to which user-specific
       runtime files and other file objects should be placed. This directory
       is defined by the environment variable $XDG_RUNTIME_DIR.

    All paths set in these environment variables must be absolute. If an
    implementation encounters a relative path in any of these variables it
    should consider the path invalid and ignore it.

    :attr XDG_DATA_HOME:
         ``$XDG_DATA_HOME`` defines the base directory relative to which user
         specific data files should be stored. If ``$XDG_DATA_HOME`` is either
         not set or empty, a default equal to $HOME/.local/share should be
         used.
    :attr XDG_CONFIG_HOME:
         ``$XDG_CONFIG_HOME`` defines the base directory relative to which user
         specific configuration files should be stored. If ``$XDG_CONFIG_HOME``
         is either not set or empty, a default equal to ``$HOME/.config``
         should be used.
    :attr XDG_DATA_DIRS:
        ``$XDG_DATA_DIRS`` defines the preference-ordered set of base
        directories to search for data files in addition to the
        ``$XDG_DATA_HOME`` base directory. The directories in
        ``$XDG_DATA_DIRS`` should be separated with a colon ``':'``.
        If $XDG_DATA_DIRS is either not set or empty, a value equal to
        ``/usr/local/share/:/usr/share/`` should be used.
    :attr XDG_CONFIG_DIRS:
        ``$XDG_CONFIG_DIRS`` defines the preference-ordered set of base
        directories to search for configuration files in addition to the
        ``$XDG_CONFIG_HOME`` base directory. The directories in
        ``$XDG_CONFIG_DIRS`` should be separated with a colon ``':'``.
        If $XDG_CONFIG_DIRS is either not set or empty, a value equal to
        ``/etc/xdg`` should be used.
    :attr XDG_CACHE_HOME:
        ``$XDG_CACHE_HOME`` defines the base directory relative to which user
        specific non-essential data files should be stored. If
        ``$XDG_CACHE_HOME`` is either not set or empty, a default equal to
        ``$HOME/.cache`` should be used.
    :attr XDG_RUNTIME_DIR:
         ``$XDG_RUNTIME_DIR`` defines the base directory relative to which
         user-specific non-essential runtime files and other file objects (such
         as sockets, named pipes, ...) should be stored. The directory **MUST**
         be owned by the user, and he **MUST** be the only one having read and
         write access to it. Its Unix access mode **MUST** be 0700.
    """

    def __init__(self, env):
        """
        Initialize a new XDG Base Directory Specification object.

        :param env:
            A mapping representing the current environment.
        """
        HOME = env.get("HOME")
        # XDG requires $HOME to be defined. This is typically not true
        # on Windows systems. There's no fall-back (it's not in scope of XDG,
        # it's better to support the Windows equivalents and use an abstraction
        # that picks the platform-specific code to use.
        if HOME is None:
            self.XDG_DATA_HOME = env.get('XDG_DATA_HOME')
            self.XDG_CONFIG_HOME = env.get('XDG_CONFIG_HOME')
            self.XDG_CACHE_HOME = env.get('XDG_CACHE_HOME')
        else:
            self.XDG_DATA_HOME = (
                env.get('XDG_DATA_HOME') or '{0}/.local/share'.format(HOME))
            self.XDG_CONFIG_HOME = (
                env.get('XDG_CONFIG_HOME') or '{0}/.config'.format(HOME))
            self.XDG_CACHE_HOME = (
                env.get('XDG_CACHE_HOME') or '{0}/.cache'.format(HOME))
        # Data and config directories are typically default and are provided
        # by the platform / distribution.
        self.XDG_DATA_DIRS = (
            env.get('XDG_DATA_DIRS') or '/usr/local/share/:/usr/share/')
        self.XDG_CONFIG_DIRS = (
            env.get('XDG_CONFIG_DIRS') or '/etc/xdg')
        # XDG runtime directory is provided by the session manager
        self.XDG_RUNTIME_DIR = env.get('XDG_RUNTIME_DIR')
        isabs = os.path.isabs
        # One last check, each directory MUST be specified with an absolute
        # path or it cannot be used. Let's check for that.
        if not (self.XDG_DATA_HOME is None or isabs(self.XDG_DATA_HOME)):
            self.XDG_DATA_HOME = None
        if not (self.XDG_CONFIG_HOME is None or isabs(self.XDG_CONFIG_HOME)):
            self.XDG_CONFIG_HOME = None
        if not (self.XDG_CACHE_HOME is None or isabs(self.XDG_CACHE_HOME)):
            self.XDG_CACHE_HOME = None
        if not (self.XDG_DATA_DIRS is None or isabs(self.XDG_DATA_DIRS)):
            self.XDG_DATA_DIRS = None
        if not (self.XDG_CONFIG_DIRS is None or isabs(self.XDG_CONFIG_DIRS)):
            self.XDG_CONFIG_DIRS = None
        if not (self.XDG_RUNTIME_DIR is None or isabs(self.XDG_RUNTIME_DIR)):
            self.XDG_RUNTIME_DIR = None


class XDG(Ingredient):

    """Ingredient for working with XDG Base Directory Specification."""

    def added(self, context):
        """
        Ingredient method called before anything else.

        Here this method adds the ``xdg_base`` object to the context.
        The object is an instance of the :class:`XDGBaseDirectorySpec`
        and provides access to all the directories specified by XDG.
        """
        context.xdg_base = XDGBaseDirectorySpec(os.environ)
