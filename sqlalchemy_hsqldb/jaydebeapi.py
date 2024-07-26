
# TODO: Implement the jdbc driver in this file.
# TODO1: fix "AttributeError("'HyperSqlDialect_jaydebeapi' object has no attribute '_on_connect_isolation_level'")"
#		 Isolation level can be passed as a query string parameter, e.g.
#			hsqldb+jaydebeapi://SA:@localhost:9001/test2?isolation_level=READ+COMMITTED
#		 HyperSqlDialect.on_connect_url method is then used to set dialect-wide per-connection options such as isolation mode.

from .base import HyperSqlDialect
from .base import HyperSqlExecutionContext
from types import ModuleType
from sqlalchemy.engine.url import make_url
from sqlalchemy.engine.url import URL
import datetime as dt

#WIP: execution context -->
class HyperSqlExecutionContext_jaydebeapi(HyperSqlExecutionContext):
#j create_cursor ; ec ; dec ; o_cx
	def create_cursor(self):
		print('### HyperSqlExecutionContext_jaydebeapi.create_cursor') #-
		# c = self._dbapi_connection.cursor() # DefaultExecutionContext._dbapi_connection
		# return c
		# breakpoint() #-
		return super().create_cursor()
	# TODO: remove this override if unused

	#- "Some dialects may wish to change the behavior of connection.cursor(),
	#- such as postgresql which may return a PG "server side" cursor."

	#- # oracle_cx overrides create_cursor, presumeably because of 'arraysize'...
	#-def create_cursor_oracle_cx(self):
	#-	c = self._dbapi_connection.cursor()
	#-	if self.dialect.arraysize:
	#-		c.arraysize = self.dialect.arraysize
	#-	return c

#j create_default_cursor ; dec ; my_ma
	def create_default_cursor(self):
		# aka client-side cursor, or buffered cursor.
		# breakpoint() #-
		return super().create_default_cursor()
	#- Maria db returns self._dbapi_connection.cursor(buffered=True)
	#- Attempting buffered=True with HSQDB results in...
	#- sqlalchemy.exc.StatementError: (builtins.TypeError) Connection.cursor() got an unexpected keyword argument 'buffered'
	# TODO: remove if unused


#j create_server_side_cursor ; dec ; my ; my_ma ; pgc ; pg_a ; pg_pg8 ; sl_a
	def create_server_side_cursor(self):
		print('### HyperSqlexecutionContext_jaydebeapi.create_server_side_cursor') #- This defo fires!
		# return HyperSqlExecutionContext.create_server_side_cursor(self)
		return super().create_server_side_cursor()
		# raise NotImplementedError
		# TODO: remove if unused

#j fetchall_for_returning ; ec ; dec ; o_cx
	def fetchall_for_returning(self):
		raise NotImplementedError

#j get_lastrowid ; dec ; a ; ms ; my_ma ; my_py
	def get_lastrowid(self):
		raise NotImplementedError

#j get_out_parameter_values ; ec ; dec ; o_cx
	def get_out_parameter_values(self):
		raise NotImplementedError

#j handle_dbapi_exception ; ec ; dec ; ms ; pg_a
	def handle_dbapi_exception(self):
		raise NotImplementedError

#j post_exec ; ec ; dec ; ms ; ms_py ; my_ma ; o_cx ; pgc_p2
	def post_exec(self):
		# print('### HypereSqlExecutionContext_jaydebeapi.post_exec') #-
		super().post_exec()
	# TODO: remove if unused

#j pre_exec ; ec ; dec ; ms ; ms_py ; o ; o_cx ; pg_a ; pg_pg8
	def pre_exec(self):
		# print('### HypereSqlExecutionContext_jaydebeapi.pre_exec') #-
		super().pre_exec()
	# TODO: remove if unused

#j rowcount ; dec ; ms ; my_ma ; my_my
	def rowcount(self):
		raise NotImplementedError
	# TODO: remove if unused

#- Note execution context methods can be overriden at both the dialect and connector class levels.
# TODO: remove lines begining with '#j'. These lines list commonly overriden execution context functions





class HyperSqlDialect_jaydebeapi(HyperSqlDialect):
	"""HyperSqlDialect implementation of Dialect using JayDeBeApi as the driver."""

	driver = 'jaydebeapi'
	jclassname = 'org.hsqldb.jdbc.JDBCDriver'

	supports_statement_cache = False
	# TODO: The supports_statement_cache must be present in both this class and its parent. Set the value to True when ready.

	execution_ctx_cls = HyperSqlExecutionContext_jaydebeapi
	#- execution context

	# TODO: Clean up the init function below after debugging. Is the method actually required?
	def __init__(self, **kwargs):
		HyperSqlDialect.__init__(self, **kwargs)

	def create_connect_args(self, url):
		""" Returns a tuple consisting of a ``(*args, **kwargs)`` suitable to send directly to the dbapi's connect function. """
		# Example in parameter 'url' string:	"hsqldb+jaydebeapi://SA:***@localhost:9001/some_database_name"
		# Example 'jdbc_url' string:			"jdbc:hsqldb:hsql://localhost:9001/some_database_name"

		# TODO: url is expected to be a URL object, so the line immediately below can be removed, possibly.
		assert(type(url) is URL)
		url = make_url(url)

		jdbc_url = 'jdbc:hsqldb:hsql://' + url.host
		if url.port != None:
			jdbc_url += ':' + str(url.port)
		jdbc_url += '/' + url.database

		connectionArgs = {
			"jclassname": self.jclassname,
			"url": jdbc_url,
			"driver_args": [url.username, url.password],
			"jars" : self.classpath, # HSQLDB executable jar file
			# "libs" : ""
		}
		return ([], connectionArgs)

# jclassname: Full qualified Java class name of the JDBC driver.
# url: Database url as required by the JDBC driver.
# driver_args: 	Dictionary or sequence of arguments to be passed to the Java DriverManager.getConnection method.
# 				Usually sequence of username and password for the db.
# 				Alternatively a dictionary of connection arguments (where user and password would probably be included).
# 				See http://docs.oracle.com/javase/7/docs/api/java/sql/DriverManager.html for more details
# jars: Jar filename or sequence of filenames for the JDBC driver
# libs: Dll/so filenames or sequence of dlls/sos used as shared library by the JDBC driver

	#- OK
	@classmethod
	def import_dbapi(cls) -> ModuleType:
		m = __import__("jaydebeapi")

		# After the jaydebeapi module is loaded we need update the converters
		# dictionary to point to our redefined functions...
		m._DEFAULT_CONVERTERS['DATE'] = _to_date
		m._DEFAULT_CONVERTERS['TIME'] = _to_time
		m._DEFAULT_CONVERTERS['TIME_WITH_TIMEZONE'] = _to_time_with_timezone
		m._DEFAULT_CONVERTERS['TIMESTAMP'] = _to_datetime
		m._DEFAULT_CONVERTERS['TIMESTAMP_WITH_TIMEZONE'] = _to_datetime_with_timezone

		# We also need to add to DBAPITypeObject._mappings for certain types...
		m.DBAPITypeObject('TIME_WITH_TIMEZONE')
		m.DBAPITypeObject('TIMESTAMP_WITH_TIMEZONE')

		# Notes:
		#	Inside jaydebeapi's __init__.py file the class is instantiated for
		#	each SQL type when the module is loaded, and the results are then
		#	assigned to variables which appear to be unused.  The instantiation
		#	above for 'TIMESTAMP_WITH_TIMEZONE' seems to work fine without the
		#	results being assigned.  But failing to instantiate it for
		#	'TIMESTAMP_WITH_TIMEZONE' causes an error message to be displayed:
		#		"UserWarning: No type mapping for JDBC type
		#		'TIMESTAMP_WITH_TIMEZONE' (constant value 2014).
		# 		Using None as a default type_code."
		#	Further investigation is needed to fully understand how this class
		#	is used.
		# 	DBAPITypeObject._mappings is a dictionary shared by all instances of the class.

		return m

# Jaydebeapi's converter methods return strings by default for for date, time
# and datetime types.  The replacement converter functions below return objects
# instead...

def _to_date(rs, col): # -> (java.sql.date | None):
	'''Returns a java.sql.date object'''
	return rs.getDate(col)

def _to_time(rs, col): # -> (java.sql.Time | None):
	'''Returns a java.sql.Time object'''
	return rs.getTime(col)

def _to_time_with_timezone(rs, col): # -> (java.time.OffsetTime | None):
	'''Returns a java.time.OffsetTime object'''
	return rs.getObject(col)

def _to_datetime(rs, col): # -> (java.sql.Timestamp | None):
	'''Returns a java.sql.Timestamp object'''
	return rs.getTimestamp(col)

def _to_datetime_with_timezone(rs, col): # -> (java.time.OffsetDateTime | None):
	'''Returns a java.time.OffsetDateTime object'''
	return rs.getObject(col)


dialect = HyperSqlDialect_jaydebeapi
# Currently troubleshooting a plug-in loading issue.
# All the other built-in dialects appear to define 'dialect' in their driver files.
# However, the driver for Access does not define 'dialect.
# Update: 'dialect' is now referenced in the module's __init__.py file.
#			This hasn't yet resolved the plug-in loading issue.
# TODO: review whether dialect actually needs defining.

