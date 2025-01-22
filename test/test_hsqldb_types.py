
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
from sqlalchemy.testing.suite.test_types import _LiteralRoundTripFixture
from sqlalchemy.types import Boolean
from sqlalchemy.types import Integer

# # Import types...
# # TODO: enable only what we need and remove the rest...
# from sqlalchemy.types import ARRAY
# from sqlalchemy.types import BIGINT
# from sqlalchemy.types import BINARY
# from sqlalchemy.types import BIT # ImportError: cannot import name 'BIT' from 'sqlalchemy.types'
# from sqlalchemy.types import BIT
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
# #- 					^^ INTEGER is defined and so vscode has hightlighted it
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

TEST_SCHEMA_NAME = 's2'

# # # class IntegerTest(_LiteralRoundTripFixture, fixtures.TestBase):
# # # class DateHistoricTest(_DateFixture, fixtures.TablesTest):
# # # 	__requires__ = ("date_historic",)
# # # 	__backend__ = True
# # # 	datatype = Date
# # # 	data = datetime.date(1727, 4, 1)


class BitTest(_LiteralRoundTripFixture, fixtures.TablesTest):
	"""TODO: Class description"""
	#__requires__ = ("boolean_type",) 			# Many test classes have a __requires__ attribute

	__backend__ = False # was True
	"""
	The __backend__ attribute seems to indicate tests should be expanded out
	for each database backend.  Most of the classes for testing SQLAlchemy's 
	built-in dialects have this attribute set to 'True'.

	__backend__ and __sparse_backend__ attributes also appear to be
	considered 'legacy symbols', replaced by test markers perhaps?
	The __backend__ attribute is processed by
	\SQLAlchemy\sqlalchemy\lib\sqlalchemy\testing\plugin\pytestplugin.py
	"""

	@classmethod
	def define_tables(cls, metadata):
		"""Define one or more tables."""
		Table(
			"bit_table",
			metadata,
			Column("id", Integer, primary_key=True, autoincrement=False),
			Column("value", Boolean),
			Column("unconstrained_value", Boolean(create_constraint=False)),
		)

	def test_render_literal_bool(self, literal_round_trip):
		literal_round_trip(Boolean(), [True, False], [True, False])

	def test_round_trip(self, connection):
		bit_table = self.tables.bit_table

		connection.execute(
			bit_table.insert(),
			{"id": 1, "value": True, "unconstrained_value": False},
		)

		row = connection.execute(
			select(bit_table.c.value, bit_table.c.unconstrained_value)
		).first()

		breakpoint() #-
		eq_(row, (True, False))
		assert isinstance(row[0], bool)

	@testing.requires.nullable_booleans
	def test_null(self, connection):
		bit_table = self.tables.bit_table

		connection.execute(
			bit_table.insert(),
			{"id": 1, "value": None, "unconstrained_value": None},
		)

		row = connection.execute(
			select(bit_table.c.value, bit_table.c.unconstrained_value)
		).first()

		eq_(row, (None, None))

	def test_whereclause(self):
		# testing "WHERE <column>" renders a compatible expression
		bit_table = self.tables.bit_table

		with config.db.begin() as conn:
			conn.execute(
				bit_table.insert(),
				[
					{"id": 1, "value": True, "unconstrained_value": True},
					{"id": 2, "value": False, "unconstrained_value": False},
				],
			)

			eq_(
				conn.scalar(
					select(bit_table.c.id).where(bit_table.c.value)
				),
				1,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(
						bit_table.c.unconstrained_value
					)
				),
				1,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(~bit_table.c.value)
				),
				2,
			)
			eq_(
				conn.scalar(
					select(bit_table.c.id).where(
						~bit_table.c.unconstrained_value
					)
				),
				2,
			)
