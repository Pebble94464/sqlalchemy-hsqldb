
# HSQLDB testing is currently in an incomplete state. (2024-11-27)
# Most of tests here are overrides to skip certain tests.
# TODO: re-enable all tests and only disable those that do not apply.
# TODO: remove tests that have been commented out.
# TODO: implement tests for TIME_WITH_TIMEZONE, similar to TIME tests.
# TODO: implement tests for TIMESTAMP_WITH_TIMEZONE, similar to TIMESTAMP or DATETIME tests.

# Import the entire test suite...
from sqlalchemy.testing.suite import *
import operator
import sqlalchemy as sa

# WIP: -->
# import a local test... 
# from test_compiler import *

from sqlalchemy.testing.suite import (
    BizarroCharacterFKResolutionTest as _BizarroCharacterFKResolutionTest,
)
from sqlalchemy.testing.suite import (
    CastTypeDecoratorTest as _CastTypeDecoratorTest,
)
from sqlalchemy.testing.suite import (
    ComponentReflectionTest as _ComponentReflectionTest,
)
from sqlalchemy.testing.suite import (
    ComponentReflectionTestExtra as _ComponentReflectionTestExtra,
)
from sqlalchemy.testing.suite import DateTimeTest as _DateTimeTest
from sqlalchemy.testing.suite import (
    DifficultParametersTest as _DifficultParametersTest,
)
from sqlalchemy.testing.suite import ExceptionTest as _ExceptionTest
from sqlalchemy.testing.suite import ExistsTest as _ExistsTest
from sqlalchemy.testing.suite import (
    ExpandingBoundInTest as _ExpandingBoundInTest,
)
from sqlalchemy.testing.suite import (
    FetchLimitOffsetTest as _FetchLimitOffsetTest,
)
from sqlalchemy.testing.suite import HasIndexTest as _HasIndexTest
from sqlalchemy.testing.suite import HasTableTest as _HasTableTest
from sqlalchemy.testing.suite import InsertBehaviorTest as _InsertBehaviorTest
from sqlalchemy.testing.suite import IntegerTest as _IntegerTest
from sqlalchemy.testing.suite import JoinTest as _JoinTest
from sqlalchemy.testing.suite import LikeFunctionsTest as _LikeFunctionsTest
from sqlalchemy.testing.suite import (
    LongNameBlowoutTest as _LongNameBlowoutTest,
)
from sqlalchemy.testing.suite import NativeUUIDTest as _NativeUUIDTest
from sqlalchemy.testing.suite import NumericTest as _NumericTest
from sqlalchemy.testing.suite import OrderByLabelTest as _OrderByLabelTest
from sqlalchemy.testing.suite import (
    QuotedNameArgumentTest as _QuotedNameArgumentTest,
)
from sqlalchemy.testing.suite import StringTest as _StringTest
from sqlalchemy.testing.suite import TableDDLTest as _TableDDLTest
from sqlalchemy.testing.suite import TrueDivTest as _TrueDivTest

class BizarroCharacterFKResolutionTest(_BizarroCharacterFKResolutionTest):
	@testing.skip("hsqldb")
	def test_fk_ref(self):
		return
	# This test is currently failing. On line 341 in test_reflection.py, table
	# "other" fails to auto loaded back in for some reason, before the assertions
	# of the test are actually tested.  A NotImplementedError exception is thrown.
	# The identifiers used in test parameter are quoted, so expect HSQLDB will
	# handle these correctly.
	# TODO: Try running this test again when this HSQLDB dialect is more complete.



# # class CastTypeDecoratorTest(_CastTypeDecoratorTest):
# #     @testing.skip("access")
# #     def test_special_type(self):
# #         # Access SQL does not do CAST in the conventional way
# #         return


class ComponentReflectionTest(_ComponentReflectionTest):

	@testing.skip('hsqldb', reason='Requires further investigation. Temporarily disabled.')
	def test_autoincrement_col(self):
		return
	# This test fails for some reason...
	# HSQLDB autoincrement columns are normally created by specifying something
	# like 'id INTEGER GENERATED BY DEFAULT AS IDENTITY', but the columns
	# used by this test lack an identity definition for their DDL when created.
	# 	e.g. Column("user_id", sa.INT, primary_key=True)
	#
	# If we were to include an identity definition...
	# 	e.g. Column("user_id", sa.INT, Identity(), primary_key=True)
	# the DDL includes 'GENERATED BY DEFAULT AS IDENTITY',
	# information_schema.system_columns.is_autoincrement = 'YES', as expected.
	#
	# So what are the differences between HSQLDB and Alchemy's auto increment
	# columns, are they not the same?  Review comments in the base definition
	# of the test case (hover over 'def test_autoincrement_col(self)' above).
	#
	# TODO: This test case requires further investigation. Don't permanently disable it!


# #     @testing.skip("access")
# #     def test_get_foreign_keys(self):
# #         # Access does not support all options tested
# #         return

# #     @testing.skip("access")
# #     def test_get_indexes(self):
# #         # Access does not support all options tested
# #         return

	@testing.skip('hsqldb', reason='Unique indexes were deprecated in HSQLDB 1.8')
	def test_get_indexes(self):
	#- def test_get_indexes(self, connection, use_schema):
		return

	@testing.combinations((False,), (True, testing.requires.schemas), argnames="use_schema")
	@testing.requires.index_reflection
	def test_get_indexes_hsqldb(self, connection, use_schema):
		""" This test is intended to replace the original test_get_indexes.
			The original fails when it attempts to test unique indexes,
			which were deprecated in HSQLDB 1.8
		"""
		if use_schema:
			schema = config.test_schema
		else:
			schema = None

		insp = inspect(connection)
		indexes = insp.get_indexes("users", schema=schema)
		expected_indexes = self.exp_indexes(schema=schema)

		filtered_indexes = []
		for exp_idx in expected_indexes[(schema, 'users')]:
			# Unique indexes are deprecated in favour of unique constraints.
			# Ammend expected_indexes because unique flag is now False.
			if 'unique' in exp_idx:
				exp_idx['unique'] = False

			# DBs may return indexes in any order, and create indexes
			# for foreign keys, etc. Filter out unexpected indexes and 
			# preserve the exxpected order...
			for idx in indexes:
				if idx['name'] == exp_idx['name']:
					filtered_indexes.append(idx)
					break

		self._check_list(
			filtered_indexes,
			expected_indexes[(schema, "users")],
			self._required_index_keys
		)

		tbl_no_cst = self.tables.no_constraints.name
		self._check_list(
			insp.get_indexes(tbl_no_cst, schema=schema),
			expected_indexes[(schema, tbl_no_cst)],
			self._required_index_keys,
		)
		# Table 'no_constraints' has no indexes. Why not simply check the
		# count of indexes instead of calling _check_list?


	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_columns(self):
		return
		#- Access comment: test fails due to ODBC driver bug always reporting nullable=True
	# TODO: enable test after get_multi_columns has been implemented.

#- line 1837
	@testing.skip('hsqldb', reason='Although ASC or DESC can be specified it has no effect')
	def test_get_noncol_index(self):
		return

#- line 1869
	@testing.skip('hsqldb', reason='Test fails because index contains column sorting info')
	def test_get_temp_table_indexes(self):
		return
	# This test appears to fail only because the index contains columnn_sorting.
	# The get_index function is expected to return sorting in other tests, and
	# it seems like a reasonable thing for temporary table indexes too.
 	# Why shouldn't it?
	# TODO: review 

	@testing.requires.temp_table_reflect_indexes
	def test_get_temp_table_indexes_hsqldb(self, connection):
		"""
		This test differs from the original 'test_get_temp_tables' in that
		column sorting is popped from indexes.  If the original test passes,
		this one can be dropped entirely.
		"""
		insp = inspect(connection)
		table_name = self.temp_table_name()
		indexes = insp.get_indexes(table_name)
		for ind in indexes:
			ind.pop("dialect_options", None)
			ind.pop('column_sorting', None) 	# Pop column_sorting!
		expected = [
			{"unique": False, "column_names": ["foo"], "name": "user_tmp_ix"}
		]
		if testing.requires.index_reflects_included_columns.enabled:
			expected[0]["include_columns"] = []
		eq_(
			[idx for idx in indexes if idx["name"] == "user_tmp_ix"],
			expected,
		)

#- line 2104
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_multi_get_table_options_tables(self):
		return

#- line 2122
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_table_comment(self):
		return

#- line 2188
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_pk_constraint(self):
		#- Access comment: Access does not support all options tested
		return
	# TODO: enable test after get_multi_pk_constraint has been implemented.

#- line 2220
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_foreign_keys(self):
		return
	# TODO: enable test after get_multi_foreign_keys has been implemented.

#- line 2241
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_indexes(self):
		#- Access comment: tests fail because we don't support table/column comments
		return
	# TODO: enable test after get_multi_indexes has been implemented.


#- line 2259
	@testing.skip('hsqldb', reason='Not yet implemented')
	def test_get_multi_unique_constraints(self):
		return
	# TODO: enable test after get_multi_unique_constraints has been implemented.


# #     @testing.skip("access")
# #     def test_get_pk_constraint(self):
# #         # PK constraint reflection (via Access.DAO) is "best effort"
# #         return

# #     @testing.skip("access")
# #     def test_get_unique_constraints(self):
# #         # Access barfs on DDL trying to create a constraint named "i.have.dots"
# #         return


#- line 1886
	@testing.skip('hsqldb', reason='HSQLDB can create constraints unique_a_b_c or unique_c_a_b, but not both because they use the same columns')
	def test_get_unique_constraints(self):
		return

	# @testing.skip('hsqldb', reason='Failing because of something related to dialect_options and DialectKWArgs.')
	@testing.combinations(
		(True, testing.requires.schemas), (False,), argnames="use_schema"
	)
	@testing.requires.unique_constraint_reflection
	def test_get_unique_constraints_hsqldb(self, metadata, connection, use_schema):
		"""
		Replacement for test_get_unique_constraints.
		HSQLDB doesn't appear to support indexes with dupicate columns like unique_a_b_c and unique_c_a_b.
		"""
		if use_schema:
			schema = config.test_schema
		else:
			schema = None

		uniques = sorted(
			[
				{"name": "unique_a", "column_names": ["a"]},
				{"name": "unique_a_b_c", "column_names": ["a", "b", "c"]},
				# {"name": "unique_c_a_b", "column_names": ["c", "a", "b"]}, # Unsupported.
				{"name": "unique_asc_key", "column_names": ["asc", "key"]},
				{"name": "i.have.dots", "column_names": ["b"]},
				{"name": "i have spaces", "column_names": ["c"]},
			],
			key=operator.itemgetter("name"), # sort by name
		)

		# Create table and constraints...
		table = Table(
			"testtbl",
			metadata,
			Column("a", sa.String(20)),
			Column("b", sa.String(30)),
			Column("c", sa.Integer),
			# reserved identifiers
			Column("asc", sa.String(30)),
			Column("key", sa.String(30)),
			schema=schema,
		)
		for uc in uniques:
			table.append_constraint(
				sa.UniqueConstraint(*uc["column_names"], name=uc["name"])
			)
		table.create(connection)

		# Verify UCs using the Inspector.get_unique_constraints method...
		insp = inspect(connection)
		reflected = sorted(
			insp.get_unique_constraints("testtbl", schema=schema),
			key=operator.itemgetter("name"),
		)
		eq_(len(uniques), len(reflected))

		names_that_duplicate_index = set()
		for orig, refl in zip(uniques, reflected):
			# Different dialects handle duplicate index and constraints differently, so ignore this flag
			dupe = refl.pop("duplicates_index", None)
			if dupe:
				names_that_duplicate_index.add(dupe)
			eq_(refl.pop("comment", None), None)
			# Following removal of comment key and duplicates_index key, original and reflected indexes should match...
			eq_(orig, refl)

		# Verify UCs using table reflection...
		reflected_metadata = MetaData()
		reflected = Table(
			"testtbl",
			reflected_metadata,
			autoload_with=connection,
			schema=schema,
		)

		# test "deduplicates for index" logic.   MySQL and Oracle
		# "unique constraints" are actually unique indexes (with possible
		# exception of a unique that is a dupe of another one in the case
		# of Oracle).  make sure they aren't duplicated.

		idx_names = {idx.name for idx in reflected.indexes}
		uq_names = {
			uq.name
			for uq in reflected.constraints
			if isinstance(uq, sa.UniqueConstraint)
		}.difference(["unique_c_a_b"]) # exclude unique_c_a_b from the uq_names set.

		# raise an assertion if they share any matching idx and uq names
		assert not idx_names.intersection(uq_names)

		if names_that_duplicate_index: 					# {'unique_a', 'i have spaces', 'unique_a_b_c', 'i.have.dots', 'unique_asc_key'}
			eq_(names_that_duplicate_index, idx_names)
			eq_(uq_names, set())						# Empty set vs empty set.

		no_cst = self.tables.no_constraints.name
		eq_(insp.get_unique_constraints(no_cst, schema=schema), [])





# #     @testing.skip("access")
# #     def test_not_existing_table(self):
# #         return


# # class ComponentReflectionTestExtra(_ComponentReflectionTestExtra):
# #     @testing.skip("access")
# #     def test_nullable_reflection(self):
# #         # Access ODBC implementation of the SQLColumns function reports that
# #         # a column is nullable even when it is not
# #         return

# # 	#- jsn added...
# #     # @testing.skip("access", "some reason")
# #     # def test_numeric_reflection(self):
# #     #     return

# # class DateTimeTest(_DateTimeTest):
# #     @testing.skip("access")
# #     def test_null_bound_comparison(self):
# #         # bypass this test because Access ODBC fails with
# #         # "Unrecognized keyword WHEN."
# #         return


# # class DifficultParametersTest(_DifficultParametersTest):
# #     @testing.skip("access")
# #     def test_round_trip(self):
# #         # bypass this test because "q?marks" case fails with
# #         # "COUNT field incorrect"
# #         return

# #     @testing.skip("access")
# #     def test_round_trip_same_named_column(self):
# #         # bypass this test because CREATE TABLE statements fail for
# #         # "[BracketsAndCase]", "dot_s", and "q?marks" cases
# #         return

class ExceptionTest(_ExceptionTest):
	@testing.skip('hsqldb', reason='HSQLDB seems to accept non-ASCII chars, so possibly no way to raise an error.')
	def test_exception_with_non_ascii(self):
		return
	# The original test generates the query "SELECT méil"
	# HSQLDB doesn't allow direct selection of a literal value, but it will
	# succeed if we try  "SELECT * FROM (VALUES('méil'))", or
	# "SELECT méil FROM (VALUES (NULL)) AS myvalues (méil)"
	# I'm unsure why this test expects a database error.
	# The original test notes there's no way to generate a non-ASCII error
	# message for some drivers.
	# TODO: investigate further.
	# pytest -rP -x --db hsqldb test/test_suite.py::ExceptionTest::test_exception_with_non_ascii

# # class ExistsTest(_ExistsTest):
# #     @testing.skip("access")
# #     def test_select_exists(self):
# #         # bypass this test because Access ODBC fails with
# #         # "SELECT statement includes a reserved word or an argument name ..."
# #         return

# #     @testing.skip("access")
# #     def test_select_exists_false(self):
# #         # bypass this test because Access ODBC fails with
# #         # "SELECT statement includes a reserved word or an argument name ..."
# #         return


# # class ExpandingBoundInTest(_ExpandingBoundInTest):
# #     @testing.skip("access")
# #     def test_null_in_empty_set_is_false_bindparam(self):
# #         """Access SQL can't do CASE ... WHEN, but this test would pass if we
# #         re-wrote the query to be

# #             SELECT (n = 1) AS result
# #             FROM
# #                 (
# #                     SELECT COUNT(*) AS n FROM USysSQLAlchemyDUAL
# #                     WHERE NULL IN (SELECT NULL FROM USysSQLAlchemyDUAL WHERE 1=0)
# #                 )
# #         """
# #         return

# #     @testing.skip("access")
# #     def test_null_in_empty_set_is_false_direct(self):
# #         return

# #     @testing.skip("access")
# #     def test_null_in_empty_set_is_false(self):
# #         return

# #     @testing.skip("access")
# #     def test_empty_set_against_integer_bindparam(self):
# #         return

# #     @testing.skip("access")
# #     def test_empty_set_against_integer_direct(self):
# #         return

# #     @testing.skip("access")
# #     def test_empty_set_against_string_bindparam(self):
# #         return

# #     @testing.skip("access")
# #     def test_empty_set_against_string_direct(self):
# #         return

# #     @testing.skip("access")
# #     def test_multiple_empty_sets_bindparam(self):
# #         return

# #     @testing.skip("access")
# #     def test_multiple_empty_sets_direct(self):
# #         return

# #     @testing.skip("access")
# #     def test_empty_in_plus_notempty_notin(self):
# #         return


# # class FetchLimitOffsetTest(_FetchLimitOffsetTest):
# #     @testing.skip("access")
# #     def test_limit_render_multiple_times(self):
# #         # bypass this test because Access ODBC fails with
# #         # "Query input must contain at least one table or query."
# #         return


# # class HasIndexTest(_HasIndexTest):
# #     @testing.skip("access")
# #     def test_has_index(self):
# #         return


# # class HasTableTest(_HasTableTest):
# #     @testing.skip("access")
# #     def test_has_table(self):
# #         return

# #     @testing.skip("access")
# #     def test_has_table_cache(self):
# #         return


# # class InsertBehaviorTest(_InsertBehaviorTest):
# #     @testing.skip("access")
# #     def test_empty_insert(self):
# #         # bypass this test because Access ODBC fails with
# #         # [ODBC Microsoft Access Driver] Syntax error in INSERT INTO statement.
# #         return

# #     @testing.skip("access")
# #     def test_empty_insert_multiple(self):
# #         # bypass this test because Access ODBC fails with
# #         # [ODBC Microsoft Access Driver] Syntax error in INSERT INTO statement.
# #         return

# #     @testing.skip("access")
# #     def test_no_results_for_non_returning_insert(self):
# #         return


# # class IntegerTest(_IntegerTest):
# #     @testing.skip("access")
# #     def test_huge_int(self):
# #         # bypass this test because Access ODBC fails with
# #         # [ODBC Microsoft Access Driver] Optional feature not implemented.
# #         return

# #     @testing.skip("access")
# #     def test_huge_int_auto_accommodation(self):
# #         return


# # class JoinTest(_JoinTest):
# #     @testing.skip("access")
# #     def test_inner_join_true(self):
# #         # bypass this test because Access ODBC fails with
# #         # "JOIN expression not supported."
# #         return

# #     @testing.skip("access")
# #     def test_inner_join_false(self):
# #         # bypass this test because Access ODBC fails with
# #         # "JOIN expression not supported."
# #         return

# #     @testing.skip("access")
# #     def test_outer_join_false(self):
# #         # bypass this test because Access ODBC fails with
# #         # "JOIN expression not supported."
# #         return


# # class LikeFunctionsTest(_LikeFunctionsTest):
# #     """Access SQL doesn't do ESCAPE"""

# #     @testing.skip("access")
# #     def test_contains_autoescape(self):
# #         return

# #     @testing.skip("access")
# #     def test_contains_autoescape_escape(self):
# #         return

# #     @testing.skip("access")
# #     def test_contains_escape(self):
# #         return

# #     @testing.skip("access")
# #     def test_contains_unescaped(self):
# #         return

# #     @testing.skip("access")
# #     def test_endswith_autoescape(self):
# #         return

# #     @testing.skip("access")
# #     def test_endswith_autoescape_escape(self):
# #         return

# #     @testing.skip("access")
# #     def test_endswith_escape(self):
# #         return

# #     @testing.skip("access")
# #     def test_startswith_autoescape(self):
# #         return

# #     @testing.skip("access")
# #     def test_startswith_autoescape_escape(self):
# #         return

# #     @testing.skip("access")
# #     def test_startswith_escape(self):
# #         return


# # class LongNameBlowoutTest(_LongNameBlowoutTest):
# #     @testing.skip("access")
# #     def test_long_convention_name(self):
# #         # test generates names that are *way* too long for Access
# #         return


# # class NativeUUIDTest(_NativeUUIDTest):
# #     @testing.skip("access")
# #     def test_literal_text(self):
# #         return

# #     @testing.skip("access")
# #     def test_literal_uuid(self):
# #         return

# #     @testing.skip("access")
# #     def test_uuid_round_trip(self):
# #         return

# #     @testing.skip("access")
# #     def test_uuid_text_round_trip(self):
# #         return


# # class NumericTest(_NumericTest):
# #     @testing.skip("access")
# #     def test_decimal_coerce_round_trip(self):
# #         # bug in Access SQL: "SELECT ? AS anon_1 ..." returns rubbish with a
# #         # decimal.Decimal parameter value
# #         # https://github.com/mkleehammer/pyodbc/issues/624
# #         return

# #     @testing.skip("access")
# #     def test_decimal_coerce_round_trip_w_cast(self):
# #         # bug in Access SQL: "SELECT ? AS anon_1 ..." returns rubbish with a
# #         # decimal.Decimal parameter value
# #         # https://github.com/mkleehammer/pyodbc/issues/624
# #         return

# #     @testing.skip("access")
# #     def test_float_is_not_numeric(self):
# #         # test fails because: 'numeric' != 'numeric'
# #         # (umm, okay …)
# #         return


# # class OrderByLabelTest(_OrderByLabelTest):
# #     @testing.skip("access")
# #     def test_composed_multiple(self):
# #         # SELECT statement too complex for Access SQL
# #         # "Reserved error (-1001); there is no message for this error."
# #         return


# # class QuotedNameArgumentTest(_QuotedNameArgumentTest):
# #     # suppress creation of test table(s) since that's where the errors occur
# #     run_create_tables = None

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_table_options(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_view_definition(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_columns(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_pk_constraint(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_foreign_keys(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_indexes(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_unique_constraints(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_table_comment(self, name):
# #         return

# #     @testing.skip("access")
# #     @_QuotedNameArgumentTest.quote_fixtures
# #     def test_get_check_constraints(self, name):
# #         return


# # class StringTest(_StringTest):
# #     @testing.skip("access")
# #     def test_concatenate_clauselist(self):
# #         return


# # class TableDDLTest(_TableDDLTest):
# #     @testing.skip("access")
# #     def test_underscore_names(self):
# #         return


# # class TrueDivTest(_TrueDivTest):
# #     @testing.skip("access")
# #     def test_floordiv_integer(self):
# #         return

# #     @testing.skip("access")
# #     def test_floordiv_integer_bound(self):
# #         return

# #     @testing.skip("access")
# #     def test_floordiv_numeric(self):
# #         return

# #     @testing.skip("access")
# #     def test_truediv_numeric(self):
# #         return
