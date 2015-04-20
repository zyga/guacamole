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
APIs for guacamole add-on developers.

This module contains the public APIs for add-on developers. Add-ons (or
plug-ins) for guacamole are called **ingredients**. The :class:`Ingredient`
class contains a description of available add-on methods.

Ingredients are somewhat similar to Django middleware as they can influence the
execution of an application across its lifecycle. All of core guacamole
features are implemented as ingredients. Developers are encouraged to read core
ingredients to understand how to formulate their own design.

Ingredient APIs are *public*. They will be maintained for backwards
compatiblity. Since Guacamole doesn't automatically enable any third-party
ingredients, application developers that wish to use them need to use the
:mod:`guacamole.mix` module to create their own guacamole out of available
ingredients. Ingredient developers are recommended in documenting how to use
each ingredient this way.

In addition this module contains the public APIs for creating custom mixes of
guacamole.  A custom mix begins with a :class:`guacamole.core.Bowl` with any
number of :class:`guacamole.core.Ingredient` objects added.

If you are familiar with the :class:`guacamole.cmd.Command` you should know
that they are using the recipe system internally. They refer to pre-made
recipes that put particular ingredients into the bowl for a ready dish.

If you wish to build a custom experience on top of guacamole, please provide a
new recipe class. Recipes are how applications should interact with any
guacamole mixtures.
"""

from __future__ import absolute_import, print_function, unicode_literals

from guacamole.core import Bowl


__all__ = (
    str('Recipe'),
    str('RecipeError'),
)


class Recipe(object):

    """Mechanism to use ingredients to dispatch and invoke commands."""

    def get_ingredients(self):
        """
        Get a list of ingredients for making guacamole.

        :returns:
            A list of initialized ingredients.
        :raises RecipeError:
            If the recipe is wrong. This is a developer error. Do not handle
            this exception. Consult the error message to understand what the
            problem is and correct the recipe instead.
        """

    def prepare(self):
        """
        Prepare a bowl with the ingredients specified by this recipe.

        :return:
            A new :class:`Bowl` instance with all the ingredients prepared.
        """
        return Bowl(self.get_ingredients())

    def main(self, argv=None):
        """
        Shortcut to prepare a bowl of guacamole and eat it.

        :param argv:
            Command line arguments or None. None means that sys.argv is used
        :return:
            Whatever is returned by the eating the guacamole.

        This method can be used to quickly take a recipe, prepare the guacamole
        and eat it. It is named main as it is applicable as the main method of
        an application.
        """
        bowl = self.prepare()
        return bowl.eat(argv)


class RecipeError(Exception):

    """
    Exception raised when the recipe for guacamole is incorrect.

    This exception is only used when a set of ingredients is ordered correctly
    or has some missing elements. Each time this exception is raised it is
    accompanied by a detailed message that should help you to resolve the
    problem.

    .. note::
        This exception should not be handled, it is a developer error.
    """
