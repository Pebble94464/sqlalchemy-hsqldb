"""
JSN note:
sqlalchemy/README.dialects.rst mentions dialect specific tests.
    test_<dialect_specific_test>.py

This file appears to be one such test, copied from sqlalchemy-access

TODO: Remove this file if unused.

NOTE: This test fails against HSQLDB. The filename will be temporarily changed to hide it,
		but has not been deleted yet because the file might be needed as a template for
        new tests later on.
"""

from sqlalchemy import testing, Table, Column, Integer
from sqlalchemy.testing import fixtures, eq_


class OperatorOverrideTest(fixtures.TablesTest):
    @testing.provide_metadata
    def test_not_equals_operator(self, connection):
        # test for issue #6
        tbl = Table(
            "ne_test",
            self.metadata,
            Column("id", Integer, primary_key=True),
        )
        tbl.create(connection)
        connection.execute(
            tbl.insert(),
            [{"id": 1}],
        )
        result = connection.execute(tbl.select().where(tbl.c.id != 1)).fetchall()
        eq_(len(result), 0)
        result = connection.execute(tbl.select().where(tbl.c.id != 2)).fetchall()
        eq_(len(result), 1)
