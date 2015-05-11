===================
VerboseCrashHandler
===================

Summary
=======

Ingredient for handling crashing commands.

Description
===========

This ingredient mimics the default behavior of python for an uncaught
exception. That is, to print the exception details, the function backtrace and
to exit the process.

Spices
======

This ingredient is not influenced by any *spices*.

Context
=======

This ingredient does not add any objects to the context. This ingredient does
use the context though, to access the crash meta-data. This includes:

``exc_type``
    The class of the exception that caused the application to crash.
``exc_value``
    The exception object itself.
``traceback``
    The traceback object.

.. note::

    The three attributes are automatically added by the
    :class:`~guacamole.core.Bowl` when something bad happens.

Command Line Arguments
======================

This ingredient is not exposing any command line arguments.
