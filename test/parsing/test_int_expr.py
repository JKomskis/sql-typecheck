import unittest

from src.parsing.int_expr import BinaryIntOp, IExprBinaryOp, IExprColumn, IExprIntLiteral, i_expr


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(i_expr.parse("0"), IExprIntLiteral(0))
        self.assertEqual(i_expr.parse("5"), IExprIntLiteral(5))
        self.assertEqual(i_expr.parse("-100"), IExprIntLiteral(-100))


class TestMultiplication(unittest.TestCase):
    def test_mult(self):
        self.assertEqual(
            i_expr.parse("1*2"),
            IExprBinaryOp(IExprIntLiteral(1),
                          BinaryIntOp.MULTIPLICATION,
                          IExprIntLiteral(2))
        )
        self.assertEqual(
            i_expr.parse("1*2 * 3"),
            IExprBinaryOp(
                IExprBinaryOp(IExprIntLiteral(1),
                              BinaryIntOp.MULTIPLICATION,
                              IExprIntLiteral(2)),
                BinaryIntOp.MULTIPLICATION,
                IExprIntLiteral(3))
        )
        self.assertEqual(
            i_expr.parse("(1*2) * 3"),
            i_expr.parse("1*2 * 3")
        )
        self.assertEqual(
            i_expr.parse("1*(2 * 3)"),
            IExprBinaryOp(
                IExprIntLiteral(1),
                BinaryIntOp.MULTIPLICATION,
                IExprBinaryOp(IExprIntLiteral(2),
                              BinaryIntOp.MULTIPLICATION,
                              IExprIntLiteral(3))
            )
        )


class TestAddition(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            i_expr.parse("1+2"),
            IExprBinaryOp(IExprIntLiteral(1),
                          BinaryIntOp.ADDITION,
                          IExprIntLiteral(2))
        )
        self.assertEqual(
            i_expr.parse("1+2 + 3"),
            IExprBinaryOp(
                IExprBinaryOp(IExprIntLiteral(1),
                              BinaryIntOp.ADDITION,
                              IExprIntLiteral(2)),
                BinaryIntOp.ADDITION,
                IExprIntLiteral(3))
        )
        self.assertEqual(
            i_expr.parse("(1+2) + 3"),
            i_expr.parse("1+2 + 3")
        )
        self.assertEqual(
            i_expr.parse("1+(2 + 3)"),
            IExprBinaryOp(
                IExprIntLiteral(1),
                BinaryIntOp.ADDITION,
                IExprBinaryOp(IExprIntLiteral(2),
                              BinaryIntOp.ADDITION,
                              IExprIntLiteral(3))
            )
        )

    def test_add_and_mult(self):
        self.assertEqual(
            i_expr.parse("1*2 + 3"),
            IExprBinaryOp(
                IExprBinaryOp(IExprIntLiteral(1),
                              BinaryIntOp.MULTIPLICATION,
                              IExprIntLiteral(2)),
                BinaryIntOp.ADDITION,
                IExprIntLiteral(3))
        )
        self.assertEqual(
            i_expr.parse("1*(2 + 3)"),
            IExprBinaryOp(
                IExprIntLiteral(1),
                BinaryIntOp.MULTIPLICATION,
                IExprBinaryOp(IExprIntLiteral(2),
                              BinaryIntOp.ADDITION,
                              IExprIntLiteral(3)))
        )
        self.assertEqual(
            i_expr.parse("3 + 1*2"),
            i_expr.parse("3 + (1*2)")
        )
        self.assertEqual(
            i_expr.parse("1*2+3*4"),
            IExprBinaryOp(
                IExprBinaryOp(IExprIntLiteral(1),
                              BinaryIntOp.MULTIPLICATION,
                              IExprIntLiteral(2)),
                BinaryIntOp.ADDITION,
                IExprBinaryOp(IExprIntLiteral(3),
                              BinaryIntOp.MULTIPLICATION,
                              IExprIntLiteral(4))
            )
        )
        self.assertEqual(
            i_expr.parse("1+2*3+4"),
            IExprBinaryOp(
                IExprBinaryOp(
                    IExprIntLiteral(1),
                    BinaryIntOp.ADDITION,
                    IExprBinaryOp(IExprIntLiteral(2),
                                  BinaryIntOp.MULTIPLICATION,
                                  IExprIntLiteral(3))
                ),
                BinaryIntOp.ADDITION,
                IExprIntLiteral(4))
        )


class TestColumnName(unittest.TestCase):
    def test_column_name(self):
        self.assertEqual(i_expr.parse("a.b"), IExprColumn(("a", "b")))

    def test_column_add(self):
        self.assertEqual(
            i_expr.parse("(a.b+2) + (3+c.d)"),
            IExprBinaryOp(
                IExprBinaryOp(
                    IExprColumn(("a", "b")),
                    BinaryIntOp.ADDITION,
                    IExprIntLiteral(2)
                ),
                BinaryIntOp.ADDITION,
                IExprBinaryOp(
                    IExprIntLiteral(3),
                    BinaryIntOp.ADDITION,
                    IExprColumn(("c", "d")),
                )
            )
        )

    def test_column_add_mult(self):
        self.assertEqual(
            i_expr.parse("(a.b+2) * (3+c.d)"),
            IExprBinaryOp(
                IExprBinaryOp(
                    IExprColumn(("a", "b")),
                    BinaryIntOp.ADDITION,
                    IExprIntLiteral(2)
                ),
                BinaryIntOp.MULTIPLICATION,
                IExprBinaryOp(
                    IExprIntLiteral(3),
                    BinaryIntOp.ADDITION,
                    IExprColumn(("c", "d")),
                )
            )
        )
        self.assertEqual(
            i_expr.parse("(a.b*2) + (3*c.d)"),
            IExprBinaryOp(
                IExprBinaryOp(
                    IExprColumn(("a", "b")),
                    BinaryIntOp.MULTIPLICATION,
                    IExprIntLiteral(2)
                ),
                BinaryIntOp.ADDITION,
                IExprBinaryOp(
                    IExprIntLiteral(3),
                    BinaryIntOp.MULTIPLICATION,
                    IExprColumn(("c", "d")),
                )
            )
        )
