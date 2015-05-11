.. _bundled_ingredients:

Recipes, Ingredients and Spices
===============================

Guacamole is a framework for creating command line applications. To understand
how to use it, you need to know about the three concepts (recipes, ingredients
and spices). They define how guacamole works (tastes) and they are how you can
make guacamole work for you in new and interesting ways.

Ingredients
-----------

Ingredients are pluggable components that can be added to a guacamole recipe.
They have well-defined APIs and are invoked by guacamole during the lifetime of
the application. You can think of ingredients as of middleware or a fancy
context manager. For an in-depth documentation see the
:class:`~guacamole.core.Ingredient` class. For a list of bundled ingredients
(batteries included) please see `bundled-ingredients`.

**Guacamole uses ingredients to avoid having complex, convoluted core. The core
literally does nothing more than to invoke all ingredients in a given order.
Applications use ingredietns indirectly, through recipes.**

Spices
------

Spices are small, optional bits of taste that can be added along with a given
ingredient. They are just a feature flag with a fancy name. You will see spices
documented along with each ingredient. For many features you will use the sane
defaults that guacamole aims to provide but sometimes you may want to tweak
something. Such elements can be hidden behind an ingredient.

**Guacamole uses spices to offer fixed cusomizability where it makes sense to
do so. Applications say witch spices they wish to use. Spices always enable
non-default behavior.**

Recipes
-------

Recipes define the sequence of ingredients to use for a tasty guacamole. In
reality a recipe is a simple function that returns a list of ingredient
instances to use in a given application.

**Guacamole uses recipes to offer easy-to-use, well-designed patterns for
creating applications. Anyone can create a recipe that uses a set of
ingredients that fit a particular purpose.**

Command?
--------

The :class:`~guacamole.recipes.cmd.Command` class is just a recipe that uses a
set of ingredients. As Guacamole matures, other recipes may be added.
