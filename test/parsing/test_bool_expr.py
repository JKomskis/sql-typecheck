import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprBoolLiteral,
                              ExprColumn, ExprIntLiteral, ExprNot, expr)


class TestLiteral(unittest.TestCase):
    def test_true(self):
        self.assertEqual(expr.parse("true"), ExprBoolLiteral(True))
        self.assertEqual(expr.parse("TRUE"), ExprBoolLiteral(True))

    def test_false(self):
        self.assertEqual(expr.parse("false"), ExprBoolLiteral(False))
        self.assertEqual(expr.parse("FALSE"), ExprBoolLiteral(False))


class TestAnd(unittest.TestCase):
    def test_and_literals(self):
        self.assertEqual(
            expr.parse("true AND false"),
            ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                         ExprBoolLiteral(False))
        )

    def test_and_nested(self):
        self.assertEqual(
            expr.parse("(true AND false) AND true"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("true AND false AND true"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("true AND (false AND true)"),
            ExprBinaryOp(
                ExprBoolLiteral(True),
                BinaryOp.AND,
                ExprBinaryOp(ExprBoolLiteral(False),
                             BinaryOp.AND, ExprBoolLiteral(True))
            )
        )
        self.assertEqual(
            expr.parse("(true AND false) AND (false AND true)"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprBinaryOp(ExprBoolLiteral(False),
                             BinaryOp.AND, ExprBoolLiteral(True))
            )
        )


class TestNot(unittest.TestCase):
    def test_not_literals(self):
        self.assertEqual(expr.parse("NOT true"),
                         ExprNot(ExprBoolLiteral(True)))
        self.assertEqual(expr.parse("NOT false"),
                         ExprNot(ExprBoolLiteral(False)))

    def test_not_and(self):
        self.assertEqual(
            expr.parse("NOT true AND false"),
            ExprBinaryOp(ExprNot(ExprBoolLiteral(True)),
                         BinaryOp.AND, ExprBoolLiteral(False))
        )
        self.assertEqual(
            expr.parse("true AND NOT false"),
            ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                         ExprNot(ExprBoolLiteral(False)))
        )
        self.assertEqual(
            expr.parse("NOT (true AND false)"),
            ExprNot(ExprBinaryOp(ExprBoolLiteral(True),
                    BinaryOp.AND, ExprBoolLiteral(False)))
        )

    def test_not_nested(self):
        self.assertEqual(
            expr.parse("NOT (true AND false) AND true"),
            ExprBinaryOp(
                ExprNot(ExprBinaryOp(ExprBoolLiteral(
                    True), BinaryOp.AND, ExprBoolLiteral(False))),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("(true AND NOT false) AND true"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True),
                             BinaryOp.AND,
                             ExprNot(ExprBoolLiteral(False))),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("NOT true AND false AND true"),
            ExprBinaryOp(
                ExprBinaryOp(ExprNot(ExprBoolLiteral(True)),
                             BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("true AND NOT false AND true"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True),
                             BinaryOp.AND,
                             ExprNot(ExprBoolLiteral(False))),
                BinaryOp.AND,
                ExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            expr.parse("true AND (false AND NOT true)"),
            ExprBinaryOp(
                ExprBoolLiteral(True),
                BinaryOp.AND,
                ExprBinaryOp(ExprBoolLiteral(False),
                             BinaryOp.AND,
                             ExprNot(ExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            expr.parse("true AND NOT (false AND true)"),
            ExprBinaryOp(
                ExprBoolLiteral(True),
                BinaryOp.AND,
                ExprNot(ExprBinaryOp(ExprBoolLiteral(
                    False), BinaryOp.AND, ExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            expr.parse("(true AND false) AND (NOT false AND true)"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprBinaryOp(ExprNot(ExprBoolLiteral(False)), BinaryOp.AND,
                             ExprBoolLiteral(True))
            )
        )
        self.assertEqual(
            expr.parse("(true AND false) AND NOT (false AND true)"),
            ExprBinaryOp(
                ExprBinaryOp(ExprBoolLiteral(True), BinaryOp.AND,
                             ExprBoolLiteral(False)),
                BinaryOp.AND,
                ExprNot(ExprBinaryOp(ExprBoolLiteral(
                    False), BinaryOp.AND, ExprBoolLiteral(True)))
            )
        )


class TestEquality(unittest.TestCase):
    ops = [("=", BinaryOp.EQUALS), ("<", BinaryOp.LESS_THAN)]

    def test_equals(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                expr.parse(f"0{op_str}0"),
                ExprBinaryOp(ExprIntLiteral(0), op, ExprIntLiteral(0))
            )
            self.assertEqual(expr.parse(
                f"0{op_str}0"), expr.parse(f"0 {op_str} 0"))
            self.assertEqual(
                expr.parse(f"-50{op_str} -50"),
                ExprBinaryOp(ExprIntLiteral(-50), op, ExprIntLiteral(-50))
            )

    def test_equals_and(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                expr.parse(f"0{op_str}0 AND false"),
                ExprBinaryOp(
                    ExprBinaryOp(ExprIntLiteral(0), op, ExprIntLiteral(0)),
                    BinaryOp.AND,
                    ExprBoolLiteral(False)
                )
            )
            self.assertEqual(
                expr.parse(f"true AND -100{op_str}-100"),
                ExprBinaryOp(
                    ExprBoolLiteral(True),
                    BinaryOp.AND,
                    ExprBinaryOp(ExprIntLiteral(-100),
                                 op, ExprIntLiteral(-100))
                )
            )
            self.assertEqual(
                expr.parse(f"true AND (-100{op_str}-100 and 0{op_str}50)"),
                ExprBinaryOp(
                    ExprBoolLiteral(True),
                    BinaryOp.AND,
                    ExprBinaryOp(
                        ExprBinaryOp(ExprIntLiteral(-100), op,
                                     ExprIntLiteral(-100)),
                        BinaryOp.AND,
                        ExprBinaryOp(ExprIntLiteral(
                            0), op, ExprIntLiteral(50))
                    )
                )
            )

    def test_equals_and_not(self):
        for op_str, op in TestEquality.ops:
            self.assertEqual(
                expr.parse(f"not 0{op_str}0 AND not false"),
                ExprBinaryOp(
                    ExprNot(ExprBinaryOp(
                        ExprIntLiteral(0), op, ExprIntLiteral(0))),
                    BinaryOp.AND,
                    ExprNot(ExprBoolLiteral(False))
                )
            )
            self.assertEqual(
                expr.parse(f"not (not true AND not -100{op_str}-100)"),
                ExprNot(ExprBinaryOp(
                    ExprNot(ExprBoolLiteral(True)),
                    BinaryOp.AND,
                    ExprNot(ExprBinaryOp(ExprIntLiteral(-100),
                                         op, ExprIntLiteral(-100)))
                ))
            )
            self.assertEqual(
                expr.parse(
                    f"not true AND not (not -100{op_str}-100 and not 0{op_str}50)"),
                ExprBinaryOp(
                    ExprNot(ExprBoolLiteral(True)),
                    BinaryOp.AND,
                    ExprNot(ExprBinaryOp(
                        ExprNot(ExprBinaryOp(ExprIntLiteral(-100),
                                             op, ExprIntLiteral(-100))),
                        BinaryOp.AND,
                        ExprNot(ExprBinaryOp(
                            ExprIntLiteral(0), op, ExprIntLiteral(50)))
                    ))
                )
            )


class TestColumn(unittest.TestCase):
    def test_column(self):
        self.assertEqual(
            expr.parse(f"a.b"),
            ExprColumn(("a", "b"))
        )

    def test_column_and(self):
        self.assertEqual(
            expr.parse(f"a.b and c.d"),
            ExprBinaryOp(
                ExprColumn(("a", "b")),
                BinaryOp.AND,
                ExprColumn(("c", "d")),
            )
        )
        self.assertEqual(
            expr.parse(f"a.b and true and c.d"),
            ExprBinaryOp(
                ExprBinaryOp(
                    ExprColumn(("a", "b")),
                    BinaryOp.AND,
                    ExprBoolLiteral(True)
                ),
                BinaryOp.AND,
                ExprColumn(("c", "d"))
            )
        )

    def test_column_and_not(self):
        self.assertEqual(
            expr.parse(f"a.b and not c.d"),
            ExprBinaryOp(
                ExprColumn(("a", "b")),
                BinaryOp.AND,
                ExprNot(ExprColumn(("c", "d"))),
            )
        )
        self.assertEqual(
            expr.parse(f"not a.b and not (true and c.d)"),
            ExprBinaryOp(
                ExprNot(ExprColumn(("a", "b"))),
                BinaryOp.AND,
                ExprNot(ExprBinaryOp(
                    ExprBoolLiteral(True),
                    BinaryOp.AND,
                    ExprColumn(("c", "d"))
                ))
            )
        )
