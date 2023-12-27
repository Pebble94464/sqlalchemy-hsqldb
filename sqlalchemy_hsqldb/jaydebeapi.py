
# TODO: Implement the jdbc driver in this file.
# TODO1: fix "AttributeError("'HyperSqlDialect_jaydebeapi' object has no attribute '_on_connect_isolation_level'")"

from .base import HyperSqlDialect
from types import ModuleType
from sqlalchemy.engine.url import make_url
from sqlalchemy.engine.url import URL

class HyperSqlDialect_jaydebeapi(HyperSqlDialect):
	"""HyperSqlDialect implementation of Dialect using JayDeBeApi as the driver."""

	driver = 'jaydebeapi'
	jclassname = 'org.hsqldb.jdbc.JDBCDriver'

	supports_statement_cache = False
	# TODO: The supports_statement_cache must be present in both this class and its parent. Set the value to True when ready.

	# TODO: Clean up the init function below after debugging. Is the method actually required?
	def __init__(self, **kwargs):
		HyperSqlDialect.__init__(self,**kwargs)

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
		return __import__("jaydebeapi")
	#- The Access dialect sets module.pooling = (False). What's that?

