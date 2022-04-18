import unittest

from src.parsing.int_expr import BinaryIntOp, IExprBinaryOp, IExprColumn, IExprIntLiteral

from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema, TypeMismatchError


class TestLiteral(unittest.TestCase):
    def test_ints(self):
        self.assertEqual(IExprIntLiteral(
            0).type_check(SymbolTable()), BaseType.INT)
        self.assertEqual(IExprIntLiteral(
            155).type_check(SymbolTable()), BaseType.INT)
        self.assertEqual(IExprIntLiteral(
            -2).type_check(SymbolTable()), BaseType.INT)


class TestBinaryOp(unittest.TestCase):
    def test_bin_op_literals(self):
        self.assertEqual(IExprBinaryOp(IExprIntLiteral(
            9), BinaryIntOp.ADDITION, IExprIntLiteral(10)).type_check(SymbolTable()), BaseType.INT)

    def test_bin_op_nested(self):
        self.assertEqual(IExprBinaryOp(
            IExprIntLiteral(2),
            BinaryIntOp.MULTIPLICATION,
            IExprBinaryOp(IExprIntLiteral(
                3), BinaryIntOp.MULTIPLICATION, IExprIntLiteral(4))
        ).type_check(SymbolTable()), BaseType.INT)
        self.assertEqual(IExprBinaryOp(
            IExprBinaryOp(
                IExprBinaryOp(IExprIntLiteral(100),
                              BinaryIntOp.MULTIPLICATION, IExprIntLiteral(4)),
                BinaryIntOp.MULTIPLICATION,
                IExprIntLiteral(5)
            ),
            BinaryIntOp.ADDITION,
            IExprBinaryOp(IExprIntLiteral(-5),
                          BinaryIntOp.ADDITION, IExprIntLiteral(0))
        ).type_check(SymbolTable()), BaseType.INT)


class TestColumn(unittest.TestCase):
    def test_column(self):
        st = SymbolTable({
            "a": Schema({"b": BaseType.INT}),
        })
        self.assertEqual(IExprColumn(("a", "b")).type_check(st), BaseType.INT)
        with self.assertRaises(KeyError):
            IExprColumn(("a", "z")).type_check(st)
        with self.assertRaises(KeyError):
            IExprColumn(("c", "b")).type_check(st)

    def test_column_bin_op(self):
        st = SymbolTable({
            "a": Schema({
                "b": BaseType.BOOL,
                "i": BaseType.INT,
                "j": BaseType.INT,
            }),
        })
        self.assertEqual(IExprBinaryOp(
            IExprColumn(("a", "i")),
            BinaryIntOp.ADDITION,
            IExprColumn(("a", "j"))
        ).type_check(st), BaseType.INT)
        self.assertEqual(IExprBinaryOp(
            IExprColumn(("a", "i")),
            BinaryIntOp.MULTIPLICATION,
            IExprIntLiteral(1000)
        ).type_check(st), BaseType.INT)
        self.assertEqual(IExprBinaryOp(
            IExprColumn(("a", "j")),
            BinaryIntOp.ADDITION,
            IExprBinaryOp(
                IExprIntLiteral(-1),
                BinaryIntOp.MULTIPLICATION,
                IExprColumn(("a", "j"))
            )
        ).type_check(st), BaseType.INT)
        with self.assertRaises(TypeMismatchError):
            IExprBinaryOp(IExprColumn(
                ("a", "b")), BinaryIntOp.MULTIPLICATION, IExprIntLiteral(1)).type_check(st)