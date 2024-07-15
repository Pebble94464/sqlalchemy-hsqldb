
r"""

TODO: like pg, hsqldb implicitly creates unique constraints. Document it here, similar to pg's below...
.. _postgresql_index_reflection:

#- line 1074
PostgreSQL Index Reflection
---------------------------

The PostgreSQL database creates a UNIQUE INDEX implicitly whenever the
UNIQUE CONSTRAINT construct is used.   When inspecting a table using
:class:`_reflection.Inspector`, the :meth:`_reflection.Inspector.get_indexes`
and the :meth:`_reflection.Inspector.get_unique_constraints`
will report on these
two constructs distinctly; in the case of the index, the key
``duplicates_constraint`` will be present in the index entry if it is
detected as mirroring a constraint.   When performing reflection using
``Table(..., autoload_with=engine)``, the UNIQUE INDEX is **not** returned
in :attr:`_schema.Table.indexes` when it is detected as mirroring a
:class:`.UniqueConstraint` in the :attr:`_schema.Table.constraints` collection
.

TODO: table options, like postgre...

#- line 1109
PostgreSQL Table Options
------------------------

Several options for CREATE TABLE are supported directly by the PostgreSQL
dialect in conjunction with the :class:`_schema.Table` construct:

* ``ON COMMIT``::

    Table("some_table", metadata, ..., postgresql_on_commit='PRESERVE ROWS')





"""



# "base.py defines the specific SQL dialect used by that database"
# [New Dialect System](https://docs.sqlalchemy.org/en/20/changelog/migration_06.html)

# TODO: delete all lines begining with '#i'. They're just copied in from interfaces.py to make sure we haven't forgotten anything.
# TODO: Implement support for specifying catalog and schema in Dialect methods if possible. DefaultDialect supports schema only.
# TODO: Ensure joins occur on the correct schema and catalog.
# TODO: Ensure all methods raise an error when expected row(s) are missing.
# TODO: prefer org.hsqldb.jdbc.JDBCConnection methods over executing SQL strings. Rewrite functions as necessary.
# TODO: prefer JayDeBeApi Connection methods over JDBCConnection methods
# TODO: Ensure dialect methods aren't prematurely closing connections.
# TODO: Dialect specific documentation, along the lines of those found at https://docs.sqlalchemy.org/en/20/dialects/
# TODO: Estimate project completion and maintenance costs. Include a count of TODOs.

import pdb

#from jpype.dbapi2 import Date as
#-import jpype # 
from jpype import JClass
import jpype.dbapi2 as jdbapi
import datetime
dt = datetime # An alias for datetime. TODO: import datetime as dt
# 

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
from sqlalchemy import exc
from sqlalchemy.schema import UniqueConstraint

from sqlalchemy import schema
from sqlalchemy.ext.compiler import compiles


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

def _getDictFromList(key, val, theList):
	"""Returns the first dictionary with a matching key value or None."""
	for dict in theList:
		item = dict.get(key)
		if item == val:
			return dict
	return None
	# TODO: update code to use this method, if it's quicker than the filter method.

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

	#- TODO: remove Oracle function below...
	def get_dbapi_type_oracle(self, dbapi):
		return dbapi.NUMBER

class TIMESTAMP(sqltypes.TIMESTAMP):
	__visit_name__ = 'TIMESTAMP'

	def __init__(self, timezone: bool = False, precision: Optional[int] = None):
		"""
		Construct a new :class:`_hsqldb.TIMESTAMP`.
		:param timezone: boolean.  Indicates that the TIMESTAMP type should
		use HyperSQL's ``TIMESTAMP WITH TIME ZONE`` datatype.
		"""
		# TODO: update description above
		print('### hsqldb TIMESTAMP constructor') #-
		super().__init__(timezone=timezone)
	# TODO: implement support for 'precision'. Defaults to 6 for timestamps.
	#- Note that none of the other dialects define a bind or results processor for TIMESTAMP.

	def bind_processor(self, dialect):
		#- used when sending data to the db.
		print('### hsqldb TIMESTAMP bind_processor') #-

		if self.timezone == False:
			return self._bind_processor_timestamp
		else:
			return self._bind_processor_offsetdatetime

	def _bind_processor_timestamp(self, value):
		if type(value) != datetime.datetime:
			return None
		year = value.year - 1900
		month = value.month - 1
		day = value.day
		hour = value.hour
		minute = value.minute
		second = value.second
		nano = value.microsecond * 1000
		JTimestamp = JClass('java.sql.Timestamp', False)
		return JTimestamp(year, month, day, hour, minute, second, nano)

	def _bind_processor_offsetdatetime(self, value):
		if type(value) != datetime.datetime:
			return None
		year = value.year
		month = value.month
		day = value.day
		hour = value.hour
		minute = value.minute
		second = value.second
		nano = value.microsecond * 1000
		timedelta = value.tzinfo.utcoffset(None)
		JOffsetDateTime = JClass('java.time.OffsetDateTime', False)
		#- https://docs.oracle.com/javase/8/docs/api/java/time/OffsetDateTime.html
		JZoneOffset = JClass('java.time.ZoneOffset')
		#- https://docs.oracle.com/javase/8/docs/api/java/time/ZoneOffset.html
		return JOffsetDateTime.of(year, month, day, hour, minute, second, nano, JZoneOffset.ofTotalSeconds(timedelta.seconds))

	def result_processor(self, dialect, coltype):
		#- used when retrieving data from the db
		print('### TIMESTAMP result_processor') #-

		if 'TIMESTAMP_WITH_TIMEZONE' in coltype.values:
			# <java class 'java.time.OffsetDateTime'>
			# TODO:3: Can we compare using the type's numerical value (2014) instead of its string?
			return self._java_time_offsetdatetime_TO_datetime
		else:
			# <java class 'java.sql.Timestamp'>
			return self._java_sql_datetime_TO_datetime

	def _java_time_offsetdatetime_TO_datetime(self, value):
		"""Convert java.time.OffsetDateTime to datetime.datetime"""
		print('### _java_time_offsetdatetime_TO_datetime') #-
		year = value.getYear()
		month = value.getMonthValue()
		day = value.getDayOfMonth()
		hour = value.getHour()
		minute = value.getMinute()
		second = value.getSecond()
		microsecond = int(value.getNano() / 1000)
		zone_offset = value.getOffset() # <java class 'java.time.ZoneOffset'>
		offset_seconds = zone_offset.getTotalSeconds()
		tzinfo1 = dt.timezone(dt.timedelta(seconds=offset_seconds))
		return dt.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo1)
	# TODO: This conversion function is fairly generic. Consider making it global instead of a class member function. Is it used elsewhere?

	def _java_sql_datetime_TO_datetime(self, value):
		"""Convert java.sql.datetime to datetime.datetime"""
		print('### _java_sql_datetime_TO_datetime') #-
		year = value.getYear() + 1900
		month = value.getMonth() + 1
		day = value.getDate()
		hours = value.getHours()
		minutes = value.getMinutes()
		seconds = value.getSeconds()
		microseconds = int(value.getNanos() / 1000)
		return dt.datetime(year, month, day, hours, minutes, seconds, microseconds)
	# TODO: This conversion function is fairly generic. Consider making it global instead of a class member function. Is it used elsewhere?


class _Date(sqltypes.Date):
	#- Stays private to the dialect because it is named with an underscore.
	#- Will be invoked via the colspecs dictionary only. 
	#- Named using camel case because it extends a generic type.
	__visit_name__ = "DATE"

#- see line 1282 for get_result_processor
	def result_processor(self, dialect, coltype):
		print('### _Date result_processor 2')
		print('### type coltype: ', type(coltype)) #- <class 'jaydebeapi.DBAPITypeObject'>
		print('### repr coltype: ', repr(coltype)) #- DBAPITypeObject('DATE')
		breakpoint() #-
		def process(value):
			assert str(value.__class__) == "<java class 'java.sql.Date'>", 'Expecting a java.sql.Date object'
			year = value.getYear() + 1900
			month = value.getMonth() + 1
			day = value.getDate()
			return dt.date(year, month, day)
		return process
# """
# # WIP: 2024-07-03
# jaydebeapi_hsqldb.py contains some redefined conversion functions.
# These were copied into jaydebeapi.py, and are assigned to _DEFAULT_CONVERTERS
# inside the import_dbapi method.

# The new conversion functions should actually only return the java objects,
# not convert values to datetime objects.

# The conversion of java objects too datetime objects belongs in the 'process'
# methods of each type, as the one defined above for class _Date.

# TODO: update all conversion methods in jaydebeapi_hsqldb.py to return java objects, not datetime objects.
# TODO: Transfer the logic contained in those conversion functions in to the 'process' methods for each type.
# TODO: But first... transfer the *_WITH_TIMEZONE types and ensure they're working as expected
# """


	def bind_processor(self, dialect):
		def processor(value):
			if type(value) == datetime.date:
				return jdbapi.Date(value.year, value.month, value.day)
			else:
				return value
		return processor

# str No matching overloads found for org.hsqldb.jdbc.JDBCPreparedStatement.setObject(int,datetime.date), options are:
# 	public synchronized void org.hsqldb.jdbc.JDBCPreparedStatement.setObject(int,java.lang.Object) throws java.sql.SQLException




	def literal_processor(self, dialect):
		print('### _Date literal_processor')
		return super().literal_processor(dialect)

class _DateTime(sqltypes.DateTime):
	__visit_name__ = "DATETIME"

	def result_processor(self, dialect, coltype):
		print('### _DateTime result_processor')
		return super().result_processor(dialect, coltype)

	def bind_processor(self, dialect):
		print('### _DateTime bind_processor')
		breakpoint() #-
		return super().bind_processor(dialect)

	def literal_processor(self, dialect):
		print('### _DateTime literal_processor')
		return super().literal_processor(dialect)



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
	sqltypes.Date: _Date,

	# sqltypes.DateTime: _DateTime,
	# ^^^ When colspecs contains an entry for DateTime it seems to prevent
	#     the TIMESTAMP constructor and bind_processor from working.
	# class _DateTime doesn't currently add any extra functionality. It's just displaying debug info at the mo. 
	# TODO: Remove _DateTime if unused.

	# sqltypes.TIMESTAMP: TIMESTAMP, # 

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
# The Access dialect uses INFORMATION_SCHEMA.COLUMNS.DATA_TYPE
#
ischema_names = {

	# TODO: Mapping BLOB to sqltypes.BLOB is probably the correct way to do it. 
	# Swap out the mapping to JDBCBlobClient and test again to verify it still works.
	#
	# WIP: trying swapping out JDBCBlobClient for BLOB...
	# "BLOB": JDBCBlobClient,
	"BLOB": sqltypes.BLOB,

	# TODO: try mapping BOOLEAN to sqltypes.BOOLEAN. Test and verify it works.
	# "BOOLEAN": HyperSqlBoolean,

	"CHARACTER": sqltypes.CHAR,
	"DOUBLE" : sqltypes.DOUBLE, # 64 bit precision floating point number
	"INTEGER": sqltypes.INTEGER,
	"NUMERIC": sqltypes.NUMERIC,
	"VARCHAR": sqltypes.VARCHAR,

# WIP: -->
	"DATE": sqltypes.DATE,
	#- "java.lang.Date": sqltypes.DATE,
	#- "DATE": _Date,

	# Copied from Oracle...
	"TIMESTAMP": TIMESTAMP,  # TIMESTAMP or DATETIME?
	"TIMESTAMP WITH TIME ZONE": TIMESTAMP,
	# "INTERVAL DAY TO SECOND": INTERVAL,

}


# TODO: Implement HyperSqlCompiler. About 400 lines. The derived subclass is also long.
#- SQLCompiler derives from class Compiled, which represents Represent a compiled SQL or DDL expression.
class HyperSqlCompiler(compiler.SQLCompiler):
#- compiler.SQLCompiler methods that are commonly inherited by dialects have been stubbed below.

#i __init__; sql; ms; ora
	def __init__(self, *args, **kwargs):
		#- self.tablealiases = {} # mssql dialect's tablealiases dict.
		super().__init__(*args, **kwargs)
	# TODO: remove this method if unused

	#- Note this __init__ method has far fewer parameters than the base class.
	#- Any additional positional parameters are fed into *args,
	#- any keyword argument parameters are fed into **kwargs, I guess.
	#- As we're not referencing them within the method, we don't need to name them. Yes?
	# TODO: review all method signatures to see whether params can be eliminated.


#i _assert_pg_ts_ext; pg
#i _check_can_use_fetch_limit; ms
#i _get_limit_or_fetch; ms; ora
#i _get_nonansi_join_whereclause; ora

#i _literal_execute_expanding_parameter_literal_binds(self, parameter, values, bind_expression_template=None):
	def _literal_execute_expanding_parameter(self, name, parameter, values):
		raise NotImplementedError('xxx: _literal_execute_expanding_parameter')
	# TODO: Unsure why this function has been stubbed. remove it?

#i _mariadb_regexp_flags; my
#i _on_conflict_target; pg
#i _regexp_match; my; pg
#i _render_json_extract_from_binary; ms; my

#i _row_limit_clause; sql; ms; ora
	#- def _row_limit_clause(self, cs, **kwargs):
	#- 	raise NotImplementedError('xxx: _row_limit_clause')
	# The base impl calls fetch clause or limit clause.
	# TODO: Unsure why this function has been stubbed. remove it?

#i _schema_aliased_table; ms
#i _use_top; ms
#i _with_legacy_schema_aliasing; ms

#i default_from; sql; my; ora	# Inherit from base class
	#- def default_from(self):
	#- 	"""Called when a ``SELECT`` statement has no froms, and no ``FROM`` clause is to be appended.
	#- 	The Oracle compiler tacks a "FROM DUAL" to the statement.
	#- 	"""
	#- 	if _compatibility_mode == 'oracle':
	#- 		return " FROM DUAL"
	#- 	return ""
	#- HSQLDB supports 'FROM DUAL' when in Oracle compatibility mode, otherwise it does not and raises an error if used. 
	# TODO: Consider a separate HyperSqlCompiler class for each of HSQLDB's compatibility modes.

#i delete_extra_from_clause; sql; ms; my; pg
	def delete_extra_from_clause(self, delete_stmt, from_table, extra_froms, from_hints, **kw):
		"""Render the DELETE .. FROM clause. Not currently supported by HSQLDB. """
		raise NotImplementedError(
			"HSQLDB doesn't support multiple tables in DELETE FROM statements",
			"e.g. DELETE FROM t1, t2 WHERE t1.c1 = t2.c1"
		)
		return "FROM " + ", ".join(
			t._compiler_dispatch(self, asfrom=True, fromhints=from_hints, **kw)
			for t in [from_table] + extra_froms
		) # e.g. returns "FROM t1, t2"
		# HSQLDB doesn't natively support multiple tables in DELETE FROM statements.
		# See:
		#	https://hsqldb.org/doc/2.0/guide/dataaccess-chapt.html#dac_delete_statement
		#	https://stackoverflow.com/questions/7916380/delete-multitable-hsqldb
		# TODO: This function can be removed.

#i delete_table_clause; sql; ms; my #- inherit from SQLCompiler

# WIP: HyperSqlCompiler -->

#i fetch_clause; sql; pg
	def fetch_clause(self, select, fetch_clause=None, require_offset=False, use_literal_execute_for_simple_int=False, **kw, ):
		raise NotImplementedError('xxx: fetch_clause')

#i for_update_clause; sql; ms; my; ora; pg
	def for_update_clause(self, select, **kw):
		raise NotImplementedError('xxx: for_update_clause')

#i format_from_hint_text; sql; pg
	def format_from_hint_text(self, sqltext, table, hint, iscrud):
		raise NotImplementedError('xxx: format_from_hint_text')

#i function_argspec; sql; ora
	def function_argspec(self, func, **kwargs):
		raise NotImplementedError('xxx: function_argspec')

#i get_crud_hint_text; sql; ms
	def get_crud_hint_text(self, table, text):
		raise NotImplementedError('xxx: get_crud_hint_text')

#i get_cte_preamble; sql; ms; ora
	def get_cte_preamble(self, recursive):
		raise NotImplementedError('xxx: get_cte_preamble')

#i get_from_hint_text; sql; ms; my
	def get_from_hint_text(self, table, text):
		raise NotImplementedError('xxx: get_from_hint_text')

#i get_render_as_alias_suffix; sql; ora # inherit
	#- def get_render_as_alias_suffix(self, alias_name_text):
	#- 	raise NotImplementedError('xxx: get_render_as_alias_suffix')

#i get_select_hint_text; sql; ora
	def get_select_hint_text(self, byfroms):
		raise NotImplementedError('xxx: get_select_hint_text')

#i get_select_precolumns; sql; ms; my; pg
	#- def get_select_precolumns(self, select, **kw): # Inherit from compiler.SQLCompiler
	#- 	raise NotImplementedError('xxx: get_select_precolumns')

# WIP: get_select_precolumns ->
#i get_statement_hint_text(self, hint_texts):
	def get(lastrowid, parameters):
		raise NotImplementedError('xxx: get')

#i label_select_column; ms

#i limit_clause; sql; ms; my; ora; pg
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

#i order_by_clause; sql; ms
	#- def order_by_clause(self, select, **kw): # Inherit from compiler.SQLCompiler
	#- 	raise NotImplementedError('xxx: order_by_clause')

#i render_bind_cast; sql; pg
	def render_bind_cast(self, type_, dbapi_type, sqltext):
		return super().render_bind_cast(type_, dbapi_type, sqltext)
	# 'render_bind_cast' gets called when HyperSqlDialect.bind_typing = BindTyping.BIND_CASTS
	# 'render_bind_cast' is not implemented in the base.
	# 'render_bind_cast' is specialised by the postgresql dialect.
	# An alternative is BindingTyping.SETINPUTSIZES, which doesn't appear to be supported by JPype.
	# TODO: investigate if render_bind_cast is appropriate for HSQLDB, or remove this method if unused.

#i render_literal_value; sql; my; pg
	def render_literal_value(self, value, type_):
		# raise NotImplementedError('xxx: render_literal_value')
		return super().render_literal_value(value, type_)
	# TODO: inherit method from base class if behaviour is unchanged.

#i returning_clause; sql; ms; ora
	def returning_clause(self, stmt, returning_cols, *, populate_result_map, **kw, ) -> str:
		raise NotImplementedError('xxx: returning_clause')

#i translate_select_structure; ms; ora

#i update_from_clause; sql; ms; my; pg
	def update_from_clause(self, update_stmt, from_table, extra_froms, from_hints, **kw):
		raise NotImplementedError('xxx: update_from_clause')

#i update_limit_clause; sql; my
	def update_limit_clause(self, update_stmt):
		raise NotImplementedError('xxx: update_limit_clause')

#i update_tables_clause; sql; my
	def update_tables_clause(self, update_stmt, from_table, extra_froms, **kw):
		raise NotImplementedError('xxx: update_tables_clause')

#i visit_aggregate_order_by; pg
#i visit_aggregate_strings_func; ms; my; ora; pg

#i visit_alias; sql; ms # inherit
	#- def visit_alias(self, alias, asfrom=False, ashint=False, iscrud=False, fromhints=None, subquery=False, lateral=False, enclosing_alias=None, from_linter=None, **kwargs, ):
	#- 	raise NotImplementedError('xxx: visit_alias')

#i visit_array; pg

#i visit_binary; sql; ms # inheriit
	#- def visit_binary(self, binary, override_operator=None, eager_grouping=False, from_linter=None, lateral_from_linter=None, **kw, ):
	#- 	raise NotImplementedError('xxx: visit_binary')

#i visit_bitwise_xor_op_binary; pg

#i visit_cast; sql; my # inherit
	#- def visit_cast(self, cast, **kwargs):
	#- 	raise NotImplementedError('xxx: visit_cast')

#i visit_char_length_func; ms; ora

#i visit_column; sql; ms # Inherit
	#- def visit_column(self, column, add_to_result_map=None, include_table=True, result_map_targets=(), ambiguous_table_name_map=None, **kwargs, ) -> str:
	#- 	raise NotImplementedError('xxx: visit_column')

#i visit_concat_op_binary; ms; my
#i visit_concat_op_expression_clauselist; ms; my
#i visit_current_date_func; ms

#i visit_empty_set_expr; sql; ms; my; ora; pg
	def visit_empty_set_expr(self, element_types, **kw):
		raise NotImplementedError('xxx: visit_empty_set_expr')

#i visit_extract; sql; ms
	def visit_extract(self, extract, **kwargs):
		raise NotImplementedError('xxx: visit_extract')

#i visit_false; sql; ms; my; ora
	#- def visit_false(self, expr, **kw): # inherit
	#- 	raise NotImplementedError('xxx: visit_false')

#i visit_function; sql; ora
	def visit_function(self, func, add_to_result_map=None, **kwargs, ) -> str:
		raise NotImplementedError('xxx: visit_function')

#i visit_getitem_binary; pg

#i visit_ilike_case_insensitive_operand; sql; pg
	def visit_ilike_case_insensitive_operand(self, element, **kw):
		raise NotImplementedError('xxx: visit_ilike_case_insensitive_operand')

#i visit_ilike_op_binary; sql; pg
	def visit_ilike_op_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_ilike_op_binary')

#i visit_is_distinct_from_binary; ms; my; ora
#i visit_is_not_distinct_from_binary; ms; my; ora

#i visit_join; sql; my; ora
	def visit_join(self, join, asfrom=False, from_linter=None, **kwargs):
		raise NotImplementedError('xxx: visit_join')

#i visit_json_getitem_op_binary; ms; my; pg
#i visit_json_path_getitem_op_binary; ms; my; pg

#i visit_length_func; ms
#i visit_match_op_binary; ms; my; ora; pg

#i visit_mod_binary; sql; ora
	def visit_mod_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_mod_binary')

#i visit_mysql_match; my

#i visit_not_ilike_op_binary; sql; pg
	def visit_not_ilike_op_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_not_ilike_op_binary')

#i visit_not_regexp_match_op_binary; sql; my; ora; pg
	def visit_not_regexp_match_op_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_not_regexp_match_op_binary')

#i visit_now_func; ms; ora
#i visit_on_conflict_do_nothing; pg
#i visit_on_conflict_do_update; pg
#i visit_on_duplicate_key_update; my
#i visit_outer_join_column; ora
#i visit_phraseto_tsquery_func; pg
#i visit_plainto_tsquery_func; pg
#i visit_random_func; my

#i visit_regexp_match_op_binary; sql; my; ora; pg
	def visit_regexp_match_op_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_regexp_match_op_binary')

#i visit_regexp_replace_op_binary; sql; my; ora; pg
	def visit_regexp_replace_op_binary(self, binary, operator, **kw):
		raise NotImplementedError('xxx: visit_regexp_replace_op_binary')

#i visit_rollback_to_savepoint; sql; ms
	def visit_rollback_to_savepoint(self, savepoint_stmt, **kw):
		raise NotImplementedError('xxx: visit_rollback_to_savepoint')

#i visit_rollup_func; my

#i visit_savepoint; sql; ms
	def visit_savepoint(self, savepoint_stmt, **kw):
		raise NotImplementedError('xxx: visit_savepoint')

#i visit_sequence; sql; ms; my; ora; pg
	def visit_sequence(self, sequence, **kw):
		raise NotImplementedError('xxx: visit_sequence')

#i visit_slice; pg
#i visit_substring_func; pg
#i visit_sysdate_func; my

#i visit_table_valued_column; sql; ora
	def visit_table_valued_column(self, element, **kw):
		raise NotImplementedError('xxx: visit_table_valued_column')

#i visit_table; sql; ms # inherit
	#- def visit_table(self, table, asfrom=False, iscrud=False, ashint=False, fromhints=None, use_schema=True, from_linter=None, ambiguous_table_name_map=None, **kwargs, ):
	#- 	raise NotImplementedError('xxx: visit_table')

#i visit_to_tsquery_func; pg
#i visit_to_tsvector_func; pg

#i visit_true; sql; ms; my; ora
	#- def visit_true(self, expr, **kw): # inherit
	#- 	raise NotImplementedError('xxx: visit_true')

#i visit_try_cast; ms
#i visit_ts_headline_func; pg

#i visit_typeclause; sql; my # inherit
	#- def visit_typeclause(self, typeclause, **kw):
	#- 	raise NotImplementedError('xxx: visit_typeclause')
	#-
	#- MySQL dialect appears to override this function in order to
	#- provide specific control or enhancements for type conversions.
	#- It appears to map sqltypes, returning strings for dialect types.
	#-
	#- Isn't this provided elsewhere by other mappings? Not quite.
	#- 		ischema_names maps strings to sqltypes.
	#- 		colspecs map sqltypes to dialect types.

#i visit_websearch_to_tsquery_func; pg



class HyperSqlDDLCompiler(compiler.DDLCompiler):
#- DDLCompiler derives from class Compiled, which represents Represent a compiled SQL or DDL expression.

#i define_constraint_cascades; ddl; ora
	#- def define_constraint_cascades(self, constraint): # inherit from DDLCompiler
	#- 	raise NotImplementedError('xxx: define_constraint_cascades')

#i define_constraint_deferrability; ddl
	def define_constraint_deferrability(self, constraint):
		if constraint.initially is not None:
			raise exc.CompileError("Constraint deferrability is not currently supported")
		return super().define_constraint_deferrability(constraint)
	# "The deferrable characteristic is an optional element of CONSTRAINT definition, not yet supported by HyperSQL."

#i define_constraint_match; ddl; my
	def define_constraint_match(self, constraint):
		#- assert constraint.match in ['FULL', 'PARTIAL', 'SIMPLE']
		return compiler.DDLCompiler.define_constraint_match(self, constraint)
	# MATCH is a keyword for HSQLDB, used with FK constraints.
	# See: https://hsqldb.org/doc/2.0/guide/databaseobjects-chapt.html
	# TODO: verify inherited define_constraint_match method works as expected for HSQLDB. If so, delete this override.

#i define_unique_constraint_distinct; ddl; pg
	#- def define_unique_constraint_distinct(self, constraint, **kw): # inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: define_unique_constraint_distinct')

#i get_column_specification; ddl; ms; my; pg
	def get_column_specification(self, column, **kwargs):
		"""Builds column DDL."""

		# A column definition consists of a <column name>...
		colspec = self.preparer.format_column(column)

		# and in most cases a <data type> or <domain name>...
		colspec += " " + self.dialect.type_compiler_instance.process(
				column.type, type_expression=column
			)

		# --------
		# The clauses below are mutually exclusive, but isn't reflected by code logic...
		# 	[ <default clause> | <identity column specification> | <identity column sequence specification> | <generation clause> ]
		# There appears to be a risk we'll end up with colspecs containing conflicting causes.
		# TODO: verify colspecs doesn't contain conflicting causes

		# <default clause>
		default = self.get_column_default_string(column)
		if default is not None:
			colspec += " DEFAULT " + default
		# The value of default should match a <default option>, i.e.
		#	<default option> ::= <literal> | <datetime value function> | USER | CURRENT_USER | CURRENT_ROLE | SESSION_USER | SYSTEM_USER | CURRENT_CATALOG | CURRENT_SCHEMA | CURRENT_PATH | NULL

		# <generation clause> ?
		if column.computed is not None:
			colspec += " " + self.process(column.computed) # See visit_computed_column()
			#- "GENERATED ALWAYS AS (%s)" % self.sql_compiler.process(generated.sqltext, include_table=False, literal_binds=True)

		# <identity column specification>
		if (
			column.identity is not None
			and self.dialect.supports_identity_columns
		):
			colspec += " " + self.process(column.identity) # See compiler.DDLCompiler.visit_identity_column()
		# --------

		# <update clause> - (seems to be missing in the docs https://hsqldb.org/doc/2.0/guide/databaseobjects-chapt.html)
		# Maybe it's the <on update clause>?
		# "This feature is not part of the SQL Standard and is similar to MySQL's ON UPDATE clause."
		# TODO: implement <update clause>

		# <column constraint definition> ?
		# Constraint definitions are missing here.
		# HSQLDB automatically turns column constraint definitions into table constraint definitions.
		# Perhaps SQLAlchemy defines constraints on tables only?

		# Except for the NOT NULL constraint...
		if not column.nullable and (
			not column.identity or not self.dialect.supports_identity_columns
		):
			# In other words, if not nullable and not an identity column then append...
			colspec += " NOT NULL"

		# <collate clause>
		# TODO: implement collate clause?

		return colspec
	# See 'column definition' in...
	# 	http://www.hsqldb.org/doc/2.0/guide/databaseobjects-chapt.html#dbc_table_creation
	#
	# Except for added comments, the function above is practically identical to the default implementation.
	# TODO: inherit the get_column_specification method from compiler.DDLCompiler


#i get_identity_options; ddl; ora
	def get_identity_options(self, identity_options):
		assert identity_options.cache is None, "HSQLDB doesn't support identity_options.cache"
		return compiler.DDLCompiler.get_identity_options(self, identity_options)
	# HSQLDB appears to support most of the identity options found in
	# compiler.DDLCompiler.get_identity_options method, except for "CACHED".
	#
	# See "<common sequence generator options>" under the "CREATE SEQUENCE" section
	# 	https://hsqldb.org/doc/2.0/guide/databaseobjects-chapt.html
	#
	# HSQLDB also has a sequence generator option named 'AS', which doesn't appear
	# to be supported by compiler.DDLCompiler.get_identity_options.
	# TODO:3: implement support for identity_option 'AS'

#i post_create_table; ddl; my; ora; pg
	def post_create_table(self, table):
		"""Build table-level CREATE options like ON COMMIT and COLLATE."""
		table_opts = []
		opts = table.dialect_options['hsqldb']
		if opts['on_commit']:
			on_commit_options = opts['on_commit'].replace('_', ' ').upper()
			table_opts.append(' ON COMMIT %s' % on_commit_options)
		return ' '.join(table_opts)
	# TODO: Is this the place to implement the <collate clause>?

	def visit_create_table(self, create, **kw):
		table = create.element
		preparer = self.preparer

		text = "\nCREATE "

		if table._prefixes:
			text += " ".join(table._prefixes) + " "
		# TODO: What are table prefixes? Are they similar to hsqldb_type?

		hsqldb_type = table.dialect_options['hsqldb']['type']
		# The line above generates an error... "sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:hsqldb"
		# It's because 'hsqldb.jaydebeapi' != 'hsqldb' when attempting to load the library; See: \sqlalchemy\util\langhelpers.py(~362)
		if hsqldb_type is not None:
			text += hsqldb_type + " "
		# TODO: restrict hsqldb_type to valid types, e.g. [MEMORY | CACHED | [GLOBAL] TEMPORARY | TEMP | TEXT ]

		text += "TABLE "
		if create.if_not_exists:
			text += "IF NOT EXISTS "

		text += preparer.format_table(table) + " "

		create_table_suffix = self.create_table_suffix(table)
		if create_table_suffix:
			text += create_table_suffix + " "

		text += "("

		separator = "\n"

		# if only one primary key, specify it along with the column
		first_pk = False
		for create_column in create.columns:
			column = create_column.element
			try:
				processed = self.process(
					create_column, first_pk=column.primary_key and not first_pk
				)
				if processed is not None:
					text += separator
					separator = ", \n"
					text += "\t" + processed
				if column.primary_key:
					first_pk = True
			except exc.CompileError as ce:
				raise exc.CompileError(
					"(in table '%s', column '%s'): %s"
					% (table.description, column.name, ce.args[0])
				) from ce

		const = self.create_table_constraints(
			table,
			_include_foreign_key_constraints=create.include_foreign_key_constraints,  # noqa
		)
		if const:
			text += separator + "\t" + const

		text += "\n)%s\n\n" % self.post_create_table(table)
		return text
		# This method overrides the base method to allow us to specify hsqldb_type,
  		# a table type such as [MEMORY | CACHED | [GLOBAL] TEMPORARY | TEMP | TEXT ]
		# The base method inserts table._prefixes, which hsqldb_type might
		# duplicate the purpose of.
		# TODO: review whether overriding visit_create_table is necessary.

#i visit_check_constraint; ddl; pg
	#- def visit_check_constraint(self, constraint, **kw): #- inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: visit_check_constraint')

#i visit_computed_column; ddl; ms; ora; pg
	def visit_computed_column(self, generated, **kw):
		if generated.persisted is False:
			raise exc.CompileError(
				"Virtual computed columns are unsupported."
				"Please set the persisted flag to None or True."
			)
		return "GENERATED ALWAYS AS (%s)" % self.sql_compiler.process(
			generated.sqltext, include_table=False, literal_binds=True
		)


# WIP: index to unique constraint -->
	# @compiles(schema.CreateColumn)
	# def compile(element, compiler, **kw):
	# 	pass

# # class CreateIndex(_CreateBase):
# #     """Represent a CREATE INDEX statement."""
# #     __visit_name__ = "create_index"
# #     def __init__(self, element, if_not_exists=False):
 
	@compiles(schema.CreateIndex, 'hsqldb')
	def _compile_create_index(createIndexObj, compiler, **kw):
		index = createIndexObj.element
		if index.unique == True and False:
			# Unique indexes are deprecated in HSQLDB since version 1.8,
			# so we need to generate DDL for a unique constraint instead.

			uc = UniqueConstraint(index.columns, name=index.name, _column_flag=False)
			raise exc.CompilerError('Unique indexes are deprecated. Use a unique constraint instead.')

			raise NotImplementedError
			return compiler.visit_add_constraint(uc, **kw)

			# index.table.append_constraint(uc)
			return compiler.visit_create_unique_index(index, **kw) # This to create a unique constraint
			# Don't add a UniqueConstraint to the metadata because that could cause other DBMSs to generate a UC.
			return compiler.visit_unique_constraint(index, **kw) #- failed
		else:
			return compiler.visit_create_index(createIndexObj, **kw)

#- signature of visit_create index...
#def visit_create_index(self, create, include_schema=False, include_table_schema=True, **kw):

	#- @compiles(schema.Index, 'hsqldb')
	#- def _compile_index(element, compiler, **kw):
	#- 	return compiler.visit_index(element, **kw) # returns index name
	#- TODO: remove

#i visit_create_index; ddl; ms; my; ora; pg
	def visit_create_index(self, create, include_schema=False, include_table_schema=True, **kw):
		index = create.element
		self._verify_index_table(index)
		preparer = self.preparer

# WIP: index to unique constraint -->
		# Index('users_t_idx',
		# 	Column('test1', CHAR(length=5), table=<users>, nullable=False), 
		# 	Column('test2', Float(), table=<users>, nullable=False),
		# 	unique=True)
		if index.unique == True and False: # temporarily disabled with False
			# Add a table-level UNIQUE constraint...
			table = index.table
			table.indexes.remove(index)
			# index.drop(bind=engine)
			# uc = UniqueConstraint((index.expressions), name=index.name)
			uc = UniqueConstraint(index.columns, name=index.name)
			table.append_constraint(uc)
			# schema.Index("users_t_idx", users.c.test1, users.c.test2, unique=True)

			# # # index.table.append_constraint(
			# # # 	schema.UniqueConstraint(
			# # # 		# *columns: _DDLColumnArgument,
			# # # 		index.columns,
			# # # 		# # ", ".join(
			# # # 		# # 	self.sql_compiler.process(
			# # # 		# # 		expr, include_table=False, literal_binds=True
			# # # 		# # 	)
			# # # 		# # 	for expr in index.expressions
			# # # 		# # ),

			# # # 		# name: _ConstraintNameArgument = None,
			# # # 		self._prepared_index_name(index, include_schema=include_schema),

			# # # 		# deferrable: Optional[bool] = None,
			# # # 		# initially: Optional[str] = None,
			# # # 		# info: Optional[_InfoType] = None,
			# # # 		# _autoattach: bool = True,
			# # # 		# _column_flag: bool = False,
			# # # 		# _gather_expressions: Optional[List[_DDLColumnArgument]] = None,
			# # # 		# **dialect_kw: Any
			# # # 	)
			# # # )
			# create a unique constraint instead, ALTER TABLE t ADD CONSTRAINT cst UNIQUE (num)
			# # text = "ALTER TABLE t ADD CONSTRAINT cst UNIQUE (num)"
			# Is there already a method for adding constraints?
			# 	Yes, visit_unique_constraint(), but this skips 'ALTER TABLE' and starts with 'CONSTRAINT'.
			# 
# WIP: add unique constraint  -->
			return None
		else:
			if index.name is None:
				raise exc.CompileError("CREATE INDEX requires an index name.")
			text = "CREATE INDEX "
			if create.if_not_exists:
				text += "IF NOT EXISTS "
			text += "%s ON %s (%s)" % (
				self._prepared_index_name(index, include_schema=include_schema),
				preparer.format_table(index.table, use_schema=include_table_schema),
				", ".join(
					self.sql_compiler.process(
						expr, include_table=False, literal_binds=True
					)
					for expr in index.expressions
				),
			)
			return text
			# Support for the ASC|DESC option not implemented because specifying
			# the sort order for indexes has no effect in HSQLDB. The asc_or_desc
   			# column is always set to 'A'.
			# TODO: Is there a case for spoofing the setting, for example to preserve the sort order between DBs?
			# TODO: Consider raising an error when desc() is called. 

#i visit_create_sequence; ddl; ms; pg
	def visit_create_sequence(self, create, **kw):
		prefix = None
		if create.element.data_type is not None:
			data_type = create.element.data_type
			prefix = " AS %s" % self.type_compiler.process(data_type)
		return super().visit_create_sequence(create, prefix=prefix, **kw)

#i visit_drop_column_comment; ddl; ms
	def visit_drop_column_comment(self, drop, **kw):
		return "COMMENT ON COLUMN %s IS ''" % self.preparer.format_column(
			drop.element, use_table=True
		)
	# COMMENT ON statement only accepts a character string literal, not a NULL,
	# even though an unset comment is initially NULL.
	# TODO: consider updating INFORMATION_SCHEMA.SYSTEM_COLUMNS.REMARKS directly.

#i visit_drop_constraint_comment; ddl; pg
	def visit_drop_constraint_comment(self, drop, **kw):
		raise exc.CompileError("Constraint comments are not supported.")
	# HSQLDB doesn't support comments on constraints.

#i visit_drop_constraint; ddl; my
	def visit_drop_constraint(self, drop, **kw):
		constraint = drop.element
		if constraint.name is not None:
			formatted_name = self.preparer.format_constraint(constraint)
		else:
			formatted_name = None

		if formatted_name is None:
			raise exc.CompileError(
				"Can't emit DROP CONSTRAINT for constraint %r; "
				"it has no name" % drop.element
			)
		return "ALTER TABLE %s DROP CONSTRAINT %s %s %s" % (
			self.preparer.format_table(drop.element.table),
			formatted_name,
			"CASCADE" if drop.cascade else "RESTRICT",
		)
	# TODO: verify each kind of constraint is dropped, pk, fk, check, etc.

#i visit_drop_index; ddl; ms; my; pg
	def visit_drop_index(self, drop, **kw):
		index = drop.element
		if index.name is None:
			raise exc.CompileError(
				"DROP INDEX requires that the index have a name"
			)
		text = "\nDROP INDEX "
		text += self._prepared_index_name(index, include_schema=True)
		#- verified include_schema=True is correct for HSQLDB
		if drop.if_exists:
			text += " IF EXISTS"
		return text
	# "Will not work if the index backs a UNIQUE of FOREIGN KEY constraint".
	# TODO:3: would it be helpful to raise an exception if the index backs a unique or FK constraint?

#i visit_drop_table_comment; ddl; ms; my; ora
	def visit_drop_table_comment(self, drop, **kw):
		return "COMMENT ON TABLE %s IS ''" % self.preparer.format_table(
			drop.element
		)
	# COMMENT ON statement only accepts a character string literal, not a NULL,
	# even though an unset comment is initially NULL.
	# TODO: consider updating INFORMATION_SCHEMA.SYSTEM_TABLES.REMARKS directly.

#i visit_drop_table; ddl # just ddl I'm guessing
	def visit_drop_table(self, drop, **kw):
		assert hasattr(drop, 'cascade') == False, "We can make use of drop.cascade if it exist. See comments on visit_drop_table"
		text = "\nDROP TABLE "
		text += self.preparer.format_table(drop.element)
		if drop.if_exists:
			text += "IF EXISTS "
		# text += "CASCADE" if drop.cascade else "RESTRICT", # TODO: enable if drop.cascade exists.
		text += ";"
		return text
	# HSQLDB supports CASCADE when dropping tables...
	#	<drop table statement> ::= DROP TABLE [ IF EXISTS ] <table name> [ IF EXISTS ] <drop behavior>
	#	<drop behavior> ::= CASCADE | RESTRICT -- (I've not verified this particular line in the docs)
	#
	# SQLAlchemy doesn't appear to support CASCADE for dropping tables,
	# although the DDLCompiler.visit_drop_constraint method does support it for constraints.
	#
	# Maybe drop.cascade is only present for certain cases, or specifiable as an additional option?
	# Maybe SQLAlchemy doesn't need drop.cascade on tables?
	# TODO: implement support for drop.cascade on tables, if it's actually needed and doable.

#i visit_foreign_key_constraint; ddl; pg
	#- def visit_foreign_key_constraint(self, constraint, **kw): #- inherit from compiler.DDLCompiler
	#-	raise NotImplementedError('xxx: visit_foreign_key_constraint')

#i visit_identity_column; ddl; ms; ora
	#- def visit_identity_column(self, identity, **kw):  #- inherit from compiler.DDLCompiler
	#- 	return super().visit_identity_column(identity, **kw)

#i visit_primary_key_constraint; ddl; ms; my
	#- def visit_primary_key_constraint(self, constraint, **kw):  #- inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: visit_primary_key_constraint')

#i visit_set_column_comment; ddl; ms; my
	#- def visit_set_column_comment(self, create, **kw):  #- inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: visit_set_column_comment')

#i visit_set_constraint_comment; ddl; pg
	#- def visit_set_constraint_comment(self, create, **kw):
	#- 	raise NotImplementedError('xxx: visit_set_constraint_comment')
	#- HSQLDB doesn't support comments on constraints.

#i visit_set_table_comment; ddl; ms; my
	#- def visit_set_table_comment(self, create, **kw):  #- inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: visit_set_table_comment')

#i visit_unique_constraint; ddl; ms
	#- def visit_unique_constraint(self, constraint, **kw):  #- inherit from compiler.DDLCompiler
	#- 	raise NotImplementedError('xxx: visit_unique_constraint')




# WIP: HyperSqlTypeCompiler -->
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

	def visit_TIMESTAMP(self, type_, **kw):
		if type_.timezone == True:
			return "TIMESTAMP WITH TIME ZONE"
		else:
			return "TIMESTAMP"


# WIP: HyperSqlIdentifierPreparer -->
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


# WIP: HyperSqlIdentifierPreparer -->
# TODO: Implement HyperSqlExecutionContext. About 55-165 lines, 2-8 methods.
class HyperSqlExecutionContext(default.DefaultExecutionContext):
	def __init__(self):
		print('#3' * 10, 'inside HyperSqlExecutionContext.__init__ method')
		assert False, 'Does a HyperSqlExecutionContext object get instantiated?'
	# TODO: remove __init__ method if this class is never instantiated.

#j create_server_side_cursor ; dec ; my ; my_ma ; pgc ; pg_a ; pg_pg8 ; sl_a
	def create_server_side_cursor(self):
		print('### HyperSqlexecutionContext.create_server_side_cursor') #-
		if self.dialect.supports_server_side_cursors:
			return self._dbapi_connection.cursor() # TODO: are any params required?
		else:
			raise NotImplementedError()
	# TODO: Should this function exist here or in HyperSqlExecutionContext_jaydebeapi?

#j fire_sequence ; ec ; ms ; my ; o ; pg
	def fire_sequence(self, seq, type_):
		"""given a :class:`.Sequence`, invoke it and return the next int value"""
		raise NotImplementedError

#j get_insert_default ; dec ; ms ; pg
	def get_insert_default(self):
		raise NotImplementedError

#j get_lastrowid ; dec ; a ; ms ; my_ma ; my_py
	def get_lastrowid(self):
		raise NotImplementedError

#j handle_dbapi_exception ; ec ; dec ; ms ; pg_a
	def handle_dbapi_exception(self):
		"""Receive a DBAPI exception which occurred upon execute, result fetch, etc."""
		raise NotImplementedError

#j post_exec ; ec ; dec ; ms ; ms_py ; my_ma ; o_cx ; pgc_p2
	def post_exec(self):
		# print('### HypereSqlExecutionContext.post_exec') #-
		super().post_exec()
	# TODO: just inherit if unused

#j pre_exec ; ec ; dec ; ms ; ms_py ; o ; o_cx ; pg_a ; pg_pg8
	def pre_exec(self):
		# print('### HypereSqlExecutionContext.pre_exec') #-
		super().pre_exec()
	# TODO: inherit if unused

#j rowcount ; dec ; ms ; my_ma ; my_my
	def rowcount(self):
		return super().rowcount()
	# TODO: just inherit if unused

# TODO: remove lines begining with '#j'. These lines list commonly overriden execution context functions
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

	Each dialect specialises DefaultExecutionContext,
	and each dialect connector then specialises further. See...
		jaydebeapi.py:
			class HyperSqlExecutionContext_jaydebeapi(HyperSqlDialect.HyperSqlExecutionContext):

	"""
#j get_result_processor ; dec
	# TODO: remove X to enable
	def get_result_processorX(self, type_, colname, coltype):
		"""jsn: Return a 'result processor' for a given type as present in cursor.description.
		Override this method for context-sensitive result type handling."""
		print('### str type_', str(type_))
		if str(type_) != 'NULL':
			breakpoint() # Break here to examine what type is being received.
		return super().get_result_processor(type_, colname, coltype)
	# This DefaultExecutionContext method is not normally overriden. It's only done here for troubleshooting purposes.
	# TODO: remove after troubleshooting


class HyperSqlDialect(default.DefaultDialect):
	"""HyperSqlDialect implementation of Dialect"""

	def __init__(self, classpath=None, **kwargs):
		default.DefaultDialect.__init__(self, **kwargs)
		self.classpath = classpath	# A path to the HSQLDB executable jar file.

# WIP: --> Where to set the default isolation level?
		# self.isolation_level = 'READ COMMITTED'

#i  CACHE_HIT = CacheStats.CACHE_HIT
#i  CACHE_MISS = CacheStats.CACHE_MISS
#i  CACHING_DISABLED = CacheStats.CACHING_DISABLED
#i  NO_CACHE_KEY = CacheStats.NO_CACHE_KEY
#i  NO_DIALECT_SUPPORT = CacheStats.NO_DIALECT_SUPPORT

#i  dispatch: dispatcher[Dialect]

#i  name: str; """identifying name for the dialect from a DBAPI-neutral point of view (i.e. 'sqlite') """
	name = "hsqldb"

	requires_name_normalize = True
	# Methods 'normalize_name' and 'denormalize_name' are only used if requires_name_normalize = True
	# Like Oracle, HSQLDB identifiers are normalised to uppercase.
	# This setting appears to affect the case of keys in the row _mapping dictionary, (as used in the get_columns function)
	# 	True = lowercase, False = uppercase

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
	#- JayDeBeApi connector may need a derived execution_ctx_cls. Stub created.

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
		(schema.Table, {
			"type": None,
			#- Note the expected values for 'type' will be: [MEMORY | CACHED | [GLOBAL] TEMPORARY | TEMP | TEXT ]
			#- Should 'GLOBAL TEMPORARY' be specified as a prefix instead? See CompileTest.test_table_options method in test_compiler.py
			"on_commit": None,		# DELETE | PRESERVE | NULL
		})
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
			"legacy_schema_aliasing": util.asbool			# mssql dialect - Deprecated and not applicable. Remove.
		}
	)
	# engine_config_types is currently unused. Leaving it here for now as an example in case we need it later.
	# Unsure what its purpose is / how it's used exactly, other than coercing a key's value to a type.
	# TODO: Remove engine_config_types if unused, or remove those commented out.

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
		#-table_name = self.denormalize_name(table_name)
		if schema is None:
			schema = self.default_schema_name
		assert schema is not None
		reflectedColumns = []
		query = """
			SELECT
			a.column_name AS "name",
			-- TODO: 'type' has to possible fields, which differ slightly for certain data types. Choose one, remove the other...
			a.type_name AS "type",		-- e.g. VARCHAR
			b.data_type AS "type_b",	-- e.g. CHARACTER VARYING
			-- TODO: 'nullable' has to possible fields, with either YES/NO or 0/1 values. Choose one and remove the other...
			a.nullable AS "nullable_01", -- 0 OR 1
			a.is_nullable AS "nullable_yesno", -- YES or NO
			a.column_def AS "default", -- TODO: What does COLUMN_DEF represent, default value, or definition?
			a.is_autoincrement AS "autoincrement",
			a.remarks AS "comment",
			-- NULL AS "computed", -- TODO: Does HSQLDB have an appropriate field?
			b.is_identity AS "identity",
			-- NULL AS "dialect_options", -- TODO: Does HSQLDB have an appropriate field?
			b.numeric_precision,
			b.numeric_scale,
			b.character_maximum_length
			FROM information_schema.system_columns AS a
			LEFT JOIN information_schema.columns AS b
			ON a.table_name = b.table_name
			AND a.column_name = b.column_name
			AND a.table_schem = b.table_schema
			AND a.table_cat = b.table_catalog -- TODO: Document or fix potential area of failure. Catalogs with duplicate objects.
			WHERE a.table_name = (?)
			AND a.table_schem = (?)
			"""
		cursorResult = connection.exec_driver_sql(query, (
			self.denormalize_name(table_name),
			self.denormalize_name(schema)
			))
		
		rows = cursorResult.all()
		if len(rows) == 0:
			# Tables must have at least one column otherwise they can't exist.
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		
		for row in rows:
			# Note: row._mapping is using column names as keys and not the aliases defined in the query.
			# 		row._mapping keys are lowercase if requires_name_normalize = True, or uppercase if False
			col_name = self.normalize_name(row._mapping['column_name']) # str """column name"""
# WIP: -->
# TODO: col_name needed normalizing. What other identifiers, PKs, FKs?
			assert row._mapping['type_name'] in ischema_names, "ischema_names is missing a key for datatype %s" % row._mapping['type_name']
			col_type = row._mapping['type_name'] # A String value, e.g. 'INTEGER'; TypeEngine[Any] """column type represented as a :class:`.TypeEngine` instance."""

			col_nullable = bool(row._mapping['nullable']) # bool """boolean flag if the column is NULL or NOT NULL"""
			col_default = row._mapping['column_def'] # Optional[str] """column default expression as a SQL string"""
			col_autoincrement = row._mapping['is_autoincrement'] == 'YES' # NotRequired[bool] """database-dependent autoincrement flag.
			# This flag indicates if the column has a database-side "autoincrement"
			# flag of some kind.   Within SQLAlchemy, other kinds of columns may
			# also act as an "autoincrement" column without necessarily having
			# such a flag on them.
			# See :paramref:`_schema.Column.autoincrement` for more background on "autoincrement".
			col_comment = row._mapping['remarks'] # NotRequired[Optional[str]] """comment for the column, if present. Only some dialects return this key """
			col_computed = None # NotRequired[ReflectedComputed] """indicates that this column is computed by the database. Only some dialects return this key.

			# TODO: The type for identity should be ReflectedIdentity, not a bool.
			col_identity = row._mapping['is_identity'] == 'YES' # NotRequired[ReflectedIdentity] indicates this column is an IDENTITY column. Only some dialects return this key.

			col_dialect_options = None # NotRequired[Dict[str, Any]] Additional dialect-specific options detected for this reflected object

			#- What happens if you attempt to query a non-existant column?
			#- e.g. idontexist = row._mapping['idontexist']
			#- 		sqlalchemy.exc.NoSuchColumnError: Could not locate column in row for column 'idontexist'

			if col_type == 'NUMERIC':
				col_numeric_precision = row._mapping['numeric_precision']
				col_numeric_scale = row._mapping['numeric_scale']
				col_type = ischema_names.get(col_type)(
					int(col_numeric_precision),
					int(col_numeric_scale)
				)
			elif col_type == 'VARCHAR':
				col_character_maximum_length = row._mapping['character_maximum_length']
				col_type = ischema_names.get(col_type)(
					int(col_character_maximum_length)
				)
			else:
				col_type = ischema_names.get(col_type)()

			# # # kwargs = {}

			# # # col_numeric_precision = row._mapping['numeric_precision']
			# # # if col_numeric_precision:
			# # # 	kwargs["precision"] = int(col_numeric_precision)

			# # # col_numeric_scale = row._mapping['numeric_scale']
			# # # if col_numeric_scale:
			# # # 	kwargs['scale'] = int(col_numeric_scale)

			# # # col_character_maximum_length = row._mapping['character_maximum_length']
			# # # if col_character_maximum_length:
			# # # 	kwargs['length'] = int(col_character_maximum_length)

			# # # if len(kwargs) > 0 and False:
			# # # 	col_type = ischema_names[col_type](**kwargs)
			# # # 	# TODO: ischema_names.get(col_type)
			# # # 	# Note Oracle doesn't pass kwargs to type constructors, only required params, e.g. col_type = NUMERIC(precision,scale) 
			# # # 	# TODO: fix... TypeError: INTEGER() takes no arguments
			# # # else:
			# # # 	col_type = ischema_names.get(col_type)()

			#- if issubclass(col_type, sqltypes.Numeric) == True:
			#- pass

			reflectedColumns.append({
				'name': col_name,
				'type': col_type,
				'nullable': col_nullable,
				'default': col_default,
				'autoincrement': col_autoincrement,
				'comment': col_comment,
				# 'computed': col_computed, # TODO: computed/generated column
				# 'identity': col_identity, # TODO: identity column
				# 'dialect_options': col_dialect_options
				})
		return reflectedColumns

	# The column tables in INFORMATION_SCHEMA do not have a 'computed' field.
	# Maybe these are referred to as 'generated' columns in HSQLDB?
	# INFORMATION_SCHEMA.COLUMNS has 'IS_GENERATED' and 'GENERATION_EXPRESSION' columns.
	# INFORMATION_SCHEMA.SYSTEM_COLUMNS has an 'IS_GENERATEDCOLUMN' column.
	# TODO: update get_columns to include computed and identity columns.


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
		"""SELECT column_name from information_schema.system_primarykeys
		WHERE table_schem = (?) AND table_name = (?)""",
		(self.denormalize_name(schema), self.denormalize_name(table_name)))
		all = cursorResult.scalars().all()
		if len(all) == 0 and self.has_table(connection, table_name, schema) == False:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)

		constrained_columns = list(map(self.normalize_name, all))
		return {
			"name": None,
			"constrained_columns": constrained_columns
			#"dialect_options" : NotRequired[Dict[str, Any]] # Additional dialect-specific options detected for this primary key
			}
		# TODO:3: understand why test_get_pk_constraint fails when 'name' is set to pk_name.

#i  def get_multi_pk_constraint(
	# TODO: for better performance implement get_multi_pk_constraint. DefaultDialect's implementation is only adequate for now.

#i  def get_foreign_keys(	# Return information about foreign_keys in ``table_name``.
	@reflection.cache
	def get_foreign_keys(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		fktable_schem = schema or self.default_schema_name
		reflectedForeignKeys = []
		query = """
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
			WHERE fktable_schem = (?) AND fktable_name = (?)
			ORDER BY key_seq ASC"""
		cursorResult = connection.exec_driver_sql(query,
			(self.denormalize_name(fktable_schem), self.denormalize_name(table_name)))
		
		rows = cursorResult.all()
		if len(rows) == 0 and self.has_table(connection, table_name, schema) == False:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)

		for row in rows:
			# Note row._mapping is using column names as keys and not the aliases defined in the query.
			fk_name = self.normalize_name(row._mapping['fk_name'])
			constrained_columns = self.normalize_name(row._mapping['fkcolumn_name'])

			if schema == None:
				referred_schema = None
			else:
				referred_schema = self.normalize_name(row._mapping['pktable_schem'])

			referred_table = self.normalize_name(row._mapping['pktable_name'])
			referred_columns = self.normalize_name(row._mapping['pkcolumn_name'])
			onupdate = row._mapping['update_rule']
			ondelete = row._mapping['delete_rule']
			deferrable = row._mapping['deferrability']
			# The values of UPDATE_RULE, DELETE_RULE, and DEFERRABILITY are all integers.
			# Somewhere as yet undiscovered, they'll probably map to FOREIGN KEY options,
			# such as [ON {DELETE | UPDATE} {CASCADE | SET DEFAULT | SET NULL}]
			# TODO: resolve FK options to strings if required for ReflectedForeignKeys.options

			# Retrieve an existing fk from the list or create a new one...
			# TODO: replace filter with call to _getDictFromList, if faster.
			filtered = tuple(filter(lambda d: 'name' in d and d['name'] == fk_name , reflectedForeignKeys))
			if(len(filtered) > 0):
				fk = filtered[0] # fk found
			else:
				# Create a new fk dictionary.
				# TODO: consider using the default dictionary instead, provided by ReflectionDefaults.foreign_keys, as used by PG and Oracle dialects.
				fk = {
					'name': fk_name, # ReflectedConstraint.name
					'constrained_columns': [],
					'referred_schema': referred_schema,
					'referred_table': referred_table,
					'referred_columns': [],
					'options': {
						'onupdate': onupdate,
						'ondelete': ondelete,
						'deferrable': deferrable # Supported?
						# TODO: Constraint deferrability is currently unsupported by HSQLDB. Exclude 'deferrable' from this line dictionary?
					}
				}
				reflectedForeignKeys.append(fk)
			fk['constrained_columns'].append(constrained_columns)
			fk['referred_columns'].append(referred_columns)
		return reflectedForeignKeys

#i  def get_multi_foreign_keys( # Return information about foreign_keys in all tables in the given ``schema``.
	# TODO: for better performance implement get_multi_foreign_keys. (currently only impl. for Oracle and PostgreSQL dialects)

#i  def get_table_names( # """Return a list of table names for ``schema``.
	@reflection.cache
	def get_table_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		cursorResult = connection.exec_driver_sql("""
			SELECT table_name FROM information_schema.tables
			WHERE table_schema = (?)
			AND table_type = 'BASE TABLE'
		""", (self.denormalize_name(schema),))
		return list(map(self.normalize_name, cursorResult.scalars().all()))

#i  def get_temp_table_names( # Return a list of temporary table names on the given connection, if supported by the underlying backend.
	@reflection.cache
	def get_temp_table_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		cursorResult = connection.exec_driver_sql("""
			SELECT table_name FROM information_schema.system_tables
			WHERE table_type = 'GLOBAL TEMPORARY' AND table_schem = (?)
		""", (self.denormalize_name(schema),))
		return cursorResult.scalars().all()
	# HSQLDB supports two types of temporary table, global and local.
	# Are local temporary table names discoverable through INFORMATION_SCHEMA? It seems not.

#i  def get_view_names( # """Return a list of all non-materialized view names available in the database.
	@reflection.cache
	def get_view_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		cursorResult = connection.exec_driver_sql("""
			SELECT table_name FROM information_schema.tables
			WHERE table_schema = (?)
			AND table_type = 'VIEW'
		""",(self.denormalize_name(schema),))
		return list(map(self.normalize_name, cursorResult.scalars().all()))

#i  def get_materialized_view_names( #Return a list of all materialized view names available in the database.
	@reflection.cache
	def get_materialized_view_names(self, connection, schema=None, **kw):
		raise NotImplementedError()
	# According to Fred Toussi, "HSQLDB does not support materialized views directly. You can use database triggers to update tables acting as materialized views."

#i  def get_sequence_names( # Return a list of all sequence names available in the database.
	@reflection.cache
	def get_sequence_names(self, connection, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		cursorResult = connection.exec_driver_sql("""
			SELECT sequence_name FROM information_schema.sequences
			WHERE sequence_schema = (?)
		""", (self.denormalize_name(schema),))
		return cursorResult.scalars().all()

#i  def get_temp_view_names( # Return a list of temporary view names on the given connection, if supported by the underlying backend.
	@reflection.cache
	def get_temp_view_names(self, connection, schema=None, **kw):
		raise NotImplementedError()
	# According to Claude HSQLDB doesn't support temporary views.

#i  def get_schema_names( # Return a list of all schema names available in the database.
	@reflection.cache
	def get_schema_names(self, connection, **kw):
		self._ensure_has_table_connection(connection)
		cursorResult = connection.exec_driver_sql("SELECT schema_name FROM information_schema.schemata")
		return list(map(self.normalize_name, cursorResult.scalars().all()))

#i  def get_view_definition( # Return plain or materialized view definition.
	@reflection.cache
	def get_view_definition(self, connection, view_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		cursorResult = connection.exec_driver_sql("""
			SELECT view_definition FROM information_schema.views
			WHERE table_name = (?)
			AND table_schema = (?)
		""", (self.denormalize_name(view_name), self.denormalize_name(schema)))
		view_def = cursorResult.scalar()
		if view_def:
			return view_def
		else:
			raise exc.NoSuchTableError(f"{schema}.{view_name}" if schema else view_name)

#i  def get_indexes(
	@reflection.cache
	def get_indexes(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		reflectedIndexList = []
		query = """
			SELECT
			table_schem
			,table_name
			,index_name
			,column_name
			-- expressions
			,non_unique
			-- include_columns
			,asc_or_desc
			--, cst.constraint_name = index_name AS duplicates_constraint
			, cst.constraint_type
			FROM information_schema.system_indexinfo
			LEFT JOIN information_schema.table_constraints cst
			ON index_name = cst.constraint_name
			--AND table_name = cst.table_name
			AND table_schem = cst.table_schema
			WHERE table_schem = (?) AND table_name = (?)
		"""
		# TODO: removed commented out fields from above query.
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(schema), self.denormalize_name(table_name)))

		rows = cursorResult.all()
		if len(rows) == 0 and self.has_table(connection, table_name, schema) == False:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		
		for row in rows:
			index_name = self.normalize_name(row._mapping['index_name'])
			constraint_type = row._mapping['constraint_type'] # PRIMARY KEY | FOREIGN KEY | UNIQUE. If NULL, the index doesn't duplicate a constraint.

			# Primary keys and unique constraints are both unique, so we can simply use the non_unique field here...
			unique = not(row._mapping['non_unique'])

			idx = _getDictFromList('name', index_name, reflectedIndexList)
			if idx == None: # i.e. not already in reflectedIndexList...
				idx = {
					'name': index_name,
					'column_names': [],
					# 'expressions': [], # Not required. Unsuppored by HSQLDB?
					'unique': unique,
					# 'duplicates_constraint': # Not required
					# 'include_columns': None, # Deprecated
					'column_sorting': {}, # Not required
					# 'dialect_options': None # Not required.
				}
				reflectedIndexList.append(idx)

			column_name = self.normalize_name(row._mapping['column_name']) # list; if none, returned in expressions list
			idx['column_names'].append(column_name)

			# expressions = None
			# TODO: Is the expressions list applicable to HSQLDB?

			if constraint_type != None and False: # Temporarily disabled
				# A non-null constraint_type indicates the index and constraint names matched, so...
				idx['duplicates_constraint'] = constraint_name = index_name
			# Indexes that duplicate a constraint should possess the 'duplicates_constraint' key,
			# but Inspector._reflect_indexes excludes such indexes from the Table.indexes collection,
			# which causes ComponentReflectionTest.test_get_unique_constraints_hsqldb to fail.
			# For this reason assignment of the duplicates_constraint key above
   			# has been disabled until the correct solution is known.
			# See JSN_notes.md for more detail.
			# TODO: review 'duplicates_constraint' key and re-enable if appropriate.

			# idx['include_columns'] = # NotRequired[List[str]] # deprecated 2.0

			column_sorting = idx.get('column_sorting')
			assert column_sorting != None, 'column_sorting is None'
			# TODO: remove assertion when done

			asc_or_desc = row._mapping['asc_or_desc'] # Can be 'A', 'D', or null
			if(asc_or_desc == 'A'):
				column_sorting[column_name] = ('asc',)
			asc_or_desc = row._mapping['asc_or_desc']
			if(asc_or_desc == 'D'):
				column_sorting[column_name] = ('desc',)
			# The tuples for each item in the column_sorting dictionary may
			# contain 'asc', 'desc', 'nulls_first', 'nulls_last'.
			# HSQLDB doesn't appear to have a field for nulls first / last,
			# and only ascending ordering has been observed so far.
			assert asc_or_desc == 'A' or asc_or_desc == 'D'
			# TODO: remove the assertion and revise comments above.

			if False:
				# The SYSTEM_INDEXINFO table has a few more columns which
				# haven't been queried for. If these are useful, update the
				# query and they can be added as dialect_options...
				idx['dialect_options'] = {
					'type': row._mapping['TYPE'],
					'ordinal_position': row._mapping['ORDINAL_POSITION'],
					'cardinality': row._mapping['CARDINALITY'],
					'pages': row._mapping['PAGES'],
					'filter_condition': row._mapping['FILTER_CONDITION'],
					'row_cardinality': row._mapping['ROW_CARDINALITY'],
				}
				# TODO: remove this block of code if unused.

		return reflectedIndexList


#i  def get_multi_indexes(
	# TODO: for better performance implement get_multi_indexes.	

#i  def get_unique_constraints(
	@reflection.cache
	def get_unique_constraints(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		reflectedUniqueConstraint = []
		query = """
			SELECT constraint_name, column_name FROM information_schema.table_constraints
			JOIN information_schema.system_indexinfo
			ON index_name = constraint_name
			WHERE constraint_type = 'UNIQUE'
			AND table_name = (?)
			AND constraint_schema = (?)
		"""
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(table_name), self.denormalize_name(schema)))

		rows = cursorResult.all()
		if len(rows) == 0 and self.has_table(connection, table_name, schema) == False:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		
		for row in rows:
			ct_name = index_name = self.normalize_name(row._mapping['constraint_name'])
			ct = _getDictFromList('name', ct_name, reflectedUniqueConstraint)
			if ct == None:
				ct = {
					'name': ct_name, # ReflectedConstraint.name
					'column_names': [],
					'duplicates_index': index_name,
					# 'dialect_options': {}
				}
				reflectedUniqueConstraint.append(ct)
			column_name = self.normalize_name(row._mapping['column_name'])
			ct['column_names'].append(column_name)
		return reflectedUniqueConstraint

#i  def get_multi_unique_constraints(
	# TODO: for better performance implement get_multi_unique_constraints.	

#i  def get_check_constraints(
	@reflection.cache
	def get_check_constraints(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		reflectedCheckConstraint = []
		query = """
			SELECT a.constraint_name, b.check_clause FROM information_schema.table_constraints a
			JOIN information_schema.check_constraints b
			ON a.constraint_name = b.constraint_name
			AND a.constraint_schema = b.constraint_schema
			AND a.constraint_catalog = b.constraint_catalog
			WHERE table_name = (?)
			AND table_schema = (?)
		"""
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(table_name), self.denormalize_name(schema)))

		rows = cursorResult.all()
		if len(rows) == 0 and self.has_table(connection, table_name, schema) == False:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		
		for row in rows:
			constraint_name = self.normalize_name(row._mapping['constraint_name'])
			check_clause = self.normalize_name(row._mapping['check_clause'])
			constraint = {
				'name': constraint_name,
				'sqltext': check_clause
			}
			reflectedCheckConstraint.append(constraint)
		return reflectedCheckConstraint

#i  def get_multi_check_constraints(
	# TODO: for better performance implement get_multi_check_constraints.	

#i  def get_table_options(; # """Return a dictionary of options specified when ``table_name`` was created.
	@reflection.cache
	def get_table_options(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		tableOptions = {}
		query = """
			SELECT
			--table_name, 
			table_type, hsqldb_type, commit_action FROM information_schema.system_tables
			WHERE table_name = (?)
			AND table_schem = (?)
			--AND table_cat = 'PUBLIC'
			--AND table_type != 'VIEW'
		"""
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(table_name), self.denormalize_name(schema)))
		row = cursorResult.first()
		if not row:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		assert row is not None, 'Row is None.'

		# table_name = row._mapping['TABLE_NAME']
		table_type = row._mapping['table_type']			# GLOBAL TEMPORARY | more...
		hsqldb_type = row._mapping['hsqldb_type']		# MEMORY | CACHED | TEXT
		on_commit = row._mapping['commit_action']  	# DELETE | PRESERVE | NULL

		# The table type options in HSQLDB are: [MEMORY | CACHED | [GLOBAL] TEMPORARY | TEMP | TEXT ]

		# Table type information is stored in one of two columns depending on the type.
		# All* temporary types are stored as 'GLOBAL TEMPORARY' in the TABLE_TYPE column,
		# while MEMORY, CACHED, and TEXT types are recorded in the HSQLDB_TYPE column.
		# [* Possibly incorrect. Local temporary tables, a.k.a session tables, are not schema objects. See: (https://hsqldb.org/doc/2.0/guide/sessions-chapt.html)]

		_table_type_key_name = 'hsqldb_type'
		# The tableOptions key chosen originally was just 'type', but this
		# results in an error when the options are validated by the
		# DialectKWArgs._validate_dialect_kwargs method, which reports...
		# 	TypeError: Additional arguments should be named <dialectname>_<argument>, got 'type'
		# Changing the key to 'hsqldb_type' appears to fix the issue.

		# Combine type information from two columns into a single key value...
		if table_type.find('TEMP') >= 0:
			# GLOBAL TEMPORARY | TEMPORARY | TEMP
			tableOptions[_table_type_key_name] = table_type
			# TODO: confirm all temporary types are treated as global temporary, and there's no other way to identify the different types of temporary table.
		else:
			# MEMORY | CACHED | TEXT
			tableOptions['%s_%s' % (self.name, 'type')] = hsqldb_type
		
		# TODO: confirm using a single key is the correct approach.
		# TODO: Additional settings for TEXT tables are configured separately. Consider exposing them here.

		if on_commit != None:
			tableOptions['%s_%s' % (self.name, 'on_commit')] = on_commit # DELETE | PRESERVE | NULL

		return tableOptions
		# TODO: Document the TableOptions attributes defined in get_table_options

#i  def get_multi_table_options( # Return a dictionary of options specified when the tables in the given schema were created.
	# TODO: for better performance implement get_multi_table_options.	

#i  def get_table_comment(; ...  ) -> ReflectedTableComment:
	@reflection.cache
	def get_table_comment(self, connection, table_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		query = """
			SELECT remarks FROM information_schema.system_tables
			WHERE table_name = (?)
			AND table_schem = (?)
		"""
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(table_name), self.denormalize_name(schema)))
		row = cursorResult.first()
		if not row:
			raise exc.NoSuchTableError(f"{schema}.{table_name}" if schema else table_name)
		return {"text": row[0]}

#i  def get_multi_table_comment(
	# TODO: for better performance implement get_multi_table_comment.	

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
			"""SELECT * FROM information_schema.tables
			WHERE table_schema = (?)
			AND table_name = (?)
			""", (self.denormalize_name(schema), self.denormalize_name(table_name)))
		return cursorResult.first() is not None
	# Tables are identified by catalog, schema, and table name in HSQLDB.
	# It's possible two tables could share matching schema and table names,
	# but in a different catalog, which might break the function above.

#i  def has_index(
	@reflection.cache
	def has_index(self, connection, table_name, index_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		query = """
			SELECT COUNT(*) FROM information_schema.system_indexinfo
			WHERE index_name = (?)
			AND table_name = (?)
			AND table_schem = (?)
			LIMIT 1
		"""
		cursorResult = connection.exec_driver_sql(query, (
			self.denormalize_name(index_name),
			self.denormalize_name(table_name),
			self.denormalize_name(schema)
			))
		return cursorResult.scalar() > 0
		# TODO: raise exc.NoSuchTableError when required

#i  def has_sequence(
	@reflection.cache
	def has_sequence(self, connection, sequence_name, schema=None, **kw):
		self._ensure_has_table_connection(connection)
		if schema is None:
			schema = self.default_schema_name
		query = """
			SELECT COUNT(*) FROM information_schema.sequences
			WHERE sequence_name = '{sequence_name}'
			AND sequence_schema = '{schema}'
			LIMIT 1
		"""
		cursorResult = connection.exec_driver_sql(query, (
			self.denormalize_name(sequence_name),
			self.denormalize_name(schema)
			))
		return cursorResult.scalar() > 0
		# TODO: raise exc.NoSuchTableError when required

#i  def has_schema(
	@reflection.cache
	def has_schema(self, connection, schema_name, **kw):
		self._ensure_has_table_connection(connection)
		query = """
			SELECT COUNT(*) FROM information_schema.schemata
			WHERE schema_name = (?)
			--AND catalog_name = 'PUBLIC'
		"""
		cursorResult = connection.exec_driver_sql(query, (self.denormalize_name(schema_name),))
		return cursorResult.scalar() > 0
		# TODO: cater for multiple catalogs

#i  def _get_server_version_info(self, connection: Connection) -> Any:
	def _get_server_version_info(self, connection):
		return connection.exec_driver_sql("CALL DATABASE_VERSION()").scalar()

#i  def _get_default_schema_name(self, connection: Connection) -> str:
	def _get_default_schema_name(self, connection):
		return connection.exec_driver_sql("VALUES(CURRENT_SCHEMA)").scalar()

#i  def do_begin(self, dbapi_connection: PoolProxiedConnection) -> None:
	def do_begin(self, dbapi_connection):
		return super().do_begin(dbapi_connection)
	# TODO: inherit from default dialect, i.e. just comment out this implementation

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
	#- def do_rollback(self, dbapi_connection): # Inherit from DefaultDialect

#i  def do_commit(self, dbapi_connection: PoolProxiedConnection) -> None:
	#- def do_commit(self, dbapi_connection): # Inherit from DefaultDialect

#i  def do_terminate(self, dbapi_connection: DBAPIConnection) -> None:
	#-  def do_terminate(... # Inherit from DefaultDialect

#i  def do_close(self, dbapi_connection: DBAPIConnection) -> None:
	#- def do_close(self, dbapi_connection): # Inherit from DefaultDialect

#i  def _do_ping_w_event(self, dbapi_connection: DBAPIConnection) -> bool:
	#- Don't implement.

#i  def do_ping(self, dbapi_connection: DBAPIConnection) -> bool: # """ping the DBAPI connection and return True if the connection is usable."""
	def do_ping(self, dbapi_connection):
		# Temporarily overriding to discover when DefaultDialect.do_ping gets called.
		raise NotImplementedError()
	# TODO: verify DefaultDialect.do_ping works with HSQLDB.

#i  def do_set_input_sizes(
	#- def do_set_input_sizes( # inherit from Dialect

#i  def create_xid(self) -> Any:
	#- def create_xid(self) -> Any: # Inherit from DefaultDialect

#i  def do_savepoint(self, connection: Connection, name: str) -> None:
	#-  def do_savepoint( # inherit from DefaultDialect

#i  def do_rollback_to_savepoint(
	#-  def do_rollback_to_savepoint( inherit from DefaultDialect
	# TODO: HSQLDB's ROLLBACK [WORK] TO SAVEPOINT has an optional keyword. What is it and does it need implementing?

#i  def do_release_savepoint(self, connection: Connection, name: str) -> None:
	#-  def do_release_savepoint( # Inherit from DefaultDialect

#i  def do_begin_twophase(self, connection: Connection, xid: Any) -> None:
	def do_begin_twophase(self, connection, xid):
		"""Begin a two phase transaction on the given connection.
		:param connection: a :class:`_engine.Connection`.
		:param xid: xid
		"""
		#- print(f'### do_begin_twophase: xid={xid}')
		self.do_begin(connection.connection)

#i  def do_prepare_twophase(self, connection: Connection, xid: Any) -> None:
	def do_prepare_twophase(self, connection, xid):
		"""Prepare a two phase transaction on the given connection.
		:param connection: a :class:`_engine.Connection`.
		:param xid: xid
		"""
		pass

#i def do_rollback_twophase(
	def do_rollback_twophase(self, connection, xid, is_prepared=True, recover=False):
		"""Rollback a two phase transaction on the given connection.
		:param connection: a :class:`_engine.Connection`.
		:param xid: xid
		:param is_prepared: whether or not :meth:`.TwoPhaseTransaction.prepare` was called.
		:param recover: if the recover flag was passed.
		"""
		self.do_rollback(connection.connection)

#i  def do_commit_twophase(
	def do_commit_twophase(self, connection, xid, is_prepared=True, recover=False): 
		"""Commit a two phase transaction on the given connection.
		:param connection: a :class:`_engine.Connection`.
		:param xid: xid
		:param is_prepared: whether or not
		:meth:`.TwoPhaseTransaction.prepare` was called.
		:param recover: if the recover flag was passed.
		"""
		if not is_prepared:
			self.do_prepare_twophase(connection, xid)
		self.do_commit(connection.connection)

#i  def do_recover_twophase(self, connection: Connection) -> List[Any]:
	def do_recover_twophase(self, connection):
		"""Recover list of uncommitted prepared two phase transaction identifiers on the given connection.
		:param connection: a :class:`_engine.Connection`.
		"""
		raise NotImplementedError("Recover two phase query for HyperSqlDialect not implemented.")

# TODO: fully implement and test the five methods above for two-phase transactions. For more info see JSN_notes.md and scratch_twophase.py

#i  def _deliver_insertmanyvalues_batches(
	#- Don't implement.

#i  def do_executemany(
	#- Inherit from DefaultDialect

#i  def do_execute(
	#- Inherit from DefaultDialect

#i  def do_execute_no_params(
	#- Inherit from DefaultDialect

#i  def is_disconnect(
	def is_disconnect(self, e, connection, cursor):
		"""Return True if the given DB-API error indicates an invalid connection"""
		if isinstance(e, (
			# self.dbapi.InterfaceError,	# my, pg
			self.dbapi.DatabaseError,
			# self.dbapi.DataError,
			# self.dbapi.OperationalError,	# my
			# self.dbapi.IntegrityError,
			# self.dbapi.InternalError,
			# self.dbapi.ProgrammingError,	# my
			# self.dbapi.NotSupportedError,
			)):
			# TODO: remove any commented out errors above that don't apply.
			return True

		# Log unhandled exceptions...
		if isinstance(e, (self.dbapi.Error, self.dbapi.Warning)): # TODO: remove 'True or'
			print('### repr e:', repr(e))
			print('### repr self.dbapi.Error:', repr(self.dbapi.Error))
			print('### repr self.dbapi.Warning:', repr(self.dbapi.Warning))
			print('### str e:', str(e))
			breakpoint() #-
			raise NotImplementedError("Unhandled exception. Update the method 'HyperSqlDialect.is_disconnect'")
		# TODO: Remove the above test

		return False
	# Unsure which errors are regarded as an 'invalid connection',
	# or what may trigger them, apart from statement 'DISCONNECT'.
	# TODO: remove exploratory code from the is_disconnect function.

#i  def connect(self, *cargs: Any, **cparams: Any) -> DBAPIConnection:
	#- Inherit from DefaultDialect

#i  def on_connect_url(self, url: URL) -> Optional[Callable[[Any], Any]]:
	def on_connect_url(self, url):
		from sqlalchemy.engine.url import URL
		isolation_level = url.query.get('isolation_level', None)
		def do_on_connect(conn):
			if isolation_level:
				self.set_isolation_level(conn, isolation_level)
		return do_on_connect
	#i This is used to set dialect-wide per-connection options such as isolation modes, Unicode modes, etc.

#i  def on_connect(self) -> Optional[Callable[[Any], Any]]:
	def on_connect(self):
		def do_on_connect(connection):
			# connection.execute("SET SPECIAL FLAGS etc")
			pass
		return do_on_connect
	# This is used to set dialect-wide per-connection options such as isolation modes, Unicode modes, etc.
	# No event listener is generated if on_connect returns None instead of a callable.
	# TODO: remove on_connect function if unused

#i  def reset_isolation_level(self, dbapi_connection: DBAPIConnection) -> None:
	#- Inherit from DefaultDialect

#i  def set_isolation_level(
	def set_isolation_level(self, dbapi_connection, level):
		if level == "AUTOCOMMIT":
			dbapi_connection.jconn.setAutoCommit(True)
		else:
			dbapi_connection.jconn.setAutoCommit(False)
			# Use a tuple to look up index values for isolation levels...
			index = ('NONE', 'READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE').index(level) # order critical
			dbapi_connection.jconn.setTransactionIsolation(index)
	# The ordering of isolation levels must match the constants defined in org.hsqldb.jdbc.JDBCConnection
	# The JayDeBeApi Connection object currently lacks an autocommit attribute or setautocommit() method.

#i  def get_isolation_level(
	def get_isolation_level(self, dbapi_connection):
		"""Given a DBAPI connection, return its isolation level."""
		with dbapi_connection.cursor() as cursor:
			cursor.execute("CALL SESSION_ISOLATION_LEVEL()") # Returns READ COMMITTED or SERIALIZABLE
			row = cursor.fetchone()
		return row[0].upper()

#i  def get_default_isolation_level(
	def get_default_isolation_level(self, dbapi_connection):
		try:
			with dbapi_connection.cursor() as cursor:
				cursor.execute('CALL DATABASE_ISOLATION_LEVEL()') # Returns READ COMMITTED or SERIALIZABLE
				row = cursor.fetchone()
			return row[0].upper()
		except:
			return 'READ COMMITTED' # HSQLDB's default isolation level
		# DATABASE_ISOLATION_LEVEL() returns the isolation level for all new sessions.
		# SESSION_ISOLATION_LEVEL() returns the level for the current session.
		# Both functions will return the same value on first connection, the point at which get_default_isolation_level is called,
		# so I presume we could use either.
		# However calling get_default_isolation_level again (unsure if this ever happens) after an isolation level has changed
		# will return different values depending on which built-in function was used. We probably want DATABASE_ISOLATION_LEVEL().
		#
		# Should we also be returning AUTOCOMMIT?  I don't currently think so. 

	# Isolation level functions
	# HSQLDB supported isolation levels are documented here - https://hsqldb.org/doc/2.0/guide/sessions-chapt.html
	# 	i.e. READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ and SERIALIZABLE
	# Documentation for members of the Dialect interface can be found here - \sqlalchemy\engine\interfaces.py
	# TODO: Reorder the position of member to match interface.py

#i  def get_isolation_level_values(
	def get_isolation_level_values(self, dbapi_conn):
		return (
			"AUTOCOMMIT",		# HSQLDB supports autocommit.
			"READ UNCOMMITTED", # HSQLDB treats a READ COMMITTED + read only
			"READ COMMITTED",
			"REPEATABLE READ",	# HSQLDB upgrades REPEATABLE READ to SERIALIZABLE
			"SERIALIZABLE"
		)
	#- Documented in \sqlalchemy\engine\interfaces.py, line 2495
	#
	# SQLAlchemy treats AUTOCOMMIT like an isolation level.
	# HSQLDB supports AUTOCOMMIT, but how autocommit and isolation levels are set differs.
	# e.g.
	#		SET AUTOCOMMIT FALSE
	#		SET TRANSACTION ISOLATION LEVEL SERIALIZABLE
	#
	# Some logic is surely required to set autocommit or isolation level, but where?
	#
	# Isolation levels and autocommit are separate in HSQLDB, as in MySQL.
	# get_isolation_level_values function for MySQL doesn't include AUTOCOMMIT, although MySQL's base.py describes it as a valid value.
	# MySQL's base.py also says... "For the special AUTOCOMMIT isolation level, DBAPI-specific techniques are used".
	#
	# SQLAlchemy documentation examples show autocommit being set, such as...
	#	with engine.connect() as connection:
	#		connection.execution_options(isolation_level="AUTOCOMMIT")
	#
	# So, where do execution pathS for AUTOCOMMIT and ISOLATION LEVELs diverge?
	# TODO: check the definitions for execution_options function on engine and connection classes.

#i  def _assert_and_set_isolation_level(
	#- def _assert_and_set_isolation_level( # Inherit from DefaultDialect

#i  def get_dialect_cls(cls, url: URL) -> Type[Dialect]:
	#- Inherit from Dialect

#i  def get_async_dialect_cls(cls, url: URL) -> Type[Dialect]:
	#- Inherit from Dialect

#i  def load_provisioning(cls) -> None:
	#- Inherit from DefaultDialect

#i  def engine_created(cls, engine: Engine) -> None:
	#- Inherit from Default Dialect

#i  def get_driver_connection(self, connection: DBAPIConnection) -> Any:
	#- Inherit from DefaultDialect

#i  def set_engine_execution_options(
	#- Inherit from DefaultDialect

#i  def set_connection_execution_options(
	#- Inherit from DefaultDialect

#i  def get_dialect_pool_class(self, url: URL) -> Type[Pool]:
	#- Inherit from DefaultDialect

	supports_schemas = True # Setting 'supports_schemas' to false disables schema level tests.
	# TODO: remove line above, i.e. inherit from DefaultDialect.supports_schemas

	#- ok
	supports_is_distinct_from = True
	# Supported since HSQLDB v2.0
	#- Default is True. Access's dialect is set to False.
	#-
	#- e.g. SELECT * FROM mytable WHERE col1 IS DISTINCT FROM col2;
	#- So you can use expressions like col1.is_distinct_from(col2) in SQLAlchemy when using the HSQLDB dialect.
	# TODO: find out where the above property is from - it's not part of the Dialect interface.

	# poolclass = pool.NullPool #- temporarily assigned to NullPool
	poolclass = pool.QueuePool
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


