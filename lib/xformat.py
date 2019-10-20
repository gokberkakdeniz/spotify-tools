#!/usr/bin/env python3
from lark import Lark, Tree

GRAMMAR = r"""
expr            : (WS | ESCAPE | VAR | STRING | group)+
group           : _GROUP_OPEN (WS | ESCAPE | VAR | STRING | group)+ func_part? _GROUP_CLOSE
VAR             : "$"  ( CNAME | _GROUP_OPEN CNAME _GROUP_CLOSE)
func_part       : _PIPE _WS* func+
func            : FUNC_NAME (_WS+ FUNC_ARG)* _WS*
_GROUP_OPEN     : "{"
_GROUP_CLOSE    : "}"
FUNC_NAME       : "@" CNAME
FUNC_ARG        : _QUOTE _STRING_ESC_INNER _QUOTE
STRING          : /[^{}| ]+/
ESCAPE          : "$" VAR | "@" FUNC_NAME | "{{" | "}}"
WS              : " "
_WS             : " "
_QUOTE          : "'"
_PIPE           : "|"

%import common._STRING_ESC_INNER
%import common.CNAME
"""


class XFormat:
    """
    Extendet string format
    """

    def __init__(self):
        self.grammar = Lark(GRAMMAR, start="expr")

    def format(self, format_, variables, functions):
        return self.list_to_str(self.tree_to_list(self.parse(format_), variables, functions))

    def parse(self, format_):
        return self.grammar.parse(format_)

    def tree_to_list(self, tree, variables, functions):
        return self._tree2list(tree, [], variables, functions)

    def list_to_str(self, list_):
        result = ""
        for item in list_:
            if isinstance(item, list):
                try:
                    has_func_group = hasattr(item[-1][0][0], "__call__")
                except KeyError:
                    has_func_group = False

                if has_func_group:
                    group_result = self.list_to_str(item[:-1])

                    for func_group in item[-1]:
                        func = func_group[0]
                        args = func_group[1:] if len(func_group) > 1 else []
                        group_result = func(group_result, args)
                    result += group_result
                else:
                    result += self.list_to_str(item)
            else:
                result += item
        return result

    def _tree2list(self, tree, result, variables, functions):
        if tree.data == "expr":
            self._visit_children(tree, result, variables, functions)
        else:
            group_result = []
            result.append(group_result)
            self._visit_children(tree, group_result, variables, functions)

        return result

    def _visit_children(self, tree, result, variables, functions):
        for child in tree.children:
            if isinstance(child, Tree):
                self._tree2list(child, result, variables, functions)
            elif child.type == "VAR":
                var_name = child[2:-1] if child[1] == "{" else child[1:]
                result.append(str(variables.get(var_name, "")))
            elif child.type == "ESCAPE":
                result.append(str(child[1:]))
            elif child.type == "FUNC_NAME":
                try:
                    result.append(functions[str(child)])
                except KeyError:
                    raise Exception("Undefined function: " + str(child))
            elif child.type == "FUNC_ARG":
                child = child[1:-1]
                if child.isdigit():
                    child = int(child)
                result.append(child)
            else:
                result.append(str(child))
