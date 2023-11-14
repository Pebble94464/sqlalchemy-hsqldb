
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
"""

# TODO: Set __version__ if required
"""
__version__ = "0.1.0.dev0"

Only the Acccess dialect seems to set its version here.
Remove if unused.
"""

