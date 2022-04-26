from dataclasses import dataclass
from typing import Tuple
from parsy import generate, whitespace

from src.parsing.data_structures import Expr, SExpr
from src.parsing.int_expr import i_expr
from src.parsing.bool_expr import b_expr
from src.parsing.terminals import c_name, identifier, string_ignore_case
from src.parsing.varchar_expr import v_expr
from src.types.symbol_table import SymbolTable
from src.types.types import Expression, Schema


@dataclass
class ExprColumn(Expr):
    table_column_name: Tuple[str, str]

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]

        return Expression(
            Schema({f"{table}.{col}": table_schema.fields[col]}),
            table_schema.fields[col]
        )

    def get_name(self) -> str:
        return self.table_column_name[1]


@generate
def expr_column():
    name = yield c_name

    return ExprColumn(name)


expr = expr_column | b_expr | i_expr | v_expr


@generate
def s_expr():
    internal_expr = yield expr
    name = yield (whitespace >> string_ignore_case("AS") >> whitespace >> identifier).optional()
    return SExpr(internal_expr, name)
