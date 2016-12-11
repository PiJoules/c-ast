# -*- coding: utf-8 -*-


from .utils import *


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


