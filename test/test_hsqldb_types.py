
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import testing
from sqlalchemy.schema import Column
from sqlalchemy.schema import Table
from sqlalchemy.testing import config
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.assertions import eq_
from sqlalchemy.testing.assertions import is_
from sqlalchemy.testing.assertions import ne_
from sqlalchemy import schema
from sqlalchemy.testing.suite.test_types import _LiteralRoundTripFixture
from sqlalchemy.types import Boolean
from sqlalchemy.types import Integer

# # Import types...
# # TODO: enable only what we need and remove the rest...
# from sqlalchemy.types import ARRAY
# from sqlalchemy.types import BIGINT
# from sqlalchemy.types import BINARY
from sqlalchemy_hsqldb import BIT
# from sqlalchemy.types import BLOB
# from sqlalchemy.types import BOOLEAN
# from sqlalchemy.types import CHAR
# from sqlalchemy.types import CLOB
# from sqlalchemy.types import DATALINK
# from sqlalchemy.types import DATE
# from sqlalchemy.types import DECIMAL
# # from sqlalchemy.types import DISTINCT
# from sqlalchemy.types import DOUBLE
# from sqlalchemy.types import FLOAT
# from sqlalchemy.types import INTEGER
# from sqlalchemy.types import JAVA_OBJECT
# from sqlalchemy.types import LONGNVARCHAR
# from sqlalchemy.types import LONGVARBINARY
# from sqlalchemy.types import LONGVARCHAR
# from sqlalchemy.types import MULTISET
# from sqlalchemy.types import NCHAR
# from sqlalchemy.types import NCLOB
# # from sqlalchemy.types import NULL # No dialect imports NULL
# from sqlalchemy.types import NUMERIC
# from sqlalchemy.types import NVARCHAR
# from sqlalchemy.types import OTHER
# from sqlalchemy.types import REAL
# from sqlalchemy.types import REF
# from sqlalchemy.types import REF_CURSOR
# from sqlalchemy.types import ROWID
# from sqlalchemy.types import SMALLINT
# from sqlalchemy.types import SQLXML
# from sqlalchemy.types import STRUCT
# from sqlalchemy.types import TIME
# from sqlalchemy.types import TIME_WITH_TIMEZONE
# from sqlalchemy.types import TIMESTAMP
# from sqlalchemy.types import TIMESTAMP_WITH_TIME_ZONE
# from sqlalchemy.types import TINYINT
# from sqlalchemy.types import VARBINARY
# from sqlalchemy.types import VARCHAR

TEST_SCHEMA_NAME = 'test_hsqldb_types'
"""A schema for testing.

Note:
A schema for testing already exists, accessible through `config.test_schema`.
Test schema(s) are not created automatically for this dialect, I may have 
previously created them manually. Other dialects have a provisions.py script 
which might be responsible for setting up databases. I need to look into this.
In the meantime each test class in this script can define the class methods
`_setup_once_tables` and `teardown_test_class` to create and drop a schema.
"""
# TODO: Can testing.provision be used to create schemas? See provisions.py

def _create_schema():
	"""Creates a schema for testing."""
	schema_name = config.test_schema #- e.g. 'test_schema'
	stmt = schema.CreateSchema(TEST_SCHEMA_NAME, if_not_exists=True)
	with testing.db.begin() as conn:
		conn.execute(stmt)

def _drop_schema():
	"""Drops the schema for testing."""
	stmt = schema.DropSchema(TEST_SCHEMA_NAME, cascade=True)
	with testing.db.begin() as conn:
		conn.execute(stmt)

class BitTest(_LiteralRoundTripFixture, fixtures.TablesTest):
	__requires__ = ('bit_type',)  # 'bit_type' is defined in requirements.py

	@classmethod
	def _setup_once_tables(cls):
		_create_schema()
		super()._setup_once_tables()
	# TODO: Remove this method if schemas are created by provisioning.

	@classmethod
	def define_tables(cls, metadata):
		"""Define one or more tables."""
		t1 = Table(
			"bit_table",
			metadata,
			Column("id", Integer, primary_key=True, autoincrement=False),
			Column("bit1", BIT),
			# Column("bit12", BIT), # Currently unsupported bit length
			Column("bit16", BIT(16)),
			schema=TEST_SCHEMA_NAME,
		)

	@classmethod
	def teardown_test_class(cls):
		_drop_schema()
	# TODO: Remove this method if schemas are dropped by provisioning.

	def test_literal_bit1(self, literal_round_trip):
		literal_round_trip(BIT, [True], [True]) # params: type, input, output

	def test_literal_bit16(self, literal_round_trip):
		literal_round_trip(BIT(16), [b'\xF2\xF3'], [b'\xF2\xF3'])

	comb1 = ((True, b'\xF0\xF0'), (False, b'\xF0\xF1'))
	@testing.combinations(*comb1, argnames="data1,data2")
	def test_round_trip(self, data1, data2, connection):
		bit_table = self.tables.get(f'{TEST_SCHEMA_NAME}.bit_table')
		connection.execute(
			bit_table.insert(), [{"id": 1, "bit1": data1, "bit16": data2},]
			)
		row = connection.execute(select(bit_table.c.bit1, bit_table.c.bit16))
		eq_(row.fetchone(), (data1, data2))

	@testing.requires.nullable_bits
	def test_null(self, connection):
		bit_table = self.tables.get(f'{TEST_SCHEMA_NAME}.bit_table')
		connection.execute(
			bit_table.insert(),
			{"id": 1, "bit1": None, "bit16": None},
		)
		row = connection.execute(
			select(bit_table.c.bit1, bit_table.c.bit16)
		).first()
		eq_(row, (None, None))

	def test_whereclause(self):
		bit_table = self.tables.get(f'{TEST_SCHEMA_NAME}.bit_table')
		with config.db.begin() as conn:
			conn.execute(
				bit_table.insert(),
				[
					{"id": 1, "bit1": True, "bit16": b'\xF2\xF3'},
					{"id": 2, "bit1": False, "bit16": b'\x00\x00'},
				],
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(bit_table.c.bit1 == True)
				),
				1,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(bit_table.c.bit16 == b'\xF2\xF3')
				),
				1,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(bit_table.c.bit1 == False)
				),
				2,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(
						bit_table.c.bit16 == b'\x00\x00'
					)
				),
				2,
			)
