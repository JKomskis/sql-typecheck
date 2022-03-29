from parsy import *
import sys

padding = regex(r"\s*")

def sep(separator):
  return padding + string(separator) + padding

def main(filename):
  space = regex(r"\s+")
  as_tok = space + string("AS") + space

  identifier = regex("[a-zA-Z][a-zA-Z0-9_]*")
  int_literal = regex("-?[0-9]+").map(int)
  bool_literal = (string("true") | string("false")).map(bool)
  type_literal = string("BOOL") | string("INT") | string("VARCHAR")

  t_name = identifier
  c_name = seq(
    t_name=t_name,
    _dot=sep("."),
    f_name=identifier,
  )
  t_element = seq(
    identifier=identifier,
    _space=space,
    ty=type_literal
  )

  i_expr = forward_declaration()
  i_expr.become(alt(
    int_literal,
    seq(
      e1=i_expr,
      _plus=padding + string("+") + padding,
      e2=i_expr,
    ),
    seq(
      e1=i_expr,
      _times=padding + string("*") + padding,
      e2=i_expr,
    ),
    c_name
  ))

  b_expr = forward_declaration()
  b_expr.become(alt(
    bool_literal,
    seq(
      e1=b_expr,
      _and=space + string("AND") + space,
      e2=b_expr,
    ),
    (string("NOT") >> space >> b_expr),
    seq(
      e1=i_expr,
      _eq=padding + string("=") + padding,
      e2=i_expr,
    ),
    seq(
      e1=i_expr,
      _less=padding + string("<") + padding,
      e2=i_expr,
    ),
    c_name
  ))

  expr = b_expr | i_expr

  table_contents = seq(
    t_name=t_name,
    alias=(as_tok >> t_name).optional()
  )
  query = forward_declaration()
  join = seq(
    q1=query,
    _join=space + string("JOIN") + space,
    q2=query,
    _on=space + string("ON") + space,
    b_expr=b_expr,
    _as=as_tok,
    t_name=t_name
  )
  select = seq(
    _select=string("SELECT") + space,
    columns=expr.sep_by(sep(","), min=1),
    _from=space + string("FROM") + space,
    table=query,
    where=(space >> string("WHERE") >> space >> b_expr).optional(),
    _end=padding + string(";")
  )
  query.become(table_contents | join | select)

  stmt = forward_declaration()
  create_table = seq(
    _create=string("CREATE") + space + string("TABLE") + space,
    t_name=t_name,
    _open=space + string("("),
    columns=t_element.sep_by(sep(","), min=1)
  )
  stmt_seq = stmt.sep_by(sep(";"), min=1)
  stmt.become(create_table | query | stmt_seq)

  with open(filename) as f:
    print(stmt.parse(f.read()))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <sql filename>")
    sys.exit(0)
  main(sys.argv[1])
