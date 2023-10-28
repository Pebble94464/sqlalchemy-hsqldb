
# TODO: Implement the jdbc driver in this file.

from base import HyperSqlDialect
from types import ModuleType

class HyperSqlDialect_jaydebeapi(HyperSqlDialect):
	"""HyperSqlDialect implementation of Dialect using JayDeBeApi as the driver."""

	#- OK
	@classmethod
	def import_dbapi(cls) -> ModuleType:
		return __import__("jaydebeapi")
	#- The Access dialect sets module.pooling = (False). What's that?

