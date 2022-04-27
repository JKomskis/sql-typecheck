import unittest

from src.parsing.expr import (BinaryOp, ExprBinaryOp, ExprColumn, ExprConcat,
                              ExprIntLiteral, ExprSubstr, ExprVarcharLiteral,
                              expr)


class TestLiteral(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(expr.parse('"test"'), ExprVarcharLiteral("test"))
        self.assertEqual(expr.parse('"1234"'), ExprVarcharLiteral("1234"))


class TestConcat(unittest.TestCase):
    def test_concat_literal(self):
        self.assertEqual(expr.parse('CONCAT("test", "test2")'),
                         ExprConcat(ExprVarcharLiteral("test"), ExprVarcharLiteral("test2")))
        self.assertEqual(expr.parse('concat(  "test"    , "test2"  )'),
                         ExprConcat(ExprVarcharLiteral("test"), ExprVarcharLiteral("test2")))

    def test_concat_col_literal(self):
        self.assertEqual(expr.parse('CONCAT("test", a.col)'),
                         ExprConcat(ExprVarcharLiteral("test"), ExprColumn(("a", "col"))))

    def test_concat_cols(self):
        self.assertEqual(expr.parse('CONCAT(b.col , a.col)'),
                         ExprConcat(ExprColumn(("b", "col")), ExprColumn(("a", "col"))))

    def test_concat_nested(self):
        self.assertEqual(expr.parse('CONCAT(b.col , CONCAT("test", a.col) )'),
                         ExprConcat(ExprColumn(("b", "col")),
                                    ExprConcat(ExprVarcharLiteral("test"), ExprColumn(("a", "col")))))

    def test_concat_substr_nested(self):
        self.assertEqual(expr.parse('CONCAT(b.col , substr("hello world", 0, 5) )'),
                         ExprConcat(ExprColumn(("b", "col")),
                                    ExprSubstr(ExprVarcharLiteral(
                                        "hello world"), ExprIntLiteral(0), ExprIntLiteral(5))
                                    ))


class TestSubstr(unittest.TestCase):
    def test_substr_literal(self):
        self.assertEqual(expr.parse('SUBSTR("test", 1, 3)'),
                         ExprSubstr(ExprVarcharLiteral("test"), ExprIntLiteral(1), ExprIntLiteral(3)))

    def test_substr_literal_add(self):
        self.assertEqual(expr.parse('SUBSTR("test", 0+1, 3)'),
                         ExprSubstr(ExprVarcharLiteral("test"),
                         ExprBinaryOp(ExprIntLiteral(0),
                                      BinaryOp.ADDITION,
                                      ExprIntLiteral(1)), ExprIntLiteral(3)))

    def test_substr_col(self):
        self.assertEqual(expr.parse('SUBSTR(a.col, 0+1, 3)'),
                         ExprSubstr(ExprColumn(("a", "col")),
                         ExprBinaryOp(ExprIntLiteral(0),
                                      BinaryOp.ADDITION,
                                      ExprIntLiteral(1)), ExprIntLiteral(3)))

    def test_substr_nested(self):
        self.assertEqual(expr.parse('SUBSTR(SUBSTR(a.col, 3, 20), 1, 5)'),
                         ExprSubstr(ExprSubstr(ExprColumn(("a", "col")),
                                               ExprIntLiteral(3),
                                               ExprIntLiteral(20)),  ExprIntLiteral(1), ExprIntLiteral(5)))

    def test_substr_concat(self):
        self.assertEqual(expr.parse('SUBSTR(CONCAT("hello", "world"), 1, 5)'),
                         ExprSubstr(
            ExprConcat(
                ExprVarcharLiteral("hello"),
                ExprVarcharLiteral("world")
            ),  ExprIntLiteral(1), ExprIntLiteral(5)))
