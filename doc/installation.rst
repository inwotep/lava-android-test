
.. _installation:

Installation
============

Prerequisites
^^^^^^^^^^^^^

The following debian packages are needed to use LAVA Test:

* python-setuptools
* python-apt
* usbutils
* python-testrepository - for running unit tests
* python-sphinx - for building documentation


Installation Options
^^^^^^^^^^^^^^^^^^^^

There are several installation options available:


Using Ubuntu PPAs
-----------------

For Ubuntu 10.04 onward there is a stable PPA (personal package archive):

* ppa:linaro-validation/ppa

To add a ppa to an Ubuntu system use the add-apt-repository command::

    sudo add-apt-repository ppa:linaro-validation/ppa

After you add the PPA you need to update your package cache::

    sudo apt-get update

Finally you can install the package, it is called `lava-test`::

    sudo apt-get install lava-test


Using Python Package Index
--------------------------

This package is being actively maintained and published in the `Python Package
Index <http://http://pypi.python.org>`_. You can install it if you have `pip
<http://pip.openplans.org/>`_ tool using just one line::

    pip install lava-test


Using source tarball
--------------------

To install from source you must first obtain a source tarball from either pypi
or from `Launchpad <http://launchpad.net/>`_. To install the package unpack the
tarball and run::

    python setup.py install

You can pass ``--user`` if you prefer to do a local (non system-wide)
installation. Note that executable programs are placed in ``~/.local/bin/`` and
this directory is not on ``PATH`` by default.
