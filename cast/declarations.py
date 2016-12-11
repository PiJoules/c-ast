# -*- coding: utf-8 -*-

from .base_node import Node
from .builtin_types import Type


class Declaration(Node):
    pass


class InlineDecl(Declaration):
    pass


class InlineFuncDecl(InlineDecl):
    """
    Similar to FunctionDeclaration, but treats functions as function pointers.
    This is how function declarations are used in structs as attributes or
    arguments in another function.
    """

    def lines(self):
        yield "{return_type} (*{name})({args})".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )


class VariableDeclaration(InlineDecl):
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
    __types__ = {"args": [InlineDecl]}

    def lines(self):
        yield ", ".join(map(str, self.args))


class FunctionDeclaration(Declaration):
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





