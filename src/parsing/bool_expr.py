from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from parsy import generate, whitespace, string, index

from src.parsing.data_structures import Expr
from src.parsing.int_expr import IExpr, i_expr
from src.parsing.terminals import bool_literal, string_ignore_case, lparen, rparen, padding, c_name

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TableFieldPair, TypeCheckingError, TypeMismatchError


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
    table_column_name: TableFieldPair

    def type_check(self, st: SymbolTable) -> Expression:
        table, col = self.table_column_name
        table_schema = st[table]

        if table_schema.fields[col] != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, table_schema.fields[col])

        return Expression(
            Schema({f"{table}.{col}": BaseType.BOOL}),
            BaseType.BOOL
        )


@dataclass
class BExprAnd(BExpr):
    left: BExpr
    right: BExpr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        if left_type.output != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, left_type)
        right_type = self.right.type_check(st)
        if right_type.output != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, right_type)
        return Expression(
            Schema.concat(left_type.inputs, right_type.inputs),
            BaseType.BOOL
        )


@dataclass
class BExprNot(BExpr):
    node: BExpr

    def type_check(self, st: SymbolTable) -> Expression:
        node_type = self.node.type_check(st)
        if node_type.output != BaseType.BOOL:
            raise TypeMismatchError(BaseType.BOOL, node_type)
        return node_type


class EqualityOperator(Enum):
    EQUALS = 1
    LESS_THAN = 2


@dataclass
class BExprEquality(BExpr):
    left: IExpr
    op: EqualityOperator
    right: IExpr

    def type_check(self, st: SymbolTable) -> Expression:
        left_type = self.left.type_check(st)
        if left_type.output == BaseType.INT or left_type.output == BaseType.VARCHAR or (
            self.op == EqualityOperator.EQUALS and left_type.output == BaseType.BOOL
        ):
            right_type = self.right.type_check(st)
            if left_type.output != right_type.output:
                raise TypeMismatchError(left_type.output, right_type.output)
            return Expression(
                Schema.concat(left_type.inputs, right_type.inputs),
                BaseType.BOOL
            )
        raise TypeCheckingError(
            f"Cannot apply operator {self.op} to type {left_type}")


@generate
def b_expr_bool_literal():
    value = yield bool_literal

    return BExprBoolLiteral(value)


@generate
def b_expr_column():
    name = yield c_name

    return BExprColumn(name)


@generate
def b_expr_equality():
    left = yield i_expr
    op_str = yield padding >> (string("=") | string("<")) << padding
    op = EqualityOperator.EQUALS
    if op_str == "=":
        op = EqualityOperator.EQUALS
    elif op_str == "<":
        op = EqualityOperator.LESS_THAN
    right = yield i_expr

    return BExprEquality(left, op, right)


@generate
def b_expr():
    node = yield b_expr_negation

    while True:
        res = yield (whitespace >> string_ignore_case("AND") << whitespace).optional()
        if res == None:
            break
        right = yield b_expr_negation

        node = BExprAnd(node, right)

    return node


@generate
def b_expr_negation():
    negate = yield (string_ignore_case("NOT") << whitespace).optional()
    node = yield b_expr_paren_terminal
    if negate != None:
        node = BExprNot(node)
    return node


@generate
def b_expr_paren_terminal():
    node = yield b_expr_bool_literal \
        | b_expr_equality \
        | b_expr_column \
        | lparen >> b_expr << rparen \
        | b_expr
    return node
