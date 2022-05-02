import unittest

from src.parsing.expr import BinaryOp, ExprBinaryOp, ExprColumn, ExprIntLiteral
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema, TypeMismatchError, Expression


class TestLiteral(unittest.TestCase):
    def test_ints(self):
        self.assertEqual(ExprIntLiteral(
            0).type_check(SymbolTable()), Expression(Schema({}), BaseType.INT))
        self.assertEqual(ExprIntLiteral(
            155).type_check(SymbolTable()), Expression(Schema({}), BaseType.INT))
        self.assertEqual(ExprIntLiteral(
            -2).type_check(SymbolTable()), Expression(Schema({}), BaseType.INT))


class TestBinaryOp(unittest.TestCase):
    def test_bin_op_literals(self):
        self.assertEqual(ExprBinaryOp(ExprIntLiteral(
            9), BinaryOp.ADDITION, ExprIntLiteral(10)).type_check(SymbolTable()),
            Expression(Schema({}), BaseType.INT))

    def test_bin_op_nested(self):
        self.assertEqual(ExprBinaryOp(
            ExprIntLiteral(2),
            BinaryOp.MULTIPLICATION,
            ExprBinaryOp(ExprIntLiteral(
                3), BinaryOp.MULTIPLICATION, ExprIntLiteral(4))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.INT))
        self.assertEqual(ExprBinaryOp(
            ExprBinaryOp(
                ExprBinaryOp(ExprIntLiteral(100),
                             BinaryOp.MULTIPLICATION, ExprIntLiteral(4)),
                BinaryOp.MULTIPLICATION,
                ExprIntLiteral(5)
            ),
            BinaryOp.ADDITION,
            ExprBinaryOp(ExprIntLiteral(-5),
                         BinaryOp.ADDITION, ExprIntLiteral(0))
        ).type_check(SymbolTable()), Expression(Schema({}), BaseType.INT))


class TestColumn(unittest.TestCase):
    def test_column(self):
        st = SymbolTable({
            "a": Schema({"b": BaseType.INT}),
        })
        self.assertEqual(ExprColumn(("a", "b")).type_check(st),
                         Expression(Schema({"a.b": BaseType.INT}), BaseType.INT))
        with self.assertRaises(KeyError):
            ExprColumn(("a", "z")).type_check(st)
        with self.assertRaises(KeyError):
            ExprColumn(("c", "b")).type_check(st)
        st = SymbolTable({
            "a1": Schema({"b": BaseType.INT}),
            "a2": Schema({"b": BaseType.BOOL}),
        })
        self.assertEqual(ExprColumn(("a1", "b")).type_check(st),
                         Expression(Schema({"a1.b": BaseType.INT}), BaseType.INT))

    def test_column_bin_op(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "i": BaseType.INT,
                "j": BaseType.INT,
            }),
        })
        self.assertEqual(ExprBinaryOp(
            ExprColumn(("a", "i")),
            BinaryOp.ADDITION,
            ExprColumn(("a", "j"))
        ).type_check(st), Expression(
            Schema({"a.i": BaseType.INT, "a.j": BaseType.INT}),
            BaseType.INT))

        self.assertEqual(ExprBinaryOp(
            ExprColumn(("a", "i")),
            BinaryOp.MULTIPLICATION,
            ExprIntLiteral(1000)
        ).type_check(st), Expression(
            Schema({"a.i": BaseType.INT}),
            BaseType.INT))

        self.assertEqual(ExprBinaryOp(
            ExprColumn(("a", "j")),
            BinaryOp.ADDITION,
            ExprBinaryOp(
                ExprIntLiteral(-1),
                BinaryOp.MULTIPLICATION,
                ExprColumn(("a", "j"))
            )
        ).type_check(st), Expression(
            Schema({"a.j": BaseType.INT, "a.j": BaseType.INT}),
            BaseType.INT))

        with self.assertRaises(TypeMismatchError):
            ExprBinaryOp(ExprColumn(
                ("a", "b")), BinaryOp.MULTIPLICATION, ExprIntLiteral(1)).type_check(st)
