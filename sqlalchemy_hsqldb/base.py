
# "base.py defines the specific SQL dialect used by that database"
# [New Dialect System](https://docs.sqlalchemy.org/en/20/changelog/migration_06.html)

from sqlalchemy.engine import default
from sqlalchemy.engine import reflection
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import compiler
from sqlalchemy.sql import sqltypes

#from sqlalchemy import types, exc, pool
from sqlalchemy import pool

# Types for mysql, pg and oracle, are defined in their respective types.py file...
# from .types import DATE
# from .types import FLOAT
# from .types import INTERVAL


# TODO: Implement HyperSqlCompiler. About 400 lines. The derived subclass is also long.
class HyperSqlCompiler(compiler.SQLCompiler):
	pass

# TODO: Implement HyperSqlDDLCompiler. About 100 lines, 7 methods.
class HyperSqlDDLCompiler(compiler.DDLCompiler):
	pass

# TODO: Implement HyperSqlTypeCompiler. About 50-150 lines, 12-25 methods.
# TODO: Solve mystery. Access dialect has 'type_compiler', others have 'type_compiler_cls'
class HyperSqlTypeCompiler(compiler.GenericTypeCompiler):
	pass

# TODO: Implement HyperSqlIdentifierPreparer. About 20-55 lines, 2-5 methods.
class HyperSqlIdentifierPreparer(compiler.IdentifierPreparer):
	pass

# TODO: Implement HyperSqlExecutionContext. About 55-165 lines, 2-8 methods.
class HyperSqlExecutionContext(default.DefaultExecutionContext):
	pass


class HyperSqlDialect(default.DefaultDialect):
	"""HyperSqlDialect implementation of Dialect"""

	def __init__(self, classpath=None, **kwargs):
		super().__init__(**kwargs)
		self.classpath = classpath	# A path to the HSQLDB executable jar file.

	# WIP: what are colspecs?
	#		Descriptions can be found here:  site-packages\sqlalchemy\engine\interfaces.py

	# 'colspecs' seems to map sqltypes to types defined in the dialect's types.py file.
	# default.DefaultDialect.colspecs: MutableMapping[Type[TypeEngine[Any]], Type[TypeEngine[Any]]] = {}
	colspecs = {
		# sqltypes.ARRAY: _array.ARRAY,
		# sqltypes.Boolean: _OracleBoolean,
		# sqltypes.Date: _OracleDate,
		# sqltypes.DateTime: _MSDateTime,
		# sqltypes.Enum: ENUM,
		# sqltypes.Interval: INTERVAL,
		# sqltypes.JSON: JSON,
		# sqltypes.JSON.JSONIndexType: JSONIndexType,
		# sqltypes.JSON.JSONPathType: JSONPathType,
		# sqltypes.Time: _BASETIMEIMPL,
		# sqltypes.Unicode: _MSUnicode,
		# sqltypes.UnicodeText: _MSUnicodeText,
		# sqltypes.Uuid: MSUUid,
		# sqltypes.Uuid: PGUuid,
	}

	#- ok...
	name = "hsqldb"

	# Set 'supports_schemas' to false to disable schema-level tests
	supports_schemas = False
	# TODO: try setting to True (or removing) when we're ready for testing. Only the Access dialect appears to set it to false. Does it take too long to test?

	# HSQLDB's BOOLEAN type conforms to the SQL Standard and represents the values TRUE, FALSE and UNKNOWN"
	supports_native_boolean = True

	supports_sane_rowcount = True
	# Some drivers, particularly third party dialects for non-relational databases,
	# may not support _engine.CursorResult.rowcount at all.
	# The _engine.CursorResult.supports_sane_rowcount attribute will indicate this.
	#
	# Like MySql, Oracle, and PG, HSQLDB is a relational database, so I have set it to True.
	# Note that Access and sqlalchemy-jdbcapi have it set to False, for some reason unknown.

	supports_sane_multi_rowcount = True
	# For an :ref:`executemany <tutorial_multiple_parameters>` execution,
	# _engine.CursorResult.rowcount may not be available either, which depends
	# highly on the DBAPI module in use as well as configured options.  The
	# attribute _engine.CursorResult.supports_sane_multi_rowcount indicates
	# if this value will be available for the current backend in use.
	#
	# The default is True. Other DBs are set to True. I suspect HSQLDB supports it too, so set it to True.
	# Note that Access and sqlalchemy set it to False, for some reason.


	supports_simple_order_by_label = True
	# Target database supports ORDER BY <labelname>, where <labelname>
	# refers to a label in the columns clause of the SELECT
	#
	# TODO: can be removed / set to True if supported. Access has it set to False.

	#- ok
	supports_is_distinct_from = True
	# Supported since HSQLDB v2.0
	#- Default is True. Access's dialect is set to False.
	#-
	#- e.g. SELECT * FROM mytable WHERE col1 IS DISTINCT FROM col2;
	#- So you can use expressions like col1.is_distinct_from(col2) in SQLAlchemy when using the HSQLDB dialect.

	poolclass = pool.NullPool
	# QueuePool is the default.
	# Claude says NullPool or StaticPool is suitable for HSQLDB, but Claude's information might be outdated.
	# The Access dialect is using NullPool.
	# poolclass is normally specified as a parameter to create_engine function, e.g.
	#   create_engine("postgresql+psycopg2://scott:tiger@localhost/test", poolclass=NullPool)
	# pool_size for QueuePool can is also specified as a create_engine parameter, e.g.
	#   create_engine("postgresql+psycopg2://me@localhost/mydb", pool_size=20, max_overflow=0)
	# Detailed info on pooling can be found here:   \sqlalchemy\doc\build\core\pooling.rst
	#
	# How is the poolclass assigned to above referenced?
	#   poolclass is returned by the get_pool_class method of the DefaultDialect.
	# TODO: Verify if the above is correct.
	#
	# TODO: See if QueuePool works, or use StaticPool instead.

	statement_compiler = HyperSqlCompiler
	ddl_compiler = HyperSqlDDLCompiler
	type_compiler = HyperSqlTypeCompiler
	preparer = HyperSqlIdentifierPreparer
	execution_ctx_cls = HyperSqlExecutionContext

	@DeprecationWarning
	@classmethod
	def dbapi(cls):
		"""
		A reference to the DBAPI module object itself. (DEPRECATED)
		It is replaced by import_dbapi, which has been implemented in jaydebeapi.py
		"""
		raise NotImplementedError

	def _get_default_schema_name(self, connection):
		return connection.exec_driver_sql("VALUES(CURRENT_SCHEMA)").scalar()

	def _has_table_query():
		pass

	@reflection.cache
	def has_table(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		assert schema is not None
		cursorResult = connection.exec_driver_sql(
			f"""SELECT * FROM "INFORMATION_SCHEMA"."TABLES"
			WHERE TABLE_SCHEMA = '{schema}'
			AND TABLE_NAME = '{table_name}'
			""")
		return cursorResult.first() is not None
	# Tables are identified by catalog, schema, and table name in HSQLDB.
	# It's possible two tables could share matching schema and table names,
	# but in a different catalog, which might break the function above.

