#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from cast.nodes import *
from cast.builtin_types import *


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

    def test_variable_definition(self):
        """Test variable definition node."""
        self.assertEqual(str(VariableDefinition(
            name="x",
            type=IntType(),
            expr=IntLiteral(2),
        )), "int x = 2")

        self.assertEqual(str(VariableDefinition(
            name="x",
            expr=IntLiteral(2),
        )), "x = 2")

    def test_function_definition(self):
        """Test function definition."""
        self.assertEqual(str(FunctionDefinition(
            return_type=VoidType(),
            name="main",
            args=ArgumentDeclarations([
                VariableDeclaration(IntType(), "argc"),
                VariableDeclaration(Pointer(StringType()), "argv")
            ]),
            body=[
                Statement(VariableDefinition(
                    type=IntType(),
                    name="x",
                    expr=IntLiteral(2),
                )),
                Statement(VariableDefinition(
                    type=CharType(),
                    name="c",
                    expr=CharLiteral("s"),
                )),
                Statement(VariableDefinition(
                    name="c",
                    expr=CharLiteral("a"),
                )),
            ]
        )), """
void main(int argc, char** argv){
    int x = 2;
    char c = 's';
    c = 'a';
}""".strip())

    def test_function_call(self):
        """Test function call node."""
        self.assertEqual(str(FunctionCall(
            func_name="printf",
            args=[
                StringLiteral("abc"),
                IntLiteral(123)
            ]
        )), "printf(\"abc\", 123)")

    def test_if_statement(self):
        """Test if statement."""
        self.assertEqual(str(If(
            conditions=[Variable("x")],
            bodies=[[Statement(Variable("a"))]]
        )), """
if (x){
    a;
}""".strip())

        self.assertEqual(str(If(
            conditions=[Variable("x")],
            bodies=[
                [Statement(Variable("a"))],
                [Statement(Variable("b"))],
            ]
        )), """
if (x){
    a;
}
else {
    b;
}""".strip())

        self.assertEqual(str(If(
            conditions=[Variable("x"), Variable("y")],
            bodies=[
                [Statement(Variable("a"))],
                [Statement(Variable("b"))],
            ]
        )), """
if (x){
    a;
}
else if (y){
    b;
}""".strip())

        self.assertEqual(str(If(
            conditions=[
                Variable("x"),
                Variable("y"),
                Variable("z"),
            ],
            bodies=[
                [Statement(Variable("a"))],
                [Statement(Variable("b"))],
                [Statement(Variable("c"))],
            ]
        )), """
if (x){
    a;
}
else if (y){
    b;
}
else if (z){
    c;
}""".strip())

        self.assertEqual(str(If(
            conditions=[
                Variable("x"),
                Variable("y"),
                Variable("z"),
            ],
            bodies=[
                [Statement(Variable("a"))],
                [Statement(Variable("b"))],
                [Statement(Variable("c"))],
                [Statement(Variable("d"))],
            ]
        )), """
if (x){
    a;
}
else if (y){
    b;
}
else if (z){
    c;
}
else {
    d;
}
""".strip())

        # Nested if statements
        self.assertEqual(str(If(
            conditions=[Variable("x")],
            bodies=[
                [
                    If(
                        conditions=[Variable("y")],
                        bodies=[[Statement(Variable("b"))]],
                    )
                ]
            ]
        )), """
if (x){
    if (y){
        b;
    }
}""".strip())

    def test_while(self):
        """Test while loop."""
        self.assertEqual(str(While(
            condition=Variable("x"),
            body=[Statement(Variable("y"))]
        )), """
while (x){
    y;
}
""".strip())

        # Nested while
        self.assertEqual(str(While(
            condition=Variable("x"),
            body=[
                While(
                    condition=Variable("y"),
                    body=[Statement(Variable("z"))]
                )
            ]
        )), """
while (x){
    while (y){
        z;
    }
}
""".strip())

    def test_dow_while(self):
        """Test do while loop."""
        self.assertEqual(str(DoWhile(
            condition=Variable("x"),
            body=[Statement(Variable("y"))]
        )), """
do {
    y;
} while (x);""".strip())

#    def test_for_loop(self):
#        """Test for loop."""
#        self.assertEqual(str(), """
#for (int i = 0; i < 2; i++){
#    z;
#}
#                         """.strip())



if __name__ == "__main__":
    unittest.main()

