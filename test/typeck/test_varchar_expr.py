from symtable import Symbol
import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprColumn, ExprConcat,
                              ExprIntLiteral, ExprSubstr, ExprVarcharLiteral,
                              expr)
from src.types.types import BaseType, Schema, TypeMismatchError, Expression
from src.types.symbol_table import SymbolTable


class TestLiteral(unittest.TestCase):
    def test_ints(self):
        self.assertEqual(ExprVarcharLiteral("test"
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.VARCHAR))
        self.assertEqual(ExprVarcharLiteral("1234"
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.VARCHAR))



class TestConcat(unittest.TestCase):
    def test_concat_literal(self):
        self.assertEqual(ExprConcat(ExprVarcharLiteral("test"), ExprVarcharLiteral("test2")
        ).type_check(SymbolTable()),
        Expression(Schema({}), BaseType.VARCHAR))

        self.assertEqual(ExprConcat(ExprVarcharLiteral("test"), ExprVarcharLiteral("test2")
        ).type_check(SymbolTable()),
        Expression(Schema({}), BaseType.VARCHAR))

    def test_concat_col_literal(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprConcat(ExprVarcharLiteral("test"), ExprColumn(("a", "col"))
        ).type_check(st),
        Expression(Schema({"a.col": BaseType.VARCHAR}), BaseType.VARCHAR))

    def test_concat_cols(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
            "b": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprConcat(ExprColumn(("b", "col")), ExprColumn(("a", "col"))
        ).type_check(st),
        Expression(Schema({"b.col": BaseType.VARCHAR, "a.col": BaseType.VARCHAR}), BaseType.VARCHAR))
        # todo/issue: the schema ordering changes & matters depending on the ordering of concat

    def test_concat_nested(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
            "b": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprConcat(ExprColumn(("b", "col")),
                                    ExprConcat(ExprVarcharLiteral("test"), ExprColumn(("a", "col")))
        ).type_check(st),
        Expression(Schema({"b.col": BaseType.VARCHAR, "a.col": BaseType.VARCHAR}), BaseType.VARCHAR))

    def test_concat_substr_nested(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
            "b": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprConcat(ExprColumn(("b", "col")),
                                    ExprSubstr(ExprVarcharLiteral(
                                        "hello world"), ExprIntLiteral(0), ExprIntLiteral(5))
                                    
        ).type_check(st),
        Expression(Schema({"b.col": BaseType.VARCHAR}), BaseType.VARCHAR))


class TestSubstr(unittest.TestCase):
    def test_substr_literal(self):
        self.assertEqual(ExprSubstr(ExprVarcharLiteral("test"), ExprIntLiteral(1), ExprIntLiteral(3)
        ).type_check(SymbolTable()),
        Expression(Schema({}), BaseType.VARCHAR))

    def test_substr_literal_add(self):
        self.assertEqual(ExprSubstr(ExprVarcharLiteral("test"),
                         ExprBinaryOp(ExprIntLiteral(0),
                                      BinaryOp.ADDITION,
                                      ExprIntLiteral(1)), ExprIntLiteral(3))
        .type_check(SymbolTable()),
        Expression(Schema({}), BaseType.VARCHAR))

    def test_substr_col(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
            "b": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprSubstr(ExprColumn(("a", "col")),
                         ExprBinaryOp(ExprIntLiteral(0),
                                      BinaryOp.ADDITION,
                                      ExprIntLiteral(1)), ExprIntLiteral(3)
        ).type_check(st),
        Expression(Schema({"a.col": BaseType.VARCHAR}), BaseType.VARCHAR))

    def test_substr_nested(self):
        st = SymbolTable({
            "a": Schema({"col": BaseType.VARCHAR}),
            "b": Schema({"col": BaseType.VARCHAR}),
        })
        self.assertEqual(ExprSubstr(ExprSubstr(ExprColumn(("a", "col")),
                                               ExprIntLiteral(3),
                                               ExprIntLiteral(20)),  ExprIntLiteral(1), ExprIntLiteral(5)
        ).type_check(st),
        Expression(Schema({"a.col": BaseType.VARCHAR}), BaseType.VARCHAR))

    def test_substr_concat(self):
        self.assertEqual(ExprSubstr(
            ExprConcat(
                ExprVarcharLiteral("hello"),
                ExprVarcharLiteral("world")
            ),  ExprIntLiteral(1), ExprIntLiteral(5)
        ).type_check(SymbolTable()),
        Expression(Schema({}), BaseType.VARCHAR))
