============================================================
Guacamole - Framework for Creating Command Line Applications
============================================================

.. image:: https://badge.fury.io/py/guacamole.png
    :target: http://badge.fury.io/py/guacamole

.. image:: https://travis-ci.org/zyga/guacamole.png?branch=master
        :target: https://travis-ci.org/zyga/guacamole

.. image:: https://pypip.in/d/guacamole/badge.png
        :target: https://pypi.python.org/pypi/guacamole

Tools, done right
=================

Guacamole is a LGPLv3 licensed toolkit for creating good command line
applications. Guacamole that does the right things for you and makes writing
applications easier.

.. testsetup::

    import guacamole 

.. doctest::

    >>> class HelloWorld(guacamole.Command):
    ...     """A simple hello-world application."""
    ...     def register_arguments(self, parser):
    ...         parser.add_argument('name')
    ...     def invoked(self, ctx):
    ...         print("Hello {0}!".format(ctx.args.name))

Running it directly is as simple as calling ``main()``:

.. doctest::

    >>> HelloWorld().main(['Guacamole'], exit=False)
    Hello Guacamole!
    0

What you didn't have to do is what matters:

 - configure the argument parser
 - define and setup application logging
 - initialize internationalization features
 - add debugging facilities
 - write a custom crash handler

Features
========

* Free software: LGPLv3 license
* Documentation: https://guacamole.readthedocs.org.
* Create command classes and run them from command line.
* Group commands to create complex tools.
* Use recipes, ingredients and spices to customize behavior
