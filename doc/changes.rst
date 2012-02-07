Version History
***************

.. _version_0_3.3:

Version 0.3.3
=============
* New perf test
* Fix dependencies for pwrmgmt and ltp tests
* Fix bug 898092 - More detail error messages when parsing the out of tree json file
* Added some documentation for many of the testsuites

.. _version_0_3.2:

Version 0.3.2
=============
* Update parse function using in LTP test suite to fix 900694
* fix a bug with tiobench

.. _version_0_2:

Version 0.2
===========

* Rewrite most of the code and deprecate old Abrek interfaces. This allowed us
  to clean up the API, rethink some of the design and integrate the code better
  with other parts of LAVA.

* Improved documentation and code reference. LAVA Test should now have
  sufficient documentation to help new users and contributors alike.

* Support for installing and running out-of-tree tests.

* Ability to define parsers that add new attachments.

* Unified command line interface with other lava tools thanks to lava-tool.

Version 0.1
===========

* Initial release (as Abrek)
