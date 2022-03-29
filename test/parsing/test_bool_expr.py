import unittest

from src.parsing.bool_expr import BExprAnd, BExprBoolLiteral, BExprNot, b_expr

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
        self.assertEqual(b_expr.parse("NOT true"), BExprNot(BExprBoolLiteral(True)))
        self.assertEqual(b_expr.parse("NOT false"), BExprNot(BExprBoolLiteral(False)))

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

    def test_and_nested(self):
        self.assertEqual(
            b_expr.parse("NOT (true AND false) AND true"),
            BExprAnd(
                BExprNot(BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND NOT false) AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprNot(BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("NOT true AND false AND true"),
            BExprAnd(
                BExprAnd(BExprNot(BExprBoolLiteral(True)), BExprBoolLiteral(False)),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND NOT false AND true"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprNot(BExprBoolLiteral(False))),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            b_expr.parse("true AND (false AND NOT true)"),
            BExprAnd(
                BExprBoolLiteral(True),
                BExprAnd(BExprBoolLiteral(False), BExprNot(BExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            b_expr.parse("true AND NOT (false AND true)"),
            BExprAnd(
                BExprBoolLiteral(True),
                BExprNot(BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True)))
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND false) AND (NOT false AND true)"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprAnd(BExprNot(BExprBoolLiteral(False)), BExprBoolLiteral(True))
            )
        )
        self.assertEqual(
            b_expr.parse("(true AND false) AND NOT (false AND true)"),
            BExprAnd(
                BExprAnd(BExprBoolLiteral(True), BExprBoolLiteral(False)),
                BExprNot(BExprAnd(BExprBoolLiteral(False), BExprBoolLiteral(True)))
            )
        )