from parsy import regex, string, seq, Parser, fail, generate

# Helper parser that ignores case


def string_ignore_case(s: str) -> Parser:
    return string(s.lower(), transform=lambda x: x.lower())


def sep(separator):
    return padding >> string(separator) << padding


space = regex(r"\s+")
padding = regex(r"\s*")
as_tok = space + string("AS") + space

keywords = ["true", "false", "BOOL", "INT", "VARCHAR",
            "AND", "NOT", "AS", "JOIN", "ON", "SELECT", "FROM", "WHERE",
            "CREATE", "TABLE"]


@generate
def identifier() -> str:
    ident = yield regex("[a-zA-Z][a-zA-Z0-9_]*")
    if ident in keywords:
        return fail("identifier cannot be a keyword")
    return ident


int_literal = regex("-?[0-9]+").map(int)
lparen = string("(")
rparen = string(")")
bool_literal = (string_ignore_case("true") | string_ignore_case(
    "false")).map(lambda x: x.lower() == "true")
type_literal = (string_ignore_case("BOOL")
                | string_ignore_case("INT")
                | string_ignore_case("VARCHAR")).map(lambda x: x.upper())

t_name = identifier
c_name = seq(
    t_name=identifier,
    _dot=sep("."),
    c_name=identifier
).map(lambda x: (x['t_name'], x['c_name']))
