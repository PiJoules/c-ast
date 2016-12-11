# -*- coding: utf-8 -*-

from .base_node import Node
from .expressions import Expression
from .declarations import Declaration
from .definitions import Definition


class Statement(Node):
    """
    Something followed by a semicolon.

    {node};
    """
    __slots__ = ("node", )
    __types__ = {"node": Node}

    def _lines_with_ending(self, lines, ending=";"):
        # Make the last element have a semicolon included
        val = next(lines)
        next_val = next(lines, None)
        while next_val is not None:
            yield val
            val = next_val
            next_val = next(lines, None)
        # val is the last elem in the iterator
        yield "{}{}".format(val, ending)



class ExprStatement(Statement):
    __slots__ = ("expr", )
    __types__ = {"expr": Expression}

    def lines(self):
        yield from self._lines_with_ending(self.expr.lines())


class DeclStmt(Statement):
    __slots__ = ("decl", )
    __types__ = {"decl": Declaration}

    def lines(self):
        yield from self._lines_with_ending(self.decl.lines())


class DefStmt(Statement):
    __slots__ = ("defn", )
    __types__ = {"defn": Definition}

    def lines(self):
        yield from self._lines_with_ending(self.defn.lines())


