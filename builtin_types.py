# -*- coding: utf-8 -*-

from utils import SlotDefinedClass


class Type(SlotDefinedClass):
    __slots__ = ("name", )
    __types__ = {"name": str}

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Type) and self.name == other.name

    def __ne__(self, other):
        return not (self == other)


class CharType(Type):
    def __init__(self):
        super().__init__(name="char")


class IntType(Type):
    def __init__(self):
        super().__init__(name="int")


class FloatType(Type):
    def __init__(self):
        super().__init__(name="float")


class VoidType(Type):
    def __init__(self):
        super().__init__(name="void")


class Pointer(Type):
    __slots__ = ("type", )
    __types__ = {"type": Type}

    def __str__(self):
        return str(self.type) + "*"

    def __eq__(self, other):
        return isinstance(other, Pointer) and self.type == other.type


class StringType(Pointer):
    def __init__(self):
        super().__init__(CharType())

