
# Compile a list of HSQLDB types and determine if equivalent SQLAlchemy type exists,
# or whether we need to create a class for the type.

# SQLAlchemy type naming is important. We need to use CamelCase or UPPERCASE correctly.
# For details, see (\sqlalchemy\lib\sqlalchemy\dialects\type_migration_guidelines.txt)

# [HSQLDB; Chapter 2. SQL Language; Data Types and Operations](https://hsqldb.org/doc/2.0/guide/sqlgeneral-chapt.html#sgc_data_type_guide)


# CamelCase types - db agnostic
# UPPERCASE types - exact types, derived from basic types, SQL types common to two or more DBMSs.
# UPPERCASE back-end specific types - may extend uppercase types with additional parameters, or represent types exclusive to the back-end.
[SQLAlchemy: The Type Hierarchy](https://docs.sqlalchemy.org/en/20/core/type_basics.html)


_Binary # sqlalchemy_type
ARRAY # 
ARRAY # sqlalchemy_type
BIGINT # fixed binary precision, 64-bit
BIGINT # sqlalchemy_type
BigInteger # sqlalchemy_type
BINARY # single byte
BINARY # sqlalchemy_type
BINARY VARYING # alias for VARBINARY?
BINARY(L) # binary string type
BIT # A single bit. Use BOOLEAN instead.
BIT VARYING(L) # alias?
BIT(L) # for bitmaps
BITVARYING(L) # for bitmaps.
BLOB # binary string type
BLOB # sqlalchemy_type

BOOLEAN # can hold TRUE, FALSE or UNKNOWN
Boolean # sqlalchemy_type
BOOLEAN # sqlalchemy_type

/*
The DDL for 'Boolean' will I think render as 'boolean'.
The DDL for BOOLEAN should render as 'BOOLEAN'.

HSQLDB will probably accept 'boolean', although the normal convension is to use uppercase keywords, i.e. 'BOOLEAN'.

HSQLDB's boolean values are TRUE, FALSE and UNKNOWN.
"This type of column can be initialised with Java boolean values, or with NULL for the UNKNOWN value."


Next steps:
	We can create a short script to test how the default settings render. Expect 'boolean'.
	We can adapt our dialect to use the BOOLEAN exact type.
	Try specifying UNKNOWN. Fails, because we're supposed to specify NULL for UNKNOWN
	We can see how other dialects have implemented BOOLEAN.

*/

/*
Interestingly... my vTableInfo view lists TYPE_NAME for each column,
and HSQLDB has a type for INFORMATION_SCHEMA.SQL_IDENTIFIER.
What other types might there be?
*/

CHAR # single character
CHAR # sqlalchemy_type
CHAR(L) # Character string, fixed widthh
CHARACTER # kw
CHARACTER VARYING # alias for VARCHAR?
CHARACTER(L) # alias for CHAR?
CLOB # Character string
CLOB # sqlalchemy_type
Concatenable # sqlalchemy_type
DATE #
Date # sqlalchemy_type
DATE # sqlalchemy_type
DATE # with timezone variation
DateTime # sqlalchemy_type
DATETIME # sqlalchemy_type
DAY # kw
DEC # alias for decimal?
DECIMAL # sqlalchemy_type
DECIMAL # user-defined decimal precision, mapped to java.math.BigDecimal. NUMERIC and DECIMAL are equivalent. SET DATABASE SQL SIZE FALSE
DECIMAL(d,f) # DECIMAL(10,2) means maximum total number of digits is 10 and there are always 2 digits after the decimal point.
DOUBLE # 64-bit. Maps to 'double' in Java double. Equiv FLOAT
Double # sqlalchemy_type
DOUBLE # sqlalchemy_type
DOUBLE_PRECISION # sqlalchemy_type
Enum # sqlalchemy_type
FLOAT # 64-bit. Maps to 'double' in Java double. Equiv DOUBLE. Bit precision can be defined but is ignored - defaults to 64-bit.
Float # sqlalchemy_type
FLOAT # sqlalchemy_type
HOUR # kw
Indexable # sqlalchemy_type
INT # fixed binary precision, bit 32
INT # sqlalchemy_type
INTEGER # fixed binary precision, bit 32
Integer # sqlalchemy_type
INTEGER # sqlalchemy_type
INTERVAL #
Interval # sqlalchemy_type
JSON # sqlalchemy_type
LARGE # kw
LargeBinary # sqlalchemy_type
LOCALTIME # kw
LOCALTIMESTAMP # kw
LONGVARBINARY # is a synonym for a long VARBINARY and can be used without specifying the size. Can map to BLOB, see sql.longvar_is_lob
LONGVARCHAR # is a synonym for a long VARCHAR and can be used without specifying the size. Can map to CLOB, see  sql.longvar_is_lob
MatchType # sqlalchemy_type
MINUTE # kw
MONTH # kw
NCHAR # kw
NCHAR # sqlalchemy_type
NCLOB # kw
NONE # kw
NULL # kw
NullType # sqlalchemy_type
NULLTYPE # sqlalchemy_type
Numeric # sqlalchemy_type
NUMERIC # sqlalchemy_type
NUMERIC # user-defined decimal precision, mapped to java.math.BigDecimal. NUMERIC and DECIMAL are equivalent
NUMERIC(d,f) # NUMERIC(10,2) means maximum total number of digits is 10 and there are always 2 digits after the decimal point.
NVARCHAR # sqlalchemy_type
OTHER # is for storage of Java objects
PickleType # sqlalchemy_type
REAL # not actually found in HSQLDB datatype list, but equiv to DOUBLE and FLOAT
REAL # sqlalchemy_type
SchemaType # sqlalchemy_type
SMALLINT # fixed binary precision, 16 bit
SMALLINT # sqlalchemy_type
SmallInteger # sqlalchemy_type
String # sqlalchemy_type
STRINGTYPE # sqlalchemy_type
SYSDATE # kw
Text # sqlalchemy_type
TEXT # sqlalchemy_type
TIME #
Time # sqlalchemy_type
TIME # sqlalchemy_type
TIME # with timezone variation
TIMESTAMP #
TIMESTAMP # sqlalchemy_type
TIMESTAMP # with timezone variation
TIMEZONE_HOUR # kw
TIMEZONE_MINUTE # kw
TINYINT # fixed binary precision, 8 bit
TODAY # kw
TupleType # sqlalchemy_type
Unicode # sqlalchemy_type
UnicodeText # sqlalchemy_type
UserDefinedType # .sql.type_api
UUID # fixed length string, stored as binary.
Uuid # sqlalchemy_type
UUID # sqlalchemy_type
VARBINARY # kw
VARBINARY # sqlalchemy_type
VARBINARY(L) # binary string type
VARCHAR # kw
VARCHAR # sqlalchemy_type
VARCHAR(L) # Character string,
Variant # .sql.type_api
VARYING # kw
YEAR # kw















