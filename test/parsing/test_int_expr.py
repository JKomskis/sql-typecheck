import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprColumn,
                              ExprIntLiteral, expr)


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(expr.parse("0"), ExprIntLiteral(0))
        self.assertEqual(expr.parse("5"), ExprIntLiteral(5))
        self.assertEqual(expr.parse("-100"), ExprIntLiteral(-100))


class TestMultiplication(unittest.TestCase):
    def test_mult(self):
        self.assertEqual(
            expr.parse("1*2"),
            ExprBinaryOp(ExprIntLiteral(1),
                         BinaryOp.MULTIPLICATION,
                         ExprIntLiteral(2))
        )
        self.assertEqual(
            expr.parse("1*2 * 3"),
            ExprBinaryOp(
                ExprBinaryOp(ExprIntLiteral(1),
                             BinaryOp.MULTIPLICATION,
                             ExprIntLiteral(2)),
                BinaryOp.MULTIPLICATION,
                ExprIntLiteral(3))
        )
        self.assertEqual(
            expr.parse("(1*2) * 3"),
            expr.parse("1*2 * 3")
        )
        self.assertEqual(
            expr.parse("1*(2 * 3)"),
            ExprBinaryOp(
                ExprIntLiteral(1),
                BinaryOp.MULTIPLICATION,
                ExprBinaryOp(ExprIntLiteral(2),
                             BinaryOp.MULTIPLICATION,
                             ExprIntLiteral(3))
            )
        )


class TestAddition(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            expr.parse("1+2"),
            ExprBinaryOp(ExprIntLiteral(1),
                         BinaryOp.ADDITION,
                         ExprIntLiteral(2))
        )
        self.assertEqual(
            expr.parse("1+2 + 3"),
            ExprBinaryOp(
                ExprBinaryOp(ExprIntLiteral(1),
                             BinaryOp.ADDITION,
                             ExprIntLiteral(2)),
                BinaryOp.ADDITION,
                ExprIntLiteral(3))
        )
        self.assertEqual(
            expr.parse("(1+2) + 3"),
            expr.parse("1+2 + 3")
        )
        self.assertEqual(
            expr.parse("1+(2 + 3)"),
            ExprBinaryOp(
                ExprIntLiteral(1),
                BinaryOp.ADDITION,
                ExprBinaryOp(ExprIntLiteral(2),
                             BinaryOp.ADDITION,
                             ExprIntLiteral(3))
            )
        )

    def test_add_and_mult(self):
        self.assertEqual(
            expr.parse("1*2 + 3"),
            ExprBinaryOp(
                ExprBinaryOp(ExprIntLiteral(1),
                             BinaryOp.MULTIPLICATION,
                             ExprIntLiteral(2)),
                BinaryOp.ADDITION,
                ExprIntLiteral(3))
        )
        self.assertEqual(
            expr.parse("1*(2 + 3)"),
            ExprBinaryOp(
                ExprIntLiteral(1),
                BinaryOp.MULTIPLICATION,
                ExprBinaryOp(ExprIntLiteral(2),
                             BinaryOp.ADDITION,
                             ExprIntLiteral(3)))
        )
        self.assertEqual(
            expr.parse("3 + 1*2"),
            expr.parse("3 + (1*2)")
        )
        self.assertEqual(
            expr.parse("1*2+3*4"),
            ExprBinaryOp(
                ExprBinaryOp(ExprIntLiteral(1),
                             BinaryOp.MULTIPLICATION,
                             ExprIntLiteral(2)),
                BinaryOp.ADDITION,
                ExprBinaryOp(ExprIntLiteral(3),
                             BinaryOp.MULTIPLICATION,
                             ExprIntLiteral(4))
            )
        )
        self.assertEqual(
            expr.parse("1+2*3+4"),
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprIntLiteral(1),
                    BinaryOp.ADDITION,
                    ExprBinaryOp(ExprIntLiteral(2),
                                 BinaryOp.MULTIPLICATION,
                                 ExprIntLiteral(3))
                ),
                BinaryOp.ADDITION,
                ExprIntLiteral(4))
        )


class TestColumnName(unittest.TestCase):
    def test_column_name(self):
        self.assertEqual(expr.parse("a.b"), ExprColumn(("a", "b")))

    def test_column_add(self):
        self.assertEqual(
            expr.parse("(a.b+2) + (3+c.d)"),
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprColumn(("a", "b")),
                    BinaryOp.ADDITION,
                    ExprIntLiteral(2)
                ),
                BinaryOp.ADDITION,
                ExprBinaryOp(
                    ExprIntLiteral(3),
                    BinaryOp.ADDITION,
                    ExprColumn(("c", "d")),
                )
            )
        )

    def test_column_add_mult(self):
        self.assertEqual(
            expr.parse("(a.b+2) * (3+c.d)"),
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprColumn(("a", "b")),
                    BinaryOp.ADDITION,
                    ExprIntLiteral(2)
                ),
                BinaryOp.MULTIPLICATION,
                ExprBinaryOp(
                    ExprIntLiteral(3),
                    BinaryOp.ADDITION,
                    ExprColumn(("c", "d")),
                )
            )
        )
        self.assertEqual(
            expr.parse("(a.b*2) + (3*c.d)"),
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprColumn(("a", "b")),
                    BinaryOp.MULTIPLICATION,
                    ExprIntLiteral(2)
                ),
                BinaryOp.ADDITION,
                ExprBinaryOp(
                    ExprIntLiteral(3),
                    BinaryOp.MULTIPLICATION,
                    ExprColumn(("c", "d")),
                )
            )
        )
