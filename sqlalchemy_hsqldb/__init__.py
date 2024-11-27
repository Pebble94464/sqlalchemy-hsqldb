
from . import base

# There are two ways we can import jaydebeapi.py here...
# 1 - immediately:
if True:
	# This block can be enabled / disabled with no apparent effect other than
	# when jaydebeapi.py gets loaded.
	from . import jaydebeapi

	base.dialect = dialect = jaydebeapi.dialect # HyperSqlDialect_jaydebeapi
	# (The built-in dialects set base.dialect but Access dialect doesn't). Why?

# 2 - delayed:
# The registry module provides a means of installing dialect entry points
# without the use of setuptools.
from sqlalchemy.dialects import registry
registry.register(
	"hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi",
	"HyperSqlDialect_jaydebeapi"
)

#- If both 1 and 2 are disabled, the dialect still appears to work in my
#- development environment. Unsure why.
#- TODO: review whether HyperSqlDialect_jaydebeapi need to be imported here.


# TODO: Import classes from base, and any other modules required...
"""
# The built-ins do this like...
from .base import BIGINT
from .base import BINARY
...
from .base import YEAR
from .dml import Insert
from .dml import insert
from .expression import match
from ...util import compat

# Access dialect does it like...
from .base import (
    AutoNumber,
    Byte,
...
    YesNo,
)
"""


# TODO: Set __all__ to explicitly define which classes this module exports...
"""
# The access module doesn't do this, but the built-in modules do, e.g.
__all__ = (
    "BIGINT",
    "BINARY",
...
    "BOOLEAN",
)
"""
