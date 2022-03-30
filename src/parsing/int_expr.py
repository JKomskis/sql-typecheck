from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string

from src.parsing.terminals import int_literal, lparen, rparen, c_name, padding


@dataclass
class IExpr():
    pass


@dataclass
class IExprIntLiteral(IExpr):
    value: int


@dataclass
class IExprColumn(IExpr):
    table_column_name: Tuple[str, str]


class BinaryIntOp(Enum):
    MULTIPLICATION = 1
    ADDITION = 2


@dataclass
class IExprBinaryOp(IExpr):
    left: IExpr
    op: BinaryIntOp
    right: IExpr


@generate
def i_expr_int_literal() -> IExprIntLiteral:
    value = yield int_literal

    return IExprIntLiteral(value)


@generate
def i_expr_column() -> IExprColumn:
    name = yield c_name

    return IExprColumn(name)


@generate
def i_expr() -> IExpr:
    node = yield i_expr_mult

    while True:
        res = yield (padding >> string("+") << padding).optional()
        if res == None:
            break
        right = yield i_expr_mult

        node = IExprBinaryOp(node, BinaryIntOp.ADDITION, right)

    return node


@generate
def i_expr_mult() -> IExpr:
    node = yield i_expr_paren_terminal

    while True:
        res = yield (padding >> string("*") << padding).optional()
        if res == None:
            break
        right = yield i_expr_paren_terminal

        node = IExprBinaryOp(node, BinaryIntOp.MULTIPLICATION, right)

    return node


@generate
def i_expr_paren_terminal() -> IExpr:
    node = yield i_expr_int_literal \
        | i_expr_column \
        | lparen >> i_expr << rparen  # \
    # | i_expr
    return node
