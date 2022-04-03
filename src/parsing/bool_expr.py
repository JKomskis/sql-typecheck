from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string, index

from src.parsing.data_structures import Expr
from src.parsing.int_expr import IExpr, i_expr
from src.parsing.terminals import bool_literal, string_ignore_case, lparen, rparen, padding, c_name


@dataclass
class BExpr(Expr):
    pass


@dataclass
class BExprBoolLiteral(BExpr):
    value: bool


@dataclass
class BExprColumn(BExpr):
    table_column_name: Tuple[str, str]


@dataclass
class BExprAnd(BExpr):
    left: BExpr
    right: BExpr


@dataclass
class BExprNot(BExpr):
    node: BExpr


class EqualityOperator(Enum):
    EQUALS = 1
    LESS_THAN = 2


@dataclass
class BExprEquality(BExpr):
    left: IExpr
    op: EqualityOperator
    right: IExpr


@generate
def b_expr_bool_literal() -> BExprBoolLiteral:
    value = yield bool_literal

    return BExprBoolLiteral(value)


@generate
def b_expr_column() -> BExprColumn:
    name = yield c_name

    return BExprColumn(name)


@generate
def b_expr_equality() -> BExprEquality:
    left = yield i_expr
    op_str = yield padding >> (string("=") | string("<")) << padding
    op = None
    if op_str == "=":
        op = EqualityOperator.EQUALS
    elif op_str == "<":
        op = EqualityOperator.LESS_THAN
    right = yield i_expr

    return BExprEquality(left, op, right)


@generate
def b_expr() -> BExpr:
    node = yield b_expr_negation

    while True:
        res = yield (whitespace >> string_ignore_case("AND") << whitespace).optional()
        if res == None:
            break
        right = yield b_expr_negation

        node = BExprAnd(node, right)

    return node


@generate
def b_expr_negation() -> BExpr:
    negate = yield (string_ignore_case("NOT") << whitespace).optional()
    node = yield b_expr_paren_terminal
    if negate != None:
        node = BExprNot(node)
    return node


@generate
def b_expr_paren_terminal() -> BExpr:
    node = yield b_expr_bool_literal \
        | b_expr_equality \
        | b_expr_column \
        | lparen >> b_expr << rparen \
        | b_expr
    return node
