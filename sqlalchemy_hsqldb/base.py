
# "base.py defines the specific SQL dialect used by that database"
# [New Dialect System](https://docs.sqlalchemy.org/en/20/changelog/migration_06.html)

from sqlalchemy.engine import default
from sqlalchemy.engine import reflection
from sqlalchemy.sql import compiler
from sqlalchemy.sql import sqltypes

# Types for mysql, pg and oracle, are defined in their respective types.py file...
# from .types import DATE
# from .types import FLOAT
# from .types import INTERVAL



class HyperSqlDialect(default.DefaultDialect):
	"""HyperSqlDialect implementation of Dialect"""

	# WIP: what are colspecs?
	#		Descriptions can be found here:  site-packages\sqlalchemy\engine\interfaces.py


	# 'colspecs' seems to map sqltypes to types defined in the dialect's types.py file.
	# default.DefaultDialect.colspecs: MutableMapping[Type[TypeEngine[Any]], Type[TypeEngine[Any]]] = {}
	colspecs = {
		# sqltypes.ARRAY: _array.ARRAY,
		# sqltypes.Boolean: _OracleBoolean,
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

	#- ok...
	name = "hsqldb"

	# Set 'supports_schemas' to false to disable schema-level tests
	supports_schemas = False
	# TODO: try setting to True (or removing) when we're ready for testing. Only the Access dialect appears to set it to false. Does it take too long to test?

	# HSQLDB's BOOLEAN type conforms to the SQL Standard and represents the values TRUE, FALSE and UNKNOWN"
	supports_native_boolean = True

	supports_sane_rowcount = True
	# Some drivers, particularly third party dialects for non-relational databases,
	# may not support _engine.CursorResult.rowcount at all.
	# The _engine.CursorResult.supports_sane_rowcount attribute will indicate this.
	#
	# Like MySql, Oracle, and PG, HSQLDB is a relational database, so I have set it to True.
	# Note that Access and sqlalchemy-jdbcapi have it set to False, for some reason unknown.

	supports_sane_multi_rowcount = True
	# For an :ref:`executemany <tutorial_multiple_parameters>` execution,
	# _engine.CursorResult.rowcount may not be available either, which depends
	# highly on the DBAPI module in use as well as configured options.  The
	# attribute _engine.CursorResult.supports_sane_multi_rowcount indicates
	# if this value will be available for the current backend in use.
	#
	# The default is True. Other DBs are set to True. I suspect HSQLDB supports it too, so set it to True.
	# Note that Access and sqlalchemy set it to False, for some reason.


	supports_simple_order_by_label = True
	# Target database supports ORDER BY <labelname>, where <labelname>
	# refers to a label in the columns clause of the SELECT
	#
	# TODO: can be removed / set to True if supported. Access has it set to False.


	_need_decimal_fix = False

	supports_is_distinct_from = False

	poolclass = pool.NullPool
	statement_compiler = HyperSqlCompiler
	ddl_compiler = HyperSqlDDLCompiler
	type_compiler = HyperSqlTypeCompiler
	preparer = HyperSqlIdentifierPreparer
	execution_ctx_cls = HyperSqlExecutionContext

	# TODO: 
	@DeprecationWarning
	@classmethod
	def dbapi(cls):
		"""
        A reference to the DBAPI module object itself. (DEPRECATED)
        It is replaced by import_dbapi, which has been implemented in jaydebeapi.py
        """
		raise NotImplementedError

# TODO: implement HyperSqlCompiler below... (it's currently just a copy of Access's)
class HyperSqlCompiler(compiler.SQLCompiler):
    extract_map = compiler.SQLCompiler.extract_map.copy()
    extract_map.update(
        {
            "month": "m",
            "day": "d",
            "year": "yyyy",
            "second": "s",
            "hour": "h",
            "doy": "y",
            "minute": "n",
            "quarter": "q",
            "dow": "w",
            "week": "ww",
        }
    )

    def visit_cast(self, cast, **kw):
        return cast.clause._compiler_dispatch(self, **kw)

    def get_select_precolumns(self, select, **kw):
        # (plagiarized from mssql/base.py)

        s = super(AccessCompiler, self).get_select_precolumns(select, **kw)

        """ Access puts TOP, it's version of LIMIT here """
        if select._offset:
            raise NotImplementedError("Access SQL does not support OFFSET")
        elif hasattr(select, "_simple_int_limit"):  # SQLA_1.3
            if select._simple_int_limit:
                # ODBC drivers and possibly others
                # don't support bind params in the SELECT clause on SQL Server.
                # so have to use literal here.
                s += "TOP %d " % select._limit
        elif select._has_row_limiting_clause and self._use_top(
            select
        ):  # SQLA_1.4
            # ODBC drivers and possibly others
            # don't support bind params in the SELECT clause on SQL Server.
            # so have to use literal here.
            kw["literal_execute"] = True
            s += "TOP %s " % self.process(
                self._get_limit_or_fetch(select), **kw
            )
            if select._fetch_clause is not None:
                if select._fetch_clause_options["percent"]:
                    s += "PERCENT "
                if select._fetch_clause_options["with_ties"]:
                    s += "WITH TIES "

        return s

    def limit_clause(self, select, **kw):
        """Limit in access is after the select keyword"""
        return ""

    def binary_operator_string(self, binary):
        """Access uses "mod" instead of "%" """
        return binary.operator == "%" and "mod" or binary.operator

    def visit_concat_op_binary(self, binary, operator, **kw):
        return "%s & %s" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    function_rewrites = {
        "current_date": "now",
        "current_timestamp": "now",
        "length": "len",
    }

    def visit_function(self, func, **kw):
        """Access function names differ from the ANSI SQL names;
        rewrite common ones"""
        func.name = self.function_rewrites.get(func.name, func.name)
        return super(AccessCompiler, self).visit_function(func)

    def for_update_clause(self, select, **kw):
        """FOR UPDATE is not supported by Access; silently ignore"""
        return ""

    # Strip schema
    def visit_table(self, table, asfrom=False, **kw):
        if asfrom:
            return self.preparer.quote(table.name)
        else:
            return ""

    def visit_join(self, join, asfrom=False, **kw):
        return (
            "("
            + self.process(join.left, asfrom=True)
            + (join.isouter and " LEFT OUTER JOIN " or " INNER JOIN ")
            + self.process(join.right, asfrom=True)
            + " ON "
            + self.process(join.onclause)
            + ")"
        )

    def visit_extract(self, extract, **kw):
        field = self.extract_map.get(extract.field, extract.field)
        return 'DATEPART("%s", %s)' % (field, self.process(extract.expr, **kw))

    def visit_empty_set_expr(self, type_, **kw):
        literal = None
        repr_ = repr(type_[0])
        if repr_.startswith("Integer("):
            literal = "1"
        elif repr_.startswith("String("):
            literal = "'x'"
        elif repr_.startswith("NullType("):
            literal = "NULL"
        else:
            raise ValueError("Unknown type_: %s" % type(type_[0]))
        stmt = "SELECT %s FROM USysSQLAlchemyDUAL WHERE 1=0" % literal
        return stmt

    def visit_ne_binary(self, binary, operator, **kw):
        return "%s <> %s" % (
            self.process(binary.left),
            self.process(binary.right),
        )

    def _get_limit_or_fetch(self, select):  # SQLA_1.4+
        if select._fetch_clause is None:
            return select._limit_clause
        else:
            return select._fetch_clause

    def _use_top(self, select):  # SQLA_1.4+
        return (
            select._offset_clause is None
            or (
                select._simple_int_clause(select._offset_clause)
                and select._offset == 0
            )
        ) and (
            select._simple_int_clause(select._limit_clause)
            or (
                # limit can use TOP with is by itself. fetch only uses TOP
                # when it needs to because of PERCENT and/or WITH TIES
                select._simple_int_clause(select._fetch_clause)
                and (
                    select._fetch_clause_options["percent"]
                    or select._fetch_clause_options["with_ties"]
                )
            )
        )
