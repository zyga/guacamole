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
The essence of guacamole.

This module defines the three essential core classes: :class:`Ingredient`,
:class:`Bowl`, :class:`Context`. All of those have stable APIs.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys

__all__ = (
    'Bowl',
    'Context',
    'Ingredient',
)


_logger = logging.getLogger('guacamole')


class Ingredient(object):

    """
    Part of guacamole.

    Ingredients are a mechanism for inserting functionality into Guacamole.
    The sequence of calls to ingredient methods is as follows:

    - :meth:`added()`

    The added method is where an ingredient can advertise itself to other
    ingredients that it explicitly collaborates with.

    - :meth:`preparse()`

    The preparse method is where ingredients can have a peek at the command
    line arguments. This can serve to optimize further actions. Essentially
    guacamole allows applications to parse arguments twice and limit the
    actions needed to do that correctly to the essential minimum required.

    - :meth:`early_init()`

    The early initialization method can be used to do additional
    initialization. It can take advantage of the fact that the whole command
    line arguments are now known and may have been analyzed further by the
    preparse method.

    - :meth:`parse()`

    The parse method is where applications are expected to fully understand
    command line arguments. This method can abort subsequent execution if
    arguments are wrong in in some way. After parsing command line arguments
    the application should be ready for execution.

    - :meth:`late_init()`

    The late initialization method mimics the early initialization method but
    is called after parsing all of the command line arguments. Again, it can be
    used to prepare addiotional resources necessary for a given application.

    - :meth:`dispatch()`

    The dispatch method is where applications execute the bulk of their
    actions.  Dispatching is typically done with one of the standard
    ingredients which will locate the appropriate method to call into the
    application.

    Depending on the outcome of the dispatch (if an exception is raised or not)
    one of :meth:`dispatch_succeeded()`` or :meth:`dispatch_failed()` is
    called.

    - :meth:`shutdown()`

    This is the last method called on all ingredients.

    Each of those methods is called with a context argument
    (:class:`Context:`).  A context is a free-for-all environment where
    ingredients can pass data around. There is no name-spacing. Ingredients
    should advertise what they do with the context and what to expect.
    """

    def __str__(self):
        """
        Get the string representation of this ingredient.

        The string method just returns the class name. Since the ingredient is
        an implemenetation detail it does not have anything that applications
        should show to the user.
        """
        return self.__class__.__name__

    def added(self, context):
        """Ingredient method called before anything else."""

    def build_early_parser(self, context):
        """Ingredient method called to build the early parser."""

    def preparse(self, context):
        """Ingredient method called to pre-parse command line aruments."""

    def early_init(self, context):
        """Ingredient method for early initialization."""

    def build_parser(self, context):
        """Ingredient method called to build the full parser."""

    def parse(self, context):
        """Ingredient method called to parse command line arguments."""

    def late_init(self, context):
        """Ingredient method for late initialization."""

    def dispatch(self, context):
        """
        Ingredient method for dispatching (execution).

        .. note::
            The first ingredient that implements this method and returns
            something other than None will stop command dispatch!
        """

    def dispatch_succeeded(self, context):
        """Ingredient method called when dispatching is correct."""

    def dispatch_failed(self, context):
        """Ingredient method called when dispatching fails."""

    def shutdown(self, context):
        """Ingredient method called after all other methods."""


class Context(object):

    """
    Context for making guacamole with ingredients.

    A context object is created and maintained throughout the life-cycle of an
    executing tool. A context is passed as argument to all ingredient methods.

    Since context has no fixed API anything can be stored and loaded.
    Particular ingredients document how they use the context object.
    """

    def __repr__(self):
        """
        Get a debugging string representation of the context.

        The debugging representation shows all of the *names* of objects added
        to the context by various ingredients. Since the actual object can have
        large and complex debugging representation containing that
        representation was considered as a step against understanding what is
        in the context.
        """
        return "<Context {{{}}}>".format(
            ', '.join(sorted(self.__dict__.keys())))


class Bowl(object):

    """
    A vessel for preparing guacamole out of ingredients.

    .. note::
        Each Bowl is single-use. If you eat it you need to get another one as
        this one is dirty and cannot be reused.
    """

    def __init__(self, ingredients):
        """Prepare a guacamole out of given ingredients."""
        self.ingredients = ingredients
        self.context = Context()
        self.context.bowl = self
        self.context.spices = set()

    def add_spice(self, spice):
        """
        Add a single spice the bowl.
        """
        self.context.spices.add(spice)

    def has_spice(self, spice):
        """
        Check if a given spice is being used.

        This method can be used to construct checks if an optional ingredient
        feature should be enabled or not. Spices are simply strings that
        describe optional features.
        """
        return spice in self.context.spices

    def eat(self, argv=None):
        """
        Eat the guacamole.

        :param argv:
            Command line arguments or None. None means that sys.argv is used
        :return:
            Whatever is returned by the first ingredient that agrees to perform
            the command dispatch.

        The eat method is called to run the application, as if it was invoked
        from command line directly.
        """
        # The setup phase, here KeyboardInterrupt is a silent sign to exit the
        # application. Any error that happens here will result in a raw
        # backtrace being printed to the user.
        try:
            self.context.argv = argv
            self._added()
            self._build_early_parser()
            self._preparse()
            self._early_init()
            self._build_parser()
            self._parse()
            self._late_init()
        except KeyboardInterrupt:
            self._shutdown()
            return
        # The execution phase. Here we differentiate SystemExit from all other
        # exceptions. SystemExit is just re-raised as that's what any piece of
        # code can raise to ask to exit the currently running application.  All
        # other exceptions are recorded in the context and the failure-path of
        # the dispatch is followed. In other case, when there are no
        # exceptions, the success-path is followed. In both cases, ingredients
        # are shut down.
        try:
            return self._dispatch()
        except SystemExit:
            raise
        except BaseException:
            (self.context.exc_type, self.context.exc_value,
             self.context.traceback) = sys.exc_info()
            self._dispatch_failed()
        else:
            self._dispatch_succeeded()
        finally:
            self._shutdown()

    def _added(self):
        """Run the added() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.added(self.context)

    def _build_early_parser(self):
        """Run build_early_parser() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.build_early_parser(self.context)

    def _preparse(self):
        """Run the peparse() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.preparse(self.context)

    def _early_init(self):
        """Run the early_init() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.early_init(self.context)

    def _build_parser(self):
        """Run build_parser() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.build_parser(self.context)

    def _parse(self):
        """Run the parse() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.parse(self.context)

    def _late_init(self):
        """Run the late_init() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.late_init(self.context)

    def _dispatch(self):
        """Run the dispatch() method on all ingredients."""
        for ingredient in self.ingredients:
            result = ingredient.dispatch(self.context)
            if result is not None:
                return result

    def _dispatch_succeeded(self):
        """Run the dispatch_succeeded() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.dispatch_succeeded(self.context)

    def _dispatch_failed(self):
        """Run the dispatch_failed() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.dispatch_failed(self.context)

    def _shutdown(self):
        """Run the shutdown() method on all ingredients."""
        for ingredient in self.ingredients:
            ingredient.shutdown(self.context)
