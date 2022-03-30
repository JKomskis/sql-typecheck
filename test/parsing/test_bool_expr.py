import unittest

from src.parsing.bool_expr import BExpr, BExprAnd, BExprBoolLiteral, BExprColumn, BExprEquality, BExprNot, EqualityOperator, b_expr
from src.parsing.int_expr import IExprIntLiteral
from src.parsing.terminals import c_name


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(b_expr.parse("true"), BExprBoolLiteral(True))
        self.assertEqual(b_expr.parse("TRUE"), BExprBoolLiteral(True))

    def test_false(self):
        self.assertEqual(b_expr.parse("false"), BExprBoolLiteral(False))
        self.assertEqual(b_expr.parse("FALSE"), BExprBoolLiteral(False))


class TestAnd(unittest.TestCase):
    def test_and_literals(self):
        self.assertEqual(
            b_expr.parse("true AND false"),
            BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False))
        )

    def test_and_nested(self):
        self.assertEqual(
            b_expr.parse("(true AND false) AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND false AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND (false AND true)"),
            BExprAnd(
                BExprBoolLiteral(True),
                BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True))
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND false) AND (false AND true)"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True))
            )
        )


class TestNot(unittest.TestCase):
    def test_not_literals(self):
        self.assertEqual(b_expr.parse("NOT true"),
                         BExprNot(BExprBoolLiteral(True)))
        self.assertEqual(b_expr.parse("NOT false"),
                         BExprNot(BExprBoolLiteral(False)))

    def test_not_and(self):
        self.assertEqual(
            b_expr.parse("NOT true AND false"),
            BExprAnd(BExprNot(BExprBoolLiteral(True)), BExprBoolLiteral(False))
        )
        self.assertEqual(
            b_expr.parse("true AND NOT false"),
            BExprAnd(BExprBoolLiteral(True), BExprNot(BExprBoolLiteral(False)))
        )
        self.assertEqual(
            b_expr.parse("NOT (true AND false)"),
            BExprNot(BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)))
        )

    def test_not_nested(self):
        self.assertEqual(
            b_expr.parse("NOT (true AND false) AND true"),
            BExprAnd(
                BExprNot(BExprAnd(BExprBoolLiteral(
                    True), BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND NOT false) AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True),
                         BExprNot(BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("NOT true AND false AND true"),
            BExprAnd(
                BExprAnd(BExprNot(BExprBoolLiteral(True)),
                         BExprBoolLiteral(False)),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND NOT false AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True),
                         BExprNot(BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND (false AND NOT true)"),
            BExprAnd(
                BExprBoolLiteral(True),
                BExprAnd(BExprBoolLiteral(False),
                         BExprNot(BExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            b_expr.parse("true AND NOT (false AND true)"),
            BExprAnd(
                BExprBoolLiteral(True),
                BExprNot(BExprAnd(BExprBoolLiteral(
                    False), BExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND false) AND (NOT false AND true)"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprAnd(BExprNot(BExprBoolLiteral(False)),
                         BExprBoolLiteral(True))
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND false) AND NOT (false AND true)"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprNot(BExprAnd(BExprBoolLiteral(
                    False), BExprBoolLiteral(True)))
            )
        )


class TestEquality(unittest.TestCase):
    ops = [("=", EqualityOperator.EQUALS), ("<", EqualityOperator.LESS_THAN)]

    def test_equals(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                b_expr.parse(f"0{op_str}0"),
                BExprEquality(IExprIntLiteral(0), op, IExprIntLiteral(0))
            )
            self.assertEqual(b_expr.parse(
                f"0{op_str}0"), b_expr.parse(f"0 {op_str} 0"))
            self.assertEqual(
                b_expr.parse(f"-50{op_str} -50"),
                BExprEquality(IExprIntLiteral(-50), op, IExprIntLiteral(-50))
            )

    def test_equals_and(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                b_expr.parse(f"0{op_str}0 AND false"),
                BExprAnd(
                    BExprEquality(IExprIntLiteral(0), op, IExprIntLiteral(0)),
                    BExprBoolLiteral(False)
                )
            )
            self.assertEqual(
                b_expr.parse(f"true AND -100{op_str}-100"),
                BExprAnd(
                    BExprBoolLiteral(True),
                    BExprEquality(IExprIntLiteral(-100),
                                  op, IExprIntLiteral(-100))
                )
            )
            self.assertEqual(
                b_expr.parse(f"true AND (-100{op_str}-100 and 0{op_str}50)"),
                BExprAnd(
                    BExprBoolLiteral(True),
                    BExprAnd(
                        BExprEquality(IExprIntLiteral(-100), op,
                                      IExprIntLiteral(-100)),
                        BExprEquality(IExprIntLiteral(
                            0), op, IExprIntLiteral(50))
                    )
                )
            )

    def test_equals_and_not(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                b_expr.parse(f"not 0{op_str}0 AND not false"),
                BExprAnd(
                    BExprNot(BExprEquality(
                        IExprIntLiteral(0), op, IExprIntLiteral(0))),
                    BExprNot(BExprBoolLiteral(False))
                )
            )
            self.assertEqual(
                b_expr.parse(f"not (not true AND not -100{op_str}-100)"),
                BExprNot(BExprAnd(
                    BExprNot(BExprBoolLiteral(True)),
                    BExprNot(BExprEquality(IExprIntLiteral(-100),
                             op, IExprIntLiteral(-100)))
                ))
            )
            self.assertEqual(
                b_expr.parse(
                    f"not true AND not (not -100{op_str}-100 and not 0{op_str}50)"),
                BExprAnd(
                    BExprNot(BExprBoolLiteral(True)),
                    BExprNot(BExprAnd(
                        BExprNot(BExprEquality(IExprIntLiteral(-100),
                                 op, IExprIntLiteral(-100))),
                        BExprNot(BExprEquality(
                            IExprIntLiteral(0), op, IExprIntLiteral(50)))
                    ))
                )
            )


class TestColumn(unittest.TestCase):
    def test_column(self):
        self.assertEqual(
            b_expr.parse(f"a.b"),
            BExprColumn(("a", "b"))
        )

    def test_column_and(self):
        self.assertEqual(
            b_expr.parse(f"a.b and c.d"),
            BExprAnd(
                BExprColumn(("a", "b")),
                BExprColumn(("c", "d")),
            )
        )
        self.assertEqual(
            b_expr.parse(f"a.b and true and c.d"),
            BExprAnd(
                BExprAnd(
                    BExprColumn(("a", "b")),
                    BExprBoolLiteral(True)
                ),
                BExprColumn(("c", "d"))
            )
        )

    def test_column_and_not(self):
        self.assertEqual(
            b_expr.parse(f"a.b and not c.d"),
            BExprAnd(
                BExprColumn(("a", "b")),
                BExprNot(BExprColumn(("c", "d"))),
            )
        )
        self.assertEqual(
            b_expr.parse(f"not a.b and not (true and c.d)"),
            BExprAnd(
                BExprNot(BExprColumn(("a", "b"))),
                BExprNot(BExprAnd(
                    BExprBoolLiteral(True),
                    BExprColumn(("c", "d"))
                ))
            )
        )
