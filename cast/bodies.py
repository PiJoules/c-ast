# -*- coding: utf-8 -*-

import cast.base_node as base_node
import cast.definitions as definitions


class Body(base_node.Node):
    """
    Block of lines.
    Statements have semicolons appended to them
    """
    __slots__ = ("contents", )
    __defaults__ = {"contents": []}

    def lines(self, indent_size=4):
        for node in self.contents:
            for line in node.lines():
                yield " " * indent_size + line


class Module(Body):
    # TODO: Add preprocessor stuff later
    __types__ = {"contents": [definitions.ALLOWED_FUNC_BODY_NODES]}


