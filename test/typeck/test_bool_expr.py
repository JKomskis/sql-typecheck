import unittest

from src.parsing.bool_expr import BExprAnd, BExprBoolLiteral, BExprColumn, BExprEquality, BExprNot, EqualityOperator

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema, TypeCheckingError, TypeMismatchError


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(BExprBoolLiteral(
            True).type_check(SymbolTable()), BaseType.BOOL)

    def test_false(self):
        self.assertEqual(BExprBoolLiteral(
            False).type_check(SymbolTable()), BaseType.BOOL)


class TestAnd(unittest.TestCase):
    def test_and_literals(self):
        self.assertEqual(BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(
            True)).type_check(SymbolTable()), BaseType.BOOL)

    def test_and_nested(self):
        self.assertEqual(BExprAnd(
            BExprBoolLiteral(True),
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True))
        ).type_check(SymbolTable()), BaseType.BOOL)
        self.assertEqual(BExprAnd(
            BExprAnd(
                BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True)),
                BExprBoolLiteral(True)
            ),
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(False))
        ).type_check(SymbolTable()), BaseType.BOOL)


class TestNot(unittest.TestCase):
    def test_not_literals(self):
        self.assertEqual(BExprNot(BExprBoolLiteral(False)).type_check(
            SymbolTable()), BaseType.BOOL)

    def test_not_nested(self):
        self.assertEqual(BExprNot(BExprNot(BExprBoolLiteral(True))).type_check(
            SymbolTable()), BaseType.BOOL)
        self.assertEqual(BExprNot(BExprAnd(
            BExprNot(BExprBoolLiteral(True)),
            BExprBoolLiteral(True)
        )).type_check(SymbolTable()), BaseType.BOOL)


class TestEquality(unittest.TestCase):
    def test_equals(self):
        self.assertEqual(BExprEquality(BExprBoolLiteral(True), EqualityOperator.EQUALS,
                         BExprBoolLiteral(False)).type_check(SymbolTable()), BaseType.BOOL)
        with self.assertRaises(TypeCheckingError):
            BExprEquality(BExprBoolLiteral(False), EqualityOperator.LESS_THAN,
                          BExprBoolLiteral(True)).type_check(SymbolTable())

    def test_equals_and_nested(self):
        self.assertEqual(BExprEquality(
            BExprBoolLiteral(True),
            EqualityOperator.EQUALS,
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(False))
        ).type_check(SymbolTable()), BaseType.BOOL)
        with self.assertRaises(TypeCheckingError):
            BExprEquality(
                BExprBoolLiteral(False),
                EqualityOperator.EQUALS,
                BExprEquality(BExprBoolLiteral(False), EqualityOperator.LESS_THAN, BExprBoolLiteral(True)
                              ).type_check(SymbolTable()))


class TestColumn(unittest.TestCase):
    def test_column(self):
        st = SymbolTable({
            "a": Schema({"b": BaseType.BOOL}),
        })
        self.assertEqual(BExprColumn(("a", "b")).type_check(st), BaseType.BOOL)
        with self.assertRaises(KeyError):
            BExprColumn(("a", "z")).type_check(st)
        with self.assertRaises(KeyError):
            BExprColumn(("c", "b")).type_check(st)

    def test_column_and(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "c": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(BExprAnd(BExprColumn(("a", "b")), BExprColumn(
            ("a", "c"))).type_check(st), BaseType.BOOL)
        self.assertEqual(BExprAnd(BExprBoolLiteral(True), BExprColumn(
            ("a", "c"))).type_check(st), BaseType.BOOL)
        self.assertEqual(BExprAnd(
            BExprAnd(BExprBoolLiteral(True), BExprColumn(("a", "c"))),
            BExprColumn(("a", "c"))
        ).type_check(st), BaseType.BOOL)
        with self.assertRaises(TypeMismatchError):
            BExprAnd(BExprBoolLiteral(True),
                     BExprColumn(("a", "i"))).type_check(st)

    def test_column_not(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(BExprNot(BExprColumn(("a", "b"))
                                  ).type_check(st), BaseType.BOOL)
        self.assertEqual(BExprAnd(
            BExprColumn(("a", "b")),
            BExprNot(BExprColumn(("a", "b")))
        ).type_check(st), BaseType.BOOL)
        with self.assertRaises(TypeMismatchError):
            BExprNot(BExprColumn(("a", "i"))).type_check(st)

    def test_column_equality(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "c": BaseType.BOOL,
                "i": BaseType.INT,
                "s": BaseType.VARCHAR,
            }),
        })
        self.assertEqual(BExprEquality(
            BExprColumn(("a", "s")),
            EqualityOperator.LESS_THAN,
            BExprColumn(("a", "s"))
        ).type_check(st), BaseType.BOOL)
        self.assertEqual(BExprEquality(
            BExprColumn(("a", "b")),
            EqualityOperator.EQUALS,
            BExprColumn(("a", "c"))
        ).type_check(st), BaseType.BOOL)
        with self.assertRaises(TypeMismatchError):
            BExprEquality(BExprColumn(("a", "i")), EqualityOperator.EQUALS, BExprColumn(
                ("a", "s"))).type_check(st)
