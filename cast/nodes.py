# -*- coding: utf-8 -*-

from .utils import *
from .builtin_types import *


INDENT_SIZE = 4


class Node(SlotDefinedClass):
    def lines(self):
        """
        Yields:
            str: Line in the string representation of this node
        """
        raise NotImplementedError

    def __str__(self):
        return "\n".join(map(str, self.lines()))

    def __iter__(self):
        yield from self.lines()

    def _body_lines(self, body):
        for node in body:
            for line in node.lines():
                yield " " * INDENT_SIZE + line


"""
Generic blocks and text
"""

class Module(Node):
    __slots__ = ("contents", )
    __types__ = {"contents": [Node]}
    __defaults__ = {"contents": []}

    def lines(self):
        for content in self.contents:
            yield from content


class InlineText(Node):
    """InlineText text."""
    __slots__ = ("text", )
    __types__ = {"text": str}
    __defaults__ = {"text": ""}

    def lines(self):
        yield self.text


"""
Declarations
"""

class VariableDeclaration(Node):
    """
    {type} {varname}
    """
    __slots__ = ("type", "name")
    __types__ = {"type": Type, "name": str}

    def lines(self):
        yield "{} {}".format(self.type, self.name)


class ArgumentDeclarations(Node):
    """
    {VariableDeclaration}, {VariableDeclaration}, ...
    """
    __slots__ = ("args", )
    __types__ = {"args": [VariableDeclaration]}

    def lines(self):
        yield ", ".join(map(str, self.args))


class FunctionDeclaration(Node):
    __slots__ = ("name", "return_type", "args")
    __types__ = {
        "name": str,
        "return_type": Type,
        "args": ArgumentDeclarations
    }

    def lines(self):
        yield "{return_type} {name}({args})".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )


"""
Operations
"""

class Operation(Node):
    __slots__ = ("symbol", )
    __types__ = {"symbol": str}


class BoolOp(Operation):
    """Operation that returns a boolean value (0 or 1)"""
    pass


class CompareOp(BoolOp):
    """Operation for comparing 2 values."""
    pass


class Eq(CompareOp):
    def __init__(self):
        super().__init__("==")


class NotEq(CompareOp):
    def __init__(self):
        super().__init__("!=")


class Lt(CompareOp):
    def __init__(self):
        super().__init__("<")


class LtE(CompareOp):
    def __init__(self):
        super().__init__("<=")


class Gt(CompareOp):
    def __init__(self):
        super().__init__(">")


class GtE(CompareOp):
    def __init__(self):
        super().__init__(">=")



"""
Expressions
"""

class Expression(Node):
    pass


class Variable(Expression):
    __slots__ = ("name", )
    __types__ = {"name": str}

    def lines(self):
        yield self.name


class Literal(Expression):
    __slots__ = ("value", )

    def lines(self):
        yield self.value


class CharLiteral(Literal):
    __types__ = {"value": str}

    def lines(self):
        yield "'{}'".format(self.value)


class StringLiteral(Literal):
    __types__ = {"value": str}

    def lines(self):
        yield '"{}"'.format(self.value)


class IntLiteral(Literal):
    __types__ = {"value": int}

    def lines(self):
        yield str(self.value)


class FloatLiteral(Literal):
    __types__ = {"value": float}

    def lines(self):
        yield str(self.value)


class FunctionCall(Expression):
    __slots__ = ("func_name", "args")
    __types__ = {
        "func_name": str,
        "args": [Expression]
    }

    def lines(self):
        yield "{name}({args})".format(
            name=self.func_name,
            args=", ".join(map(str, self.args))
        )


class BinaryOp(Expression):
    """
    An expression that is in the format {lhs} {op} {rhs}
    """
    __slots__ = ("lhs", "op", "rhs")
    __types__ = {
        "lhs": Expression,
        "op": Operation,
        "rhs": Expression
    }

    def lines(self):
        yield "{lhs} {op} {rhs}".format(
            lhs=self.lhs,
            op=self.op,
            rhs=self.rhs
        )


class BoolExpr(BinaryOp):
    __types__ = merge_dicts(BinaryOp.__types__, {"op": BoolOp})



"""
Definitions
"""

class VariableDefinition(Node):
    """
    [type] {name} = {expr}
    """
    __slots__ = ("name", "expr", "type")
    __types__ = {
        "name": str,
        "expr": Expression,
        "type": optional(Type)
    }
    __defaults__ = {"type": None}

    def lines(self):
        fmt = "{name} = {expr}"
        if self.type is not None:
            fmt = "{type} " + fmt
        yield fmt.format(
            type=self.type,
            name=self.name,
            expr=self.expr
        )


class FunctionDefinition(Node):
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
        "body": [Node]
    }

    def lines(self):
        yield "{return_type} {name}({args}){{".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )
        for part in self.body:
            for line in part.lines():
                yield " " * INDENT_SIZE + line
        yield "}"



"""
Statements
"""

class Statement(Node):
    """
    Something followed by a semicolon.

    {node};
    """
    __slots__ = ("node", )
    __types__ = {"node": Node}

    def lines(self):
        # Make the last element have a semicolon included
        lines = self.node.lines()
        val = next(lines)
        next_val = next(lines, None)
        while next_val is not None:
            yield val
            val = next_val
            next_val = next(lines, None)
        # val is the last elem in the iterator
        yield "{};".format(val)


"""
Control flow
"""

class If(Node):
    """
    If requires at least 1 condition.
    bodies is a list of lists containing Nodes.
    There must be at least 1 body for every condition.
    For n conditions, there can be either n or n+1 bodies,
    where the first n are the bodies for each respective condition,
    and the last is the else condition.

    if ({cond1}){
        {body1}
    }
    else if ({cond2}){
        {body2}
    }
    ...
    else if ({condn}){
        {bodyn}
    }
    else {
        {bodyn+1}
    }
    """

    __slots__ = ("conditions", "bodies")
    __types__ = {
        "conditions": [Expression],
        "bodies": [[Node]]
    }

    def lines(self):
        yield "if ({cond}){{".format(
            cond=self.conditions[0]
        )
        # First body
        yield from self._body_lines(self.bodies[0])
        yield "}"

        # Else if statements
        for i in range(1, len(self.conditions)):
            yield "else if ({cond}){{".format(
                cond=self.conditions[i]
            )
            yield from self._body_lines(self.bodies[i])
            yield "}"


        if len(self.bodies) > len(self.conditions):
            yield "else {"
            yield from self._body_lines(self.bodies[len(self.conditions)])
            yield "}"


class While(Node):
    __slots__ = ("condition", "body")
    __types__ = {
        "condition": Expression,
        "body": [Node]
    }

    def lines(self):
        yield "while ({cond}){{".format(
            cond=self.condition
        )
        yield from self._body_lines(self.body)
        yield "}"



class DoWhile(Node):
    __slots__ = ("condition", "body")
    __types__ = {
        "condition": Expression,
        "body": [Node]
    }

    def lines(self):
        yield "do {"
        yield from self._body_lines(self.body)
        yield "}} while ({cond});".format(
            cond=self.condition
        )


class For(Node):
    __slots__ = ("start", "condition", "update", "body")
    __types__ = {
        "start": optional(VariableDefinition),
        "condition": optional(Expression),
        "update": optional(Node),
        "body": [Node]
    }
    __defaults__ = {
        "start": None,
        "condition": None,
        "update": None
    }

    def lines(self):
        yield "for ({start}; {cond}; {update}){{".format(
            start=self.start,
            cond=self.condition,
            update=self.update
        )
        yield from self._body_lines(body)
        yield "}"

