__all__ = ["bool_expr", "data_structures", "expr",
           "int_expr", "query", "statements", "terminals"]

from src.parsing.statements import stmt_sequence, StmtSequence

def parse_sql_program(sql: str) -> StmtSequence:
    return stmt_sequence.parse(sql)
