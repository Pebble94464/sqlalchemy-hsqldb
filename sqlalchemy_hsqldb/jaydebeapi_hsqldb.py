# JSN 2024

# WIP: Figure out how the jaydebeapi module is loaded and where to insert the code in this file

"""
Jaydebeapi by default returns timestamps, dates and times as strings.
This script provides new conversion functions that return objects instead of
strings for datetime, date and time objects.
"""
import datetime as dt
import jaydebeapi as jdb

def _get_calendar():
	# This function shows how we might get a Calendar object jpype, but is
	# currently unused. Document for future reference and delete when done.
	import jpype
	return jpype.java.util.Calendar.getInstance()
	# TODO: delete _get_calendar function if unused

# Redefine some jaydebeapi conversion functions...
# result set (rs), column index (col)
# rs is a <java class 'org.hsqldb.jdbc.JDBCResultSet'> 'https://hsqldb.org/doc/2.0/apidocs/org.hsqldb/org/hsqldb/jdbc/JDBCResultSet.html'

def _to_datetime(rs, col) -> (dt.datetime | None):
	'''Convert from java.sql.Timestamp to datetime.datetime'''
	obj = rs.getTimestamp(col)
	if not obj:
		return None
	assert str(obj.__class__) == "<java class 'java.sql.Timestamp'>"
	year = obj.getYear() + 1900
	month = obj.getMonth() + 1
	day = obj.getDate()
	hours = obj.getHours()
	minutes = obj.getMinutes()
	seconds = obj.getSeconds()
	microseconds = int(obj.getNanos() / 1000)
	return dt.datetime(year, month, day, hours, minutes, seconds, microseconds)

def _to_datetime_with_timezone(rs, col) -> (dt.datetime | None):
	'''Convert from java.time.OffsetDateTime to datetime.datetime'''
	obj = rs.getObject(col)
	if not obj:
		return None
	assert str(obj.__class__) == "<java class 'java.time.OffsetDateTime'>"
	year = obj.getYear()
	month = obj.getMonthValue()
	day = obj.getDayOfMonth()
	hour = obj.getHour()
	minute = obj.getMinute()
	second = obj.getSecond()
	microsecond = int(obj.getNano() / 1000)
	zone_offset = obj.getOffset() # <java class 'java.time.ZoneOffset'>
	offset_seconds = zone_offset.getTotalSeconds()
	tzinfo1 = dt.timezone(dt.timedelta(seconds=offset_seconds))
	return dt.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo1)

def _to_date(rs, col) -> (dt.date | None):
	'''Convert from java.sql.Date to datetime.date'''
	obj = rs.getDate(col)
	if not obj:
		return None
	assert str(obj.__class__) == "<java class 'java.sql.Date'>"
	year = obj.getYear() + 1900
	month = obj.getMonth() + 1
	day = obj.getDate()
	return dt.date(year, month, day)

def _to_time(rs, col) -> (dt.time | None):
	'''Convert from java.sql.Time to datetime.time'''
	obj = rs.getTime(col)
	if not obj:
		return None
	assert str(obj.__class__) == "<java class 'java.sql.Time'>"
	hours = obj.getHours()
	minutes = obj.getMinutes()
	seconds = obj.getSeconds()
	return dt.time(hours, minutes, seconds)

def _to_time_with_timezone(rs, col) -> (dt.time | None):
	'''Convert from java.time.ZoneOffset to datetime.time'''
	obj = rs.getObject(col) # <java class 'java.time.ZoneOffset'>
	if not obj:
		return None
	assert str(obj.__class__) == "<java class 'java.time.ZoneOffset'>"
	hour = obj.getHour()
	minute = obj.getMinute()
	second = obj.getSecond()
	zone_offset = obj.getOffset() # <java class 'java.time.ZoneOffset'>
	offset_seconds = zone_offset.getTotalSeconds()
	tzinfo1 = dt.timezone(dt.timedelta(seconds=offset_seconds))
	return dt.time(hour, minute, second, tzinfo=tzinfo1)

def _intercept_unknown_types(rs, col) -> None:
	'''Replacement for jaydebeapi's _unknownSqlTypeConverter method, to display additional debugging info.'''
	from sys import _getframe
	file_name = _getframe().f_code.co_filename
	function_name = _getframe().f_code.co_name
	line_number = _getframe().f_lineno
	java_val = rs.getObject(col)
	column_type_name = str(rs.getMetaData().getColumnTypeName(col))
	print('Debugging info...')
	print('\tJava type: \t', type(java_val))
	print('\tColumn type: \t', column_type_name)
	print('\tValue: \t\t', str(java_val))
	print(f'\tFile: \t\t {file_name}:{line_number}')
	print('An entry can be added to _DEFAULT_CONVERTERS to resolve this issue.')
	raise TypeError(f'Unrecognized type in function {function_name!r}')
jdb._unknownSqlTypeConverter = _intercept_unknown_types
# TODO: The above function can be removed when all types have been identified.


jdb._DEFAULT_CONVERTERS['TIMESTAMP'] = _to_datetime
jdb._DEFAULT_CONVERTERS['TIMESTAMP_WITH_TIMEZONE'] = _to_datetime_with_timezone
jdb._DEFAULT_CONVERTERS['DATE'] = _to_date
jdb._DEFAULT_CONVERTERS['TIME'] = _to_time
jdb._DEFAULT_CONVERTERS['TIME_WITH_TIMEZONE'] = _to_time_with_timezone

breakpoint()
jdb.DATETIME.values += ('TIME_WITH_TIMEZONE',)

if __name__ == '__main__':
	pass

#- Possible column types... (see http://download.oracle.com/javase/8/docs/api/java/sql/Types.html)
#- ARRAY
#- BIGINT
#- BINARY, jdb
#- BIT, jdb
#- BLOB
#- BOOLEAN, jdb
#- CHAR
#- CLOB
#- DATALINK
#- DATE, jdb, hyp
#- DECIMAL, jdb
#- DISTINCT
#- DOUBLE, jdb
#- FLOAT, jdb
#- INTEGER, jdb
#- JAVA_OBJECT
#- LONGNVARCHAR
#- LONGVARBINARY
#- LONGVARCHAR
#- NCHAR
#- NCLOB
#- NULL
#- NUMERIC, jdb
#- NVARCHAR
#- OTHER
#- REAL
#- REF
#- REF_CURSOR
#- ROWID
#- SMALLINT, jdb
#- SQLXML
#- STRUCT
#- TIME, jdb, hyp
#- TIME_WITH_TIMEZONE, hyp
#- TIMESTAMP, jdb, hyp
#- TIMESTAMP_WITH_TIMEZONE, hyp
#- TINYINT, jdb
#- VARBINARY
#- VARCHAR
