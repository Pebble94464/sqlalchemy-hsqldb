from . import base

# There are a couple of ways we can import jaydebeapi.py here...
# 1 - immediately:
if True:
	# This block can be enabled / disabled with no apparent effect other than
	# when jaydebeapi.py gets loaded.
	from . import jaydebeapi

	base.dialect = dialect = jaydebeapi.dialect # HyperSqlDialect_jaydebeapi
	# (The built-in dialects set base.dialect but Access dialect doesn't). Why?

# 2 - delayed:
# The registry module provides a way to install dialect entry points without
# the use of setuptools.
from sqlalchemy.dialects import registry
registry.register(
	"hsqldb.jaydebeapi", "sqlalchemy_hsqldb.jaydebeapi",
	"HyperSqlDialect_jaydebeapi"
)

from .base import ARRAY
from .base import BIGINT
from .base import BINARY
from .base import BIT
from .base import BLOB
from .base import BOOLEAN
from .base import CHAR
from .base import CLOB
from .base import DATALINK
from .base import DATE
from .base import DECIMAL
# from .base import DISTINCT
from .base import DOUBLE
from .base import FLOAT
from .base import INTEGER
from .base import JAVA_OBJECT
from .base import LONGNVARCHAR
from .base import LONGVARBINARY
from .base import LONGVARCHAR
from .base import MULTISET
from .base import NCHAR
from .base import NCLOB
# from .base import NULL # No dialect imports NULL
from .base import NUMERIC
from .base import NVARCHAR
from .base import OTHER
from .base import REAL
from .base import REF
from .base import REF_CURSOR
from .base import ROWID
from .base import SMALLINT
from .base import SQLXML
from .base import STRUCT
from .base import TIME
from .base import TIME_WITH_TIMEZONE
from .base import TIMESTAMP
from .base import TIMESTAMP_WITH_TIME_ZONE
from .base import TINYINT
from .base import VARBINARY
from .base import VARCHAR

__all__ = (
	'dialect',
	'ARRAY',
	'BIGINT',
	'BINARY',
	'BIT',
	'BLOB',
	'BOOLEAN',
	'CHAR',
	'CLOB',
	'DATALINK',
	'DATE',
	'DECIMAL',
#	'DISTINCT',
	'DOUBLE',
	'FLOAT',
	'INTEGER',
	'JAVA_OBJECT',
	'LONGNVARCHAR',
	'LONGVARBINARY',
	'LONGVARCHAR',
	'MULTISET',
	'NCHAR',
	'NCLOB',
	'NUMERIC',
	'NVARCHAR',
	'OTHER',
	'REAL',
	'REF',
	'REF_CURSOR',
	'ROWID',
	'SMALLINT',
	'SQLXML',
	'STRUCT',
	'TIME',
	'TIME_WITH_TIMEZONE',	# hsqldb's Types.java file defines this, but...
	# 'TIME_WITH_TIME_ZONE', 	# my dialect defines this
	'TIMESTAMP',
	'TIMESTAMP_WITH_TIME_ZONE',
	# 'TIMESTAMP_WITH_TIMEZONE',
	'TINYINT',
	'VARBINARY',
	'VARCHAR'
)
