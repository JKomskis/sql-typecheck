import sys

from src.parsing.statements import stmt_sequence
from src.types import symbol_table


def main(filename):
    with open(filename) as f:
        statements = stmt_sequence.parse(f.read())
        print(statements.type_check(symbol_table.SymbolTable()))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <sql filename>")
        sys.exit(0)
    main(sys.argv[1])
