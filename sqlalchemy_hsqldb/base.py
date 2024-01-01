
# "base.py defines the specific SQL dialect used by that database"
# [New Dialect System](https://docs.sqlalchemy.org/en/20/changelog/migration_06.html)

# TODO: delete all lines begining with '#i'. They're just copied in from interfaces.py to make sure we haven't forgotten anything.
# TODO: Implement support for specifying catalog and schema in Dialect methods if possible. DefaultDialect supports schema only.

from sqlalchemy.engine import default
from sqlalchemy.engine import reflection
from sqlalchemy.engine.base import Connection
from sqlalchemy.engine.reflection import ReflectionDefaults
from sqlalchemy.sql import compiler
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql import quoted_name
from sqlalchemy import schema
from sqlalchemy import BindTyping
from sqlalchemy import util

from sqlalchemy.sql.compiler import InsertmanyvaluesSentinelOpts
# TODO: remove InsertmanyvaluesSentinelOpts and all other unused imports

#from sqlalchemy import types, exc, pool
from sqlalchemy import pool

# Types for mysql, pg and oracle, are defined in their respective types.py file...
# from .types import DATE
# from .types import FLOAT
# from .types import INTERVAL
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

#-class JDBCBlobClient(types.BLOB):
class _LargeBinary(types.BLOB):
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

# Map SQLAlchemy types to HSQLDB dialect types.
# Note:	If a type doesn't specify any special behavior for bind_processor() or result_processor() and does not indicate
#		a special type only available in this database, it must be *removed* from the module and from this dictionary.
colspecs = {
	# sqltypes.LargeBinary: JDBCBlobClient,
	sqltypes.LargeBinary: _LargeBinary,
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

# ischema_names provides a mapping between types returned by the database and SQLAlchemy types.
# The ischema_names dictionary uses db types for the keys, and SQLAlchemy types as the values.
# Normally the values are specified as the uppercase SQLAlchemy types, unless there is nothing analogous.
# If a dialect-specific type matches an SQLAlchemy type, but has extra arguments, map to the dialect-specific type.
#
# The keys match what is returned by the database. I'm currently unsure which of the following two fields should be used...
#
# INFORMATION_SCHEMA.SYSTEM_COLUMNS.TYPE_NAME
#	e.g. VARCHAR
#
# INFORMATION_SCHEMA.COLUMNS.DATA_TYPE
#	e.g. CHARACTER VARYING
#
# The Access dialect apparently uses INFORMATION_SCHEMA.COLUMNS.DATA_TYPE
#
ischema_names = {

	# TODO: Mapping BLOB to sqltypes.BLOB is probably the correct way to do it. Swap out the mapping to JDBCBlobClient and test again to verify it still works.
	# WIP: trying swapping out JDBCBlobClient for BLOB...
	# "BLOB": JDBCBlobClient,
	"BLOB": sqltypes.BLOB,

	# TODO: try mapping BOOLEAN to sqltypes.BOOLEAN. Test and verify it works.
	# "BOOLEAN": HyperSqlBoolean,

	"NUMERIC": sqltypes.NUMERIC,
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

	def render_bind_cast(self, type_, dbapi_type, sqltext):
		return super().render_bind_cast(type_, dbapi_type, sqltext)
	# 'render_bind_cast' gets called when HyperSqlDialect.bind_typing = BindTyping.BIND_CASTS
	# 'render_bind_cast' is not implemented in the base.
	# 'render_bind_cast' is specialised by the postgresql dialect.
	# An alternative is BindingTyping.SETINPUTSIZES, which doesn't appear to be supported by JPype.
	# TODO: investigate if render_bind_cast is appropriate for HSQLDB, or remove this method if unused.


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

	# SQLAlchemy normalises identifiers by converting them to lowercase.
	# HSQLDB normalises them by converting to uppercase, as does Oracle, Firebird and DB2.
	# The format_table function below attempts to force the quoting of table names,
	# which helped solve one test failure but caused another.
	# None of the other dialects attempt to force quoting of table names this way,
	# so my implementation is most likely wrong.
	# TODO: re-examine the test that format_table was meant to fix.
	# TODO: remove format_table below. (temporarily renamed format_tableX)
	def format_tableX(self, table, use_schema=True, name=None):
		"""Prepare a quoted table and schema name."""

		if name is None:
			name = table.name

		name = quoted_name(name, True)
		# HSQLDB normally changes table names to uppercase, unless the identifier is double quoted.
		# The line of code above is added to ensure the name is always wrapped in quotes.
		# An alternative solutions might be to ensure the name is converted to uppercase,
		# or maybe there is a configuration setting in HSQLDB or SQLAlchemy that changes the default behaviour. 

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



#i  CACHE_HIT = CacheStats.CACHE_HIT
#i  CACHE_MISS = CacheStats.CACHE_MISS
#i  CACHING_DISABLED = CacheStats.CACHING_DISABLED
#i  NO_CACHE_KEY = CacheStats.NO_CACHE_KEY
#i  NO_DIALECT_SUPPORT = CacheStats.NO_DIALECT_SUPPORT

#i  dispatch: dispatcher[Dialect]

#i  name: str; """identifying name for the dialect from a DBAPI-neutral point of view (i.e. 'sqlite') """
	name = "hsqldb"

#i  driver: str
#i  """identifying name for the dialect's DBAPI"""

#i  dialect_description: str

#i  dbapi: Optional[ModuleType]
#i  """A reference to the DBAPI module object itself.

#i  SQLAlchemy dialects import DBAPI modules using the classmethod
#i  :meth:`.Dialect.import_dbapi`. The rationale is so that any dialect
#i  module can be imported and used to generate SQL statements without the
#i  need for the actual DBAPI driver to be installed.  Only when an
#i  :class:`.Engine` is constructed using :func:`.create_engine` does the
#i  DBAPI get imported; at that point, the creation process will assign
#i  the DBAPI module to this attribute.

#i  Dialects should therefore implement :meth:`.Dialect.import_dbapi`
#i  which will import the necessary module and return it, and then refer
#i  to ``self.dbapi`` in dialect code in order to refer to the DBAPI module
#i  contents.

#i  .. versionchanged:: The :attr:`.Dialect.dbapi` attribute is exclusively
#i  used as the per-:class:`.Dialect`-instance reference to the DBAPI
#i  module.   The previous not-fully-documented ``.Dialect.dbapi()``
#i  classmethod is deprecated and replaced by :meth:`.Dialect.import_dbapi`.

#i  """

	@DeprecationWarning
	@classmethod
	def dbapi(cls):
		"""
		A reference to the DBAPI module object itself. (DEPRECATED)
		It is replaced by import_dbapi, which has been implemented in jaydebeapi.py
		"""
		raise NotImplementedError
	# TODO: remove the deprecated function above.




#i  def loaded_dbapi(self) -> ModuleType:
#i    """same as .dbapi, but is never None; will raise an error if no
#i    DBAPI was set up.

#i    .. versionadded:: 2.0

#i    """
#i    raise NotImplementedError()

#i  positional: bool
#i  """True if the paramstyle for this Dialect is positional."""

#i  paramstyle: str
#i  """the paramstyle to be used (some DB-APIs support multiple
#i  paramstyles).
#i  """

#i  compiler_linting: Linting

#i  statement_compiler: Type[SQLCompiler]; """a :class:`.Compiled` class used to compile SQL statements"""
	statement_compiler = HyperSqlCompiler

#i  ddl_compiler: Type[DDLCompiler]; """a :class:`.Compiled` class used to compile DDL statements"""
	ddl_compiler = HyperSqlDDLCompiler

#i  type_compiler_cls: ClassVar[Type[TypeCompiler]]; """a :class:`.Compiled` class used to compile SQL type objects"""
	type_compiler_cls = HyperSqlTypeCompiler

#i  type_compiler_instance: TypeCompiler; JSN: see DefaultDialect's constructor

#i  type_compiler: Any; JSN: assigned in DefaultDialect's constructor.

#i  preparer: Type[IdentifierPreparer]; """a :class:`.IdentifierPreparer` class used to quote identifiers."""
	preparer = HyperSqlIdentifierPreparer

#i  identifier_preparer: IdentifierPreparer; assigned in DefaultDialect's constructor.


#i  server_version_info: Optional[Tuple[Any, ...]]; assigned in DefaultDialect's "initialise" function

#i  default_schema_name: Optional[str]; JSN: use the default's property, don't implement.

#i  default_isolation_level: Optional[IsolationLevel] ; assigned in DefaultDialect's 'initialise' function.


#i  _on_connect_isolation_level: Optional[IsolationLevel]; assigned in DefaultDialect's ctor

#i  execution_ctx_cls: Type[ExecutionContext]; """a :class:`.ExecutionContext` class used to handle statement execution"""
	execution_ctx_cls = HyperSqlExecutionContext

#i  execute_sequence_format: tuple # JSN: Use the DefaultDialect's property.
	# execute_sequence_format: tuple # inherit from DefaultDialect

#i  supports_alter: bool
	supports_alter = True

#i  max_identifier_length: int """The maximum length of identifier names."""
	max_identifier_length = 128

#i  supports_server_side_cursors: bool """indicates if the dialect supports server side cursors"""
	supports_server_side_cursors = True

#i  server_side_cursors: bool """deprecated; indicates if the dialect should attempt to use server side cursors by default"""

#i  supports_sane_rowcount: bool; """Indicate whether the dialect properly implements rowcount for ``UPDATE`` and ``DELETE`` statements. """
	supports_sane_rowcount = True
	# Some drivers, particularly third party dialects for non-relational databases,
	# may not support _engine.CursorResult.rowcount at all.
	# The _engine.CursorResult.supports_sane_rowcount attribute will indicate this.
	#
	# Like MySql, Oracle, and PG, HSQLDB is a relational database, so I have set it to True.
	# Note that Access and sqlalchemy-jdbcapi have it set to False, for reason unknown.

#i  supports_sane_multi_rowcount: bool; """Indicate whether the dialect properly implements rowcount for ``UPDATE`` and ``DELETE`` statements when executed via executemany."""
	supports_sane_multi_rowcount = True
	# For an :ref:`executemany <tutorial_multiple_parameters>` execution,
	# _engine.CursorResult.rowcount may not be available either, which depends
	# highly on the DBAPI module in use as well as configured options.  The
	# attribute _engine.CursorResult.supports_sane_multi_rowcount indicates
	# if this value will be available for the current backend in use.
	#
	# The default is True. Other DBs are set to True. I suspect HSQLDB supports it too, so set it to True.
	# Note that Access and sqlalchemy set it to False, for some reason.

#i  supports_empty_insert: bool; """dialect supports INSERT () VALUES (), i.e. a plain INSERT with no columns in it """
	supports_empty_insert = False
	# Unsure of the correct setting for 'supports_empty_insert'.
	# HSQLDB's INSERT statement can work without specifying columns, and
	# I've got a feeling auto generated values don't always need specifying.
	# The major dialects appear to set it to false, so I've done the same for now.
	# TODO: Confirm the correct setting for supports_empty_insert.

#i  supports_default_values: bool; """dialect supports INSERT... DEFAULT VALUES syntax"""
	supports_default_values = True
	#- proven to work


#i  supports_default_metavalue: bool; """dialect supports INSERT...(col) VALUES (DEFAULT) syntax.
	supports_default_metavalue = True

#i  default_metavalue_token: str = "DEFAULT"; """for INSERT... VALUES (DEFAULT) syntax, the token to put in parenthesis.
	default_metavalue_token = "DEFAULT"

#i  supports_multivalues_insert: bool; e.g. INSERT INTO table (cols) VALUES (...), (...), (...), ...
	supports_multivalues_insert = True

#i  insert_executemany_returning: bool; the database supports INSERT...RETURNING when dialect.do_executemany() is used.
	insert_executemany_returning = False
	# RETURNING doesn't appear to be a recognised keyword.

#i  insert_executemany_returning_sort_by_parameter_order: bool
	insert_executemany_returning_sort_by_parameter_order = False

#i  update_executemany_returning: bool; """dialect supports UPDATE..RETURNING with executemany."""
	update_executemany_returning = False

#i  delete_executemany_returning: bool; """dialect supports DELETE..RETURNING with executemany."""
	delete_executemany_returning = False

#i  use_insertmanyvalues: bool; #i  """if True, indicates "insertmanyvalues" functionality should be used to allow for ``insert_executemany_returning`` behavior, if possible.
	use_insertmanyvalues = True
	# This setting likely has no effect for HSQLDB because it doesn't support RETURNING.
	# It can probably be set to either True or False (preferred).
	# However setting attribute 'use_insertmanyvalues_wo_returning' to True implies
	# a different code path is executed, one that doesn't depend on RETURNING.
	# Let's try setting both attributes to True for now and review the decision later.
	# TODO: compare with the generated when both the mentioned attributes are set to False

#i  use_insertmanyvalues_wo_returning: bool; #i  """if True, and use_insertmanyvalues is also True, INSERT statements that don't include RETURNING will also use "insertmanyvalues".
	use_insertmanyvalues_wo_returning = True
	# See TODO comments on 'use_insertmanyvalues'.


#i  insertmanyvalues_implicit_sentinel: InsertmanyvaluesSentinelOpts; #i  """Options indicating the database supports a form of bulk INSERT where the autoincrement integer primary key can be reliably used as an ordering for INSERTed rows.
	insertmanyvalues_implicit_sentinel = (compiler.InsertmanyvaluesSentinelOpts.NOT_SUPPORTED)
	# The sentinel tests require 'insert_returning'. Not supported.


#i  insertmanyvalues_page_size: int; Number of rows to render into an individual INSERT..VALUES() statement
	insertmanyvalues_page_size = 0xFFFFFFFF # default value of DefaultDialect is 1000.
#i  insertmanyvalues_max_parameters: int; # Alternate to insertmanyvalues_page_size, will additionally limit page size based on number of parameters total in the statement.
	insertmanyvalues_max_parameters = 0xFFFFFFFF # DefaultDialect's value is 32700
	#
	# HSQLDB does not impose limits on the size of databases (rows, columns, etc).
	# Does the VALUES statement limit the number of rows or columns specified?
	# Assuming it doesn't, the limits imposed by insertmanyvalues_page_size
	# and insertmanyvalues_max_parameters can be removed.
	#
	#  TODO: figure out the correct way to specify no limits for insertmanyvalues_page_size and insertmanyvalues_max_parameters.

#i  preexecute_autoincrement_sequences: bool
	preexecute_autoincrement_sequences: False
	# The default value is False. PostgreSQL has it set to true.
	# TODO: verify correct setting for HSQLDB

#i  insert_returning: bool; #i  """if the dialect supports RETURNING with INSERT
	insert_returning = False

#i  update_returning: bool; #i  """if the dialect supports RETURNING with UPDATE
	update_returning = False

#i  update_returning_multifrom: bool; #i  """if the dialect supports RETURNING with UPDATE..FROM
	update_returning_multifrom = False

#i  delete_returning: bool; #i  """if the dialect supports RETURNING with DELETE
	delete_returning = False

#i  delete_returning_multifrom: bool; #i  """if the dialect supports RETURNING with DELETE..FROM
	delete_returning_multifrom = False

#i  favor_returning_over_lastrowid: bool; #i  """for backends that support both a lastrowid and a RETURNING insert strategy, favor RETURNING for simple single-int pk inserts.
	favor_returning_over_lastrowid = False

#i  supports_identity_columns: bool; #i  """target database supports IDENTITY"""
	supports_identity_columns = True

#i  cte_follows_insert: bool; # target database, when given a CTE with an INSERT statement, needs the CTE to be below the INSERT"""
	cte_follows_insert = False

#i  colspecs: MutableMapping[Type[TypeEngine[Any]], Type[TypeEngine[Any]]]
	colspecs = colspecs
	ischema_names = ischema_names
	# ischema_names and colspecs are required members on the Dialect class, according to type_migration_guidelines.txt
	# TODO: although ischema_names is a required property of the Dialect class, it doesn't appear to be a property of the interface. Why?

#i  supports_sequences: bool; # Indicates if the dialect supports CREATE SEQUENCE or similar."""
	supports_sequences = True

#i  sequences_optional: bool
	sequences_optional: True
	# TODO: verify correct setting for sequences_optional

#i  default_sequence_base: int; # the default value that will be rendered as the "START WITH" portion of a CREATE SEQUENCE DDL statement.
	default_sequence_base = 0

#i  supports_native_enum: bool; # Indicates if the dialect supports a native ENUM construct. This will prevent :class:`_types.Enum` from generating a CHECK constraint when that type is used in "native" mode.
	supports_native_enum = False
	# "HyperSQL translates MySQL's ENUM data type to VARCHAR with a check constraint on the enum values"

#i  supports_native_boolean: bool; """Indicates if the dialect supports a native boolean construct. This will prevent :class:`_types.Boolean` from generating a CHECK constraint when that type is used."""
	supports_native_boolean = True
	# HSQLDB's BOOLEAN type conforms to the SQL Standard and represents the values TRUE, FALSE and UNKNOWN"

#i  supports_native_decimal: bool; # indicates if Decimal objects are handled and returned for precision numeric types, or if floats are returned"""
	supports_native_decimal = True

#i  supports_native_uuid: bool; # indicates if Python UUID() objects are handled natively by the driver for SQL UUID datatypes.
	supports_native_uuid = True

#i  returns_native_bytes: bool; # indicates if Python bytes() objects are returned natively by the driver for SQL "binary" datatypes.
	returns_native_bytes = True

#i  construct_arguments: Optional[
#i    List[Tuple[Type[Union[SchemaItem, ClauseElement]], Mapping[str, Any]]]
#i  ] = None
#i  """Optional set of argument specifiers for various SQLAlchemy constructs, typically schema items.

#i  To implement, establish as a series of tuples, as in::

#i    construct_arguments = [
#i      (schema.Index, {
#i        "using": False,
#i        "where": None,
#i        "ops": None
#i      })
#i    ]

#i  If the above construct is established on the PostgreSQL dialect,
#i  the :class:`.Index` construct will now accept the keyword arguments
#i  ``postgresql_using``, ``postgresql_where``, nad ``postgresql_ops``.
#i  Any other argument specified to the constructor of :class:`.Index`
#i  which is prefixed with ``postgresql_`` will raise :class:`.ArgumentError`.

#i  A dialect which does not include a ``construct_arguments`` member will
#i  not participate in the argument validation system.  For such a dialect,
#i  any argument name is accepted by all participating constructs, within
#i  the namespace of arguments prefixed with that dialect name.  The rationale
#i  here is so that third-party dialects that haven't yet implemented this
#i  feature continue to function in the old way.

#i  .. seealso::

#i    :class:`.DialectKWArgs` - implementing base class which consumes
#i    :attr:`.DefaultDialect.construct_arguments`
#i  """
#- (https://docs.sqlalchemy.org/en/20/core/foundation.html#sqlalchemy.sql.base.DialectKWArgs)

	construct_arguments = [
		(schema.Index, {}),
		(schema.Table, {})
	]
	# Not yet fully implemented because we don't immediately know what the valid parameters will be.
	# Providing a partial implementation with the expectation that an ArgumentError will be raised
	# when unrecognised parameters are encountered, so we can later fill in the blanks.
	#
	# Example entry...
	# 	(schema.Index, {
	# 		"using": False,
	# 		"where": None,
	# 		"ops": None
	# 	}),
	#
	# TODO: complete construct_arguments







#i  reflection_options: Sequence[str] = () # Sequence of string names to be passed as "reflection options" when using Table.autoload_with.
	reflection_options = ()
	# TODO: reflection_options is currently empty. Remove or comment out if unused.


#i  dbapi_exception_translation_map: Mapping[str, str] = util.EMPTY_DICT
#i  """A dictionary of names that will contain as values the names of
#i  pep-249 exceptions ("IntegrityError", "OperationalError", etc)
#i  keyed to alternate class names, to support the case where a
#i  DBAPI has exception classes that aren't named as they are
#i  referred to (e.g. IntegrityError = MyException).   In the vast
#i  majority of cases this dictionary is empty.
#i  """
	dbapi_exception_translation_map = {
		# "SomeWarning" : "Warning",
		# "SomeError" : "Error",
		# "" : "InterfaceError",
		# "" : "DatabaseError",
		# "" : "DataError",
		# "" : "OperationalError",
		# "" : "IntegrityError",
		# "" : "InternalError",
		# "" : "ProgrammingError",
		# "" : "NotSupportedError",
	}
	# This dictionary maps DBAPI exceptions to the exceptions of
	# PEP 249 – Python Database API Specification v2.0.
	# See: (https://peps.python.org/pep-0249/#exceptions)
	# In most cases it will be empty apparently.
	# TODO: update dbapi_exception_translation_map as and when dbapi errors are encountered. Remove if not it remains empty.


#i  supports_comments: bool; """Indicates the dialect supports comment DDL on tables and columns."""
	supports_comments = True
	# HyperSQL supports comments on tables and columns, possibly in some non-standard way though.
	# TODO: verify the effect of this setting on HSQLDB.

#i  inline_comments: bool; # supported by mysql
	inline_comments = False

#i  supports_constraint_comments: bool; # Indicates if the dialect supports comment DDL on constraints.
	supports_constraint_comments = False

#i  _has_events = False

#i  supports_statement_cache: bool = True; """indicates if this dialect supports caching.
	supports_statement_cache = False
	# All other dialects set supports_statement_cache to True.
	# A release note indicates it should be set on a dialect, and that there's some check for it.
	# See comments in interfaces.py for more info.
	# It should also be set on derived classes.
	# Excluding it causes test 'test_binary_roundtrip' to fail.
	# Important detail, see: [Engine third-party caching](https://docs.sqlalchemy.org/en/20/core/connections.html#engine-thirdparty-caching)
	# TODO: revise / remove above comments


#i  _supports_statement_cache: bool
#i  """internal evaluation for supports_statement_cache"""

#i  bind_typing = BindTyping.NONE; define a means of passing typing information to the database and/or driver for bound parameters.
	bind_typing = BindTyping.NONE
	# The options are... NONE | SETINPUTSIZES | RENDER_CASTS
	#
	# According to JPype documentation, the setinputsizes method has not been implemented. See...
	# (https://jpype.readthedocs.io/en/latest/dbapi2.html#jpype.dbapi2.Cursor.setinputsizes)
	# So, presumeably unsupported by HSQLDB via JayDeBeApi.
	#
	# Setting BindTyping to RENDER_CASTS results in calls to SQLCompiler.render_bind_casts
	# The base class's method is not implemented. However the PG dialect overrides it.
	# TODO: Investigate further. Can HSQLDB use RENDER_CASTS?

#i  is_async: bool; # """Whether or not this dialect is intended for asyncio use."""
	is_async = False
	# We'll initially test with is_async set to false, in order to simplify debugging during development.
	# TODO: set is_async to True, unless we're still debugging

#i  has_terminate: bool # """Whether or not this dialect has a separate "terminate" implementation that does not block or require awaiting."""
	has_terminate = True
	# HSQLDB can terminate sessions or transactions in various ways using
	# statements ALTER SESSION, COMMIT, ROLLBACK, and DISCONNECT.
	# For details see https://hsqldb.org/doc/guide/sessions-chapt.html
	#
	# Is this what 'has_terminate' is used for?  Unsure, so let's set it to true
	# for now and wait for it to fail before attempting to implement support.

#i  engine_config_types: Mapping[str, Any]; # A mapping of string keys that can be in an engine config linked to type conversion functions.
	engine_config_types = default.DefaultDialect.engine_config_types.union(
		{
			# "pool_timeout": util.asint,					# DefaultDialect
			# "echo": util.bool_or_str("debug"),			# DefaultDialect
			# "echo_pool": util.bool_or_str("debug"),		# DefaultDialect
			# "pool_recycle": util.asint,					# DefaultDialect
			# "pool_size": util.asint,						# DefaultDialect
			# "max_overflow": util.asint,					# DefaultDialect
			# "future": util.asbool,						# DefaultDialect
			"legacy_schema_aliasing": util.asbool			# mssql dialect - not applicable - remove
		}
	)
	# TODO: Remove any engine_config_types that are commented out or inapplicable. Add entries if required. Remove final engine_config_types if completely empty.

#i  label_length: Optional[int]; # optional user-defined max length for SQL labels"""
	label_length = 128
	# Unknown. Will assume label_length is the same value as max_identifier_length for now.
	# TODO: verify correct value for label_length

#i  include_set_input_sizes: Optional[Set[Any]] # set of DBAPI type objects that should be included in automatic cursor.setinputsizes() calls.
	# include_set_input_sizes = {} # n/a because SET_INPUT_SIZES is unsupported

#i  exclude_set_input_sizes: Optional[Set[Any]]; # set of DBAPI type objects that should be excluded in automatic cursor.setinputsizes() calls.
	# exclude_set_input_sizes = {} # n/a because SET_INPUT_SIZES is unsupported

#i  supports_simple_order_by_label: bool; """target database supports ORDER BY <labelname>, where <labelname> refers to a label in the columns clause of the SELECT"""
	supports_simple_order_by_label = True
	# Target database supports ORDER BY <labelname>, where <labelname>
	# refers to a label in the columns clause of the SELECT
	# TODO: can be removed / set to True if supported. Access has it set to False.

#i  div_is_floordiv: bool # target database treats the / division operator as "floor division" """
	div_is_floordiv: True
	# Verified. VALUES(5/3) returns 1

#i  tuple_in_values: bool # target database supports tuple IN, i.e. (x, y) IN ((q, p), (r, z))"""
	tuple_in_values = True
	# Verified.

#i  _bind_typing_render_casts: bool

#i  _type_memos: MutableMapping[TypeEngine[Any], _TypeMemoDict]

#i  def _builtin_onconnect(self) -> Optional[_ListenerFnType]:
#i    raise NotImplementedError()

#i  def create_connect_args(self, url: URL) -> ConnectArgsType:
#i    """Build DB-API compatible connection arguments.

#i    Given a :class:`.URL` object, returns a tuple
#i    consisting of a ``(*args, **kwargs)`` suitable to send directly
#i    to the dbapi's connect function.   The arguments are sent to the
#i    :meth:`.Dialect.connect` method which then runs the DBAPI-level
#i    ``connect()`` function.

#i    The method typically makes use of the
#i    :meth:`.URL.translate_connect_args`
#i    method in order to generate a dictionary of options.

#i    The default implementation is::

#i      def create_connect_args(self, url):
#i        opts = url.translate_connect_args()
#i        opts.update(url.query)
#i        return ([], opts)

#i    :param url: a :class:`.URL` object

#i    :return: a tuple of ``(*args, **kwargs)`` which will be passed to the
#i    :meth:`.Dialect.connect` method.

#i    .. seealso::

#i      :meth:`.URL.translate_connect_args`

#i    """

#i    raise NotImplementedError()
#- jsn: use DefaultDialect.create_connect_args


#i  def import_dbapi(cls) -> ModuleType: # Import the DBAPI module that is used by this dialect.
	#- def import_dbapi(cls): raise NotImplementedError() # implemented by jaydebeapi.py

#i  def type_descriptor(cls, typeobj: TypeEngine[_T]) -> TypeEngine[_T]: #i Transform a generic type to a dialect-specific type.
	#- def type_descriptor(cls, typeobj: TypeEngine[_T]) # inherit from DefaultDialect


#i  def initialize(self, connection: Connection) -> None: """Called during strategized creation of the dialect with a connection.

	def initialize(self, connection):
		super().initialize(connection)
	# Allows dialects to configure options based on server version info or other properties.
	# E.g., self.supports_identity_columns = self.server_version_info >= (10,)

#i  if TYPE_CHECKING:
#i    def _overrides_default(self, method_name: str) -> bool:
#i      ...

#i  def get_columns(
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
			B.IS_IDENTITY AS "identity",
			-- NULL AS "dialect_options", -- TODO: Does HSQLDB have an appropriate field?
			B.NUMERIC_PRECISION,
			B.NUMERIC_SCALE,
			B.CHARACTER_MAXIMUM_LENGTH
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
				col_type = row._mapping['TYPE_NAME'] # TypeEngine[Any] """column type represented as a :class:`.TypeEngine` instance."""

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

				kwargs = {}

				col_numeric_precision = row._mapping['NUMERIC_PRECISION']
				if col_numeric_precision:
					kwargs["precision"] = int(col_numeric_precision)

				col_numeric_scale = row._mapping['NUMERIC_SCALE']
				if col_numeric_scale:
					kwargs['scale'] = int(col_numeric_scale)

				col_character_maximum_length = row._mapping['CHARACTER_MAXIMUM_LENGTH']
				if col_character_maximum_length:
					kwargs['length'] = int(col_character_maximum_length)

				if len(kwargs) > 0:
					col_type = ischema_names[col_type](**kwargs)
				else:
					col_type = ischema_names[col_type]

				#- if issubclass(col_type, sqltypes.Numeric) == True:
				#- pass

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

#i  def get_multi_columns(
	# TODO: for better performance implement get_multi_columns. DefaultDialect's implementation is only adequate for now.

#i  def get_pk_constraint( # Return information about the primary key constraint on table_name`.
	@reflection.cache
	def get_pk_constraint(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		assert schema is not None
		cursorResult = connection.exec_driver_sql(
		f"""SELECT column_name from "INFORMATION_SCHEMA"."SYSTEM_PRIMARYKEYS"
		WHERE table_schem = '{schema}' AND table_name = '{table_name}'
		""")
		return {
			"constrained_columns": cursorResult.scalars().all()
			#"dialect_options" : NotRequired[Dict[str, Any]] # Additional dialect-specific options detected for this primary key
			}

#i  def get_multi_pk_constraint(
	# TODO: for better performance implement get_multi_pk_constraint. DefaultDialect's implementation is only adequate for now.

#i  def get_foreign_keys(	# Return information about foreign_keys in ``table_name``.
	@reflection.cache
	def get_foreign_keys(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		assert schema is not None
		reflectedForeignKeys = []
		query = f"""
			SELECT
			fk_name,
			fkcolumn_name AS constrained_columns,
			pktable_schem AS referred_schema,
			pktable_name AS referrred_table,
			pkcolumn_name AS referred_columns,
			update_rule,
			delete_rule,
			deferrability
			FROM information_schema.system_crossreference
			WHERE fktable_schem = '{schema}' AND fktable_name = '{table_name}'"""
		with connection as conn:
			cursorResult = conn.exec_driver_sql(query)
			for row in cursorResult.all():
				# Note row._mapping is using column names as keys and not the aliases defined in the query.
				fk_name = row._mapping['FK_NAME']
				constrained_columns = row._mapping['FKCOLUMN_NAME']
				referred_schema = row._mapping['PKTABLE_SCHEM']
				referrred_table = row._mapping['PKTABLE_NAME']
				referred_columns = row._mapping['PKCOLUMN_NAME']
				onupdate = row._mapping['update_rule']
				ondelete = row._mapping['delete_rule']
				deferrable = row._mapping['deferrability']
				# The values of UPDATE_RULE, DELETE_RULE, and DEFERRABILITY are all integers.
				# Somewhere as yet undiscovered, they'll probably map to FOREIGN KEY options,
				# such as [ON {DELETE | UPDATE} {CASCADE | SET DEFAULT | SET NULL}]
				# TODO: resolve FK options to strings if required for ReflectedForeignKeys.options

				# Retrieve an existing fk from the list or create a new one...
				# Note: 'name' isn't strictly a member of reflectedForeignKeys.
				#       I have added it so we can identify which rows belong to a foreign key.
				#       Information on the relationship is lost without it. Unsure how Alchemy maintains this.
				# TODO: consider dropping 'name' attributes from items in the reflectedForeignKeys list before return
				filtered = tuple(filter(lambda d: 'name' in d and d['name'] == fk_name , reflectedForeignKeys))
				if(len(filtered) > 0):
					fk = filtered[0] # fk found
				else:
					# Create a new fk dictionary.
					# TODO: consider using the default dictionary instead, provided by ReflectionDefaults.foreign_keys, as used by PG and Oracle dialects.
					fk = {
						'name': fk_name, # This isn't a member of ReflectedForeignKeys
						'constrained_columns': [],
						'referred_schema': referred_schema,
						'referrred_table': referrred_table,
						'referred_columns': [],
						'options': {
							'onupdate': onupdate,
							'ondelete': ondelete,
							'deferrable': deferrable
						}
					}
					reflectedForeignKeys.append(fk)
				fk['constrained_columns'].append(constrained_columns)
				fk['referred_columns'].append(referred_columns)
		return reflectedForeignKeys

#i  def get_multi_foreign_keys( # Return information about foreign_keys in all tables in the given ``schema``.
	# TODO: for better performance implement get_multi_foreign_keys.

#i  def get_table_names( # """Return a list of table names for ``schema``.
	@reflection.cache
	def get_table_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		with connection as conn:
			cursorResult = conn.exec_driver_sql(f"""
				SELECT table_name FROM information_schema.tables
				WHERE table_schema = '{schema}'
				AND table_type = 'BASE TABLE'
			""")
		return cursorResult.scalars().all()

#i  def get_temp_table_names( # Return a list of temporary table names on the given connection, if supported by the underlying backend.
	@reflection.cache
	def get_temp_table_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		with connection as conn:
			cursorResult = conn.exec_driver_sql(f"""
				SELECT table_name FROM information_schema.system_tables
				WHERE table_type = 'GLOBAL TEMPORARY' AND table_schem = '{schema}'
			""")
		return cursorResult.scalars().all()
	# HSQLDB supports two types of temporary table, global and local.
	# Are local temporary table names discoverable through INFORMATION_SCHEMA? It seems not.

#i  def get_view_names( # """Return a list of all non-materialized view names available in the database.
	@reflection.cache
	def get_view_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		with connection as conn:
			cursorResult = conn.exec_driver_sql(f"""
				SELECT table_name FROM information_schema.tables
				WHERE table_schema = '{schema}'
				AND table_type = 'VIEW'
			""")
		return cursorResult.scalars().all()

#i  def get_materialized_view_names( #Return a list of all materialized view names available in the database.
	def get_materialized_view_names(self, connection, schema=None, **kw):
		raise NotImplementedError()
	# According to Fred Toussi, "HSQLDB does not support materialized views directly. You can use database triggers to update tables acting as materialized views."

#i  def get_sequence_names( # Return a list of all sequence names available in the database.
	@reflection.cache
	def get_sequence_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		with connection as conn:
			cursorResult = conn.exec_driver_sql(f"""
				SELECT sequence_name FROM information_schema.sequences
				WHERE sequence_schema = '{schema}'
			""")
		return cursorResult.scalars().all()

# WIP: -->
#i  def get_temp_view_names(
#i    self, connection: Connection, schema: Optional[str] = None, **kw: Any
#i  ) -> List[str]:
#i    """Return a list of temporary view names on the given connection,
#i    if supported by the underlying backend.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_temp_view_names`.

#i    """

#i    raise NotImplementedError()

#i  def get_schema_names(self, connection: Connection, **kw: Any) -> List[str]:
#i    """Return a list of all schema names available in the database.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_schema_names`.
#i    """
#i    raise NotImplementedError()

#i  def get_view_definition(
#i    self,
#i    connection: Connection,
#i    view_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> str:
#i    """Return plain or materialized view definition.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_view_definition`.

#i    Given a :class:`_engine.Connection`, a string
#i    ``view_name``, and an optional string ``schema``, return the view
#i    definition.
#i    """

#i    raise NotImplementedError()

#i  def get_indexes(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> List[ReflectedIndex]:
#i    """Return information about indexes in ``table_name``.

#i    Given a :class:`_engine.Connection`, a string
#i    ``table_name`` and an optional string ``schema``, return index
#i    information as a list of dictionaries corresponding to the
#i    :class:`.ReflectedIndex` dictionary.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_indexes`.
#i    """

#i    raise NotImplementedError()

#i  def get_multi_indexes(
#i    self,
#i    connection: Connection,
#i    schema: Optional[str] = None,
#i    filter_names: Optional[Collection[str]] = None,
#i    **kw: Any,
#i  ) -> Iterable[Tuple[TableKey, List[ReflectedIndex]]]:
#i    """Return information about indexes in in all tables
#i    in the given ``schema``.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_multi_indexes`.

#i    .. note:: The :class:`_engine.DefaultDialect` provides a default
#i    implementation that will call the single table method for
#i    each object returned by :meth:`Dialect.get_table_names`,
#i    :meth:`Dialect.get_view_names` or
#i    :meth:`Dialect.get_materialized_view_names` depending on the
#i    provided ``kind``. Dialects that want to support a faster
#i    implementation should implement this method.

#i    .. versionadded:: 2.0

#i    """

#i    raise NotImplementedError()

#i  def get_unique_constraints(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> List[ReflectedUniqueConstraint]:
#i    r"""Return information about unique constraints in ``table_name``.

#i    Given a string ``table_name`` and an optional string ``schema``, return
#i    unique constraint information as a list of dicts corresponding
#i    to the :class:`.ReflectedUniqueConstraint` dictionary.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_unique_constraints`.
#i    """

#i    raise NotImplementedError()

#i  def get_multi_unique_constraints(
#i    self,
#i    connection: Connection,
#i    schema: Optional[str] = None,
#i    filter_names: Optional[Collection[str]] = None,
#i    **kw: Any,
#i  ) -> Iterable[Tuple[TableKey, List[ReflectedUniqueConstraint]]]:
#i    """Return information about unique constraints in all tables
#i    in the given ``schema``.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_multi_unique_constraints`.

#i    .. note:: The :class:`_engine.DefaultDialect` provides a default
#i    implementation that will call the single table method for
#i    each object returned by :meth:`Dialect.get_table_names`,
#i    :meth:`Dialect.get_view_names` or
#i    :meth:`Dialect.get_materialized_view_names` depending on the
#i    provided ``kind``. Dialects that want to support a faster
#i    implementation should implement this method.

#i    .. versionadded:: 2.0

#i    """

#i    raise NotImplementedError()

#i  def get_check_constraints(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> List[ReflectedCheckConstraint]:
#i    r"""Return information about check constraints in ``table_name``.

#i    Given a string ``table_name`` and an optional string ``schema``, return
#i    check constraint information as a list of dicts corresponding
#i    to the :class:`.ReflectedCheckConstraint` dictionary.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_check_constraints`.

#i    """

#i    raise NotImplementedError()

#i  def get_multi_check_constraints(
#i    self,
#i    connection: Connection,
#i    schema: Optional[str] = None,
#i    filter_names: Optional[Collection[str]] = None,
#i    **kw: Any,
#i  ) -> Iterable[Tuple[TableKey, List[ReflectedCheckConstraint]]]:
#i    """Return information about check constraints in all tables
#i    in the given ``schema``.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_multi_check_constraints`.

#i    .. note:: The :class:`_engine.DefaultDialect` provides a default
#i    implementation that will call the single table method for
#i    each object returned by :meth:`Dialect.get_table_names`,
#i    :meth:`Dialect.get_view_names` or
#i    :meth:`Dialect.get_materialized_view_names` depending on the
#i    provided ``kind``. Dialects that want to support a faster
#i    implementation should implement this method.

#i    .. versionadded:: 2.0

#i    """

#i    raise NotImplementedError()

#i  def get_table_options(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> Dict[str, Any]:
#i    """Return a dictionary of options specified when ``table_name``
#i    was created.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_table_options`.
#i    """
#i    raise NotImplementedError()

#i  def get_multi_table_options(
#i    self,
#i    connection: Connection,
#i    schema: Optional[str] = None,
#i    filter_names: Optional[Collection[str]] = None,
#i    **kw: Any,
#i  ) -> Iterable[Tuple[TableKey, Dict[str, Any]]]:
#i    """Return a dictionary of options specified when the tables in the
#i    given schema were created.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_multi_table_options`.

#i    .. note:: The :class:`_engine.DefaultDialect` provides a default
#i    implementation that will call the single table method for
#i    each object returned by :meth:`Dialect.get_table_names`,
#i    :meth:`Dialect.get_view_names` or
#i    :meth:`Dialect.get_materialized_view_names` depending on the
#i    provided ``kind``. Dialects that want to support a faster
#i    implementation should implement this method.

#i    .. versionadded:: 2.0

#i    """
#i    raise NotImplementedError()

#i  def get_table_comment(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> ReflectedTableComment:
#i    r"""Return the "comment" for the table identified by ``table_name``.

#i    Given a string ``table_name`` and an optional string ``schema``, return
#i    table comment information as a dictionary corresponding to the
#i    :class:`.ReflectedTableComment` dictionary.

#i    This is an internal dialect method. Applications should use
#i    :meth:`.Inspector.get_table_comment`.

#i    :raise: ``NotImplementedError`` for dialects that don't support
#i    comments.

#i    .. versionadded:: 1.2

#i    """

#i    raise NotImplementedError()

#i  def get_multi_table_comment(
#i    self,
#i    connection: Connection,
#i    schema: Optional[str] = None,
#i    filter_names: Optional[Collection[str]] = None,
#i    **kw: Any,
#i  ) -> Iterable[Tuple[TableKey, ReflectedTableComment]]:
#i    """Return information about the table comment in all tables
#i    in the given ``schema``.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.get_multi_table_comment`.

#i    .. note:: The :class:`_engine.DefaultDialect` provides a default
#i    implementation that will call the single table method for
#i    each object returned by :meth:`Dialect.get_table_names`,
#i    :meth:`Dialect.get_view_names` or
#i    :meth:`Dialect.get_materialized_view_names` depending on the
#i    provided ``kind``. Dialects that want to support a faster
#i    implementation should implement this method.

#i    .. versionadded:: 2.0

#i    """

#i    raise NotImplementedError()

#i  def normalize_name(self, name: str) -> str:
#i    """convert the given name to lowercase if it is detected as
#i    case insensitive.

#i    This method is only used if the dialect defines
#i    requires_name_normalize=True.

#i    """
#i    raise NotImplementedError()

#i  def denormalize_name(self, name: str) -> str:
#i    """convert the given name to a case insensitive identifier
#i    for the backend if it is an all-lowercase name.

#i    This method is only used if the dialect defines
#i    requires_name_normalize=True.

#i    """
#i    raise NotImplementedError()

#i  def has_table(
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





#i  def has_index(
#i    self,
#i    connection: Connection,
#i    table_name: str,
#i    index_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> bool:
#i    """Check the existence of a particular index name in the database.

#i    Given a :class:`_engine.Connection` object, a string
#i    ``table_name`` and string index name, return ``True`` if an index of
#i    the given name on the given table exists, ``False`` otherwise.

#i    The :class:`.DefaultDialect` implements this in terms of the
#i    :meth:`.Dialect.has_table` and :meth:`.Dialect.get_indexes` methods,
#i    however dialects can implement a more performant version.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.has_index`.

#i    .. versionadded:: 1.4

#i    """

#i    raise NotImplementedError()

#i  def has_sequence(
#i    self,
#i    connection: Connection,
#i    sequence_name: str,
#i    schema: Optional[str] = None,
#i    **kw: Any,
#i  ) -> bool:
#i    """Check the existence of a particular sequence in the database.

#i    Given a :class:`_engine.Connection` object and a string
#i    `sequence_name`, return ``True`` if the given sequence exists in
#i    the database, ``False`` otherwise.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.has_sequence`.
#i    """

#i    raise NotImplementedError()

#i  def has_schema(
#i    self, connection: Connection, schema_name: str, **kw: Any
#i  ) -> bool:
#i    """Check the existence of a particular schema name in the database.

#i    Given a :class:`_engine.Connection` object, a string
#i    ``schema_name``, return ``True`` if a schema of the
#i    given exists, ``False`` otherwise.

#i    The :class:`.DefaultDialect` implements this by checking
#i    the presence of ``schema_name`` among the schemas returned by
#i    :meth:`.Dialect.get_schema_names`,
#i    however dialects can implement a more performant version.

#i    This is an internal dialect method. Applications should use
#i    :meth:`_engine.Inspector.has_schema`.

#i    .. versionadded:: 2.0

#i    """

#i    raise NotImplementedError()

#i  def _get_server_version_info(self, connection: Connection) -> Any:
#i    """Retrieve the server version info from the given connection.

#i    This is used by the default implementation to populate the
#i    "server_version_info" attribute and is called exactly
#i    once upon first connect.

#i    """

#i    raise NotImplementedError()

#i  def _get_default_schema_name(self, connection: Connection) -> str:
	def _get_default_schema_name(self, connection):
		return connection.exec_driver_sql("VALUES(CURRENT_SCHEMA)").scalar()
#i    """Return the string name of the currently selected schema from
#i    the given connection.

#i    This is used by the default implementation to populate the
#i    "default_schema_name" attribute and is called exactly
#i    once upon first connect.

#i    """

#i    raise NotImplementedError()

#i  def do_begin(self, dbapi_connection: PoolProxiedConnection) -> None:
#i    """Provide an implementation of ``connection.begin()``, given a
#i    DB-API connection.

#i    The DBAPI has no dedicated "begin" method and it is expected
#i    that transactions are implicit.  This hook is provided for those
#i    DBAPIs that might need additional help in this area.

#i    :param dbapi_connection: a DBAPI connection, typically
#i    proxied within a :class:`.ConnectionFairy`.

#i    """

#i    raise NotImplementedError()

#i  def do_rollback(self, dbapi_connection: PoolProxiedConnection) -> None:
#i    """Provide an implementation of ``connection.rollback()``, given
#i    a DB-API connection.

#i    :param dbapi_connection: a DBAPI connection, typically
#i    proxied within a :class:`.ConnectionFairy`.

#i    """

#i    raise NotImplementedError()

#i  def do_commit(self, dbapi_connection: PoolProxiedConnection) -> None:
#i    """Provide an implementation of ``connection.commit()``, given a
#i    DB-API connection.

#i    :param dbapi_connection: a DBAPI connection, typically
#i    proxied within a :class:`.ConnectionFairy`.

#i    """

#i    raise NotImplementedError()

#i  def do_terminate(self, dbapi_connection: DBAPIConnection) -> None:
#i    """Provide an implementation of ``connection.close()`` that tries as
#i    much as possible to not block, given a DBAPI
#i    connection.

#i    In the vast majority of cases this just calls .close(), however
#i    for some asyncio dialects may call upon different API features.

#i    This hook is called by the :class:`_pool.Pool`
#i    when a connection is being recycled or has been invalidated.

#i    .. versionadded:: 1.4.41

#i    """

#i    raise NotImplementedError()

#i  def do_close(self, dbapi_connection: DBAPIConnection) -> None:
#i    """Provide an implementation of ``connection.close()``, given a DBAPI
#i    connection.

#i    This hook is called by the :class:`_pool.Pool`
#i    when a connection has been
#i    detached from the pool, or is being returned beyond the normal
#i    capacity of the pool.

#i    """

#i    raise NotImplementedError()

#i  def _do_ping_w_event(self, dbapi_connection: DBAPIConnection) -> bool:
#i    raise NotImplementedError()

#i  def do_ping(self, dbapi_connection: DBAPIConnection) -> bool:
#i    """ping the DBAPI connection and return True if the connection is
#i    usable."""
#i    raise NotImplementedError()

#i  def do_set_input_sizes(
#i    self,
#i    cursor: DBAPICursor,
#i    list_of_tuples: _GenericSetInputSizesType,
#i    context: ExecutionContext,
#i  ) -> Any:
#i    """invoke the cursor.setinputsizes() method with appropriate arguments

#i    This hook is called if the :attr:`.Dialect.bind_typing` attribute is
#i    set to the
#i    :attr:`.BindTyping.SETINPUTSIZES` value.
#i    Parameter data is passed in a list of tuples (paramname, dbtype,
#i    sqltype), where ``paramname`` is the key of the parameter in the
#i    statement, ``dbtype`` is the DBAPI datatype and ``sqltype`` is the
#i    SQLAlchemy type. The order of tuples is in the correct parameter order.

#i    .. versionadded:: 1.4

#i    .. versionchanged:: 2.0  - setinputsizes mode is now enabled by
#i    setting :attr:`.Dialect.bind_typing` to
#i    :attr:`.BindTyping.SETINPUTSIZES`.  Dialects which accept
#i    a ``use_setinputsizes`` parameter should set this value
#i    appropriately.


#i    """
#i    raise NotImplementedError()

#i  def create_xid(self) -> Any:
#i    """Create a two-phase transaction ID.

#i    This id will be passed to do_begin_twophase(),
#i    do_rollback_twophase(), do_commit_twophase().  Its format is
#i    unspecified.
#i    """

#i    raise NotImplementedError()

#i  def do_savepoint(self, connection: Connection, name: str) -> None:
#i    """Create a savepoint with the given name.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param name: savepoint name.

#i    """

#i    raise NotImplementedError()

#i  def do_rollback_to_savepoint(
#i    self, connection: Connection, name: str
#i  ) -> None:
#i    """Rollback a connection to the named savepoint.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param name: savepoint name.

#i    """

#i    raise NotImplementedError()

#i  def do_release_savepoint(self, connection: Connection, name: str) -> None:
#i    """Release the named savepoint on a connection.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param name: savepoint name.
#i    """

#i    raise NotImplementedError()

#i  def do_begin_twophase(self, connection: Connection, xid: Any) -> None:
#i    """Begin a two phase transaction on the given connection.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param xid: xid

#i    """

#i    raise NotImplementedError()

#i  def do_prepare_twophase(self, connection: Connection, xid: Any) -> None:
#i    """Prepare a two phase transaction on the given connection.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param xid: xid

#i    """

#i    raise NotImplementedError()

#i  def do_rollback_twophase(
#i    self,
#i    connection: Connection,
#i    xid: Any,
#i    is_prepared: bool = True,
#i    recover: bool = False,
#i  ) -> None:
#i    """Rollback a two phase transaction on the given connection.

#i    :param connection: a :class:`_engine.Connection`.
#i    :param xid: xid
#i    :param is_prepared: whether or not
#i    :meth:`.TwoPhaseTransaction.prepare` was called.
#i    :param recover: if the recover flag was passed.

#i    """

#i    raise NotImplementedError()

#i  def do_commit_twophase(
#i    self,
#i    connection: Connection,
#i    xid: Any,
#i    is_prepared: bool = True,
#i    recover: bool = False,
#i  ) -> None:
#i    """Commit a two phase transaction on the given connection.


#i    :param connection: a :class:`_engine.Connection`.
#i    :param xid: xid
#i    :param is_prepared: whether or not
#i    :meth:`.TwoPhaseTransaction.prepare` was called.
#i    :param recover: if the recover flag was passed.

#i    """

#i    raise NotImplementedError()

#i  def do_recover_twophase(self, connection: Connection) -> List[Any]:
#i    """Recover list of uncommitted prepared two phase transaction
#i    identifiers on the given connection.

#i    :param connection: a :class:`_engine.Connection`.

#i    """

#i    raise NotImplementedError()

#i  def _deliver_insertmanyvalues_batches(
#i    self,
#i    cursor: DBAPICursor,
#i    statement: str,
#i    parameters: _DBAPIMultiExecuteParams,
#i    generic_setinputsizes: Optional[_GenericSetInputSizesType],
#i    context: ExecutionContext,
#i  ) -> Iterator[_InsertManyValuesBatch]:
#i    """convert executemany parameters for an INSERT into an iterator
#i    of statement/single execute values, used by the insertmanyvalues
#i    feature.

#i    """
#i    raise NotImplementedError()

#i  def do_executemany(
#i    self,
#i    cursor: DBAPICursor,
#i    statement: str,
#i    parameters: _DBAPIMultiExecuteParams,
#i    context: Optional[ExecutionContext] = None,
#i  ) -> None:
#i    """Provide an implementation of ``cursor.executemany(statement,
#i    parameters)``."""

#i    raise NotImplementedError()

#i  def do_execute(
#i    self,
#i    cursor: DBAPICursor,
#i    statement: str,
#i    parameters: Optional[_DBAPISingleExecuteParams],
#i    context: Optional[ExecutionContext] = None,
#i  ) -> None:
#i    """Provide an implementation of ``cursor.execute(statement,
#i    parameters)``."""

#i    raise NotImplementedError()

#i  def do_execute_no_params(
#i    self,
#i    cursor: DBAPICursor,
#i    statement: str,
#i    context: Optional[ExecutionContext] = None,
#i  ) -> None:
#i    """Provide an implementation of ``cursor.execute(statement)``.

#i    The parameter collection should not be sent.

#i    """

#i    raise NotImplementedError()

#i  def is_disconnect(
#i    self,
#i    e: Exception,
#i    connection: Optional[Union[PoolProxiedConnection, DBAPIConnection]],
#i    cursor: Optional[DBAPICursor],
#i  ) -> bool:
#i    """Return True if the given DB-API error indicates an invalid
#i    connection"""

#i    raise NotImplementedError()

#i  def connect(self, *cargs: Any, **cparams: Any) -> DBAPIConnection:
#i    r"""Establish a connection using this dialect's DBAPI.

#i    The default implementation of this method is::

#i      def connect(self, *cargs, **cparams):
#i        return self.dbapi.connect(*cargs, **cparams)

#i    The ``*cargs, **cparams`` parameters are generated directly
#i    from this dialect's :meth:`.Dialect.create_connect_args` method.

#i    This method may be used for dialects that need to perform programmatic
#i    per-connection steps when a new connection is procured from the
#i    DBAPI.


#i    :param \*cargs: positional parameters returned from the
#i    :meth:`.Dialect.create_connect_args` method

#i    :param \*\*cparams: keyword parameters returned from the
#i    :meth:`.Dialect.create_connect_args` method.

#i    :return: a DBAPI connection, typically from the :pep:`249` module
#i    level ``.connect()`` function.

#i    .. seealso::

#i      :meth:`.Dialect.create_connect_args`

#i      :meth:`.Dialect.on_connect`

#i    """
#i    raise NotImplementedError()

#i  def on_connect_url(self, url: URL) -> Optional[Callable[[Any], Any]]:
#i    """return a callable which sets up a newly created DBAPI connection.

#i    This method is a new hook that supersedes the
#i    :meth:`_engine.Dialect.on_connect` method when implemented by a
#i    dialect.   When not implemented by a dialect, it invokes the
#i    :meth:`_engine.Dialect.on_connect` method directly to maintain
#i    compatibility with existing dialects.   There is no deprecation
#i    for :meth:`_engine.Dialect.on_connect` expected.

#i    The callable should accept a single argument "conn" which is the
#i    DBAPI connection itself.  The inner callable has no
#i    return value.

#i    E.g.::

#i      class MyDialect(default.DefaultDialect):
#i        # ...

#i        def on_connect_url(self, url):
#i          def do_on_connect(connection):
#i            connection.execute("SET SPECIAL FLAGS etc")

#i          return do_on_connect

#i    This is used to set dialect-wide per-connection options such as
#i    isolation modes, Unicode modes, etc.

#i    This method differs from :meth:`_engine.Dialect.on_connect` in that
#i    it is passed the :class:`_engine.URL` object that's relevant to the
#i    connect args.  Normally the only way to get this is from the
#i    :meth:`_engine.Dialect.on_connect` hook is to look on the
#i    :class:`_engine.Engine` itself, however this URL object may have been
#i    replaced by plugins.

#i    .. note::

#i      The default implementation of
#i      :meth:`_engine.Dialect.on_connect_url` is to invoke the
#i      :meth:`_engine.Dialect.on_connect` method. Therefore if a dialect
#i      implements this method, the :meth:`_engine.Dialect.on_connect`
#i      method **will not be called** unless the overriding dialect calls
#i      it directly from here.

#i    .. versionadded:: 1.4.3 added :meth:`_engine.Dialect.on_connect_url`
#i    which normally calls into :meth:`_engine.Dialect.on_connect`.

#i    :param url: a :class:`_engine.URL` object representing the
#i    :class:`_engine.URL` that was passed to the
#i    :meth:`_engine.Dialect.create_connect_args` method.

#i    :return: a callable that accepts a single DBAPI connection as an
#i    argument, or None.

#i    .. seealso::

#i      :meth:`_engine.Dialect.on_connect`

#i    """
#i    return self.on_connect()

#i  def on_connect(self) -> Optional[Callable[[Any], Any]]:
#i    """return a callable which sets up a newly created DBAPI connection.

#i    The callable should accept a single argument "conn" which is the
#i    DBAPI connection itself.  The inner callable has no
#i    return value.

#i    E.g.::

#i      class MyDialect(default.DefaultDialect):
#i        # ...

#i        def on_connect(self):
#i          def do_on_connect(connection):
#i            connection.execute("SET SPECIAL FLAGS etc")

#i          return do_on_connect

#i    This is used to set dialect-wide per-connection options such as
#i    isolation modes, Unicode modes, etc.

#i    The "do_on_connect" callable is invoked by using the
#i    :meth:`_events.PoolEvents.connect` event
#i    hook, then unwrapping the DBAPI connection and passing it into the
#i    callable.

#i    .. versionchanged:: 1.4 the on_connect hook is no longer called twice
#i    for the first connection of a dialect.  The on_connect hook is still
#i    called before the :meth:`_engine.Dialect.initialize` method however.

#i    .. versionchanged:: 1.4.3 the on_connect hook is invoked from a new
#i    method on_connect_url that passes the URL that was used to create
#i    the connect args.   Dialects can implement on_connect_url instead
#i    of on_connect if they need the URL object that was used for the
#i    connection in order to get additional context.

#i    If None is returned, no event listener is generated.

#i    :return: a callable that accepts a single DBAPI connection as an
#i    argument, or None.

#i    .. seealso::

#i      :meth:`.Dialect.connect` - allows the DBAPI ``connect()`` sequence
#i      itself to be controlled.

#i      :meth:`.Dialect.on_connect_url` - supersedes
#i      :meth:`.Dialect.on_connect` to also receive the
#i      :class:`_engine.URL` object in context.

#i    """
#i    return None

#i  def reset_isolation_level(self, dbapi_connection: DBAPIConnection) -> None:
#i    """Given a DBAPI connection, revert its isolation to the default.

#i    Note that this is a dialect-level method which is used as part
#i    of the implementation of the :class:`_engine.Connection` and
#i    :class:`_engine.Engine`
#i    isolation level facilities; these APIs should be preferred for
#i    most typical use cases.

#i    .. seealso::

#i      :meth:`_engine.Connection.get_isolation_level`
#i      - view current level

#i      :attr:`_engine.Connection.default_isolation_level`
#i      - view default level

#i      :paramref:`.Connection.execution_options.isolation_level` -
#i      set per :class:`_engine.Connection` isolation level

#i      :paramref:`_sa.create_engine.isolation_level` -
#i      set per :class:`_engine.Engine` isolation level

#i    """

#i    raise NotImplementedError()

#i  def set_isolation_level(
#i    self, dbapi_connection: DBAPIConnection, level: IsolationLevel
#i  ) -> None:
#i    """Given a DBAPI connection, set its isolation level.

#i    Note that this is a dialect-level method which is used as part
#i    of the implementation of the :class:`_engine.Connection` and
#i    :class:`_engine.Engine`
#i    isolation level facilities; these APIs should be preferred for
#i    most typical use cases.

#i    If the dialect also implements the
#i    :meth:`.Dialect.get_isolation_level_values` method, then the given
#i    level is guaranteed to be one of the string names within that sequence,
#i    and the method will not need to anticipate a lookup failure.

#i    .. seealso::

#i      :meth:`_engine.Connection.get_isolation_level`
#i      - view current level

#i      :attr:`_engine.Connection.default_isolation_level`
#i      - view default level

#i      :paramref:`.Connection.execution_options.isolation_level` -
#i      set per :class:`_engine.Connection` isolation level

#i      :paramref:`_sa.create_engine.isolation_level` -
#i      set per :class:`_engine.Engine` isolation level

#i    """

#i    raise NotImplementedError()
	def set_isolation_level(self, dbapi_connection, level):
		cursor = dbapi_connection.cursor()
		cursor.execute(f"SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL {level}")
		cursor.execute("COMMIT")
		cursor.close()

#i  def get_isolation_level(
#i    self, dbapi_connection: DBAPIConnection
#i  ) -> IsolationLevel:
#i    """Given a DBAPI connection, return its isolation level.

#i    When working with a :class:`_engine.Connection` object,
#i    the corresponding
#i    DBAPI connection may be procured using the
#i    :attr:`_engine.Connection.connection` accessor.

#i    Note that this is a dialect-level method which is used as part
#i    of the implementation of the :class:`_engine.Connection` and
#i    :class:`_engine.Engine` isolation level facilities;
#i    these APIs should be preferred for most typical use cases.


#i    .. seealso::

#i      :meth:`_engine.Connection.get_isolation_level`
#i      - view current level

#i      :attr:`_engine.Connection.default_isolation_level`
#i      - view default level

#i      :paramref:`.Connection.execution_options.isolation_level` -
#i      set per :class:`_engine.Connection` isolation level

#i      :paramref:`_sa.create_engine.isolation_level` -
#i      set per :class:`_engine.Engine` isolation level


#i    """

#i    raise NotImplementedError()
	def get_isolation_level(self, dbapi_connection):
		cursor = dbapi_connection.cursor()
		cursor.execute("CALL SESSION_ISOLATION_LEVEL()")
		val = cursor.fetchone()[0]
		cursor.close()
		return val.upper()



#i  def get_default_isolation_level(
#i    self, dbapi_conn: DBAPIConnection
#i  ) -> IsolationLevel:
#i    """Given a DBAPI connection, return its isolation level, or
#i    a default isolation level if one cannot be retrieved.

#i    This method may only raise NotImplementedError and
#i    **must not raise any other exception**, as it is used implicitly upon
#i    first connect.

#i    The method **must return a value** for a dialect that supports
#i    isolation level settings, as this level is what will be reverted
#i    towards when a per-connection isolation level change is made.

#i    The method defaults to using the :meth:`.Dialect.get_isolation_level`
#i    method unless overridden by a dialect.

#i    .. versionadded:: 1.3.22

#i    """
#i    raise NotImplementedError()

	# Isolation level functions
	# HSQLDB supported isolation levels are documented here - https://hsqldb.org/doc/2.0/guide/sessions-chapt.html
	# Documentation for members of the Dialect interface can be found here - \sqlalchemy\engine\interfaces.py
	# TODO: Reorder the position of member to match interface.py

#i  def get_isolation_level_values(
	def get_isolation_level_values(self, dbapi_conn):
		return (
			"SERIALIZABLE",
			"READ UNCOMMITTED",
			"READ COMMITTED",
			"REPEATABLE READ",
			"AUTOCOMMIT"
		)
	#- Documented in \sqlalchemy\engine\interfaces.py, line 2495



#i  def _assert_and_set_isolation_level(
#i    self, dbapi_conn: DBAPIConnection, level: IsolationLevel
#i  ) -> None:
#i    raise NotImplementedError()

#i  def get_dialect_cls(cls, url: URL) -> Type[Dialect]:
#i    """Given a URL, return the :class:`.Dialect` that will be used.

#i    This is a hook that allows an external plugin to provide functionality
#i    around an existing dialect, by allowing the plugin to be loaded
#i    from the url based on an entrypoint, and then the plugin returns
#i    the actual dialect to be used.

#i    By default this just returns the cls.

#i    """
#i    return cls

#i  def get_async_dialect_cls(cls, url: URL) -> Type[Dialect]:
#i    """Given a URL, return the :class:`.Dialect` that will be used by
#i    an async engine.

#i    By default this is an alias of :meth:`.Dialect.get_dialect_cls` and
#i    just returns the cls. It may be used if a dialect provides
#i    both a sync and async version under the same name, like the
#i    ``psycopg`` driver.

#i    .. versionadded:: 2

#i    .. seealso::

#i      :meth:`.Dialect.get_dialect_cls`

#i    """
#i    return cls.get_dialect_cls(url)

#i  def load_provisioning(cls) -> None:
#i    """set up the provision.py module for this dialect.

#i    For dialects that include a provision.py module that sets up
#i    provisioning followers, this method should initiate that process.

#i    A typical implementation would be::

#i      @classmethod
#i      def load_provisioning(cls):
#i        __import__("mydialect.provision")

#i    The default method assumes a module named ``provision.py`` inside
#i    the owning package of the current dialect, based on the ``__module__``
#i    attribute::

#i      @classmethod
#i      def load_provisioning(cls):
#i        package = ".".join(cls.__module__.split(".")[0:-1])
#i        try:
#i          __import__(package + ".provision")
#i        except ImportError:
#i          pass

#i    .. versionadded:: 1.3.14

#i    """

#i  def engine_created(cls, engine: Engine) -> None:
#i    """A convenience hook called before returning the final
#i    :class:`_engine.Engine`.

#i    If the dialect returned a different class from the
#i    :meth:`.get_dialect_cls`
#i    method, then the hook is called on both classes, first on
#i    the dialect class returned by the :meth:`.get_dialect_cls` method and
#i    then on the class on which the method was called.

#i    The hook should be used by dialects and/or wrappers to apply special
#i    events to the engine or its components.   In particular, it allows
#i    a dialect-wrapping class to apply dialect-level events.

#i    """

#i  def get_driver_connection(self, connection: DBAPIConnection) -> Any:
#i    """Returns the connection object as returned by the external driver
#i    package.

#i    For normal dialects that use a DBAPI compliant driver this call
#i    will just return the ``connection`` passed as argument.
#i    For dialects that instead adapt a non DBAPI compliant driver, like
#i    when adapting an asyncio driver, this call will return the
#i    connection-like object as returned by the driver.

#i    .. versionadded:: 1.4.24

#i    """
#i    raise NotImplementedError()

#i  def set_engine_execution_options(
#i    self, engine: Engine, opts: CoreExecuteOptionsParameter
#i  ) -> None:
#i    """Establish execution options for a given engine.

#i    This is implemented by :class:`.DefaultDialect` to establish
#i    event hooks for new :class:`.Connection` instances created
#i    by the given :class:`.Engine` which will then invoke the
#i    :meth:`.Dialect.set_connection_execution_options` method for that
#i    connection.

#i    """
#i    raise NotImplementedError()

#i  def set_connection_execution_options(
#i    self, connection: Connection, opts: CoreExecuteOptionsParameter
#i  ) -> None:
#i    """Establish execution options for a given connection.

#i    This is implemented by :class:`.DefaultDialect` in order to implement
#i    the :paramref:`_engine.Connection.execution_options.isolation_level`
#i    execution option.  Dialects can intercept various execution options
#i    which may need to modify state on a particular DBAPI connection.

#i    .. versionadded:: 1.4

#i    """
#i    raise NotImplementedError()

#i  def get_dialect_pool_class(self, url: URL) -> Type[Pool]:
#i    """return a Pool class to use for a given URL"""
#i    raise NotImplementedError()
















	# Set 'supports_schemas' to false to disable schema-level tests
	supports_schemas = False
	# TODO: try setting to True (or removing) when we're ready for testing. Only the Access dialect appears to set it to false. Does it take too long to test?
	# TODO: find out where the above property is from - it's not part of the Dialect interface.

	#- ok
	supports_is_distinct_from = True
	# Supported since HSQLDB v2.0
	#- Default is True. Access's dialect is set to False.
	#-
	#- e.g. SELECT * FROM mytable WHERE col1 IS DISTINCT FROM col2;
	#- So you can use expressions like col1.is_distinct_from(col2) in SQLAlchemy when using the HSQLDB dialect.
	# TODO: find out where the above property is from - it's not part of the Dialect interface.

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
	# TODO: find out where the above property is from - it's not part of the Dialect interface.
	#
	# TODO: See if QueuePool works, or use StaticPool instead.

	default_paramstyle = "qmark"
	# TODO: verify the recently added setting above is required, and works as expected.
	# TODO: find out where the above property is from - it's not part of the Dialect interface.



"""
	# @reflection.cache
	# def get_check_constraints(self, connection, table_name, schema=None, **kw):
	# 	# Does this actually need implementing, and does it belong to this class?
	# 	raise NotImplementedError()

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
"""

