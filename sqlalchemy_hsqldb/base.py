
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


# List of SQL Standard Keywords...
RESERVED_WORDS_1 = set(
"""ABS ALL ALLOCATE ALTER AND ANY ARE ARRAY AS ASENSITIVE ASYMMETRIC AT ATOMIC
AUTHORIZATION AVG BEGIN BETWEEN BIGINT BINARY BLOB BOOLEAN BOTH BY CALL CALLED
CARDINALITY CASCADED CASE CAST CEIL CEILING CHAR CHAR_LENGTH CHARACTER
CHARACTER_LENGTH CHECK CLOB CLOSE COALESCE COLLATE COLLECT COLUMN COMMIT
COMPARABLE CONDITION CONNECT CONSTRAINT CONVERT CORR CORRESPONDING COUNT
COVAR_POP COVAR_SAMP CREATE CROSS CUBE CUME_DIST CURRENT CURRENT_CATALOG
CURRENT_DATE CURRENT_DEFAULT_TRANSFORM_GROUP CURRENT_PATH CURRENT_ROLE
CURRENT_SCHEMA CURRENT_TIME CURRENT_TIMESTAMP CURRENT_TRANSFORM_GROUP_FOR_TYPE
CURRENT_USER CURSOR CYCLE DATE DAY DEALLOCATE DEC DECIMAL DECLARE DEFAULT
DELETE DENSE_RANK DEREF DESCRIBE DETERMINISTIC DISCONNECT DISTINCT DO DOUBLE
DROP DYNAMIC EACH ELEMENT ELSE ELSEIF END END_EXEC ESCAPE EVERY EXCEPT EXEC
EXECUTE EXISTS EXIT EXP EXTERNAL EXTRACT FALSE FETCH FILTER FIRST_VALUE FLOAT
FLOOR FOR FOREIGN FREE FROM FULL FUNCTION FUSION GET GLOBAL GRANT GROUP
GROUPING HANDLER HAVING HOLD HOUR IDENTITY IN INDICATOR INNER INOUT INSENSITIVE
INSERT INT INTEGER INTERSECT INTERSECTION INTERVAL INTO IS ITERATE JOIN LAG
LANGUAGE LARGE LAST_VALUE LATERAL LEAD LEADING LEAVE LEFT LIKE LIKE_REGEX LN
LOCAL LOCALTIME LOCALTIMESTAMP LOOP LOWER MATCH MAX MAX_CARDINALITY MEMBER
MERGE METHOD MIN MINUTE MOD MODIFIES MODULE MONTH MULTISET NATIONAL NATURAL
NCHAR NCLOB NEW NO NONE NORMALIZE NOT NTH_VALUE NTILE NULL NULLIF NUMERIC
OCCURRENCES_REGEX OCTET_LENGTH OF OFFSET OLD ON ONLY OPEN OR ORDER OUT OUTER
OVER OVERLAPS OVERLAY PARAMETER PARTITION PERCENT_RANK PERCENTILE_CONT
PERCENTILE_DISC PERIOD POSITION POSITION_REGEX POWER PRECISION PREPARE PRIMARY
PROCEDURE RANGE RANK READS REAL RECURSIVE REF REFERENCES REFERENCING REGR_AVGX
REGR_AVGY REGR_COUNT REGR_INTERCEPT REGR_R2 REGR_SLOPE REGR_SXX REGR_SXY
REGR_SYY RELEASE REPEAT RESIGNAL RESULT RETURN RETURNS REVOKE RIGHT ROLLBACK
ROLLUP ROW ROW_NUMBER ROWS SAVEPOINT SCOPE SCROLL SEARCH SECOND SELECT
SENSITIVE SESSION_USER SET SIGNAL SIMILAR SMALLINT SOME SPECIFIC SPECIFICTYPE
SQL SQLEXCEPTION SQLSTATE SQLWARNING SQRT STACKED START STATIC STDDEV_POP
STDDEV_SAMP SUBMULTISET SUBSTRING SUBSTRING_REGEX SUM SYMMETRIC SYSTEM
SYSTEM_USER TABLE TABLESAMPLE THEN TIME TIMESTAMP TIMEZONE_HOUR TIMEZONE_MINUTE
TO TRAILING TRANSLATE TRANSLATE_REGEX TRANSLATION TREAT TRIGGER TRIM TRIM_ARRAY
TRUE TRUNCATE UESCAPE UNDO UNION UNIQUE UNKNOWN UNNEST UNTIL UPDATE UPPER USER
USING VALUE VALUES VAR_POP VAR_SAMP VARBINARY VARCHAR VARYING WHEN WHENEVER
WHERE WHILE WIDTH_BUCKET WINDOW WITH WITHIN WITHOUT YEAR"""
.split())

# List of SQL Keywords Disallowed as HyperSQL Identifiers...
RESERVED_WORDS_2 = set(
"""ALL AND ANY AS AT AVG BETWEEN BOTH BY CALL CASE CAST COALESCE CONVERT
CORRESPONDING COUNT CREATE CROSS CUBE DEFAULT DISTINCT DROP ELSE EVERY EXCEPT
EXISTS FETCH FOR FROM FULL GRANT GROUP GROUPING HAVING IN INNER INTERSECT INTO
IS JOIN LEADING LEFT LIKE MAX MIN NATURAL NOT NULLIF ON OR ORDER OUTER PRIMARY
REFERENCES RIGHT ROLLUP SELECT SET SOME STDDEV_POP STDDEV_SAMP SUM TABLE THEN
TO TRAILING TRIGGER UNION UNIQUE USING VALUES VAR_POP VAR_SAMP WHEN WHERE WITH"""
.split())

# Special Function Keywords...
RESERVED_WORDS_3 = set("CURDATE CURTIME NOW SYSDATE SYSTIMESTAMP TODAY".split())

# TODO: Implement HyperSqlCompiler. About 400 lines. The derived subclass is also long.
class HyperSqlCompiler(compiler.SQLCompiler):

	def limit_clause(self, select, **kw):
		#- raise NotImplementedError
		text = ""
		if select._limit_clause is not None:
			text += " \n LIMIT " + self.process(select._limit_clause, **kw)
		if select._offset_clause is not None:
			if select._limit_clause is None:
				text += "\n LIMIT 0"	# For HSQLDB zero means no limit
			text += " OFFSET " + self.process(select._offset_clause, **kw)
		return text


#- SQLCompiler derives from class Compiled, which represents Represent a compiled SQL or DDL expression.




# TODO: Implement HyperSqlDDLCompiler. About 100 lines, 7 methods.
class HyperSqlDDLCompiler(compiler.DDLCompiler):
	pass
#- DDLCompiler derives from class Compiled, which represents Represent a compiled SQL or DDL expression.




# TODO: Implement HyperSqlTypeCompiler. About 50-150 lines, 12-25 methods.
# TODO: Solve mystery. Access dialect has 'type_compiler', others have 'type_compiler_cls'
class HyperSqlTypeCompiler(compiler.GenericTypeCompiler):
	pass
"""
class GenericTypeCompiler(TypeCompiler):
	class TypeCompiler(util.EnsureKWArg):
		"Produces DDL specification for TypeEngine objects."

"""


# TODO: Implement HyperSqlIdentifierPreparer. About 20-55 lines, 2-5 methods.
class HyperSqlIdentifierPreparer(compiler.IdentifierPreparer):
	# Reserved words can be a union of sets 1 and 3, or 2 and 3.
	reserved_words = RESERVED_WORDS_1.union(RESERVED_WORDS_3)

	pass
"""
class IdentifierPreparer:
	"Handle quoting and case-folding of identifiers based on options."

HSQLDB:
SET DATABASE SQL NAMES { TRUE | FALSE }
Allows or disallows the keywords as identifiers.
The default mode is FALSE and allows the use of most keywords as identifiers.
Even in this mode, FALSE, keywords cannot be used as USER or ROLE identifiers.
When the mode is TRUE, none of the keywords listed below can be used as identifiers.
All keywords can be used with double quotes as identifiers.

[HSQLDB List of Keywords](https://hsqldb.org/doc/2.0/guide/lists-app.html)


Identifiers must begin with a letter.
Setting 'SET DATABASE SQL REGULAR NAMES FALSE' relaxes the rules and allows
identifiers to begin with an underscore '_', and include dollar signs in the name.

Identifier length must be between 1 and 128 characters.

"""



# TODO: Implement HyperSqlExecutionContext. About 55-165 lines, 2-8 methods.
class HyperSqlExecutionContext(default.DefaultExecutionContext):
	pass

"""
https://docs.sqlalchemy.org/en/14/core/internals.html
default.DefaultExecutionContext derives from an ExecutionContext.
What is an execution context?
interfaces.py, line 2907, describes it as...
	"A messenger object for a Dialect that corresponds to a single execution."

Dialect		line count
-------		----------
ms			150
access		4
mysql		20
oracle		27
pg			54
"""



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

#################
	supports_statement_cache = False
	# All other dialects set supports_statement_cache to True.
	# A release note indicates it should be set on a dialect, and that there's some check for it.
	# It should also be set on derived classes.
	# Excluding it caused test 'test_binary_roundtrip' to fail.
	# Important detail, see: [Engine third-party caching](https://docs.sqlalchemy.org/en/20/core/connections.html#engine-thirdparty-caching)
	# TODO: revise / remove above comments

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


""" WIP:
This is the SQL currently generated by the default dialect...

CREATE TABLE sample_table (
	"Respondent" BIGINT, 
	"MainBranch" TEXT, 
	"YearsCode" FLOAT,
	...
)

For HSQLDB it should probably look something like this...

CREATE MEMORY TABLE IF NOT EXIST "PUBLIC"."sample_table" (
	"Respondent" BIGINT, 
	"MainBranch" VARCHAR(80), 
	"YearsCode" FLOAT, 
)

How do Dialects generate the correct data type?

"""
