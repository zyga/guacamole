====================
Philosophy Statement
====================

The power of Guacamole is based on the simplicity of conventions and sane
defaults. Let's talk about some of the conventions that are followed here.

.. note::

    You will see how the philosophy turns into practice in the command
    turtorial section.

Defaults Matter
===============

Important things make nice applications and tools behave better than random,
ad-hoc scripts that have no consistency and happily crash on anything
unexpected. Guacamole strives to enable important things that make using
applications pleasant.

By default Guacamole will:

 - Expose detailed help and usage messages.
 - Use translated messages for everything it does.
 - Handle logging for you so that it is useful.
 - Handle crashes for you so that users can send feedback.
 - Use the right directories in your filesystem.
 - Use color-coded information, if supported, for readability.
 - Teach you, the developer, if you make a mistake that it can detect.

Some defaults say to turn a feature off. Guacamole uses *spices* to let
developers opt-into those features that they wish to use. You will learn about
spices later in this document. For now just remember that they are equivalent
to feature flags.

Documentation Is Important
==========================

Documentation is the most important thing you can get wrong easily. You can
create perfect tools that do some operation correctly and efficiently but it
will all go to waste if nobody can use your product.

Guacamole encourages developers to write useful documentation. The most basic
form of documentation is the *docstring*. The docstring is powerful. You see it
while writing your code. Other people can see it by various means, using tools
like ``pydoc`` or by reading a document generated with a tool like sphinx.

Guacamole has rich support for documentation. By default, a lot of information
is extracted from your command docstrings. You can reuse all of that, for free,
to create proper manual pages. Quality tools come with documentation and
command line tools use manual pages as the most common, most discoverable means
of learning about a particular program.

Internationalization is Important
=================================

Internationalization is important to many users. While many developers and
system administrators are comfortable with reading English it is strongly
recommended to support localization. Modern software gets this right.

Guacamole supports internationalization by default. Commands can advertise
their gettext domain using the ``gettext_domain`` attribute (see
:meth:`~guacamole.recipes.cmd.Command.get_gettext_domain()` for details).
Guacamole will carefully work with your docstrings to feed them to gettext and
extract the useful bits out.

Commands can mix-and-match different gettext domains without issues. If you are
writing a non-trivial application which is composed of commands coming from
various sources they will all work correctly together.

Convention over Configuration
=============================

Guacamole has a lot of APIs. Most of the time you won't have to work with them.
Guacamole will reuse information that you can provide without defining methods.

This is how the docstrings are used for documentation. This is how you can
define numerous attributes to describe specific features of your commands.
Instead of working with the methods you can just define an item. This has the
advantage that Guacamole can look at your command class and can educate you if
you make a mistake. This is easier to work with than reading through
back-traces or working with type annotations that may or may not be enough to
capture something you want to express.
