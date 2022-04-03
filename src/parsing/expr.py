from dataclasses import dataclass
from typing import Tuple
from parsy import generate

from src.parsing.data_structures import Expr
from src.parsing.int_expr import i_expr
from src.parsing.bool_expr import b_expr
from src.parsing.terminals import c_name


@dataclass
class ExprColumn(Expr):
    table_column_name: Tuple[str, str]


@generate
def expr_column() -> ExprColumn:
    name = yield c_name

    return ExprColumn(name)


expr = expr_column | b_expr | i_expr
