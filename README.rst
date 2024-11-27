sqlalchemy-hsqldb
=================
A HyperSQL dialect for SQLAlchemy

Description
-----------
The mighty objective of this project is to enable 
`SQLAlchemy <https://www.sqlalchemy.org/>`_ support for
`HyperSQL <https://hsqldb.org/>`_ 2.0 databases (aka HSQLDB).

As an initial release this version has limitations and still contains much
debug code. However the great news is "It works on my Windows based system",
currently passing about 38 percent of the dialect test suite.
Testing on other environments will follow in due course.

This project depends on a modified version of the
`JayDeBeApi <https://github.com/baztian/jaydebeapi>`_ module to provide
JDBC connectivity and a DB-API 2.0 interface. The module should install itself
automatically. If not, my project can be found here on GitHub:
`jaydebeapi-hsqldb <https://github.com/Pebble94464/jaydebeapi-hsqldb.git>`_

License
-------
sqlalchemy-hsqldb is distributed under the
`MIT license <https://opensource.org/licenses/MIT>`_.

Installation
------------
TODO: installation instructions
TODO: publish package on pypi.
::
pip install sqlalchemy-hsqldb

Configuration
-------------
TODO: write configuration section
# sqlalchemy-hsqldb://username:password@host:port/database

Getting Started
---------------
TODO: write example code

Troubleshooting
---------------

Contributing
------------

Testing
-------

Changelog
---------

Links
-----
