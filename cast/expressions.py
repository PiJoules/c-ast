# -*- coding: utf-8 -*-

from .base_node import Node
from .operations import *
from .utils import merge_dicts


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


