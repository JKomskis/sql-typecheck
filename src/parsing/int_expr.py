from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string

from src.parsing.data_structures import Expr
from src.parsing.terminals import int_literal, lparen, rparen, c_name, padding

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TableFieldPair, TypeMismatchError


@dataclass
class IExpr(Expr):
    pass


@dataclass
class IExprIntLiteral(IExpr):
    value: int

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.INT
        )

    def get_name(self) -> str:
        return str(self.value)


@dataclass
class IExprColumn(IExpr):
    table_column_name: TableFieldPair

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]

        if table_schema.fields[col] != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, table_schema.fields[col])

        return Expression(
            Schema({f"{table}.{col}": BaseType.INT}),
            BaseType.INT
        )

    def get_name(self) -> str:
        return self.table_column_name[1]


class BinaryIntOp(Enum):
    MULTIPLICATION = "times"
    ADDITION = "plus"


@dataclass
class IExprBinaryOp(IExpr):
    left: IExpr
    op: BinaryIntOp
    right: IExpr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        if left_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, left_type)
        right_type = self.right.type_check(st)
        if right_type.output != BaseType.INT:
            raise TypeMismatchError(BaseType.INT, right_type)
        return Expression(
            Schema.concat(left_type.inputs, right_type.inputs),
            BaseType.INT
        )

    def get_name(self) -> str:
        return f"{self.left.get_name()}_{self.op.value}_{self.right.get_name()}"


@generate
def i_expr_int_literal():
    value = yield int_literal

    return IExprIntLiteral(value)


@generate
def i_expr_column():
    name = yield c_name

    return IExprColumn(name)


@generate
def i_expr():
    node = yield i_expr_mult

    while True:
        res = yield (padding >> string("+") << padding).optional()
        if res == None:
            break
        right = yield i_expr_mult

        node = IExprBinaryOp(node, BinaryIntOp.ADDITION, right)

    return node


@generate
def i_expr_mult():
    node = yield i_expr_paren_terminal

    while True:
        res = yield (padding >> string("*") << padding).optional()
        if res == None:
            break
        right = yield i_expr_paren_terminal

        node = IExprBinaryOp(node, BinaryIntOp.MULTIPLICATION, right)

    return node


@generate
def i_expr_paren_terminal():
    node = yield i_expr_int_literal \
        | i_expr_column \
        | lparen >> i_expr << rparen
    return node
