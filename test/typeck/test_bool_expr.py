import unittest

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Expression, Schema, TypeCheckingError, TypeMismatchError
from src.parsing.expr import BinaryOp, ExprBinaryOp, ExprBoolLiteral, ExprColumn, ExprIntLiteral, ExprNot


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(ExprBoolLiteral(
            True).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_false(self):
        self.assertEqual(ExprBoolLiteral(
            False).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))


class TestAnd(unittest.TestCase):
    def test_and_literals(self):
        self.assertEqual(ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND, ExprBoolLiteral(
            True)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_and_nested(self):
        self.assertEqual(ExprBinaryOp(
            ExprBoolLiteral(True),
            BinaryOp.AND,
            ExprBinaryOp(ExprBoolLiteral(False),
                         BinaryOp.AND, ExprBoolLiteral(True))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(False),
                             BinaryOp.AND, ExprBoolLiteral(True)),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            ),
            BinaryOp.AND,
            ExprBinaryOp(ExprBoolLiteral(False),
                         BinaryOp.AND, ExprBoolLiteral(False))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))


class TestNot(unittest.TestCase):
    def test_not_literals(self):
        self.assertEqual(ExprNot(ExprBoolLiteral(False)).type_check(
            SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_not_nested(self):
        self.assertEqual(ExprNot(ExprNot(ExprBoolLiteral(True))).type_check(
            SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(ExprNot(ExprBinaryOp(
            ExprNot(ExprBoolLiteral(True)),
            BinaryOp.AND,
            ExprBoolLiteral(True)
        )).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))

    def test_not_bool(self):
        with self.assertRaises(TypeCheckingError):
            self.assertEqual(ExprNot(ExprIntLiteral(0)
                                     ).type_check(SymbolTable()))


class TestEquality(unittest.TestCase):
    def test_equals(self):
        self.assertEqual(ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.EQUALS,
                         ExprBoolLiteral(False)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        with self.assertRaises(TypeCheckingError):
            ExprBinaryOp(ExprBoolLiteral(False), BinaryOp.LESS_THAN,
                         ExprBoolLiteral(True)).type_check(SymbolTable())

    def test_equals_and_nested(self):
        self.assertEqual(ExprBinaryOp(
            ExprBoolLiteral(True),
            BinaryOp.EQUALS,
            ExprBinaryOp(ExprBoolLiteral(False),
                         BinaryOp.AND, ExprBoolLiteral(False))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        with self.assertRaises(TypeCheckingError):
            ExprBinaryOp(
                ExprBoolLiteral(False),
                BinaryOp.EQUALS,
                ExprBinaryOp(ExprBoolLiteral(False), BinaryOp.LESS_THAN, ExprBoolLiteral(True)
                             ).type_check(SymbolTable()))

    def test_equals_int(self):
        self.assertEqual(ExprBinaryOp(ExprIntLiteral(2), BinaryOp.EQUALS,
                         ExprIntLiteral(3)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(ExprIntLiteral(-3), BinaryOp.LESS_THAN,
                         ExprIntLiteral(3)).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        with self.assertRaises(TypeCheckingError):
            ExprBinaryOp(ExprIntLiteral(0), BinaryOp.LESS_THAN,
                         ExprBoolLiteral(False)).type_check(SymbolTable())
        with self.assertRaises(TypeCheckingError):
            ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.EQUALS,
                         ExprIntLiteral(1)).type_check(SymbolTable())

    def test_equals_and_int(self):
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(
                ExprIntLiteral(-1),
                BinaryOp.EQUALS,
                ExprIntLiteral(1)
            ),
            BinaryOp.EQUALS,
            ExprBoolLiteral(True)
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(
                ExprIntLiteral(42),
                BinaryOp.EQUALS,
                ExprIntLiteral(42)
            ),
            BinaryOp.AND,
            ExprBinaryOp(
                ExprIntLiteral(-6),
                BinaryOp.EQUALS,
                ExprIntLiteral(-9)
            )
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(
                ExprIntLiteral(42),
                BinaryOp.EQUALS,
                ExprIntLiteral(42)
            ),
            BinaryOp.AND,
            ExprBinaryOp(
                ExprBoolLiteral(True),
                BinaryOp.EQUALS,
                ExprBoolLiteral(False)
            )
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.BOOL))
        with self.assertRaises(TypeCheckingError):
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprIntLiteral(-1),
                    BinaryOp.EQUALS,
                    ExprIntLiteral(1)
                ),
                BinaryOp.AND,
                ExprIntLiteral(0)
            ).type_check(SymbolTable())


class TestColumn(unittest.TestCase):
    def test_column(self):
        st = SymbolTable({
            "a": Schema({"b": BaseType.BOOL}),
        })
        self.assertEqual(ExprColumn(("a", "b")).type_check(
            st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        with self.assertRaises(KeyError):
            ExprColumn(("a", "z")).type_check(st)
        with self.assertRaises(KeyError):
            ExprColumn(("c", "b")).type_check(st)

    def test_column_and(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "c": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(ExprBinaryOp(ExprColumn(("a", "b")), BinaryOp.AND, ExprColumn(
            ("a", "c"))).type_check(st), Expression(Schema({"a.b": BaseType.BOOL, "a.c": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND, ExprColumn(
            ("a", "c"))).type_check(st), Expression(Schema({"a.c": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                         ExprColumn(("a", "c"))),
            BinaryOp.AND,
            ExprColumn(("a", "c"))
        ).type_check(st), Expression(Schema({"a.c": BaseType.BOOL}), BaseType.BOOL))
        with self.assertRaises(TypeMismatchError):
            ExprBinaryOp(ExprBoolLiteral(True),
                         BinaryOp.AND,
                         ExprColumn(("a", "i"))).type_check(st)

    def test_column_not(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "i": BaseType.INT,
            }),
        })
        self.assertEqual(ExprNot(ExprColumn(("a", "b"))
                                 ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprColumn(("a", "b")),
            BinaryOp.AND,
            ExprNot(ExprColumn(("a", "b")))
        ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL}), BaseType.BOOL))
        with self.assertRaises(TypeMismatchError):
            ExprNot(ExprColumn(("a", "i"))).type_check(st)

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
        # self.assertEqual(ExprBinaryOp(
        #     VExprColumn(("a", "s")),
        #     BinaryOp.LESS_THAN,
        #     VExprColumn(("a", "s"))
        # ).type_check(st), Expression(Schema({"s": BaseType.VARCHAR, "s": BaseType.VARCHAR}), BaseType.BOOL))
        self.assertEqual(ExprBinaryOp(
            ExprColumn(("a", "b")),
            BinaryOp.EQUALS,
            ExprColumn(("a", "c"))
        ).type_check(st), Expression(Schema({"a.b": BaseType.BOOL, "a.c": BaseType.BOOL}), BaseType.BOOL))
        with self.assertRaises(TypeMismatchError):
            ExprBinaryOp(ExprColumn(("a", "i")), BinaryOp.EQUALS, ExprColumn(
                ("a", "s"))).type_check(st)
