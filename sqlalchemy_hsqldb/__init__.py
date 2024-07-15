
from . import base
from . import jaydebeapi

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

# TODO: Set the default dialect, if required...
"""
base.dialect = dialect = jaydebeapi.dialect

The built-in dialects set this, but the Access dialect doesn't.
Is 'dialect' actually declared anywhere in base.py? Can't find it.

Update: recently defined 'dialect' at the bottom of jaydebeapi.py.
"""
base.dialect = dialect = jaydebeapi.dialect


# TODO: Set __version__ if required
"""
__version__ = "0.1.0.dev0"

Only the Acccess dialect seems to set its version here.
Remove if unused.
"""

# The registry module provides a means of installing dialect entrypoints without the use of setuptools
from sqlalchemy.dialects import registry
registry.register(
	"hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi", "HyperSqlDialect_jaydebeapi"
)
# The three lines above are identical to those found in conftest.py,
# and very similar to what's found in the __init__.py for Access.
# Up until now we've been relying on the PluginLoader class in langhelpers.py,
# which I believe makes use of the entry points defined in setup.py
# TODO: review if we really need to register here, or can this be removed?