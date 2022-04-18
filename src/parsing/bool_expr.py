from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string, index

from src.parsing.data_structures import Expr
from src.parsing.int_expr import IExpr, i_expr
from src.parsing.terminals import bool_literal, string_ignore_case, lparen, rparen, padding, c_name

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TypeCheckingError, TypeMismatchError


@dataclass
class BExpr(Expr):
    pass


@dataclass
class BExprBoolLiteral(BExpr):
    value: bool

    def type_check(self, _: SymbolTable) -> Expression:
        return Expression(
            Schema({}),
            BaseType.BOOL
        )


@dataclass
class BExprColumn(BExpr):
    table_column_name: Tuple[str, str]

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]
        return Expression(
            Schema({table_schema.fields[col], BaseType.BOOL}),
            BaseType.BOOL
        )


@dataclass
class BExprAnd(BExpr):
    left: BExpr
    right: BExpr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        right_type = self.right.type_check(st)
        return Expression(
            Schema.concat(left_type.inputs, right_type.inputs),
            BaseType.BOOL
        )


@dataclass
class BExprNot(BExpr):
    node: BExpr

    def type_check(self, st: SymbolTable) -> Expression:
        return Expression(
            self.node.type_check(st).inputs,
            BaseType.BOOL
        )


class EqualityOperator(Enum):
    EQUALS = 1
    LESS_THAN = 2


@dataclass
class BExprEquality(BExpr):
    left: IExpr
    op: EqualityOperator
    right: IExpr

    def type_check(self, st: SymbolTable) -> Expression:
        # left_type = self.left.type_check(st)
        # if left_type == BaseType.INT or left_type == BaseType.VARCHAR or (
        #     self.op == EqualityOperator.EQUALS and left_type == BaseType.BOOL
        # ):
        #     self.right.expect_type(st, left_type)
        #     return BaseType.BOOL
        # raise TypeCheckingError(
        #     f"Cannot apply operator {self.op} to type {left_type}")
        left_type = self.left.type_check(st)
        right_type = self.right.type_check(st)
        return Expression(
            Schema.concat(left_type.inputs, right_type.inputs),
            BaseType.BOOL
        )


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
