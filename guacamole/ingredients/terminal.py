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
Terminal identification and feature status.

This module contains a number of classes that culminate in the
:class:`TerminalAwareness` class. The support code is separated into the
following classes:

:class:`TerminalPreset`
    Presets allow applications to work with high-level concepts without having
    to check if each interesting feature is implemented or not. They are not
    directly related to :class:`TerminalFeature` objects, more to the needs of
    the color ingredient defined in :mod:`guacamole.ingredients.color`.  The
    module-level constants can be identified by the ``PRESET_`` prefix.

:class:`TerminalFeature`
    Feature objects describe a single terminal capability. Currently all the
    features are related to ANSI SGR commands needed by the color ingredient.
    Later on additional features may be added, e.g. for non-canonical mode and
    other things that might help to improve the `textland` project.  The
    module-level constants can be identified by the ``ANSI_`` prefix.

:class:`TerminalFeatureStatus`
    Status objects describe the state of implementation of particular features.
    There are just a few possible statuses but they all carry additional
    information useful to some applications. The module-level constants can be
    identified by the ``STATUS_`` prefix.

:class:`TerminalProfile`
    Profile objects contain data and APIs needed to detect a particular
    implementation of a terminal emulator. They are never instantiated.
    Information that they provide is used to create instances of
    :class:`Terminal` objects.

:class:`Terminal`
    Read-only information about the terminal. Exposes all the features and
    their implementation status. This is what the :class:`TerminalAwareness`
    inserts into the context as the ``ctx.terminal`` object.
"""

from __future__ import absolute_import, print_function, unicode_literals

import collections
import gettext
import logging
import os
import platform
import re
import subprocess
import sys

from guacamole.core import Ingredient

__all__ = (
    'TerminalAwareness',
    'TerminalPreset',
    'PRESET_PRIMITIVE',
    'PRESET_COMMON',
    'PRESET_MODERN',
    'TerminalFeature',
    'ANSI_COLOR_BG_INDEXED_16',
    'ANSI_COLOR_BG_INDEXED_256',
    'ANSI_COLOR_BG_INDEXED_8',
    'ANSI_COLOR_BG_TRUECOLOR',
    'ANSI_COLOR_DIM',
    'ANSI_COLOR_FG_INDEXED_16',
    'ANSI_COLOR_FG_INDEXED_256',
    'ANSI_COLOR_FG_INDEXED_8',
    'ANSI_COLOR_FG_TRUECOLOR',
    'ANSI_COLOR_REVERSE',
    'ANSI_FONT_BOLD',
    'ANSI_FONT_ITALIC',
    'ANSI_TEXT_BLINK_FAST',
    'ANSI_TEXT_BLINK_SLOW',
    'ANSI_TEXT_CONCEALED',
    'ANSI_TEXT_CROSSED',
    'ANSI_TEXT_UNDERLINE',
    'TerminalFeatureStatus',
    'STATUS_UNSUPPORTED',
    'STATUS_BROKEN',
    'STATUS_CONFIGURABLE',
    'STATUS_SUPPORTED',
    'STATUS_UNKNOWN',
    'TerminalProfile',
    'Terminal',
    'TerminalAwareness',
)

_logger = logging.getLogger('guacamole')
_string_types = (type(""), str)


def _(msgid):
    return gettext.dgettext("guacamole", msgid)


class NamedSlug(object):

    """
    Support class for descriptive identifiers.

    This class assumes the presence of two attributes, :attr:`name` and
    :attr:`slug`. Name is displayed in string context. Slug is used for
    comparison with other strings and for hashing.

    This class is used as a base for all the constants in this module.
    """

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.slug)

    def __eq__(self, other):
        if isinstance(other, _string_types):
            return self.slug == other
        else:
            return super(NamedSlug, self).__eq__(other)

    def __ne__(self, other):
        if isinstance(other, _string_types):
            return self.slug == other
        else:
            return super(NamedSlug, self).__ne__(other)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.slug)


TerminalPresetBase = collections.namedtuple(
    "TerminalPresetBase", "slug name palette_preference")


class TerminalPreset(NamedSlug, TerminalPresetBase):

    """
    Information about a terminal preset.

    Each preset is described by these attributes:

    :ivar slug:
        This is just the fixed identifier of the preset. Note that presets
        compare equal to strings that match the slug. This is done to avoid the
        need to import anything from this module in most applications.

    :ivar name:
        A human-readable, localized name of the preset. This is something that
        suits a bullet-list very well. Preset names are not sentences and are
        not capitalized. An example name might be "primitive terminal".

    :ivar palette_preference:
        An integer representing one of ``PREFER_`` constants from the color
        module. This can be used to set the preferred lookup mode for the
        global palette object.

    Presets have two purposes. On the outside they help applications deal with
    the numerous little features, compatibilities and bugs. Instead having to
    check if a particular feature is supported you can just look at the preset.
    Since there are just a few presets (way less than combination of features
    and their statuses) this provides a far easier approach to doing
    conditional rendering in applications.

    On the inside of guacamole they help the color controller set good defaults
    for how the color palette is supposed to lookup colors. Guacamole has
    several "color types" that correspond to various features implemented by
    particular terminal emulators.
    """

#: Terminal preset for primitive terminals.
#:
#: Primitive terminals support classic ANSI colors and nothing much else.
#: Other features maybe available (broken or not), please inspect the terminal
#: feature mapping for details. Notable examples of this preset are the Linux
#: console and the Windows Command Prompt (cmd.exe).
PRESET_PRIMITIVE = TerminalPreset("primitive", _("primitive terminal"), 0)

#: Terminal preset for common terminals.
#:
#: Common terminals support way more features and typically provide at least
#: 256-color palette, bold and a few other text styles. Most terminal emulators
#: that people actually use will be compatible with this preset. Notable
#: examples are: Putty, Apple's Terminal.app, older versions of xterm,
#  Gnome Terminal and the KDE Konsole.
PRESET_COMMON = TerminalPreset("common", _("common terminal"), 1)

#: Terminal preset for modern terminals.
#:
#: Modern terminals support almost all the features possible but are typically
#: exclusively available on the most recent versions of various Linux
#: distributions. One of the distinguishing features is the ability to access
#: the true color palette. Modern terminals also have less bugs and generally
#: work better in every situation then their less-capable brethren. Notable
#: examples include the: Gnome Terminal (since version 3.14)
PRESET_MODERN = TerminalPreset("modern", _("modern terminal"), 2)


TerminalFeatureBase = collections.namedtuple(
    "TerminalFeatureBase", "slug name test_sgr")


class TerminalFeature(NamedSlug, TerminalFeatureBase):

    """
    Information about a particular terminal emulator feature.

    Each feature is described by these attributes:

    :ivar slug:
        This is just the fixed identifier of the feature. Note that it contains
        dashes rather than underscores. Example slug looks like
        ``ansi-font-bold`` which implies that it denotes support for ANSI SGR
        control sequences that control bold font face. Currently all the
        features start with ``ansi`` but it is expected that platform-specific
        features will be exposed later and they will use a different prefix as
        they are not standardized.

    :ivar name:
        A human-readable, localized name of the feature. This is something that
        suits a bullet-list very well. Feature names are not sentences and are
        not capitalized. An example name might be "bold font face".

    :ivar test_srg:
        A dictionary with a set of SGR directives supported by the
        ANSIFormatter() class from the ``ansi`` ingredient. Those are expected
        to be applied as keyword arguments to something like ``ctx.aprint()``
        or ``ctx.ansi()``. This is meant to serve as a testing feature. Please
        have a look at the example program ``examples/terminal.py`` for
        inspiration on how to take advantage of this in your applications.

    Each terminal feature object is hashable (it hashes to the same value as
    the slug does). When converted to a string it becomes the name of the
    feature.

    Inside a guacamole-based application you can safely hard-code strings that
    correspond to slug of particular features you care about. Those are
    promised to be maintained forever as a part of the public API.
    """

#: Feature representing support for eight "classic" background colors.
#:
#: Those colors can be used with their string identifiers or with the "classic"
#: convention of ``-(1 + color_index)``, that is, with negative numbers from
#: -9 all the way up to -1.
#:
#: This feature is widely supported. It works on all the major platforms.
#: Non-niche terminal emulators implement it correctly.
ANSI_COLOR_BG_INDEXED_8 = TerminalFeature(
    'ansi-color-bg-indexed-8', _("8 background colors"), {'bg': -3})

#: Feature representing support for sixteen "classic" background colors.
#:
#: The first eight is identical to ``ANSI_COLOR_BG_INDEXED_8`` and the other
#: eight contain a brighter version of the same colors.  Those colors can be
#: used with their string identifiers or with the "classic" convention of
#: ``-(1 + color_index)``, that is, with negative numbers from -16 all the way
#: up to -1.
#:
#: This feature is widely supported although, most notably, it is not available
#: in the classic Linux console (running in a virtual terminal). If you target
#: server applications that are not operated remotely over SSH you should not
#: use it.
ANSI_COLOR_BG_INDEXED_16 = TerminalFeature(
    'ansi-color-bg-indexed-16', _("16 background colors"), {'bg': -11})

#: Feature representing support for 256 indexed palette background colors.
#:
#: The colors are split into three bands. Colors from 0 till 16 (exclusive) are
#: the same as those described by ``ANSI_COLOR_BG_INDEXED_16``. Depending on
#: terminal settings though, they might render differently. Terminal emulators
#: that allow the user to customize some colors normally only expose the
#: 16-color set. Using colors from this range usually gives the application
#: reliable and predictable look.
#:
#: This feature is widely supported in graphical environments with the notable
#: exception of the Windows ``cmd.exe`` "console". It is also not supported on
#: some older systems but it can be considered as a baseline standard for many
#: tools.
ANSI_COLOR_BG_INDEXED_256 = TerminalFeature(
    'ansi-color-bg-indexed-256', _("256 background colors"), {'bg': 0x1C})

#: Feature representing support for 16 million (non indexed) background colors.
#:
#: The colors have no associated color-space and are expected to correspond
#: directly to typical RGB colors. This feature is not widely supported.
#: Currently there are no terminal emulators available for neihter Windows
#: nor Mac OS X that support this feature.
ANSI_COLOR_BG_TRUECOLOR = TerminalFeature(
    'ansi-color-bg-truecolor', _("16M background colors"), {
        'bg': (0x00, 0x7f, 0x00)})

#: Feature representing support for dimming foreground and background color.
#:
#: This feature makes the foreground (and sometimes background) colors visibly
#: dimmer. It can be used to create a subtle effect but it is rather
# inconsistent across different terminal emulators. Some older terminal
# emulators implement it incorrectly or map it to a different color altogether.
ANSI_COLOR_DIM = TerminalFeature(
    'ansi-color-dim', _("dim color"), {'dim': 1})

#: Feature representing support for eight "classic" foreground colors.
#:
#: Those colors can be used with their string identifiers or with the "classic"
#: convention of ``-(1 + color_index)``, that is, with negative numbers from
#: -9 all the way up to -1.
#:
#: This feature is widely supported. It works on all the major platforms.
#: Non-niche terminal emulators implement it correctly.
ANSI_COLOR_FG_INDEXED_8 = TerminalFeature(
    'ansi-color-fg-indexed-8', _("8 foreground colors"), {'fg': -3})

#: Feature representing support for sixteen "classic" foreground colors.
#:
#: The first eight is identical to ``ANSI_COLOR_BG_INDEXED_8`` and the other
#: eight contain a brighter version of the same colors.  Those colors can be
#: used with their string identifiers or with the "classic" convention of
#: ``-(1 + color_index)``, that is, with negative numbers from -16 all the way
#: up to -1.
#:
#: This feature is widely supported although, most notably, it is not available
#: in the classic Linux console (running in a virtual terminal). If you target
#: server applications that are not operated remotely over SSH you should not
#: use it.
ANSI_COLOR_FG_INDEXED_16 = TerminalFeature(
    'ansi-color-fg-indexed-16', _("16 foreground colors"), {'fg': -11})

#: Feature representing support for 256 indexed palette foreground colors.
#:
#: The colors are split into three bands. Colors from 0 till 16 (exclusive) are
#: the same as those described by ``ANSI_COLOR_FG_INDEXED_16``. Depending on
#: terminal settings though, they might render differently. Terminal emulators
#: that allow the user to customize some colors normally only expose the
#: 16-color set. Using colors from this range usually gives the application
#: reliable and predictable look.
#:
#: This feature is widely supported in graphical environments with the notable
#: exception of the Windows ``cmd.exe`` "console". It is also not supported on
#: some older systems but it can be considered as a baseline standard for many
#: tools.
ANSI_COLOR_FG_INDEXED_256 = TerminalFeature(
    'ansi-color-fg-indexed-256', _("256 foreground colors"), {'fg': 0x1C})

#: Feature representing support for 16 million (non indexed) foreground colors.
#:
#: The colors have no associated color-space and are expected to correspond
#: directly to typical RGB colors. This feature is not widely supported.
#: Currently there are no terminal emulators available for neither Windows
#: nor Mac OS X that support this feature.
ANSI_COLOR_FG_TRUECOLOR = TerminalFeature(
    'ansi-color-fg-truecolor', _("16M foreground colors"), {
        'fg': (0x00, 0x7f, 0x00)})

#: Feature representing support for reversing foreground and background colors.
#:
#: This feature makes both the foreground and background color inverted. It
#: can be useful for making simple highlight effects without resorting
#: to working colors explicitly.
#:
#: It is most notably not supported on Windows, due to some ancient deliberate
#: incompatibility  but the colorama module implements it by modifying colors
#: explicitly behind the scenes.
ANSI_COLOR_REVERSE = TerminalFeature(
    'ansi-color-reverse', _("reversed colors"), {'reverse': 1})

#: Feature representing support for bold font face type.
#:
#: This feature makes the terminal emulator render a portion of the text
#: using an bold variant of the font. It is sometimes unsupported simply
#: because the terminal font lacks the italic variant.
#:
#: NOTE that this feature is ambiguous. It may also render as brighter
#: colored text instead of the bold font face. It is also often explicitly
#: configurable.
#: Apart from font and configuration issues it is widely supported everywhere
#: except for the Windows command prompt.
ANSI_FONT_BOLD = TerminalFeature(
    'ansi-font-bold', _("bold font face"), {'bold': 1})

#: Feature representing support for italic font face type.
#:
#: This feature makes the terminal emulator render a portion of the text
#: using an italic variant of the font. It is sometimes unsupported simply
#: because the terminal font lacks the italic variant.
ANSI_FONT_ITALIC = TerminalFeature(
    'ansi-font-italic', _("italic font face"), {'italic': 1})

#: Feature representing support for fast-blinking text.
#:
#: So far no terminal emulator implements this feature correctly.
#: Certain emulators use alternative background color but nobody really
#: makes the text blink.
ANSI_TEXT_BLINK_FAST = TerminalFeature(
    'ansi-text-blink-fast', _("fast-blinking text"), {'blink_fast': 1})

#: Feature representing support for slow-blinking text.
#:
#: This feature was recently dropped from Gnome Terminal in order to improve
#: energy efficiency.
ANSI_TEXT_BLINK_SLOW = TerminalFeature(
    'ansi-text-blink-slow', _("slow-blinking text"), {'blink_slow': 1})

#: Feature representing support for concealed text.
#:
#: Concealed text is technically printed to the terminal can can be copy-pasted
#: but cannot be seen, even after highlighting it in order to perform a copy
#: operation.
#:
#: This feature is not widely supported but modern terminals have started to
#: implement it correctly.
ANSI_TEXT_CONCEALED = TerminalFeature(
    'ansi-text-concealed', _("concealed text"), {'concealed': 1})

#: Feature representing support for crossed text.
#:
#: Crossed text looks like someone had drawn a line in the middle through
#: all the letters. It can be useful to mark text modifications but it seems
#: to be used rather infrequently.
ANSI_TEXT_CROSSED = TerminalFeature(
    'ansi-text-crossed', _("crossed text"), {'crossed': 1})

#: Feature representing support for underlined text.
#:
#: Underlined text has a line beneath all the letters. It looks like a typical
#: hyperlink in a web browser. This feature is used commonly and is supported
#: pretty well by common terminals.
ANSI_TEXT_UNDERLINE = TerminalFeature(
    'ansi-text-underline', _("underlined text"), {'underline': 1})


#: Internal tuple of all the available features.
_all_features = (
    ANSI_COLOR_BG_INDEXED_16,
    ANSI_COLOR_BG_INDEXED_256,
    ANSI_COLOR_BG_INDEXED_8,
    ANSI_COLOR_BG_TRUECOLOR,
    ANSI_COLOR_DIM,
    ANSI_COLOR_FG_INDEXED_16,
    ANSI_COLOR_FG_INDEXED_256,
    ANSI_COLOR_FG_INDEXED_8,
    ANSI_COLOR_FG_TRUECOLOR,
    ANSI_COLOR_REVERSE,
    ANSI_FONT_BOLD,
    ANSI_FONT_ITALIC,
    ANSI_TEXT_BLINK_FAST,
    ANSI_TEXT_BLINK_SLOW,
    ANSI_TEXT_CONCEALED,
    ANSI_TEXT_CROSSED,
    ANSI_TEXT_UNDERLINE,
)


TerminalFeatureStatusBase = collections.namedtuple(
    "TerminalFeatureStatusBase", "slug name")


class TerminalFeatureStatus(NamedSlug, TerminalFeatureStatusBase):

    """
    Information about the status of a terminal emulator feature.

    This class simply encodes the status. There are several concrete objects
    available. Please see below.

    :ivar slug:
        Unique identifier of this feature status within Guacamole.
    :ivar name:
        A human readable, translated name of this status.
    """

#: Status indicating unsupported terminal features.
#:
#: This status means that the feature is simply not implemented. At the same
#: time the feature does not cause the terminal to malfunction or misinterpret
#: the feature in any way.
#:
#: This is the default status for all the features.
STATUS_UNSUPPORTED = TerminalFeatureStatus('unsupported', _("unsupported"))

#: Status indicating broken or malfunctioning features.
#:
#: This status means that the terminal emulator reacts in an incorrect way
#: to the use of this feature. This may include using alternate rendering
#: (that perhaps is indistinguishable from another feature) or unexpected
#: mishandling as another feature (typically due to incorrect parsing of
#: the SGR command).
STATUS_BROKEN = TerminalFeatureStatus('broken', _("broken"))

#: Status indicating features under user control.
#:
#: This status means that a feature is understood but depends on the
#: configuration of the terminal emulator. As of this time guacamole
#: does not contain the ability to check what is the effective value.
STATUS_CONFIGURABLE = TerminalFeatureStatus('configurable', _("configurable"))

#: Status indicating correctly functioning feature.
#:
#: This status means that the feature is working as expected and described
#: in the documentation of guacamole. Sometimes a feature is "recognized"
#: but the rendering differs from what is expect, with the notable exception
#: of the ANSI_FONT_BOLD feature this is always mapped to the broken status.
STATUS_SUPPORTED = TerminalFeatureStatus('supported', _("supported"))

#: Status indicating that guacamole cannot determine if the feature works.
#:
#: This status means that insufficient information is available to accurately
#: know if the feature will be recognized and implemented correctly.
#:
#: This is typically encountered in terminal emulators that emulate a terminal
#: emulator itself (multiplexers, such as screen) where the information about
#: the outer emulator is simply not available and is actually not constant as
#: they can be re-attached to another terminal emulator with a different
#: feature set.
#:
#: This status is also used for remote connections when again, the real
#: terminal emulator is behind a network connection and no information about
#: its identity is provided.
STATUS_UNKNOWN = TerminalFeatureStatus("unknown", _("unknown"))


class TerminalProfile(object):

    """
    Base class for declaring terminal emulator "profiles".

    A profile in this context is meant to describe both the fingerprinting
    information necessary to detect and distinguish one emulator from another
    as well as some out-of-band facts about that terminal.
    """

    # Detectors

    #: A detector that looks for a given ``TERM`` environment variable.
    #: See :meth:`is_running()` for details. This can be safely None.
    TERM = None

    #: A detector that looks for a given ``TERM_PROGRAM`` environment variable.
    #: See :meth:`is_running()` for details. This can be safely None.
    TERM_PROGRAM = None

    #: Flag indicating if this terminal is a multiplexer.
    #:
    #: Multiplexers preserve the environment form the external terminal
    #: emulator, this includes TERM_PROGRAM and TERM_PROGRAM_VERSION which
    #: should be ignored in such cases.
    is_multiplexer = False

    #: A detector that looks for a given process name in the list of parent
    #: processes of an application using guacamole. Note that the name
    #: is always in parentheses and is truncated to certain fixed length.
    #: See :meth:`is_running()` for details. This can be safely None.
    comm = None

    #: A detector for knowing how to execute the terminal emulator to get
    #: the version string in the output.
    #: See :meth:`get_version()` for details. This can be safely None.
    version_query_cmd = None

    #: A detector for locating the version string in the output of the
    #: terminal emulator specified by :attr:`version_query_cmd`.
    #: See :meth:`get_version()` for details. This can be safely None.
    version_pattern = None

    # Facts

    #: Unique identifier of the terminal within guacamole.
    slug = None

    #: human-readable,translated name of the terminal emulator.
    name = None

    #: A :class:`TerminalPreset` object recommended for this emulator.
    preset = None

    #: A list of features that are explicitly unsupported.
    #:
    #: Note that by default everything is unsupported. Therefore this attribute
    #: is simply provided for completeness but is not useful in itself.
    unsupported_features = ()

    #: A dictionary mapping version strings to a lists of unsupported features.
    unsupported_versioned_features = {}

    #: A list of features that are supported.
    supported_features = ()

    #: A dictionary mapping version strings to a lists of supported features.
    supported_versioned_features = {}

    #: A list of features that are broken.
    broken_features = ()

    #: A dictionary mapping version strings to a lists of broken features.
    broken_versioned_features = {}

    #: A list of features that are configurable.
    configurable_features = ()

    #: A dictionary mapping version strings to a lists of configurable
    #: features.
    configurable_versioned_features = {}

    #: A list of features that are of unknown status.
    unknown_features = ()

    #: A dictionary mapping version strings to a lists of features of unknown
    #: status.
    unknown_versioned_features = {}

    @classmethod
    def is_running(cls, proc_info_list):
        """
        Check if this process is running in a terminal matching this profile.

        :param proc_info_list:
            A list of information about all the parent processes.  This might
            be empty. It is currently only provided on Linux systems. Each
            element is a tuple with contains at least the named attribute
            `comm` which corresponds to the process name.
        :returns:
            True if the terminal described by this profile is running.

        This method looks for signs of the terminal in the following means:

        - The ``TERM`` environment variable is equal to the :attr:`TERM`
          attribute (only when other than None).
        - The ``TERM_PROGRAM`` environment variable is equal to the
          :attr:`TERM_PROGRAM` attribute (only when other than None)
        - There is a process in `proc_info_list` that matches the :attr:`comm`
          attribute (only when other than None).
        """
        # Look for TERM environment variable
        if cls.TERM is not None:
            if os.getenv("TERM") == cls.TERM:
                return True
        # Multiplexers cannot take advantage of TERM_PROGRAM as it is the
        # version of the outer host terminal.
        if not cls.is_multiplexer:
            # Look for TERM_PROGRAM environment variable
            if cls.TERM_PROGRAM is not None:
                if os.getenv("TERM_PROGRAM") == cls.TERM_PROGRAM:
                    return True
        # Look at the list of processes to see if the terminal is running
        if cls.comm is not None:
            for info in proc_info_list:
                if info.comm == cls.comm:
                    return info

    @classmethod
    def get_version(cls):
        """
        Try to determine the version of the terminal emulator.

        :returns:
            The version of the terminal emulator program or None if it cannot
            be determined.

        This method inspect the ``TERM_PROGRAM_VERSION`` environment variable.
        If it is defined then the value is immediately returned. This allows
        terminals to efficiently provide this information, even across SSH (but
        only if everything is configured correctly, currently this is not true
        on an system).

        As a slower alternative this method runs the terminal emulator program
        as described by :attr:`version_query_cmd`. The output (combined stdout
        and stderr) is then matched to the :attr:`version_pattern` regular
        expression and the first unnamed group from that expression is used as
        the return value. Both of those attributes need to be provided for this
        code to be active.

        .. note::
            This method is only called when :meth:`is_running()` returned True.
        """
        # Multiplexers cannot take advantage of TERM_PROGRAM_VERSION as it is
        # the version of the outer host terminal.
        if not cls.is_multiplexer:
            # Look for TERM_PROGRAM_VERSION environment variable
            version = os.getenv("TERM_PROGRAM_VERSION")
            if version:
                # This takes priority over the more costly methods. It is
                # assumed that if the environment variable _does_ exist it is
                # set to the correct value. As of this writing only
                # Terminal.app on OS X sets this variable.
                return version
        # Ask the terminal executable for its version if one is available
        if (cls.version_query_cmd is not None and
                cls.version_pattern is not None):
            proc = subprocess.Popen(
                cls.version_query_cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output = proc.communicate()[0]
            try:
                output = output.decode("UTF-8")
            except UnicodeDecodeError:
                return
            # Get the version from the output if a pattern is provided
            match = re.search(cls.version_pattern, output, re.M)
            if match:
                version = match.group(1)
                return version

    @classmethod
    def get_comparable_version(cls, version):
        """
        Get a interpretation of version that is useful for comparisons.

        :param version:
            A text string that represents the version a terminal emulator.
        :returns:
            A tuple that can be compared with other versions better than the
            string alone could.

        This method essentially splits the `version` string into a
        dot-separated tuple of components. Each component is also converted to
        a number but this conversion can silently fail (a string is used in
        such a case)
        """
        def maybe_int(value):
            try:
                return int(value)
            except ValueError:
                return value
        if version is not None:
            version = [maybe_int(v_part) for v_part in version.split('.')]
        return version

    @classmethod
    def get_broken_features(cls, version):
        """
        Get a list of broken features present in the specified version.

        :param:
            Version string of the terminal emulator (or None)
        :returns:
            A list of :class:`TerminalFeature` objects that describe broken
            features.

        This method returns an union of :attr:`broken_features` and all the
        :attr:`broken_versioned_features` that are greater or equal to the
        `version` passed as argument. Versions are compared with the aid of
        :meth:`get_comparable_version()`
        """
        broken_features = list(cls.broken_features)
        if version is not None:
            comparable_version = cls.get_comparable_version(version)
            for since_version in sorted(
                    cls.broken_versioned_features,
                    key=lambda v: v.split('.')):
                if comparable_version >= cls.get_comparable_version(
                        since_version):
                    broken_features.extend(
                        cls.broken_versioned_features[since_version])
        return broken_features

    @classmethod
    def get_supported_features(cls, version):
        """
        Get a list of supported features present in the specified version.

        :param:
            Version string of the terminal emulator (or None)
        :returns:
            A list of :class:`TerminalFeature` objects that describe supported
            features.

        This method returns an union of :attr:`supported_features` and all the
        :attr:`supported_versioned_features` that are greater or equal to the
        `version` passed as argument. Versions are compared with the aid of
        :meth:`get_comparable_version()`.
        """
        supported_features = list(cls.supported_features)
        if version is not None:
            comparable_version = cls.get_comparable_version(version)
            for since_version in sorted(
                    cls.supported_versioned_features,
                    key=lambda v: v.split('.')):
                if comparable_version >= cls.get_comparable_version(
                        since_version):
                    supported_features.extend(
                        cls.supported_versioned_features[since_version])
        return supported_features

    @classmethod
    def get_configurable_features(cls, version):
        """
        Get a list of configurable features present in the specified version.

        :param:
            Version string of the terminal emulator (or None)
        :returns:
            A list of :class:`TerminalFeature` objects that describe
            configurable features.

        This method returns an union of :attr:`configurable_features` and all
        the :attr:`configurable_versioned_features` that are greater or equal
        to the `version` passed as argument. Versions are compared with the aid
        of :meth:`get_comparable_version()`.
        """
        configurable_features = list(cls.configurable_features)
        if version is not None:
            comparable_version = cls.get_comparable_version(version)
            for since_version in sorted(
                    cls.configurable_versioned_features,
                    key=lambda v: v.split('.')):
                if comparable_version >= cls.get_comparable_version(
                        since_version):
                    configurable_features.extend(
                        cls.configurable_versioned_features[since_version])
        return configurable_features

    @classmethod
    def get_unsupported_features(cls, version):
        """
        Get a list of unsupported features present in the specified version.

        :param:
            Version string of the terminal emulator (or None)
        :returns:
            A list of :class:`TerminalFeature` objects that describe
            unsupported features.

        This method returns an union of :attr:`unsupported_features` and all
        the :attr:`unsupported_versioned_features` that are greater or equal to
        the `version` passed as argument. Versions are compared with the aid of
        :meth:`get_comparable_version()`.
        """
        unsupported_features = list(cls.unsupported_features)
        if version is not None:
            comparable_version = cls.get_comparable_version(version)
            for since_version in sorted(
                    cls.unsupported_versioned_features,
                    key=lambda v: v.split('.')):
                if comparable_version >= cls.get_comparable_version(
                        since_version):
                    unsupported_features.extend(
                        cls.unsupported_versioned_features[since_version])
        return unsupported_features

    @classmethod
    def get_unknown_features(cls, version):
        """
        Get a list of features of unknown status present in a given version.

        :param:
            Version string of the terminal emulator (or None)
        :returns:
            A list of :class:`TerminalFeature` objects that describe
            features of unknown status.

        This method returns an union of :attr:`unknown_features` and all the
        :attr:`unknown_versioned_features` that are greater or equal to the
        `version` passed as argument. Versions are compared with the aid of
        :meth:`get_comparable_version()`.
        """
        unknown_features = list(cls.unknown_features)
        if version is not None:
            comparable_version = cls.get_comparable_version(version)
            for since_version in sorted(
                    cls.unknown_versioned_features,
                    key=lambda v: v.split('.')):
                if comparable_version >= cls.get_comparable_version(
                        since_version):
                    unknown_features.extend(
                        cls.unknown_versioned_features[since_version])
        return unknown_features


class UnknownRemoteSshProfile(TerminalProfile):

    """Terminal profile for all remote connections (e.g. ssh)."""

    # Facts
    name = _("Unknown Terminal over SSH Connection")
    slug = str("remote-ssh")
    preset = PRESET_COMMON
    supported_features_xterm = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
    )

    @classmethod
    def is_running(cls, proc_info_list):
        if os.getenv("SSH_CONNECTION"):
            return True

    @classmethod
    def get_supported_features(cls, version):
        TERM = os.getenv("TERM")
        # XXX: putty has conservative defaults while it actually supports
        # xterm-256color profile more than this.
        if TERM == 'xterm':
            return cls.supported_features_xterm
        else:
            return super(UnknownRemoteSshProfile, cls).get_supported_features(
                version)

    @classmethod
    def get_unknown_features(cls, version):
        return set(_all_features) - set(cls.get_supported_features(version))


class ScreenProfile(TerminalProfile):

    """Terminal profile for screen."""

    # Detectors
    TERM = 'screen'
    comm = '(screen)'
    version_query_cmd = ['screen', '--version']
    version_pattern = 'Screen version ([0-9.]+?) '
    is_multiplexer = True

    # Facts
    name = _("Screen Terminal Multiplexer")
    slug = str("multiplexer-screen")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
        ANSI_COLOR_DIM,
    )
    broken_features = (
        ANSI_FONT_ITALIC,
    )


class TmuxProfile(TerminalProfile):

    """Terminal profile for tmux."""

    # Detectors
    comm = '(tmux)'
    version_query_cmd = ['tmux', '-V']
    version_pattern = 'tmux ([0-9.]+)'
    is_multiplexer = True

    # Facts
    name = _("Tmux Terminal Multiplexer")
    slug = str("multiplexer-tmux")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
        ANSI_TEXT_CONCEALED,
        ANSI_COLOR_DIM,
        ANSI_FONT_ITALIC,
    )


class CmdExeProfile(TerminalProfile):

    """Terminal profile for cmd.exe on Windows."""

    # Facts
    name = _('Windows Command Prompt')
    slug = str("windows-command-prompt")
    preset = PRESET_PRIMITIVE
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_FONT_BOLD,  # emulated as white text by colorama
    )

    @classmethod
    def is_running(cls, proc_info_list):
        # This is a bit lame but I'm not sure how to traverse the process
        # tree on windows.
        if sys.platform == 'win32' and sys.stdout.isatty():
            return True

    @classmethod
    def get_version(cls):
        return platform.win32_ver()[1]


class TerminalAppProfile(TerminalProfile):

    """Terminal profile for Terminal.app on OS X."""

    # Detectors
    TERM_PROGRAM = 'Apple_Terminal'

    # Facts
    name = _('Terminal.app')
    slug = str("osx-apple-terminal")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_TEXT_BLINK_SLOW,
        ANSI_TEXT_CONCEALED,
        ANSI_TEXT_UNDERLINE,
    )
    configurable_features = (
        # Depending on the theme italic text might not display correctly. Some
        # of the themes use a font with just the monospace variant but without
        # the italics variant.
        ANSI_FONT_ITALIC,
        # Bold-face fonts support is a configurable property of each theme. I
        # don't know what the defaults are though.
        ANSI_FONT_BOLD,
    )


class iTermProfile(TerminalProfile):

    """Terminal profile for iTerm.app on OS X."""

    # Detectors
    TERM_PROGRAM = 'iTerm.app'

    # Facts
    name = _('iTerm.app')
    slug = str("osx-iterm")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_TEXT_BLINK_SLOW,
        ANSI_TEXT_UNDERLINE,
    )
    configurable_features = (
        # Depending on the theme italic text might not display correctly. Some
        # of the themes use a font with just the monospace variant but without
        # the italics variant.
        ANSI_FONT_ITALIC,
        # Bold-face fonts support is a configurable property of each theme. I
        # don't know what the defaults are though.
        ANSI_FONT_BOLD,
        # Another configurable setting
        ANSI_TEXT_BLINK_SLOW,
    )


class LinuxConsoleProfile(TerminalProfile):

    # Detectors
    comm = '(login)'
    TERM = 'linux'
    version_pattern = "([0-9.]+)"

    # Facts
    name = _("Linux Console")
    slug = str("linux-console")
    preset = PRESET_PRIMITIVE
    broken_features = (
        # Those just render to other colors
        ANSI_COLOR_DIM,
        ANSI_FONT_ITALIC,
        ANSI_TEXT_UNDERLINE,
    )
    broken_versioned_features = {
        '3.19.0': (
            ANSI_COLOR_FG_INDEXED_256,
            ANSI_COLOR_FG_TRUECOLOR,
            ANSI_TEXT_BLINK_SLOW,
        ),
    }
    supported_features = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
    )

    @classmethod
    def get_version(cls):
        version = os.uname()[2]  # [2] is the "release" field
        # Filter-away package release number from the kernel version
        if cls.version_pattern is not None:
            match = re.match(cls.version_pattern, version)
            if match:
                version = match.group(1)
        return version


class GnomeTerminalProfile(TerminalProfile):

    # Detectors
    comm = '(gnome-terminal)'
    version_query_cmd = ['gnome-terminal', '--version']
    # NOTE: The output of --version is localized. Here we're just
    # looking for anything that is a dotted number. The part before
    # (or perhaps after) the number is not relevant to us.
    version_pattern = '.*?([0-9.]+)'

    # Facts
    name = _('Gnome Terminal')
    slug = str("linux-gnome-terminal")
    preset = PRESET_MODERN
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_DIM,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_CONCEALED,
        ANSI_TEXT_CROSSED,
        ANSI_TEXT_UNDERLINE,
    )
    supported_versioned_features = {
        '3.14.2': {
            ANSI_COLOR_BG_TRUECOLOR,
            ANSI_COLOR_FG_TRUECOLOR,
            ANSI_FONT_ITALIC,
        }
    }
    unsupported_versioned_features = {
        '3.14.2': (
            ANSI_TEXT_BLINK_SLOW,
        )
    }


class GnomeTerminalServerProfile(GnomeTerminalProfile):

    # This is the truncated 'gnome-terminal-server' executable
    comm = '(gnome-terminal-)'


class KonsoleProfile(TerminalProfile):

    """Terminal profile for the KDE Konsole."""

    # Detectors
    comm = '(konsole)'
    version_query_cmd = ['konsole', '-version']
    version_pattern = 'Konsole: (.+)'

    name = _("Konsole")
    slug = str("linux-kde-konsole")
    preset = PRESET_MODERN
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_BG_TRUECOLOR,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_FG_TRUECOLOR,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_BLINK_SLOW,
        ANSI_TEXT_UNDERLINE,
    )
    supported_versioned_features = {
        '3.0.1': (
            ANSI_FONT_ITALIC,
        )
    }


class XTermProfile(TerminalProfile):

    """Terminal profile for XTerm."""

    # Detectors
    comm = '(xterm)'
    version_query_cmd = ['xterm', '-version']
    version_pattern = 'XTerm\((.+)\)'

    # Facts
    name = _('X Terminal Emulator')
    slug = str("linux-x11-terminal")
    preset = PRESET_COMMON
    supported_versioned_features = {
        # XXX: The version is approximate.
        # It is possible that some features are available earlier.
        '271': (
            ANSI_COLOR_BG_INDEXED_16,
            ANSI_COLOR_BG_INDEXED_256,
            ANSI_COLOR_BG_INDEXED_8,
            ANSI_COLOR_FG_INDEXED_16,
            ANSI_COLOR_FG_INDEXED_256,
            ANSI_COLOR_FG_INDEXED_8,
            ANSI_COLOR_REVERSE,
            ANSI_FONT_BOLD,
            ANSI_TEXT_BLINK_SLOW,
            ANSI_TEXT_CONCEALED,
            ANSI_TEXT_UNDERLINE,
        ),
        # XXX: The version is approximate.
        # It is possible that some features are available earlier.
        '312': (
            ANSI_COLOR_BG_TRUECOLOR,
            ANSI_COLOR_DIM,
            ANSI_COLOR_FG_TRUECOLOR,
            ANSI_FONT_ITALIC,
            ANSI_TEXT_CROSSED,
        )
    }


class TerminologyProfile(TerminalProfile):

    """Terminal profile for the Terminology terminal emulator."""

    # Detectors
    comm = '(terminology)'
    version_query_cmd = ['terminology', '--version']
    version_pattern = 'Version: (.+)'

    # Facts
    name = _('Terminology')
    slug = str("linux-misc-terminology")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_DIM,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_CONCEALED,
        ANSI_TEXT_CROSSED,
        ANSI_TEXT_UNDERLINE,
    )


class TerminatorProfile(TerminalProfile):

    """Terminal profile for the Terminator terminal emulator."""

    # Detectors
    comm = '(/usr/bin/termin)'
    version_query_cmd = ['terminator', '--version']
    version_pattern = 'terminator (.+)'

    # Facts
    name = _("Terminator")
    slug = str("linux-misc-terminator")
    preset = PRESET_COMMON
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_DIM,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_CONCEALED,
        ANSI_TEXT_CROSSED,
        ANSI_TEXT_UNDERLINE,
    )


class RXVTProfile(TerminalProfile):

    """Terminal profile for the RXVT terminal emulator."""

    # Detectors
    comm = '(rxvt)'
    version_query_cmd = ['rxvt', '-help']
    version_pattern = 'Usage v(.+?) '

    # Facts
    name = _("RXVT")
    slug = str("linux-misc-rxvt")
    preset = PRESET_COMMON
    broken_features = (
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_TEXT_BLINK_SLOW,
    )
    supported_features = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
    )


class PTermProfile(TerminalProfile):

    """Terminal profile for the *pterm* terminal emulator."""

    # Detectors
    comm = '(pterm)'
    # NOTE: There's no way to query for version

    # Facts
    name = _("Putty Terminal")
    slug = str("linux-misc-eterm")
    preset = PRESET_COMMON
    broken_features = (
        # NOTE: Those two render to some odd color
        ANSI_TEXT_BLINK_FAST,
        ANSI_TEXT_BLINK_SLOW,
    )
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
    )


class ATermProfile(TerminalProfile):

    """Terminal profile for the *aterm* terminal emulator."""

    # Detectors
    comm = '(aterm)'

    # Facts
    name = _("Afterstep XVT")
    slug = str("linux-misc-aterm")
    preset = PRESET_COMMON
    broken_features = (
        # This renders to some unexpected color
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_256,
        # This renders to some odd color
        ANSI_TEXT_BLINK_SLOW,
    )
    supported_features = (
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
    )


class ETermProfile(TerminalProfile):

    """Terminal profile for the *eterm* terminal emulator."""

    # Detectors
    comm = '(Eterm)'
    version_query_cmd = ['Eterm', '--version']
    version_pattern = 'Eterm (.+?) '

    # Facts
    name = _("Enlightened Terminal Emulator")
    slug = str("linux-misc-eterm")
    preset = PRESET_COMMON
    broken_features = (
        # This renders to some odd color
        ANSI_TEXT_BLINK_SLOW,
        # This renders to an _overline_
        ANSI_TEXT_BLINK_FAST,
    )
    supported_features = (
        ANSI_COLOR_BG_INDEXED_16,
        ANSI_COLOR_BG_INDEXED_256,
        ANSI_COLOR_BG_INDEXED_8,
        ANSI_COLOR_FG_INDEXED_16,
        ANSI_COLOR_FG_INDEXED_256,
        ANSI_COLOR_FG_INDEXED_8,
        ANSI_COLOR_REVERSE,
        ANSI_FONT_BOLD,
        ANSI_TEXT_UNDERLINE,
    )


_all_terminal_profiles = (
    # Remote connections
    UnknownRemoteSshProfile,
    # Terminal multiplexers
    ScreenProfile,
    TmuxProfile,
    # Windows
    CmdExeProfile,
    # Mac OS X
    TerminalAppProfile,
    iTermProfile,
    # Mainstream Terminals
    GnomeTerminalProfile,
    GnomeTerminalServerProfile,
    KonsoleProfile,
    LinuxConsoleProfile,
    # Linux (other niche emulators)
    ATermProfile,
    ETermProfile,
    PTermProfile,
    RXVTProfile,
    TerminatorProfile,
    TerminologyProfile,
    XTermProfile,
)


processinfo = collections.namedtuple("processinfo", "pid ppid comm")


TerminalBase = collections.namedtuple(
    "TerminalBase", "slug name version preset features")


class Terminal(NamedSlug, TerminalBase):

    """
    A terminal (emulator).

    Terminal object exposes the following information about the terminal
    emulator program that a guacamole-based application is running on.

    The terminal is described by these attributes:

    :ivar slug:
        Unique identifier of the terminal emulator program. Those identifiers
        are assigned by guacamole developers. They are not related to any
        upstream identification systems.

    :ivar name:
        Name of the terminal emulator program. This is always a human-readable,
        translated version of the name.

    :ivar version:
        Version of the terminal emulator program. This property is rarely
        available. This is sometimes None (some terminals don't provide this
        information).

    :ivar preset:
        Terminal feature preset that this terminal is mostly compatible with.
        This is always one of :attr:`PRESET_PRIMITIVE`, :attr:`PRESET_COMMON`
        or :attr:`PRESET_MODERN`.

    :ivar features:
        A mapping from features (:class:`TerminalFeature`) to support status
        (:class:`TerminalFeatureStatus`). For simplicity it can be indexed with
        regular strings, by the identifier of each feature, e.g.
        ``"ansi-font-bold"``. The support status is always one of values:
        :attr:`STATUS_UNSUPPORTED`, :attr:`STATUS_BROKEN`,
        :attr:`STATUS_CONFIGURABLE`, :attr:`STATUS_SUPPORTED` or
        :attr:`STATUS_UNKNOWN`. Again for simplicity those also compare to
        strings such as ``"unsupported"``
    """

    @property
    def unsupported_features(self):
        """List of supported features."""
        return sorted([feature for feature, status in self.features.items()
                       if status is STATUS_UNSUPPORTED])

    @property
    def broken_features(self):
        """List of supported features."""
        return sorted([feature for feature, status in self.features.items()
                       if status is STATUS_BROKEN])

    @property
    def configurable_features(self):
        """List of supported features."""
        return sorted([feature for feature, status in self.features.items()
                       if status is STATUS_CONFIGURABLE])

    @property
    def supported_features(self):
        """List of supported features."""
        return sorted([feature for feature, status in self.features.items()
                       if status is STATUS_SUPPORTED])

    @property
    def unknown_features(self):
        """List of features of unknown status."""
        return sorted([feature for feature, status in self.features.items()
                       if status is STATUS_UNKNOWN])


class TerminalAwareness(Ingredient):

    """
    Ingredient for detecting features of the terminal emulator.

    This ingredient is responsible for detecting the terminal used by the
    application using guacamole and exposing relevant information about the
    terminal through the context.

    This ingredient also collaborates behind the scenes with the color
    controller ingredient to ensure that colors just work, if possible, and
    that colors are gracefully degrading on less capable emulators.

    Applications can access the terminal object explicitly. This can be useful
    for applications that simply depend on certain feature for proper
    functionality. Please familiarize yourself with the :class:`Terminal`
    object and various features and status objects linked from therein.

    One simple way of treating terminals is to look at the
    :attr:`Terminal.preset` attribute. It provides a simple generalization of
    what kind of terminal is being used at the moment.

    If the terminal preset is :attr:`PRESET_PRIMITIVE` then you can do very
    little with the terminal. Here various rendering hints should be
    non-essential as they will often not work at all.

    If the terminal preset is :attr:`PRESET_COMMON`, which is true for most
    actually commonly used terminal emulators, except Windows, then you can use
    many features without issues. Here visual hints can play an important role
    in your application.

    Lastly if the terminal preset is :attr:`PRESET_MODERN` then you have extra
    visual fidelity available at your disposal. Please note that applications
    that depend on such features will run almost exclusively on modern Linux
    distributions and when using a mainstream Linux terminal emulator. In other
    words Windows, OS X and some older Linux distributions are not supported.

    Lastly, remember that Guacamole tries to help you. The color controller
    will successfully hide many issues related to the handling of colors across
    environments. If that is your only need then you can never touch the
    terminal object. Everything will be done automatically behind the scenes.
    """

    def added(self, context):
        """
        Ingredient method called before anything else.

        This method implements terminal emulator fingerprinting. The resulting
        terminal object is published as ``context.terminal``.
        """
        context.terminal = self._probe_terminal()

    def _probe_terminal(self):
        features = {feature: STATUS_UNSUPPORTED for feature in _all_features}
        if sys.platform.startswith('linux'):
            proc_info_list = list(self._get_linux_process_tree(os.getpid()))
        else:
            proc_info_list = []
        for profile in _all_terminal_profiles:
            if profile.is_running(proc_info_list):
                slug = profile.slug
                name = profile.name
                version = profile.get_version()
                preset = profile.preset
                for feature_id in profile.get_supported_features(version):
                    features[feature_id] = STATUS_SUPPORTED
                for feature_id in profile.get_broken_features(version):
                    features[feature_id] = STATUS_BROKEN
                for feature_id in profile.get_configurable_features(version):
                    features[feature_id] = STATUS_CONFIGURABLE
                for feature_id in profile.get_unsupported_features(version):
                    features[feature_id] = STATUS_UNSUPPORTED
                for feature_id in profile.get_unknown_features(version):
                    features[feature_id] = STATUS_UNKNOWN
                break
        else:
            name = _("Unknown")
            slug = "unknown"
            preset = PRESET_PRIMITIVE
        return Terminal(slug, name, version, preset, features)

    def _get_linux_process_tree(self, pid):
        while True:
            try:
                with open('/proc/{}/stat'.format(pid), 'rt') as stream:
                    fields = stream.readline().strip().split()
            except (IOError, OSError):
                break
            comm = fields[1]
            ppid = int(fields[3])
            if ppid:
                yield processinfo(pid, ppid, comm)
                pid = ppid
            else:
                break
