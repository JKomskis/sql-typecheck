from parsy import regex, string, Parser

# Helper parser that ignores case
def string_ignore_case(s: str) -> Parser:
    return string(s.lower(), transform=lambda x: x.lower())

space = regex(r"\s+")
as_tok = space + string("AS") + space

identifier = regex("[a-zA-Z][a-zA-Z0-9_]*")
int_literal = regex("-?[0-9]+").map(int)
lparen = string("(")
rparen = string(")")
bool_literal = (string_ignore_case("true") | string_ignore_case("false")).map(lambda x: x.lower() == "true")
type_literal = string_ignore_case("BOOL") \
               | string_ignore_case("INT") \
               | string_ignore_case("VARCHAR")