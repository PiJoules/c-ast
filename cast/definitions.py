# -*- coding: utf-8 -*-

import cast.base_node as base_node
import cast.expressions as expressions
import cast.builtin_types as builtin_types
import cast.declarations as declarations
import cast.bodies as bodies


ALLOWED_FUNC_BODY_NODES = (
    text.InlineText,
    statements.ExprStatement,
)


class Definition(base_node.Node):
    pass


class VariableDefinition(Definition):
    """
    {type} {name} = {expr}
    """
    __slots__ = ("name", "expr", "type")
    __types__ = {
        "name": str,
        "expr": Expression,
        "type": Type
    }

    def lines(self):
        yield "{type} {name} = {expr}".format(
            type=self.type,
            name=self.name,
            expr=self.expr
        )


class FunctionBody(Body):
    """Similar to module, but function definition is not allowed."""
    __types__ = {"contents": [ALLOWED_FUNC_BODY_NODES]}


class FunctionDefinition(Definition):
    """
    {return_type} {name}({args}){{
        {body}
    }}
    """
    __slots__ = ("return_type", "name", "args", "body")
    __types__ = {
        "return_type": Type,
        "name": str,
        "args": ArgumentDeclarations,
        "body": FunctionBody
    }

    def lines(self):
        yield "{return_type} {name}({args}){{".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )
        yield from self._body_lines(self.body)
        yield "}"


