# import unittest
# from src.parsing.bool_expr import BExprColumn

# from src.parsing.statements import StmtCreateTable, StmtQuery, StmtSequence, TableElement, stmt_create_table, stmt_sequence
# from src.parsing.query import QueryJoin, QuerySelect, QueryTable
# from src.parsing.expr import ExprColumn
# from src.types.symbol_table import SymbolTable
# from src.types.types import BaseType, RedefinedNameError, Schema


# class TestStmtCreate(unittest.TestCase):
#     student_table_schema = Schema({
#         "ssn": BaseType.INT,
#         "gpa": BaseType.INT,
#         "year": BaseType.INT,
#         "graduate": BaseType.BOOL,
#     })
#     student_create_table_ast = StmtCreateTable(
#         "students",
#         [
#             TableElement("ssn", BaseType.INT),
#             TableElement("gpa", BaseType.INT),
#             TableElement("year", BaseType.INT),
#             TableElement("graduate", BaseType.BOOL),
#         ]
#     )

#     enrolled_table_schema = Schema({
#         "id": BaseType.INT,
#         "grade": BaseType.INT,
#         "dropped": BaseType.BOOL,
#     })
#     enrolled_create_table_ast = StmtCreateTable(
#         "enrolled",
#         [
#             TableElement("id", BaseType.INT),
#             TableElement("grade", BaseType.INT),
#             TableElement("dropped", BaseType.BOOL),
#         ]
#     )

#     def test_stmt_create(self):
#         st = SymbolTable()
#         self.assertEqual(
#             StmtSequence([TestStmtCreate.student_create_table_ast]
#                          ).type_check(st),
#             ("students", TestStmtCreate.student_table_schema)
#         )
#         self.assertEqual(st,
#                          SymbolTable({"students": TestStmtCreate.student_table_schema}))

#         st = SymbolTable()
#         self.assertEqual(
#             StmtSequence([TestStmtCreate.student_create_table_ast,
#                           TestStmtCreate.enrolled_create_table_ast]
#                          ).type_check(st),
#             ("enrolled", TestStmtCreate.enrolled_table_schema)
#         )
#         self.assertEqual(st,
#                          SymbolTable({"students": TestStmtCreate.student_table_schema,
#                                       "enrolled": TestStmtCreate.enrolled_create_table_ast}))

#     def test_stmt_create_redefine_table(self):
#         st = SymbolTable()
#         with self.assertRaises(RedefinedNameError):
#             StmtSequence([TestStmtCreate.student_create_table_ast,
#                           TestStmtCreate.student_create_table_ast]
#                          ).type_check(st)

#     def test_stmt_create_redefine_column(self):
#         st = SymbolTable()
#         with self.assertRaises(RedefinedNameError):
#             StmtSequence([StmtCreateTable(
#                 "a",
#                 [
#                     TableElement("b", BaseType.INT),
#                     TableElement("b", BaseType.BOOL),
#                 ]
#             )]).type_check(st)


# class TestStmtQuery(unittest.TestCase):
#     student_table_schema = Schema({
#         "ssn": BaseType.INT,
#         "gpa": BaseType.INT,
#         "year": BaseType.INT,
#         "graduate": BaseType.BOOL,
#     })
#     student_create_table_ast = StmtCreateTable(
#         "students",
#         [
#             TableElement("ssn", BaseType.INT),
#             TableElement("gpa", BaseType.INT),
#             TableElement("year", BaseType.INT),
#             TableElement("graduate", BaseType.BOOL),
#         ]
#     )

#     enrolled_table_schema = Schema({
#         "id": BaseType.INT,
#         "grade": BaseType.INT,
#         "dropped": BaseType.BOOL,
#     })
#     enrolled_create_table_ast = StmtCreateTable(
#         "enrolled",
#         [
#             TableElement("id", BaseType.INT),
#             TableElement("grade", BaseType.INT),
#             TableElement("dropped", BaseType.BOOL),
#         ]
#     )

#     def test_stmt_query(self):
#         st = SymbolTable({"students": self.student_table_schema})
#         self.assertEqual(
#             StmtSequence([StmtQuery(QueryTable("students"))]).type_check(st),
#             ("students", self.student_table_schema)
#         )

#         self.assertEqual(
#             StmtSequence([StmtQuery(QuerySelect(
#                 [ExprColumn(("students", "ssn"))],
#                 QueryTable("students"),
#                 BExprColumn(("students", "graduate"))
#             ))]).type_check(st),
#             None
#         )
#         self.assertEqual(
#             stmt_sequence.parse(
#                 "students join enrolled ON students.id = enrolled.id AS s_e"),
#             StmtSequence([StmtQuery(QueryJoin(
#                 QueryTable("students"),
#                 QueryTable("enrolled"),
#                 BExprEquality(
#                     IExprColumn(("students", "id")),
#                     EqualityOperator.EQUALS,
#                     IExprColumn(("enrolled", "id"))
#                 ),
#                 "s_e"
#             ))])
#         )
