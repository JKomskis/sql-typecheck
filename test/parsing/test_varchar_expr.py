import unittest

from src.parsing.int_expr import BinaryIntOp, IExprBinaryOp, IExprColumn, IExprIntLiteral, i_expr
from src.parsing.varchar_expr import VExprColumn, VExprConcat, VExprSubstr, VExprVarcharLiteral, v_expr


class TestLiteral(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(v_expr.parse('"test"'), VExprVarcharLiteral("test"))
        self.assertEqual(v_expr.parse('"1234"'), VExprVarcharLiteral("1234"))


class TestConcat(unittest.TestCase):
    def test_concat_literal(self):
        self.assertEqual(v_expr.parse('CONCAT("test", "test2")'), 
            VExprConcat( VExprVarcharLiteral("test"),VExprVarcharLiteral("test2") ))
        self.assertEqual(v_expr.parse('concat(  "test"    , "test2"  )'), 
            VExprConcat( VExprVarcharLiteral("test"),VExprVarcharLiteral("test2") ))


    def test_concat_col_literal(self):
        self.assertEqual(v_expr.parse('CONCAT("test", a.col)'), 
            VExprConcat( VExprVarcharLiteral("test"),VExprColumn(("a", "col")) ))

    def test_concat_cols(self):
        self.assertEqual(v_expr.parse('CONCAT(b.col , a.col)'), 
            VExprConcat( VExprColumn(("b", "col")) ,VExprColumn(("a", "col")) ))

    def test_concat_nested(self):
        self.assertEqual(v_expr.parse('CONCAT(b.col , CONCAT("test", a.col) )'), 
            VExprConcat( VExprColumn(("b", "col")) ,
                VExprConcat( VExprVarcharLiteral("test"),VExprColumn(("a", "col"))) ))

    def test_concat_substr_nested(self):
        self.assertEqual(v_expr.parse('CONCAT(b.col , substr("hello world", 0, 5) )'), 
            VExprConcat( VExprColumn(("b", "col")) ,
                VExprSubstr( VExprVarcharLiteral("hello world"), IExprIntLiteral(0), IExprIntLiteral(5) ) 
                ))



class TestSubstr(unittest.TestCase):
    def test_substr_literal(self):
        self.assertEqual(v_expr.parse('SUBSTR("test", 1, 3)'), 
            VExprSubstr( VExprVarcharLiteral("test"), IExprIntLiteral(1), IExprIntLiteral(3) ))

    def test_substr_literal_add(self):
        self.assertEqual(v_expr.parse('SUBSTR("test", 0+1, 3)'), 
            VExprSubstr( VExprVarcharLiteral("test"), 
                IExprBinaryOp(IExprIntLiteral(0),
                            BinaryIntOp.ADDITION,
                            IExprIntLiteral(1))
                , IExprIntLiteral(3) ))
    
    def test_substr_col(self):
        self.assertEqual(v_expr.parse('SUBSTR(a.col, 0+1, 3)'), 
            VExprSubstr( VExprColumn(("a", "col")), 
                IExprBinaryOp(IExprIntLiteral(0),
                            BinaryIntOp.ADDITION,
                            IExprIntLiteral(1))
                , IExprIntLiteral(3) ))

    def test_substr_nested(self):
        self.assertEqual(v_expr.parse('SUBSTR(SUBSTR(a.col, 3, 20), 1, 5)'), 
            VExprSubstr( VExprSubstr(VExprColumn(("a", "col")), 
                    IExprIntLiteral(3), 
                    IExprIntLiteral(20) )
                ,  IExprIntLiteral(1), IExprIntLiteral(5)))

    def test_substr_concat(self):
        self.assertEqual(v_expr.parse('SUBSTR(CONCAT("hello", "world"), 1, 5)'), 
            VExprSubstr(  
                VExprConcat(
                    VExprVarcharLiteral("hello"),
                    VExprVarcharLiteral("world")
                )
                ,  IExprIntLiteral(1), IExprIntLiteral(5)))