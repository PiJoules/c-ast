# -*- coding: utf-8 -*-

"""
Textual nodes
"""

from .base_node import Node


class InlineText(Node):
    """InlineText text."""
    __slots__ = ("text", )
    __types__ = {"text": str}
    __defaults__ = {"text": ""}

    def lines(self):
        yield self.text

