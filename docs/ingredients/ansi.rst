====
ANSI
====

Summary
=======

Ingredient for working with ANSI Control Codes

Description
===========

The ANSI ingredient exposes ANSI control codes in a simple way. ANSI codes can
be used to control text color and style on compatible terminals.

Linux terminal emulators commonly support a wide subset of control codes.
Particular support differs between the classic Linux console, *Xterm*,
*gnome-terminal* and *konsole* (and the backing libraries). Some features are
supported more widely than others. In particular, the text console is rather
limited and will likely remain so until the systemd-based replacement is
commonly used.

The terminal emulator included in Apple's OS X supports a subset of the
features (3rd party terminal emulators for OS X were not tested, contributions
are welcome). In general you can treat OS X like a poor version of Linux.

The windows command prompt is the most limited environment as it only support
several foreground and background colors and nothing else at all. It also has
issues with Unicode (as in, it doesn't support it at all). On Windows, usage of
ANSI depends on the availability of ``colorama``. Colorama is a third party
library that wraps ``sys.stdout`` and ``sys.stderr``, parses ANSI control codes
and converts them to the corresponding Windows API calls.

Spices
======

This ingredient is not influenced by any *spices*.

Context
=======

This ingredient adds two objects to the context:

``ansi``
    An instance of :class:`~guacamole.ingredients.ansi.ANSIFormatter`. The
    object is automatically configured (disabled) when the extra control codes
    are undesired (stdout not attached to a terminal emulator).
``aprint``
    The :meth:`~guacamole.ingredients.ansi.ANSIFormatter.aprint` method, as a
    shorthand for ``ctx.ansi.aprint``.

Command Line Arguments
======================

This ingredient is not exposing any command line arguments.

Examples
========

Let's construct a simple example. Note that typically you will use the context
that is provided to you from the
:meth:`~guacamole.recipes.cmd.Command.invoked()` method of a command.

.. doctest::

    >>> from guacamole.core import Context
    >>> from guacamole.ingredients import ansi
    >>> ctx = Context()
    >>> ansi.ANSIIngredient(enable=True).added(ctx)

The context now has the ``ansi`` object, which is an instance of
:class:`~guacamole.ingredients.ansi.ANSIFormatter`.

It has some methods and properties that we'll see below but it is also
callable and darn convenient to use.

You can use the ``fg`` and ``bg`` keyword arguments to control the
*foreground* and *background* text color respectively.

.. doctest::

    >>> ctx.ansi('red on blue', fg='red', bg='blue')
    '\x1b[31;44mred on blue\x1b[0m'

You can use keyword arguments that correspond to *each* of the countless
``sgr_`` constants available in the class
:class:`~guacamole.ingredients.ansi.ANSI`. Here, let's get bold text
using the :attr:`~guacamole.ingredients.ansi.ANSI.sgr_bold` code.

.. doctest::

    >>> ctx.ansi('bold text', bold=1)
    '\x1b[1mbold text\x1b[0m'

In some cases you may want to use different code knowing that the output will
be colorized (e.g. use color codes instead of longer text labels).  You can
achieve that by testing :meth`~guacamole.ingredients.ansi.ANSI.is_enabled`.

.. doctest::

    >>> # Let's disable the ANSI support for this test
    >>> ansi.ANSIIngredient(enable=False).added(ctx)
    >>> if ctx.ansi.is_enabled:
    ...     ctx.aprint('!!!', fg='red')
    ... else:
    ...     ctx.aprint('ALARM')
    ALARM

Expressing colors
=================

Guacaomle supports several styles of colors:

- Named colors represented as strings:

  * ``"black"``
  * ``"red"``
  * ``"green"``
  * ``"yellow"``
  * ``"blue"``
  * ``"magenta"``
  * ``"cyan"``
  * ``"white"``

- Bright variant of named colors (not repeated)
- Indexed colors represented as an integer in range(256):

  * 0x00-0x07: standard colors (as in ``ESC [ 30–37 m``)
  * 0x08-0x0F: high intensity colors (as in ``ESC [ 90–97 m``)
  * 0x10-0xE7: 6 × 6 × 6 = 216 colors:
    16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
  * 0xE8-0xFF: grayscale from black to white in 24 steps
- RGB colors represented as (r, g, b) where each component is an integer in
  range(256)
- The special value ``"auto"`` which picks the complementary (readable)
  variant. Auto may be used in one of ``fg=`` or ``bg=`` if ``bg=`` or ``fg=``
  (respectively) are using a concrete color.

.. note::
    The actual colors behind the string-named colors vary between different
    terminal emulators. Sometimes the color is just slightly different.
    Sometimes it is just totally unrelated to the one specified in the ANSI
    standard.

.. warning::
    RGB colors are not supported on Windows and OS X. They are only supported
    on modern terminal emulators, typically on Linux distributions.
