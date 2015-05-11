.. _commands:

===================
Using Stock Recipes
===================

The Command Recipe
==================

The command recipe contains the distilled, correct behavior for command line
applications. The main face of the command recipe is the
:class:`~guacamole.recipes.cmd.Command` class.

.. note::

    Guacamole values conventions. Instead of overriding many of the methods
    that comprise the Command class, you can just define a variable that will
    take priority. This leads to shorter and more readable code.

Defining commands
-----------------

Let's build a simple hello-world example again:

.. testsetup::

    import guacamole

.. doctest::

    >>> class HelloWorld(guacamole.Command):
    ...     def invoked(self, ctx):
    ...         print("Hello World!")


The central entry point of each command is the
:meth:`~guacamole.recipes.cmd.Command.invoked()` method. The method is called
once the command is ready to be dispatched. This is what you would put inside
your ``main()`` function, after the boiler-plate code that Guacamole handles
for you. What you do here is up to you.

For now, let's just run our simple example with the convenience method
:meth:`~guacamole.recipes.cmd.Command.main()`. Note that here we're passing
extra arguments to control how the tool executes, normally you would just call
main without any arguments and it will do the right thing.

.. doctest::

    >>> HelloWorld().main([], exit=False)
    Hello World!
    0
    
For now let's ignore the argument `ctx`. It is extremely handy, as we will see
shortly, but we don't need it yet.

.. note::

    This little example is available in the ``examples/`` directory in the
    source distribution. The version of Guacaomle packaged in Debian has them
    in the directory ``/usr/share/doc/python-guacamole-doc/examples``.  As the
    directory name implies, you have to install the ``python-guacamole-doc``
    package to get them.
    
    Do use the example and play around with it, see how it behaves if you run
    it with various arguments. The idea is that Guacamole is supposed to create
    *good* command line applications. Good applications do the right stuff
    internally. The ``hello-world`` example is trivial but we'll see more of
    what is going on internally soon.

Working with arguments & The Context
------------------------------------

Commands typically take arguments. To say which arguments are understood by our
command we need to implement the second method
:meth:`~guacamole.recipes.cmd.Command.register_arguments()`. This method is
called with the familiar :py:class:`argparse.ArgumentParser` instance. You've
seen this code over and over, here you should just focus on configuring the
arguments and options. Guacamole handles the parser for you.

.. doctest::

    >>> class HelloWorld(guacamole.Command):
    ...     def register_arguments(self, parser):
    ...         parser.add_argument('name')
    ...     def invoked(self, ctx):
    ...         print("Hello {0}!".format(ctx.args.name))

As you can see, the context is how you reach the command line arguments parsed
by `argparse`. What else is there you might ask? The answer is *everything*.

The context is how *ingredients* can expose useful capabilities to commands.
The command recipe is comprised of several ingredients, as you will later see.
One of those ingredients parsers command line arguments and adds the results to
the context as the ``args`` object.

.. note::

    When reading documentation about particular ingredients make sure to see
    how they interact with the context. Each ingredient documents that clearly.

Let's run our improved command and see what happens:

.. doctest::

    >>> HelloWorld().main(["Guacamole"], exit=False)
    Hello Guacamole!
    0

No surprises there. We can see that the command printed the hello message and
then returned the exit code ``0``. The exit code is normally passed to the
system so that your application can be scripted.

.. note::
    Guacamole will return ``0`` for you if you don't return anything. If you do
    return a value we'll just preserve it for you.  You can also raise
    SystemExit with any value and we'll do the right thing yet again.

This should be all quite familiar to everyone so we won't spend more time on
arguments now. You can read the :py:ref:`argparse-tutorial` if you want.

A small digression, why argparse?
---------------------------------

By default, all command line parsing is handled by :py:mod:`argparse`.
    
Guacamole doesn't force you to use argparse (nothing really is wired to depend
on it in the core) but the stock set of ingredients do use it.  Argparse is
familiar to many developers and by having it by default you can quickly convert
your application code over to guacamole without learning two new things at a
time.

Nesting Commands
----------------

Many common tools expose everything from a top-level command, e.g. ``git
commit``.  Here, ``git`` gets invoked, looks at the command line arguments and
delegates the dispatching to the ``git-commit`` command.

All Guacamole commands can be nested. Let's build a quick git-like command to
see how to do that.

.. doctest::

    >>> class git_commit(guacamole.Command):
    ...     name = 'commit'
    ...     def invoked(self, ctx):
    ...         print("commit invoked")

    >>> class git_log(guacamole.Command):
    ...     def invoked(self, ctx):
    ...         print("log invoked")

    >>> class git(guacamole.Command):
    ...     name = 'git'
    ...     sub_commands = (
    ...         (None, git_commit),
    ...         ('log', git_log),
    ...     )

As you see it's all based on declarations. Each command now cares about the
name it is using. Names can be assigned in the ``sub_commands`` list or
individually in each class, by defining the ``name`` attribute.

The name listed in sub_commands takes precedence over the name defined in the
class. Here, the ``git_log`` command doesn't define a ``name`` so we provide
one explicitly as the first element of the pair, as sequence of which is stored
in ``sub_commands``.

.. note::
    Behind the scenes Guacamole actually calls a number of methods for
    everything. See :meth:`~guacamole.recipes.cmd.Command.get_sub_commands()`
    and :meth:`~guacamole.recipes.cmd.Command.get_cmd_name()` for the two used
    here. There are *many* more methods though.

Let's invoke our fake git to see how that works now:

.. doctest::

    >>> git().main(["commit"], exit=False)
    commit invoked
    0

    >>> git().main(["log"], exit=False)
    log invoked
    0

So far everything behaves as expected. Let's see what happens if we run
something that we've not coded:

.. doctest::

    >>> git().main(["status"], exit=False)
    2

This won't fit the *doctest* above (it's printed on stderr) but in reality the
application will also say something like this::
    
    usage: git [-h] {commit,log} ...
    setup.py: error: invalid choice: 'status' (choose from 'commit', 'log')

.. note::

    Technically the :class:`~guacamole.recipes.cmd.Command` class has numerous
    methods. Most of those methods are of no interest to most of the
    developers. Feel free to read the API reference later if you are
    interested.
