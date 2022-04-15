import unittest
from src.parsing.bool_expr import BExprBoolLiteral, BExprColumn, BExprEquality, BExprNot, EqualityOperator
from src.parsing.expr import ExprColumn
from src.parsing.int_expr import IExprColumn, IExprIntLiteral

from src.parsing.query import QueryJoin, QuerySelect, QueryUnion, QueryIntersect, QueryIntersectUnion, QueryTable, query


class TestQueryTable(unittest.TestCase):
    def test_query_table(self):
        self.assertEqual(query.parse("a"), QueryTable("a"))
        self.assertEqual(query.parse("a AS b"), QueryTable("a", "b"))


class TestQuerySelect(unittest.TestCase):
    def test_query_select(self):
        self.assertEqual(
            query.parse("SELECT students.ssn FROM students"),
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students")
            )
        )
        self.assertEqual(
            query.parse("SELECT students.ssn, students.year FROM students"),
            QuerySelect(
                [ExprColumn(("students", "ssn")),
                 ExprColumn(("students", "year"))],
                QueryTable("students")
            )
        )

    def test_query_select_where(self):
        self.assertEqual(
            query.parse("SELECT students.ssn FROM students WHERE true"),
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprBoolLiteral(True)
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn, students.year FROM students WHERE students.ssn = students.year"),
            QuerySelect(
                [ExprColumn(("students", "ssn")),
                    ExprColumn(("students", "year"))],
                QueryTable("students"),
                BExprEquality(
                    IExprColumn(("students", "ssn")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("students", "year"))
                )
            )
        )

    def test_query_select_where_groupby(self):
            self.assertEqual(
                query.parse("SELECT students.ssn FROM students WHERE true GROUP BY id"),
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprBoolLiteral(True),
                    "id"
                )
            )

    def test_query_select_nested(self):
        self.assertEqual(
            query.parse(
                "SELECT s.ssn FROM SELECT s.ssn, s.gpa FROM students AS s"),
            QuerySelect(
                [ExprColumn(("s", "ssn"))],
                QuerySelect(
                    [ExprColumn(("s", "ssn")),
                        ExprColumn(("s", "gpa"))],
                    QueryTable("students", "s"),

                )
            )
        )


class TestQueryUnion(unittest.TestCase):
    def test_query_union(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    UNION SELECT students.ssn FROM students WHERE students.undergraduate"),
            QueryUnion([
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprColumn(("students", "graduate"))
            ), 
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprColumn(("students", "undergraduate"))
            )
            ])
        )


class TestQueryIntersect(unittest.TestCase):
    def test_query_union(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    INTERSECT SELECT students.ssn FROM students WHERE students.graduate"),
            QueryIntersect([
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprColumn(("students", "graduate"))
            ), 
            QuerySelect(
                [ExprColumn(("students", "ssn"))],
                QueryTable("students"),
                BExprColumn(("students", "graduate"))
            )
            ])
        )



class TestQueryIntersectUnion(unittest.TestCase):
    def test_query_union(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.graduate\
                    INTERSECT SELECT students.ssn FROM students WHERE students.undergraduate\
                    UNION \
                    SELECT students.ssn FROM students WHERE students.enrolled\
                    INTERSECT SELECT students.ssn FROM students WHERE students.graduate"),
            QueryIntersectUnion([
                QueryIntersect([
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprColumn(("students", "graduate"))
                ), 
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprColumn(("students", "undergraduate"))
                )
                ]),
                QueryIntersect([
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprColumn(("students", "enrolled"))
                ), 
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprColumn(("students", "graduate"))
                )
                ])
            ])
        )



class TestQueryJoin(unittest.TestCase):
    def test_query_join(self):
        self.assertEqual(
            query.parse(
                "students join enrolled ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QueryTable("students"),
                QueryTable("enrolled"),
                BExprEquality(
                    IExprColumn(("students", "id")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )

    def test_query_join_select(self):
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.gpa < 3 join enrolled ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QuerySelect(
                    [ExprColumn(("students", "ssn"))],
                    QueryTable("students"),
                    BExprEquality(
                        IExprColumn(("students", "gpa")),
                        EqualityOperator.LESS_THAN,
                        IExprIntLiteral(3)
                    )
                ),
                QueryTable("enrolled"),
                BExprEquality(
                    IExprColumn(("students", "id")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )
        self.assertEqual(
            query.parse(
                "SELECT students.ssn FROM students WHERE students.gpa < 3 join enrolled ON students.id = enrolled.id AS s_e"),
            query.parse(
                "(SELECT students.ssn FROM students WHERE students.gpa < 3) join enrolled ON students.id = enrolled.id AS s_e"),
        )
        self.assertEqual(
            query.parse(
                "students join SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped ON students.id = enrolled.id AS s_e"),
            QueryJoin(
                QueryTable("students"),
                QuerySelect(
                    [ExprColumn(("enrolled", "id"))],
                    QueryTable("enrolled"),
                    BExprNot(
                        BExprColumn(("enrolled", "dropped"))
                    )
                ),
                BExprEquality(
                    IExprColumn(("students", "id")),
                    EqualityOperator.EQUALS,
                    IExprColumn(("enrolled", "id"))
                ),
                "s_e"
            )
        )
        self.assertEqual(
            query.parse(
                "students join SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped ON students.id = enrolled.id AS s_e"),
            query.parse(
                "students join (SELECT enrolled.id FROM enrolled WHERE not enrolled.dropped) ON students.id = enrolled.id AS s_e"),
        )

    def test_select_from_join(self):
        self.assertEqual(
            query.parse(
                "SELECT students.id, enrolled.grade FROM students join enrolled ON students.id = enrolled.id AS s_e WHERE students.graduate"),
            QuerySelect(
                [ExprColumn(("students", "id")),
                 ExprColumn(("enrolled", "grade"))],
                QueryJoin(
                    QueryTable("students"),
                    QueryTable("enrolled"),
                    BExprEquality(
                        IExprColumn(("students", "id")),
                        EqualityOperator.EQUALS,
                        IExprColumn(("enrolled", "id"))
                    ),
                    "s_e"
                ),
                BExprColumn(("students", "graduate"))
            )

        )
