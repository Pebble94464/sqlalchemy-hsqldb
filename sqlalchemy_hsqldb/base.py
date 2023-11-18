
# "base.py defines the specific SQL dialect used by that database"
# [New Dialect System](https://docs.sqlalchemy.org/en/20/changelog/migration_06.html)

from sqlalchemy.engine import default
from sqlalchemy.engine import reflection
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import compiler
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql import quoted_name

#from sqlalchemy import types, exc, pool
from sqlalchemy import pool

# Types for mysql, pg and oracle, are defined in their respective types.py file...
# from .types import DATE
# from .types import FLOAT
# from .types import INTERVAL

#- from sqlalchemy.types import NUMERIC # already imported under sqltypes on line 9

# Don't create types for UPPERCASE types that already exist and are used as-is. Import them instead...
# TODO: import all UPPERCASE types that are used as-is...
# e.g.	from sqlalchemy.types import INTEGER



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

from sqlalchemy import types # TODO: relocate to top of file

class JDBCBlobClient(types.BLOB):
	__visit_name__ = "BLOB"

	# def bind_processor(self, dialect):
	# 	return None

	def result_processor(self, dialect, coltype):
		def process(value):
			assert repr(value) == "<java object 'org.hsqldb.jdbc.JDBCBlobClient'>" # type check for Java object
			return bytes(value.getBytes(1,int(value.length())))
		return process

# TODO: replace type checks for Java objects that are comparing strings, e.g. repr(value) == "<java object 'org.hsqldb.jdbc.JDBCBlobClient'>"

# <java class 'java.lang.Boolean'>
class HyperSqlBoolean(types.BOOLEAN):
	__visit_name__ = "BOOLEAN"
	def result_processor(self, dialect, coltype):
		def process(value):
			if value == None:
				return value
			assert str(type(value)) == "<java class 'java.lang.Boolean'>" # type check for Java object
			return bool(value)
		return process

class _HyperBoolean(types.BOOLEAN): # _CamelCase, stays private, invoked only by colspecs
	__visit_name__ = "_HyperBoolean"
	#- def __init__(self):
	#- 	print('_HyperBoolean.__init__()') #-

	#- TODO: remove Oracle function below...
	def get_dbapi_type_oracle(self, dbapi):
		return dbapi.NUMBER


# WIP: what are colspecs?
#		Descriptions can be found here:  site-packages\sqlalchemy\engine\interfaces.py
#		"colspecs" is a required Dialect class member according to type_migration_guidelines.txt

# 'colspecs' seems to map sqltypes to types defined in the dialect's types.py file.
# default.DefaultDialect.colspecs: MutableMapping[Type[TypeEngine[Any]], Type[TypeEngine[Any]]] = {}
#
# type_migration_guidelines.txt reads...
#		5. "colspecs" now is a dictionary of generic or uppercased types from sqlalchemy.types
#		linked to types specified in the dialect.   Again, if a type in the dialect does not
#		specify any special behavior for bind_processor() or result_processor() and does not
#		indicate a special type only available in this database, it must be *removed* from the 
#		module and from this dictionary.
#

# Map SQLAlchemy types to HSQLDB dialect types...
colspecs = {
	sqltypes.LargeBinary: JDBCBlobClient,
	sqltypes.Boolean: HyperSqlBoolean,

	# sqltypes.BLOB: JDBCBlobClient,
	# sqltypes.BINARY: JDBCBlobClient2,
	# sqltypes.PickleType: JDBCBlobClient,
	# sqltypes.ARRAY: _array.ARRAY,
	#sqltypes.Boolean: _HyperBoolean, #- TODO: remove mapping, and the class itself. Behavior doesn't differ
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

#- Map names returned by the "type_name" column of pyodbc's Cursor.columns method to our dialect types.
#- These names are what you would retrieve from INFORMATION_SCHEMA.COLUMNS.DATA_TYPE if Access supported those types of system views.
ischema_names = {
	"BLOB": JDBCBlobClient,
	# "boolean": HyperSqlBoolean,
	# "Boolean": HyperSqlBoolean,
	# "BOOLEAN": HyperSqlBoolean,
	"NUMERIC": sqltypes.NUMERIC,
	# "_Binary": JDBCBlobClient2,
	# "Binary": JDBCBlobClient2,
	# "BINARY": JDBCBlobClient2,
	# "org.hsqldb.jdbc.JDBCBlobClient": JDBCBlobClient3,
	# "LargeBinary": JDBCBlobClient,
	# "PickleType": JDBCBlobClient,
	# "boolean": YESNO,
	# "boolean": _HyperBoolean,
	# <key>: <our data_type class>
}


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

	# TODO: remove visit_Boolean below...
	def visit_Boolean_X(self, type_, **kw):
		# TODO: This function is not called. Remove it.
		raise NotImplementedError
		return _HyperBoolean.__visit_name__

	# TODO: remove visit_BOOLEAN below...
	def visit_BOOLEAN_X(self, type_, **kw):
		# This function gets called for Boolean and BOOLEAN, but duplicates the default BOOLEAN behaviour, so remove it.
		return _HyperBoolean.__visit_name__


# TODO: Implement HyperSqlIdentifierPreparer. About 20-55 lines, 2-5 methods.
class HyperSqlIdentifierPreparer(compiler.IdentifierPreparer):
	# Reserved words can be a union of sets 1 and 3, or 2 and 3.
	reserved_words = RESERVED_WORDS_1.union(RESERVED_WORDS_3)

	def __init__(self, dialect, **kwargs):
		super().__init__(dialect, **kwargs)

	def format_table(self, table, use_schema=True, name=None):
		"""Prepare a quoted table and schema name."""

		if name is None:
			name = table.name

		name = quoted_name(name, True)
		# HSQLDB normally changes table names to uppercase, unless the identifier is double quoted.
		# The line of code above is added to ensure the name is always wrapped in quotes.
		# An alternative solutions might be to ensure the name is converted to uppercase,
		# or maybe there is a configuration setting in HSQLDB or SQLAlchemy that changes the default behaviour. 
		# TODO: review table identifier case settings. Is the solution above sensible?

		result = self.quote(name)

		effective_schema = self.schema_for_object(table)

		if not self.omit_schema and use_schema and effective_schema:
			result = self.quote_schema(effective_schema) + "." + result
		return result



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

	#- ok...
	name = "hsqldb"




	supports_comments = True
	# HyperSQL supports comments on tables and columns, possibly in some non-standard way though.
	# TODO: verify the effect of this setting on HSQLDB.

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

	# TODO: verify the recently added setting below is required, and works as expected.
	default_paramstyle = "qmark"

	# ischema_names and colspecs are required members on the Dialect class, according to type_migration_guidelines.txt
	ischema_names = ischema_names
	colspecs = colspecs




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

	# @reflection.cache
	# def get_check_constraints(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	@reflection.cache
	def get_columns(self, connection, table_name, schema=None, **kw):
		if schema is None:
			schema = self.default_schema_name
		assert schema is not None
		reflectedColumns = []
		query = f"""
			SELECT
			A.COLUMN_NAME AS "name",
			-- TODO: 'type' has to possible fields, which differ slightly for certain data types. Choose one, remove the other...
			A.TYPE_NAME AS "type",		-- e.g. VARCHAR
			B.DATA_TYPE AS "type_b",	-- e.g. CHARACTER VARYING
			-- TODO: 'nullable' has to possible fields, with either YES/NO or 0/1 values. Choose one and remove the other...
			A.NULLABLE AS "nullable_01", -- 0 OR 1
			A.IS_NULLABLE AS "nullable_yesno", -- YES or NO
			A.COLUMN_DEF AS "default", -- TODO: What does COLUMN_DEF represent, default value, or definition?
			A.IS_AUTOINCREMENT AS "autoincrement",
			A.REMARKS AS "comment",
			-- NULL AS "computed", -- TODO: Does HSQLDB have an appropriate field?
			B.IS_IDENTITY AS "identity"
			-- NULL AS "dialect_options", -- TODO: Does HSQLDB have an appropriate field?
			FROM "INFORMATION_SCHEMA"."SYSTEM_COLUMNS" AS "A"
			LEFT JOIN "INFORMATION_SCHEMA"."COLUMNS" AS "B"
			ON A.TABLE_NAME = B.TABLE_NAME
			AND A.COLUMN_NAME = B.COLUMN_NAME
			AND A.TABLE_SCHEM = B.TABLE_SCHEMA
			AND A.TABLE_CAT = B.TABLE_CATALOG -- TODO: Document or fix potential area of failure. Catalogs with duplicate objects.
			WHERE A.TABLE_NAME = '{table_name}'
			AND A.TABLE_SCHEM = '{schema}'
			"""
		with connection as conn:
			cursorResult = conn.exec_driver_sql(query)
			for row in cursorResult.all():
				# Note row._mapping is using column names as keys and not the aliases defined in the query.

				col_name = row._mapping['COLUMN_NAME'] # str """column name"""

				assert row._mapping['TYPE_NAME'] in ischema_names, "ischema_names is missing a key for datatype %s" % row._mapping['TYPE_NAME']
				col_type = ischema_names[row._mapping['TYPE_NAME']] # TypeEngine[Any] """column type represented as a :class:`.TypeEngine` instance."""

				col_nullable = bool(row._mapping['NULLABLE']) # bool """boolean flag if the column is NULL or NOT NULL"""
				col_default = row._mapping['COLUMN_DEF'] # Optional[str] """column default expression as a SQL string"""
				col_autoincrement = row._mapping['IS_AUTOINCREMENT'] == 'YES' # NotRequired[bool] """database-dependent autoincrement flag.
				# This flag indicates if the column has a database-side "autoincrement"
				# flag of some kind.   Within SQLAlchemy, other kinds of columns may
				# also act as an "autoincrement" column without necessarily having
				# such a flag on them.
				# See :paramref:`_schema.Column.autoincrement` for more background on "autoincrement".
				col_comment = row._mapping['REMARKS'] # NotRequired[Optional[str]] """comment for the column, if present. Only some dialects return this key """
				col_computed = None # NotRequired[ReflectedComputed] """indicates that this column is computed by the database. Only some dialects return this key.

				# TODO: The type for identity should be ReflectedIdentity, not a bool.
				col_identity = row._mapping['IS_IDENTITY'] == 'YES' # NotRequired[ReflectedIdentity] indicates this column is an IDENTITY column. Only some dialects return this key.

				col_dialect_options = None # NotRequired[Dict[str, Any]] Additional dialect-specific options detected for this reflected object

			reflectedColumns.append({
				'name': col_name,
				'type': col_type,
				'nullable': col_nullable,
				'default': col_default,
				'autoincrement': col_autoincrement,
				'comment': col_comment,
				# 'computed': col_computed,
				# 'identity': col_identity,
				# 'dialect_options': col_dialect_options
				})
		return reflectedColumns

	# @reflection.cache
	# def get_foreign_keys(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_indexes(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_pk_constraint(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_schema_names(self, connection, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_sequence_names(self, connection, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_table_comment(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_table_names(self, connection, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_table_options(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_temp_table_names(self, connection, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_unique_constraints(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_view_definition(self, connection, view_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def get_view_names(self, connection, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def has_sequence(self, connection, sequence_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

	# @reflection.cache
	# def has_table(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

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
