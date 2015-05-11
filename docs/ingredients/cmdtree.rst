==================
CommandTreeBuilder
==================

Summary
=======

Ingredient for arranging all the :class:`~guacamole.recipes.cmd.Command`
classes into a tree of objects.

Description
===========

The command tree builder ingredient is a part of the command recipe. It is
responsible for instantiating all sub-commands and arranging them into a tree
for other ingredients to work with (most notably the argument parser
ingredient).

The secondary task is to add the *spices* requested by the top-level command to
the bowl.  This lets other ingredients act differently and effectively allows
the top-level command to influence the runtime behavior of the whole recipe.

Spices
======

This ingredient is not influenced by any *spices*.

Context
=======

This ingredient adds two objects to the context:

``cmd_tree``
    A tree of tuples that describes all of the commands and their sub commands.
``cmd_toplevel``
    The top-level command object.

In addition, this ingredient inspects the *spieces* required by the top-level
command and adds them to the bowl.

.. todo::
    Add a reference to an article about spices here.

Command Line Arguments
======================

This ingredient is not exposing any command line arguments.

Examples
========

Let's create two examples below. One for a simple command and another for a
hierarchical command. This example will not use the full command recipe, to
focus on the side effects of just the command tree builder ingredient.

Flat Command
------------

We'll need a command object:

.. doctest::

    >>> from guacamole.recipes.cmd import Command
    >>> class HelloWorld(Command):
    ...     pass

Note that the tree builder is called with an *instance* of the command, not the
class. This allows the top-level command to have a custom initializer, which
might be helpful.

.. doctest::

    >>> from guacamole.core import Context
    >>> from guacamole.ingredients import cmdtree 
    >>> ctx = Context()
    >>> cmdtree.CommandTreeBuilder(HelloWorld()).added(ctx)

The context now has the ``cmd_toplevel`` object which is just the instance of
the command we've used.

.. doctest::

    >>> ctx.cmd_toplevel
    <HelloWorld>

Similarly, we'll have a tree of all the commands and their names in ``cmd_tree``:

.. doctest::

    >>> ctx.cmd_tree
    cmd_tree_node(cmd_name=None, cmd_obj=<HelloWorld>, children=())

The first element of the tuple is the effective command name. This can be used
to rename a sub-command. Note that typically the ``command.name`` attribute is
used (see :meth:`~guacamole.recipes.cmd.Command.get_cmd_name()`). The second
element is the instance and the last element is a tuple of identical
``cmd_tree_node`` tuples, one for each of the sub-commands. We'll see how that
looks like in the next example.

Nested Commands
---------------

We'll need a few commands for this example. Let's replicate the ``git``, ``git
commit``, ``git stash``, ``git stash pop`` and ``git stash list`` commands.

.. doctest::

    >>> from guacamole.recipes.cmd import Command
    >>> class StashList(Command):
    ...     pass
    >>> class StashPop(Command):
    ...     pass
    >>> class Stash(Command):
    ...     sub_commands = (('list', StashList), ('pop', StashPop))
    >>> class Commit(Command):
    ...     pass
    >>> class Git(Command):
    ...     sub_commands = (('commit', Commit), ('stash', Stash))

Now, let's feed the ``Git`` class to the context.

.. doctest::

    >>> from guacamole.core import Context
    >>> from guacamole.ingredients import cmdtree 
    >>> ctx = Context()
    >>> cmdtree.CommandTreeBuilder(Git()).added(ctx)

The ``cmd_toplevel`` is as before (the ``Git`` *instance*). Let's look at the
more interesting command tree.

.. doctest::
    :options: +NORMALIZE_WHITESPACE

    >>> ctx.cmd_tree
    cmd_tree_node(cmd_name=None, cmd_obj=<Git>,
        children=(cmd_tree_node(cmd_name='commit', cmd_obj=<Commit>,
        children=()), cmd_tree_node(cmd_name='stash',
        cmd_obj=<Stash>, children=(cmd_tree_node(cmd_name='list',
        cmd_obj=<StashList>, children=()), cmd_tree_node(cmd_name='pop',
        cmd_obj=<StashPop>, children=())))))

Blah, that's mouthful. Let's see particular fragments to understand it better.

.. doctest::

    >>> ctx.cmd_tree.children[0].cmd_name
    'commit'
    >>> ctx.cmd_tree.children[1].cmd_name
    'stash'
    >>> ctx.cmd_tree.children[1].children[0].cmd_name
    'list'
    >>> ctx.cmd_tree.children[1].children[1].cmd_name
    'pop'

Most of the time you won't have to use this data. Typically, it is consumed by
the argument parser ingredient. Still, if you need it, here it is.

=====================
CommandTreeDispatcher
=====================

Summary
=======

Ingredient for executing the :meth:`~guacamole.recipes.cmd.Command.invoked()`
methods of all the commands that were selected by the user on command line.

Description
===========

This ingredient is responsible for invoking commands. It works during the
dispatch phase of the application life-cycle. Since earlier stages can be
interrupted it is not aways reached. E.g. when the application is invoked with
the ``--help`` argument.

The way this ingredient works is simple. It assumes that the argument parser
creates a specific structure of references to command objects. The structure is
stored in the ``argparse`` name-space object (which is available in
``ctx.args`` after the parsing phase. The structure is a sequence of attributes
``ctx.args.command0``, ``ctx.args.command1``, ``ctx.args.command2``, etc. The
first one, ``ctx.args.command0`` is always present. Subsequent attributes are
present if sub-commands are specified on the command line. For example, keeping
our git sample in mind, the following command::

    $ git stash

Will result in ``ctx.args.command0`` instance of the `Git` command and
``ctx.args.command1`` an instance of the `GitStash` command. The dispatcher
ingredient will invoke the ``command0``, look at the return value and then
(most likely) proceed to ``command1`` (N+1 in general).

The way return value is interpreted is interesting. In general, there are three cases:

- None is interpreted as "nothing special happened". In the example above. The
  ``git stash`` will first call ``Git.invoked()``, see the (default) None and
  will proceed to call ``GitStash.invoked()``.
- A generator is interpreted as a context-manager like. This allows, for
  example, the ``git`` command to use a context manager in its ``invoked()``
  method to provide some managed resource to each sub-command. Note that the
  `invoked` method must behave as it if was decorated with
  ``@functools.contextmanager`` but it must not be actually decorated like
  that.
- Any other return value is interpreted as an error code and stops recursive
  command dispatch. It will be finally returned from the ``main()`` method or
  raised as a ``SystemExit`` exception.

Spices
======

This ingredient is not influenced by any *spices*.

Context
=======

This ingredient does not change the context. It does depend on the ``args``
object that is published by the argument parser ingredient.

Command Line Arguments
======================

This ingredient is not exposing any command line arguments.

Examples
========

Let's see how command invocation works in the few specific examples below.

Single Command
--------------

Let's start with a hello-world command first:

.. doctest::

    >>> from guacamole.recipes.cmd import Command
    >>> class HelloWorld(Command):
    ...     def invoked(self, ctx):
    ...         print("Hello World")

Let's create the necessary infrastructure for using the dispatcher:

.. doctest::

    >>> import argparse
    >>> from guacamole.core import Context
    >>> from guacamole.ingredients import cmdtree 
    >>> ctx = Context()
    >>> ctx.args = argparse.Namespace()

Now let's run the `HelloWorld` command:

.. doctest::

    >>> ctx.args.command0 = HelloWorld()
    >>> cmdtree.CommandTreeDispatcher().dispatch(ctx)
    Hello World

Success! The print worked and we also got the exit code (None, which is not
printed by the repl).

Next, let's implement the classic UNIX ``false(1)`` command:

.. doctest::

    >>> class false(Command):
    ...     def invoked(self, ctx):
    ...         return 1

Now, let's invoke it:

.. doctest::

    >>> ctx.args.command0 = false()
    >>> cmdtree.CommandTreeDispatcher().dispatch(ctx)
    1

One. Also good.

All command line tools return an exit code. If you actually run this command in
the shell you can inspect the return code in several ways (depending on what is
your shell). On Windows that is::

    echo %ERRORLEVEL%

And on all other systems, that are mostly using Bash by default::

    echo $?

In both cases, you should see ``1`` being printed by those echo statements.

Nested Commands
---------------

Let's expand the Git example to examine the context-manager-like behavior.

.. doctest::

    >>> class GitLibrary(object):
    ...     def __enter__(self):
    ...         print("Git initialized")
    ...         return self
    ...     def __exit__(self, *args):
    ...         print("Git finalized")
    ...     def commit(self):
    ...         print("Using git to commit")

    >>> class Commit(Command):
    ...     def invoked(self, ctx):
    ...         with GitLibrary() as git:
    ...             git.commit()

    >>> class Git(Command):
    ...     sub_commands = (('commit', Commit),)

Now, let's see what dispatch does here:

.. doctest::

    >>> ctx.args.command0 = Git()
    >>> ctx.args.command1 = Commit()
    >>> cmdtree.CommandTreeDispatcher().dispatch(ctx)
    Git initialized
    Using git to commit
    Git finalized

If you have many commands that need to use some shared resource, you may be
tempted to move the initialization to a shared code path. Guacamole allows you
to do this by calling **all** the ``invoked()`` methods of all of the commands
specified on command line.

Let's modify the example to show this. The git library code will say as-is. The
commit and git commands will be changed, to move the initialization code
around.

.. doctest::

    >>> class Commit(Command):
    ...     def invoked(self, ctx):
    ...         ctx.git.commit()

    >>> class Git(Command):
    ...     sub_commands = (('commit', Commit),)
    ...     def invoked(self, ctx):
    ...         with GitLibrary() as git:
    ...             ctx.git = git
    ...             yield

Now, let's see what dispatch does now:

.. doctest::

    >>> ctx.args.command0 = Git()
    >>> ctx.args.command1 = Commit()
    >>> cmdtree.CommandTreeDispatcher().dispatch(ctx)
    Git initialized
    Using git to commit
    Git finalized

No change, that's running exactly as before but now we can add more commands
without duplicating the relevant code over and over.

.. note::

    Here, the finalization will happen even if something bad happens (e.g.
    ``Commit`` raising an exception). It's not useful often but it can be a way
    to use the context manager protocol with commands.
