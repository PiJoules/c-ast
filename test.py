#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from nodes import *
from builtin_types import *


class TestTypes(unittest.TestCase):
    def test_base_types(self):
        """Test the base unit types."""
        self.assertEqual(str(IntType()), "int")
        self.assertEqual(str(FloatType()), "float")
        self.assertEqual(str(CharType()), "char")

        self.assertNotEqual(IntType(), FloatType())

    def test_pointers(self):
        """Test pointer types."""
        self.assertEqual(str(Pointer(IntType())), "int*")
        self.assertEqual(str(Pointer(Pointer(FloatType()))), "float**")
        self.assertEqual(Pointer(IntType()).type, IntType())

    def test_string_type(self):
        """Test the string type."""
        self.assertEqual(StringType(), Pointer(CharType()))
        self.assertEqual(str(StringType()), str(Pointer(CharType())))


class TestNodes(unittest.TestCase):
    def test_module(self):
        """Test the module node."""
        self.assertEqual(str(Module()), "")

    def test_inline_text(self):
        """Test inline text node."""
        self.assertEqual(str(InlineText()), "")
        self.assertEqual(str(InlineText(text="abc")), "abc")

    def test_declaration(self):
        """Test VariableDeclaration node."""
        self.assertEqual(str(VariableDeclaration(IntType(), "x")), "int x")
        self.assertEqual(str(VariableDeclaration(Type("custom type"), "x")), "custom type x")

    def test_statement(self):
        """Test base statement node."""
        self.assertEqual(str(Statement(InlineText("text"))), "text;")
        node = Module([
            Statement(InlineText("text1")),
            Statement(InlineText("text2")),
        ])
        self.assertEqual(str(node), "text1;\ntext2;")

    def test_func_arguments(self):
        """Test function argument declarations."""
        self.assertEqual(str(
            ArgumentDeclarations([
                VariableDeclaration(IntType(), "arg1"),
                VariableDeclaration(StringType(), "arg2"),
            ])
        ), "int arg1, char* arg2")

    def test_func_declaration(self):
        """Test function declaration node."""
        self.assertEqual(str(FunctionDeclaration(
            return_type=VoidType(),
            name="func",
            args=ArgumentDeclarations([
                VariableDeclaration(IntType(), "arg1"),
                VariableDeclaration(StringType(), "arg2"),
            ]))
        ), "void func(int arg1, char* arg2)")


if __name__ == "__main__":
    unittest.main()

