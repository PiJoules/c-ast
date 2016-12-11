#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from cast import *


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
        self.assertEqual(str(Module([InlineText("abc")])), "abc")

    def test_inline_text(self):
        """Test inline text node."""
        self.assertEqual(str(InlineText()), "")
        self.assertEqual(str(InlineText(text="abc")), "abc")

    def test_declaration(self):
        """Test VariableDeclaration node."""
        self.assertEqual(str(VariableDeclaration(IntType(), "x")), "int x")
        self.assertEqual(str(VariableDeclaration(Type("custom type"), "x")), "custom type x")

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

    def test_function_definition(self):
        """Test function definition."""
        self.assertEqual(str(FunctionDefinition(
            return_type=VoidType(),
            name="main",
            args=ArgumentDeclarations([
                VariableDeclaration(IntType(), "argc"),
                VariableDeclaration(Pointer(StringType()), "argv")
            ]),
            body=FunctionBody([
                VarDefStmt(VariableDefinition(
                    type=IntType(),
                    name="x",
                    expr=IntLiteral(2),
                )),
                VarDefStmt(VariableDefinition(
                    type=CharType(),
                    name="c",
                    expr=CharLiteral("s"),
                )),
            ])
        )), """
void main(int argc, char** argv){
    int x = 2;
    char c = 's';
}""".strip())

    def test_variable_assingment(self):
        """Test variable assignment."""
        self.assertEqual(str(VariableAssignment(
            lhs="x",
            rhs=IntLiteral(2)
        )), "x = 2")
        self.assertEqual(str(VariableAssignment(
            lhs="x",
            rhs=IntLiteral(2),
            op=Mult()
        )), "x *= 2")
        self.assertEqual(str(AugmentedAssgn(
            lhs="x",
            rhs=IntLiteral(2),
            op=Mult()
        )), "x *= 2")

    def test_function_call(self):
        """Test function call node."""
        self.assertEqual(str(FunctionCall(
            func="printf",
            args=[
                StringLiteral("abc"),
                IntLiteral(123)
            ]
        )), "printf(\"abc\", 123)")

    def test_if_statement(self):
        """Test if statement."""
        self.assertEqual(str(If(
            conds=[Variable("x")],
            bodies=[ControlFlowBody([ExprStmt(Variable("a"))])]
        )), """
if (x){
    a;
}""".strip())

        self.assertEqual(str(If(
            conds=[Variable("x")],
            bodies=[
                ControlFlowBody([ExprStmt(Variable("a"))]),
                ControlFlowBody([ExprStmt(Variable("b"))]),
            ]
        )), """
if (x){
    a;
}
else {
    b;
}""".strip())

        self.assertEqual(str(If(
            conds=[Variable("x"), Variable("y")],
            bodies=[
                ControlFlowBody([ExprStmt(Variable("a"))]),
                ControlFlowBody([ExprStmt(Variable("b"))]),
            ]
        )), """
if (x){
    a;
}
else if (y){
    b;
}""".strip())

        self.assertEqual(str(If(
            conds=[
                Variable("x"),
                Variable("y"),
                Variable("z"),
            ],
            bodies=[
                ControlFlowBody([ExprStmt(Variable("a"))]),
                ControlFlowBody([ExprStmt(Variable("b"))]),
                ControlFlowBody([ExprStmt(Variable("c"))]),
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
            conds=[
                Variable("x"),
                Variable("y"),
                Variable("z"),
            ],
            bodies=[
                ControlFlowBody([ExprStmt(Variable("a"))]),
                ControlFlowBody([ExprStmt(Variable("b"))]),
                ControlFlowBody([ExprStmt(Variable("c"))]),
                ControlFlowBody([ExprStmt(Variable("d"))]),
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
            conds=[Variable("x")],
            bodies=[
                ControlFlowBody([
                    If(
                        conds=[Variable("y")],
                        bodies=[ControlFlowBody([ExprStmt(Variable("b"))])],
                    )
                ])
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
            body=ControlFlowBody([ExprStmt(Variable("y"))])
        )), """
while (x){
    y;
}
""".strip())

        # Nested while
        self.assertEqual(str(While(
            condition=Variable("x"),
            body=ControlFlowBody([
                While(
                    condition=Variable("y"),
                    body=ControlFlowBody([ExprStmt(Variable("z"))])
                )
            ])
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
            body=ControlFlowBody([ExprStmt(Variable("y"))])
        )), """
do {
    y;
} while (x);""".strip())

    def test_for_loop(self):
        """Test for loop."""
        self.assertEqual(str(For(
            start=VariableDefinition(
                IntType(), "i", IntLiteral(0)
            ),
            cond=BinaryOp(
                Variable("i"), Lt(), IntLiteral(2)
            ),
            update=PostInc("i"),
            body=ControlFlowBody([ExprStmt(Variable("z"))])
        )), """
for (int i = 0; i < 2; i++){
    z;
}
                         """.strip())

    def test_switch_statement(self):
        """Test switch statement."""
        self.assertEqual(str(Switch(
            cond=Variable("x"),
            cases=[
                Variable("y"),
                Variable("z")
            ],
            bodies=[
                ControlFlowBody([ExprStmt(FunctionCall("y", [])), Break()]),
                ControlFlowBody([Break()]),
                ControlFlowBody([Break()])
            ]
        )), """
switch (x){
    case y:
        y();
        break;
    case z:
        break;
    default:
        break;
}
                         """.strip())

    def test_arrays(self):
        """Test arrays."""
        self.assertEqual(str(ArrayLiteral(
            [FloatLiteral(100.0), FloatLiteral(10.0), FloatLiteral(0.13)]
        )), "{100.0, 10.0, 0.13}")

        self.assertEqual(str(ArrayAccess(
            FunctionCall(Variable("func1"), []), FunctionCall(Variable("func2"), [])
        )), "func1()[func2()]")

        # Can be one of multiple values
        self.assertIn(str(ArrayDesignatedInitializer(
            {
                4: IntLiteral(100),
                10: FunctionCall("func1")
            }
        )), ("""
{
    [4]=100,
    [10]=func1(),
}
                         """.strip(),
    """
{
    [10]=func1(),
    [4]=100,
}
                         """.strip()
        ))

    def test_struct(self):
        """Test structs."""
        self.assertEqual(str(StructLiteral(
            [FloatLiteral(100.0), FloatLiteral(10.0), FloatLiteral(0.13)]
        )), """
{
    100.0,
    10.0,
    0.13,
}""".strip())

        self.assertEqual(str(StructAccess(
            FunctionCall(Variable("func1")), "attr2"
        )), "func1().attr2")

        self.assertEqual(str(StructRefAccess(
            FunctionCall(Variable("func1")), "attr2"
        )), "func1()->attr2")

        # Can be one of multiple values
        self.assertIn(str(StructDesignatedInitializer(
            {
                "attr1": IntLiteral(100),
                "attr2": FunctionCall("func1")
            }
        )), ("""
{
    .attr1=100,
    .attr2=func1(),
}
                         """.strip(),
    """
{
    .attr2=func1(),
    .attr1=100,
}
                         """.strip()
        ))

        self.assertEqual(str(StructDefStmt(Struct(
            name="S",
            attrs=[VarDeclStmt(VariableDeclaration(CharType(), "i"))]
        ))), """
struct S {
    char i;
};
                         """.strip())

        self.assertEqual(str(StructDefStmt(Struct(
            name="S",
            attrs=[
                VarDeclStmt(VariableDeclaration(CharType(), "i")),
                VarDeclStmt(VariableDeclaration(InlineStruct(
                    attrs=[VarDeclStmt(VariableDeclaration(CharType(), "i"))]
                ), "i2"))
            ]
        ))), """
struct S {
    char i;
    struct {char i;} i2;
};
                         """.strip())

    def test_union(self):
        """Test union."""
        self.assertEqual(str(UnionAccess(
            FunctionCall(Variable("func1")), "attr2"
        )), "func1().attr2")

        self.assertEqual(str(UnionRefAccess(
            FunctionCall(Variable("func1")), "attr2"
        )), "func1()->attr2")

        self.assertEqual(str(UnionDefStmt(Union(
            name="S",
            attrs=[VarDeclStmt(VariableDeclaration(CharType(), "i"))]
        ))), """
union S {
    char i;
};
                         """.strip())

        self.assertEqual(str(UnionDefStmt(Union(
            name="S",
            attrs=[
                VarDeclStmt(VariableDeclaration(CharType(), "i")),
                VarDeclStmt(VariableDeclaration(InlineUnion(
                    attrs=[VarDeclStmt(VariableDeclaration(CharType(), "i"))]
                ), "i2"))
            ]
        ))), """
union S {
    char i;
    union {char i;} i2;
};
                         """.strip())




if __name__ == "__main__":
    unittest.main()

