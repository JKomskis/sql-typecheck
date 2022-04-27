import unittest

from src.parsing.statements import stmt_sequence
from src.types.symbol_table import SymbolTable
from src.types.types import BaseType, Schema
from test.e2e.tables import (student_create_table_statement,
                             enrolled_create_table_statement,
                             course_create_table_statement)


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
                    SELECT s.student_id, CONCAT(s.name, "!"), s.year + 4 AS start_year, not s.graduate as undergraduate
                    FROM student AS s"""
            ).type_check(SymbolTable()),
            ("s", Schema({
                "student_id": BaseType.INT,
                "name_!": BaseType.VARCHAR,
                "start_year": BaseType.INT,
                "undergraduate": BaseType.BOOL
            }))
        )
