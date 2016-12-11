# -*- coding: utf-8 -*-

from .base_node import Node


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
