import unittest
from test.e2e.tables import (course_create_table_statement,
                             enrolled_create_table_statement,
                             student_create_table_statement)

from src.parsing.statements import stmt_sequence
from src.types.symbol_table import SymbolTable
from src.types.types import (AggregationMismatchError, BaseType, Schema,
                             TypeMismatchError)


class TestQueryTable(unittest.TestCase):
    def test_query_table(self):
        st = SymbolTable()
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student"""
            ).type_check(st),
            ("student", Schema({
                "student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT
            }))
        )

        st = SymbolTable()
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    course AS c"""
            ).type_check(st),
            ("c", Schema({
                "course_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "capacity": BaseType.INT,
                "instructor": BaseType.VARCHAR
            }))
        )


class TestQuerySelect(unittest.TestCase):
    def test_query_select(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, CONCAT(s.name, "!"), s.year + -4 AS start_year, not s.graduate as undergraduate
                    FROM student AS s"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR,
                "start_year": BaseType.INT,
                "undergraduate": BaseType.BOOL
            }))
        )

        with self.assertRaises(KeyError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, s.no_such_field
                    FROM student AS s"""
            ).type_check(SymbolTable())


class TestQuerySelectWhere(unittest.TestCase):
    def test_query_select_where(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, CONCAT(s.name, "!")
                    FROM student AS s
                    WHERE s.alumni = True"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR
            }))
        )

        with self.assertRaises(KeyError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, s.no_such_field
                    FROM student AS s
                    WHERE s.alumni = True"""
            ).type_check(SymbolTable())

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.student_id, CONCAT(s.name, "!")
                    FROM student AS s
                    WHERE s.gpa"""
            ).type_check(SymbolTable())


class TestJoin2(unittest.TestCase):
    def test_join_2(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student JOIN enrolled ON student.student_id = enrolled.student_id AS s_e"""
            ).type_check(SymbolTable()),
            ("s_e", Schema({
                "student.student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "enrolled.student_id": BaseType.INT,
                "course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )

        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student AS s JOIN enrolled AS e ON e.grade < s.gpa AS s_e"""
            ).type_check(SymbolTable()),
            ("s_e", Schema({
                "s.student_id": BaseType.INT,
                "name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "e.student_id": BaseType.INT,
                "course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL
            }))
        )

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student AS s JOIN enrolled AS e ON s.gpa AS s_e"""
            ).type_check(SymbolTable())


class TestJoin3(unittest.TestCase):
    def test_join_3(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    student JOIN enrolled ON student.student_id = enrolled.student_id AS s_e
                        JOIN course ON s_e.course_id = course.course_id as s_e_c"""
            ).type_check(SymbolTable()),
            ("s_e_c", Schema({
                "student.student_id": BaseType.INT,
                "s_e.name": BaseType.VARCHAR,
                "year": BaseType.INT,
                "graduate": BaseType.BOOL,
                "alumni": BaseType.BOOL,
                "gpa": BaseType.INT,
                "enrolled.student_id": BaseType.INT,
                "s_e.course_id": BaseType.INT,
                "semester": BaseType.VARCHAR,
                "grade": BaseType.INT,
                "dropped": BaseType.BOOL,
                "course.course_id": BaseType.INT,
                "course.name": BaseType.VARCHAR,
                "capacity": BaseType.INT,
                "instructor": BaseType.VARCHAR
            }))
        )


class TestQuerySelectWhereGroupBy(unittest.TestCase):
    def test_query_select_where_groupby(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year + -4 as start_year, AVG(s.gpa)
                    FROM student AS s
                    WHERE s.alumni = True AND 2010 < s.year
                    GROUP BY s.year"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "start_year": BaseType.INT,
                "avg_gpa": BaseType.INT
            }))
        )

        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year + -4 as start_year, AVG(s.gpa)
                    FROM student AS s
                    WHERE s.alumni = True AND 2010 < s.year
                    GROUP BY s.year, s.graduate"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "start_year": BaseType.INT,
                "avg_gpa": BaseType.INT
            }))
        )

        with self.assertRaises(AggregationMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year, s.name
                    FROM student AS s
                    WHERE s.alumni = True
                    GROUP BY s.year"""
            ).type_check(SymbolTable())

        with self.assertRaises(AggregationMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year
                    FROM student AS s
                    WHERE COUNT(s.student_id) < 5000
                    GROUP BY s.year"""
            ).type_check(SymbolTable())


class TestQuerySelectWhereGroupByHaving(unittest.TestCase):
    def test_query_select_where_groupby_having(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year + -4 as start_year, AVG(s.gpa)
                    FROM student AS s
                    WHERE s.alumni = True
                    GROUP BY s.year
                    HAVING 2010 < s.year AND AVG(s.gpa) < 3"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "start_year": BaseType.INT,
                "avg_gpa": BaseType.INT
            }))
        )

        with self.assertRaises(AggregationMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year + -4 as start_year, AVG(s.gpa)
                    FROM student AS s
                    WHERE s.alumni = True
                    GROUP BY s.year
                    HAVING 2010 < MIN(s.year)"""
            ).type_check(SymbolTable())

        with self.assertRaises(AggregationMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.year + -4 as start_year, AVG(s.gpa)
                    FROM student AS s
                    WHERE s.alumni = True
                    GROUP BY s.year
                    HAVING s.name = \"\""""
            ).type_check(SymbolTable())


class TestQueryUnion(unittest.TestCase):
    def test_query_union(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.name
                    FROM student AS s
                    WHERE s.gpa = 4
                    UNION
                    SELECT s.name
                    FROM student AS s
                    WHERE s.gpa = 3"""
            ).type_check(SymbolTable()),
            ("ss_ss", Schema({
                "name_name": BaseType.VARCHAR
            }))
        )

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.name
                    FROM student AS s
                    WHERE s.gpa = 4
                    UNION
                    SELECT e.course_id
                    FROM enrolled AS e
                    WHERE e.grade = 90"""
            ).type_check(SymbolTable())


class TestQueryIntersect(unittest.TestCase):
    def test_query_intersect(self):
        self.assertEqual(
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                        {enrolled_create_table_statement}
                        {course_create_table_statement}
                        SELECT s.name
                        FROM student AS s
                        WHERE s.gpa = 4
                        INTERSECT
                        SELECT s.name
                        FROM student AS s
                        WHERE s.graduate"""
            ).type_check(SymbolTable()),
            ("ss_ss", Schema({
                "name_name": BaseType.VARCHAR
            }))
        )

        with self.assertRaises(TypeMismatchError):
            stmt_sequence.parse(
                f"""{student_create_table_statement}
                    {enrolled_create_table_statement}
                    {course_create_table_statement}
                    SELECT s.name
                    FROM student AS s
                    WHERE s.gpa = 4
                    INTERSECT
                    SELECT e.course_id
                    FROM enrolled AS e
                    WHERE e.grade = 90"""
            ).type_check(SymbolTable())
