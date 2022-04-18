import unittest

from src.parsing.bool_expr import BExprAnd, BExprBoolLiteral, BExprColumn, BExprEquality, BExprNot, EqualityOperator
from src.parsing.int_expr import IExprIntLiteral

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TypeCheckingError, TypeMismatchError


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(BExprBoolLiteral(
            True).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_false(self):
        self.assertEqual(BExprBoolLiteral(
            False).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))


class TestAnd(unittest.TestCase):
    def test_and_literals(self):
        self.assertEqual(BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(
            True)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_and_nested(self):
        self.assertEqual(BExprAnd(
            BExprBoolLiteral(True),
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(BExprAnd(
            BExprAnd(
                BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True)),
                BExprBoolLiteral(True)
            ),
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(False))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))


class TestNot(unittest.TestCase):
    def test_not_literals(self):
        self.assertEqual(BExprNot(BExprBoolLiteral(False)).type_check(
            SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_not_nested(self):
        self.assertEqual(BExprNot(BExprNot(BExprBoolLiteral(True))).type_check(
            SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(BExprNot(BExprAnd(
            BExprNot(BExprBoolLiteral(True)),
            BExprBoolLiteral(True)
        )).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))


class TestEquality(unittest.TestCase):
    def test_equals(self):
        self.assertEqual(BExprEquality(BExprBoolLiteral(True), EqualityOperator.EQUALS,
                         BExprBoolLiteral(False)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeCheckingError):
        #     BExprEquality(BExprBoolLiteral(False), EqualityOperator.LESS_THAN,
        #                   BExprBoolLiteral(True)).type_check(SymbolTable())

    def test_equals_and_nested(self):
        self.assertEqual(BExprEquality(
            BExprBoolLiteral(True),
            EqualityOperator.EQUALS,
            BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(False))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeCheckingError):
        #     BExprEquality(
        #         BExprBoolLiteral(False),
        #         EqualityOperator.EQUALS,
        #         BExprEquality(BExprBoolLiteral(False), EqualityOperator.LESS_THAN, BExprBoolLiteral(True)
        #                       ).type_check(SymbolTable()))

    def test_equals_int(self):
        self.assertEqual(BExprEquality(IExprIntLiteral(2), EqualityOperator.EQUALS,
                         IExprIntLiteral(3)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(BExprEquality(IExprIntLiteral(-3), EqualityOperator.LESS_THAN,
                         IExprIntLiteral(3)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeCheckingError):
        #     BExprEquality(IExprIntLiteral(0), EqualityOperator.LESS_THAN,
        #                   BExprBoolLiteral(False)).type_check(SymbolTable())
        # with self.assertRaises(TypeCheckingError):
        #     BExprEquality(BExprBoolLiteral(True), EqualityOperator.EQUALS,
        #                   IExprIntLiteral(1)).type_check(SymbolTable())

    def test_equals_and_int(self):
        self.assertEqual(BExprEquality(
            BExprEquality(
                IExprIntLiteral(-1),
                EqualityOperator.EQUALS,
                IExprIntLiteral(1)
            ),
            EqualityOperator.EQUALS,
            BExprBoolLiteral(True)
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(BExprAnd(
            BExprEquality(
                IExprIntLiteral(42),
                EqualityOperator.EQUALS,
                IExprIntLiteral(42)
            ),
            BExprEquality(
                IExprIntLiteral(-6),
                EqualityOperator.EQUALS,
                IExprIntLiteral(-9)
            )
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(BExprAnd(
            BExprEquality(
                IExprIntLiteral(42),
                EqualityOperator.EQUALS,
                IExprIntLiteral(42)
            ),
            BExprEquality(
                BExprBoolLiteral(True),
                EqualityOperator.EQUALS,
                BExprBoolLiteral(False)
            )
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeCheckingError):
        #     BExprAnd(
        #         BExprEquality(
        #             IExprIntLiteral(-1),
        #             EqualityOperator.EQUALS,
        #             IExprIntLiteral(1)
        #         ),
        #         IExprIntLiteral(0)
        #     ).type_check(SymbolTable())


class TestColumn(unittest.TestCase):
    def test_column(self):
        st = SymbolTable({
            "a": Schema({"b": BaseType.BOOL}),
        })
        self.assertEqual(BExprColumn(("a", "b")).type_check(
            st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        # with self.assertRaises(KeyError):
        #     BExprColumn(("a", "z")).type_check(st)
        # with self.assertRaises(KeyError):
        #     BExprColumn(("c", "b")).type_check(st)
        # TODO: handle above error

    def test_column_and(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "c": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(BExprAnd(BExprColumn(("a", "b")), BExprColumn(
            ("a", "c"))).type_check(st), Expression(Schema({"a.b": BaseType.BOOL, "a.c": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(BExprAnd(BExprBoolLiteral(True), BExprColumn(
            ("a", "c"))).type_check(st), Expression(Schema({"a.c": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(BExprAnd(
            BExprAnd(BExprBoolLiteral(True), BExprColumn(("a", "c"))),
            BExprColumn(("a", "c"))
        ).type_check(st), Expression(Schema({"a.c": BaseType.BOOL}), BaseType.BOOL))
        # with self.assertRaises(TypeMismatchError):
        #     BExprAnd(BExprBoolLiteral(True),
        #              BExprColumn(("a", "i"))).type_check(st)

    def test_column_not(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(BExprNot(BExprColumn(("a", "b"))
                                  ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(BExprAnd(
            BExprColumn(("a", "b")),
            BExprNot(BExprColumn(("a", "b")))
        ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeMismatchError):
        #     BExprNot(BExprColumn(("a", "i"))).type_check(st)

    def test_column_equality(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "c": BaseType.BOOL,
                "i": BaseType.INT,
                "s": BaseType.VARCHAR,
            }),
        })
        # TODO: add varchar expressions
        # self.assertEqual(BExprEquality(
        #     VExprColumn(("a", "s")),
        #     EqualityOperator.LESS_THAN,
        #     VExprColumn(("a", "s"))
        # ).type_check(st), Expression(Schema({"s": BaseType.VARCHAR, "s": BaseType.VARCHAR}), BaseType.BOOL))
        self.assertEqual(BExprEquality(
            BExprColumn(("a", "b")),
            EqualityOperator.EQUALS,
            BExprColumn(("a", "c"))
        ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL, "a.c": BaseType.BOOL}), BaseType.BOOL))
        # TODO: fix error
        # with self.assertRaises(TypeMismatchError):
        #     BExprEquality(BExprColumn(("a", "i")), EqualityOperator.EQUALS, BExprColumn(
        #         ("a", "s"))).type_check(st)
