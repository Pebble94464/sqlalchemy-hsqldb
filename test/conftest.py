
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
registry.register(
	"hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi", "HyperSqlDialect_jaydebeapi"
)

import pytest

# The line below suppresses spurious warnings from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *

