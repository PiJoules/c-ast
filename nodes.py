# -*- coding: utf-8 -*-

from utils import *
from builtin_types import *


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


"""
Generic blocks and text
"""

class Module(Node):
    __slots__ = ("contents", )
    __defaults__ = {"contents": []}

    def lines(self):
        for content in self.contents:
            yield from content


class InlineText(Node):
    """InlineText text."""
    __slots__ = ("text", )
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

    def lines(self):
        yield "{} {}".format(self.type, self.name)


class ArgumentDeclarations(Node):
    """
    {VariableDeclaration}, {VariableDeclaration}, ...
    """
    __slots__ = ("args", )

    def lines(self):
        yield ", ".join(map(str, self.args))


class FunctionDeclaration(Node):
    __slots__ = ("name", "return_type", "args")

    def lines(self):
        yield "{return_type} {name}({args})".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )


"""
Expressions
"""

class Expression(Node):
    pass


class Variable(Expression):
    __slots__ = ("name", )

    def lines(self):
        yield self.name


class Literal(Expression):
    __slots__ = ("value", )

    def lines(self):
        yield self.value


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



"""
Definitions
"""

class VariableDefinition(Node):
    """
    [type] {name} = {expr}
    """
    __slots__ = ("name", "expr", "type")
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

    {operation};
    """
    __slots__ = ("operation", )

    def lines(self):
        # Make the last element have a semicolon included
        lines = self.operation.lines()
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

class If(Statement):
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

    def __body_lines(self, body):
        for node in body:
            for line in node.lines():
                yield " " * INDENT_SIZE + line

    def lines(self):
        yield "if ({cond}){{".format(
            cond=self.conditions[0]
        )
        # First body
        yield from self.__body_lines(self.bodies[0])
        yield "}"

        # Else if statements
        for i in range(1, len(self.conditions)):
            yield "else if ({cond}){{".format(
                cond=self.conditions[i]
            )
            yield from self.__body_lines(self.bodies[i])
            yield "}"


        if len(self.bodies) > len(self.conditions):
            yield "else {"
            yield from self.__body_lines(self.bodies[len(self.conditions)])
            yield "}"

