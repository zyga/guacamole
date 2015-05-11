============
Installation
============

The recommended installation method varies per platform. In general
``pip``-based installs work everywhere but it is recommended to use other
methods if possible.

Linux Distributions
===================

Debian (and derivatives)
------------------------

Install either ``python-guacamole`` or ``python3-guacamole`` (preferred) using
your preferred package manager front-end. An off-line copy of the documentation
is available in the ``python-guacamole-doc`` package. The same package includes
all of the bundled examples.

.. note::
    The version of Guacamole available in Debian might not be the most recent
    version but it was manually reviewed by Debian maintainers. The Debian
    archive contains cryptographically strong integrity and security
    guarantees. This method of installation is more trustworthy (and harder to
    attack) than the one used by pip.

Fedora (and derivatives)
------------------------

Currently there is no version of Guacamole packaged and available for Fedora. A
*copr* repository might be created if there is demand. Proper integration into
the Fedora archive is on the roadmap but was not attempted at this time.

Other distributions
-------------------

There are no other packages as of this writing. Please contribute one if you
can. See the :ref:`contributing` for details.

Other platforms
===============

At the command line run::

    $ pip install guacamole 

.. note::

    This section applies to all versions of Windows and OS X.
