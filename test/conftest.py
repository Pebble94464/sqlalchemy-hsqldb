
# "This script bootstraps SQLAlchemy's pytest plugin into the pytest runner.
# This script can also be used to install your third party dialect into
# SQLAlchemy without using the setuptools entrypoint system; this allows
# your dialect to be present without any explicit setup.py step needed."

# The registry module provides a means of installing dialect entrypoints without the use of setuptools
from sqlalchemy.dialects import registry
registry.register(
	"hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi", "HyperSqlDialect_jaydebeapi"
)

import pytest

# The line below suppresses spurious warnings from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *

