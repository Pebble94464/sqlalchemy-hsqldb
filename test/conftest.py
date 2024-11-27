
# "This script bootstraps SQLAlchemy's pytest plugin into the pytest runner.
# This script can also be used to install your third party dialect into
# SQLAlchemy without using the setuptools entrypoint system; this allows
# your dialect to be present without any explicit setup.py step needed."

import os
os.environ['JAVA_HOME'] = "C:\\Program Files\\Java\\jre-1.8\\bin"

# Set CLASSPATH...
os.environ['CLASSPATH'] = "/PROGS/HSQLDB/hsqldb-osgi-jdk8.jar"
# The path can also be specified when calling create_engine, using the
# 'classpath' parameter, but I'm not currently aware of how create_engine
# parameters can be configured for use in the test environment.
# For this reason only we are going to use the environment variable above.
#
# '_get_classpath()' in the JayDeBeApi module reads the environment variable.


# The registry module provides a means of installing dialect entrypoints without the use of setuptools
from sqlalchemy.dialects import registry
if False:
	# Register 'hsqldb.jaydebeapi' - fails
	registry.register("hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi", "HyperSqlDialect_jaydebeapi")
else:
	# Register 'hsqldb' - succeeds (workaround)
	registry.register("hsqldb", "sqlalchemy_hsqldb.jaydebeapi", "HyperSqlDialect_jaydebeapi")
"""
TODO: fix conftest.py registry.register 'hsqldb.jaydebeapi' error...

When 'hsqldb.jaydebeapi' is registered as above, an error will occur when we attempt to execute tests:
	sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:hsqldb
If we register as 'hsqldb' instead, the error does not occur.
For some reason the testing framework seems to expect 'hsqldb', not 'hsqldb.jaydebeapi'.

Example command line being used to executing a test:
	pytest -rP -x --db hsqldb test/test_suite.py::DateTest::test_select_direct

Note the line above is using '--db hsqldb', which is defined in test.cfg as:
	[db]
	hsqldb = hsqldb+jaydebeapi://SA:@localhost:9001/test2

The error doesn't occur outside testing when we call create_engin in our scripts,
e.g.
	engine = create_engine("hsqldb+jaydebeapi://SA:@localhost/test2", echo=True)

Which is correct, 'hsqldb' or 'hsqldb.jaydebeapi'?  The latter, apparently...
The call to registry.register should reflect the entry points defined in setup.py,

    entry_points={
        "sqlalchemy.dialects": [
            "hsqldb.jaydebeapi = sqlalchemy_hsqldb.jaydebeapi:HyperSqlDialect_jaydebeapi",
            # "<dialect.driver> = <sqlalchemy_dialect.driver>:<dialect driver class>"
        ]
    },

"""
import pytest

# The line below suppresses spurious warnings from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *

