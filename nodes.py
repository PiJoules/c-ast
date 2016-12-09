# -*- coding: utf-8 -*-

from utils import SlotDefinedClass
from builtin_types import *


class Node(SlotDefinedClass):
    def lines(self):
        """
        Yields:
            str: Line in the string representation of this node
        """
        raise NotImplementedError

    def __str__(self):
        return "\n".join(self.lines())

    def __iter__(self):
        yield from self.lines()


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

class Declaration(Node):
    """
    {type} {varname}
    """
    __slots__ = ("type", "name")
    __types__ = {"type": Type, "name": str}

    def lines(self):
        yield "{} {}".format(self.type, self.name)


"""
Statements
"""

class Statement(Node):
    """
    Something followed by a semicolon.

    {operation};
    """
    __slots__ = ("operation", )
    __types__ = {"operation": Node}

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


class VariableDeclaration(Statement):
    """Wrapper for Declaration as a statement."""
    def __init__(self, type, name):
        super().__init__(Declaration(type, name))


