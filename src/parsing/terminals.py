from parsy import regex, string, seq, Parser, fail, generate


def string_ignore_case(s: str) -> Parser:
    """Helper parser that ignores case"""
    return string(s.lower(), transform=lambda x: x.lower())


def sep(separator):
    return padding >> string(separator) << padding


space = regex(r"\s+")
padding = regex(r"\s*")
as_tok = space + string("AS") + space

keywords = ["true", "false", "BOOL", "INT", "VARCHAR",
            "AND", "NOT", "AS", "JOIN", "ON", "SELECT", "FROM", "WHERE",
            "CREATE", "TABLE", "UNION", "INTERSECT", "GROUP", "BY",
            "HAVING", "MIN", "MAX", "COUNT", "AVG", "CONCAT", "SUBSTR"]


@generate
def identifier():
    ident = yield regex("[a-zA-Z][a-zA-Z0-9_\.]*")
    if ident in keywords:
        return fail("identifier cannot be a keyword")
    return ident


int_literal = regex("-?[0-9]+").map(int)
varchar_literal = regex('[^"]*').map(str)
lparen = string("(")
rparen = string(")")
bool_literal = (string_ignore_case("true") | string_ignore_case(
    "false")).map(lambda x: x.lower() == "true")
type_literal = (string_ignore_case("BOOL")
                | string_ignore_case("INT")
                | string_ignore_case("VARCHAR")).map(lambda x: x.upper())


@generate
def t_name():
    ident = yield identifier
    if ident.find('.') != -1:
        return fail("Table name must not contain a .")
    return ident


@generate
def c_name():
    ident = yield identifier
    parts = ident.split('.', 1)
    if len(parts) < 2:
        return fail("Column name must have table table and field name")
    return (parts[0], parts[1])
