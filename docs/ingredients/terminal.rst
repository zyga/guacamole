.. _terminal_awareness:

.. currentmodule:: guacamole.ingredients.terminal

=================
TerminalAwareness
=================

Summary
=======

Ingredient for detecting features of the terminal emulator.

Description
===========

This ingredient is responsible for detecting the terminal used by the
application using guacamole and exposing relevant information about the
terminal through the context.

This ingredient also collaborates behind the scenes with the color controller
ingredient to ensure that colors just work, if possible, and that colors are
gracefully degrading on less capable emulators.

Applications can access the terminal object explicitly. This can be useful for
applications that simply depend on certain feature for proper functionality.
Please familiarize yourself with the :class:`Terminal` object and various
features and status objects linked from therein.

One simple way of treating terminals is to look at the
:attr:`Terminal.preset` attribute. It provides a simple generalization
of what kind of terminal is being used at the moment.

If the terminal preset is :attr:`PRESET_PRIMITIVE` then you can do very
little with the terminal. Here various rendering hints should be
non-essential as they will often not work at all.

If the terminal preset is :attr:`PRESET_COMMON`, which is true for most
actually commonly used terminal emulators, except Windows, then you can
use many features without issues. Here visual hints can play an important
role in your application.

Lastly if the terminal preset is :attr:`PRESET_MODERN` then you have extra
visual fidelity available at your disposal. Please note that applications
that depend on such features will run almost exclusively on modern Linux
distributions and when using a mainstream Linux terminal emulator. In other
words Windows, OS X and some older Linux distributions are not supported.

Lastly, remember that Guacamole tries to help you. The color controller
will successfully hide many issues related to the handling of colors across
environments. If that is your only need then you can never touch the
terminal object. Everything will be done automatically behind the scenes.

Spices
======

This ingredient is not influenced by any *spices*.

Context
=======

This ingredient adds one object to the context:

``terminal``
    An instance of :class:`~guacamole.ingredients.terminal.Terminal`. The
    object exposes all of the information about the currently used terminal.

Command Line Arguments
======================

This ingredient is not exposing any command line arguments.

Examples
========

This ingredient does not have any in-line examples but please refer to the
``examples/terminal.py`` file for a thorough exercise of all available
features.

Reference
=========

Please refer to the documentation of the :mod:`guacamole.ingredients.terminal`
for many additional details.
