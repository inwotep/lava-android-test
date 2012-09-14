
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

Using Python Package Index
--------------------------

This package is being actively maintained and published in the `Python Package
Index <http://http://pypi.python.org>`_. You can install it if you have `pip
<http://pip.openplans.org/>`_ tool using just one line::

    pip install lava-android-test


Using source tarball
--------------------

To install from source you must first obtain a source tarball from either pypi
or from `Launchpad <http://launchpad.net/>`_. To install the package unpack the
tarball and run::

    python setup.py install

You can pass ``--user`` if you prefer to do a local (non system-wide)
installation. Note that executable programs are placed in ``~/.local/bin/`` and
this directory is not on ``PATH`` by default.

Installing for development
--------------------------

An easy way to set things up for local development is to create a python
virtualenv. You can create the virtualenv anyway in your filesystem. In
the example below, its simply put under the bzr repo where development
is being done from::

    bzr branch lp:lava-android-test
    cd lava-android-test
    virtualenv .venv ; . ./venv/bin/activate
    pip install keyring
    ./setup.py develop
