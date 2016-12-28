# -*- coding: utf-8 -*-

from .utils import *
from .builtin_types import *
from .defaults import BASE_INDENT_SIZE


class Node(SlotDefinedClass):
    """Base node class."""

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


"""
Mixins
"""

class AllowedModuleNode(Mixin):
    """A Node allowed in the body of a module."""


class AllowedFuncBodyNode(Mixin):
    """A node allowed in a function body."""


class AllowedAllNode(AllowedModuleNode, AllowedFuncBodyNode):
    """A node allowed anywhere."""


class AssignableNode(Mixin):
    """A node that can be assigned a value."""


"""
Text based nodes
"""


class InlineText(Node, AllowedAllNode):
    """Literal text"""
    __slots__ = ("text", )
    __types__ = {"text": str}
    __defaults__ = {"text": ""}

    def lines(self):
        yield self.text


"""
Body nodes for blocks of text
"""

class Body(Node):
    """
    Block of lines.
    Statements have semicolons appended to them
    """
    __slots__ = ("contents", )
    __defaults__ = {"contents": []}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        for node in self.contents:
            for line in node.lines():
                yield " " * indent_size + line


class Module(Body):
    # TODO: Add preprocessor stuff later
    __types__ = {"contents": [Node]}

    def lines(self):
        # Module is root, so 0 indent_size
        yield from super().lines(indent_size=0)


"""
Expressions
"""

class Expression(Node):
    pass


class Variable(Expression, AssignableNode):
    __slots__ = ("name", )
    __types__ = {"name": str}

    def lines(self):
        yield self.name


class Literal(Expression, AssignableNode):
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


class ArrayLiteral(Literal):
    __types__ = {"value": [Expression]}

    def lines(self):
        yield "{{{}}}".format(", ".join(map(str, self.value)))


class ArrayDesignatedInitializer(Literal):
    """
    This is only allowed by GCC.
    TODO: Check for compiler
    """
    __types__ = {"value": {(int, CharLiteral): Expression}}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        yield "{"
        for idx, expr in self.value.items():
            yield " " * indent_size + "[{}]={},".format(idx, expr)
        yield "}"


class Access(Expression, AssignableNode):
    pass


class ArrayAccess(Access):
    __slots__ = ("arr", "idx")
    __types__ = {"arr": Expression, "idx": Expression}

    def lines(self):
        yield "{}[{}]".format(self.arr, self.idx)


class StructLiteral(Literal):
    __types__ = {"value": [Expression]}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        yield "{"
        for expr in self.value:
            yield " " * indent_size + "{},".format(expr)
        yield "}"


class StructDesignatedInitializer(Literal):
    """
    This is only allowed by GCC.
    TODO: Check for compiler
    """
    __types__ = {"value": {str: Expression}}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        yield "{"
        for attr, expr in self.value.items():
            yield " " * indent_size + ".{}={},".format(attr, expr)
        yield "}"


class StructAccess(Access):
    __slots__ = ("expr", "attr")
    __types__ = {"expr": Expression, "attr": str}

    def lines(self):
        yield "{}.{}".format(self.expr, self.attr)


class StructRefAccess(Access):
    __slots__ = ("expr", "attr")
    __types__ = {"expr": Expression, "attr": str}

    def lines(self):
        yield "{}->{}".format(self.expr, self.attr)


class UnionAccess(Access):
    __slots__ = ("expr", "attr")
    __types__ = {"expr": Expression, "attr": str}

    def lines(self):
        yield "{}.{}".format(self.expr, self.attr)


class UnionRefAccess(Access):
    __slots__ = ("expr", "attr")
    __types__ = {"expr": Expression, "attr": str}

    def lines(self):
        yield "{}->{}".format(self.expr, self.attr)


class FunctionCall(Expression):
    __slots__ = ("func", "args")
    __types__ = {
        "func": (Expression, str),
        "args": [Expression]
    }
    __defaults__ = {"args": []}

    def lines(self):
        yield "{name}({args})".format(
            name=self.func,
            args=", ".join(map(str, self.args))
        )


class Cast(Expression):
    __slots__ = ("type", "expr")
    __types__ = {
        "type": Type,
        "expr": Expression
    }

    def lines(self):
        yield "({})({})".format(self.type, self.expr)


class OrderedExpr(Expression):
    """An expression where order of operations matters."""


"""
Operations
"""

class Operator(Node):
    __slots__ = ("symbol", )
    __types__ = {"symbol": str}

    def lines(self):
        yield self.symbol


class BinOp(Operator):
    """An operation that requires 2 arguments."""


class UnOp(Operator):
    """An operation that requires 1 argument."""


class Increment(UnOp):
    def __init__(self):
        super().__init__("++")


class Decrement(UnOp):
    def __init__(self):
        super().__init__("--")


class Address(UnOp):
    def __init__(self):
        super().__init__("&")


class Reference(UnOp):
    def __init__(self):
        super().__init__("*")


class Positive(UnOp):
    def __init__(self):
        super().__init__("+")


class Negative(UnOp):
    def __init__(self):
        super().__init__("-")


class Complement(UnOp):
    def __init__(self):
        super().__init__("~")


class Negation(UnOp):
    def __init__(self):
        super().__init__("!")


class NumericOp(BinOp):
    """Operator that is meant to return a range of numeric values, as opposed
    boolean operations which return either 0 or 1.

    These operations can be used with augmented assignments.
    """


class ArithmeticOp(NumericOp):
    pass


class Add(ArithmeticOp):
    def __init__(self):
        super().__init__("+")


class Sub(ArithmeticOp):
    def __init__(self):
        super().__init__("-")


class Mult(ArithmeticOp):
    def __init__(self):
        super().__init__("*")


class Div(ArithmeticOp):
    def __init__(self):
        super().__init__("/")


class Mod(ArithmeticOp):
    def __init__(self):
        super().__init__("%")


class BitwiseOp(BinOp):
    pass


class LShift(BitwiseOp):
    def __init__(self):
        super().__init__("<<")


class RShift(BitwiseOp):
    def __init__(self):
        super().__init__(">>")


class BitOr(BitwiseOp):
    def __init__(self):
        super().__init__("|")


class BitOr(BitwiseOp):
    def __init__(self):
        super().__init__("&")


class BitXor(BitwiseOp):
    def __init__(self):
        super().__init__("^")


class BoolOp(BinOp):
    """Operator that is meant to return a boolean value (0 or 1)"""


class Or(BoolOp):
    def __init__(self):
        super().__init__("||")


class And(BoolOp):
    def __init__(self):
        super().__init__("&&")


class CompareOp(BoolOp):
    """Operator for comparing 2 values."""


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


class Increment(Expression):
    __slots__ = ("var", )
    __types__ = {"var": str}


class PostInc(Increment):
    def lines(self):
        yield "{}++".format(self.var)


class PreInc(Increment):
    def lines(self):
        yield "++{}".format(self.var)


class Decrement(Expression):
    __slots__ = ("var", )
    __types__ = {"var": str}


class PostDec(Decrement):
    def lines(self):
        yield "{}--".format(self.var)


class PreDec(Decrement):
    def lines(self):
        yield "--{}".format(self.var)


class UnaryOp(OrderedExpr):
    """
    An expression that is in the format {op}{expr} or {expr}{op}
    """
    __slots__ = ("op", "expr")
    __types__ = {
        "op": BinOp,
        "expr": Expression
    }

    def lines(self):
        # Wrap in parenthesis to preserve order of operations
        if isinstance(self.expr, OrderedExpr):
            expr = "({expr})"
        else:
            expr = "{expr}"
        yield ("{op} " + expr).format(
            op=self.op,
            expr=self.expr
        )


class BinaryOp(OrderedExpr):
    """
    An expression that is in the format {lhs} {op} {rhs}
    """
    __slots__ = ("lhs", "op", "rhs")
    __types__ = {
        "lhs": Expression,
        "op": BinOp,
        "rhs": Expression
    }

    def lines(self):
        # Wrap in parenthesis to preserve order of operations
        if isinstance(self.lhs, OrderedExpr):
            lhs = "({lhs})"
        else:
            lhs = "{lhs}"
        if isinstance(self.rhs, OrderedExpr):
            rhs = "({rhs})"
        else:
            rhs = "{rhs}"
        yield (lhs + " {op} " + rhs).format(
            lhs=self.lhs,
            op=self.op,
            rhs=self.rhs
        )


class BoolExpr(BinaryOp):
    __types__ = merge_dicts(BinaryOp.__types__, {"op": BoolOp})


"""
Declarations
"""

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

"""
Definitions
"""

class Definition(Node):
    pass


class VariableDefinition(Definition):
    """
    {type} {name} = {expr}
    """
    __slots__ = ("type", "name", "expr")
    __types__ = {
        "name": (AssignableNode, str),
        "expr": Expression,
        "type": Type
    }

    def lines(self):
        yield "{type} {name} = {expr}".format(
            type=self.type,
            name=self.name,
            expr=self.expr
        )


class FunctionBody(Body):
    """Similar to module, but function definition is not allowed."""
    __types__ = {"contents": [AllowedFuncBodyNode]}


class FunctionDefinition(Definition):
    """
    {return_type} {name}({args}){{
        {body}
    }}
    """
    __slots__ = ("return_type", "name", "args", "body")
    __types__ = {
        "return_type": Type,
        "name": str,
        "args": ArgumentDeclarations,
        "body": FunctionBody
    }

    def lines(self):
        yield "{return_type} {name}({args}){{".format(
            return_type=self.return_type,
            name=self.name,
            args=self.args
        )
        yield from self.body
        yield "}"


"""
Assignments
"""

class VariableAssignment(Node):
    __slots__ = ("lhs", "op", "rhs")
    __types__ = {
        "lhs": (AssignableNode, str),
        "op": optional(NumericOp),
        "rhs": Expression
    }
    __defaults__ = {"op": None}

    def lines(self):
        yield "{lhs} {op}= {rhs}".format(
            lhs=self.lhs,
            rhs=self.rhs,
            op=self.op or ""
        )


class AugmentedAssgn(VariableAssignment):
    __types__ = merge_dicts(VariableAssignment.__types__, {"op": NumericOp})



"""
Statements
"""

class Statement(Node):
    def _lines_with_ending(self, lines, ending=";"):
        # Make the last element have a semicolon included
        val = next(lines)
        next_val = next(lines, None)
        while next_val is not None:
            yield val
            val = next_val
            next_val = next(lines, None)
        # val is the last elem in the iterator
        yield "{}{}".format(val, ending)


class Return(Statement):
    __slots__ = ("expr", )
    __types__ = {"expr": Expression}

    def lines(self):
        yield "return {};".format(self.expr)


class ExprStmt(Statement, AllowedFuncBodyNode):
    __slots__ = ("expr", )
    __types__ = {"expr": Expression}

    def lines(self):
        yield from self._lines_with_ending(self.expr.lines())


class VarDeclStmt(Statement, AllowedFuncBodyNode):
    __slots__ = ("decl", )
    __types__ = {"decl": Declaration}

    def lines(self):
        yield from self._lines_with_ending(self.decl.lines())


class VarDefStmt(Statement, AllowedFuncBodyNode):
    __slots__ = ("defn", )
    __types__ = {"defn": Definition}

    def lines(self):
        yield from self._lines_with_ending(self.defn.lines())


class Continue(Statement, AllowedFuncBodyNode):
    def lines(self):
        yield "continue;"


class Break(Statement, AllowedFuncBodyNode):
    def lines(self):
        yield "break;"


class Group(Type):
    __slots__ = Type.__slots__ + ("group_name", "contents", "separator")
    __types__ = merge_dicts(Type.__types__, {
        "group_name": str,
        "separator": str,
    })

    def __str__(self):
        return "{} {}".format(self.group_name, self.name)

    def whole(self, indent_size=BASE_INDENT_SIZE):
        """The whole group representation."""
        yield "{} {{".format(self)
        for content in self.contents:
            yield " " * indent_size + str(content) + self.separator
        yield "}"


class UnattributedGroup(Group):
    __types__ = merge_dicts(Group.__types__, {
        "contents": [str],
    })
    __defaults__ = {"separator": ","}


class AttributedGroup(Group):
    __types__ = merge_dicts(Group.__types__, {
        "contents": [VariableDeclaration]
    })
    __defaults__ = {"separator": ";"}


class InlineGroup(Group):
    """
    The name is not specified and the string representation
    of this group is the whole declaration of the fields.
    """
    __defaults__ = {"name": ""}

    def _inline_contents(self):
        for content in self.contents:
            yield str(content) + self.separator

    def __str__(self):
        return "{} {{".format(self.group_name) + " ".join(map(str, self._inline_contents())) + "}"


class AttributedInlineGroup(InlineGroup, AttributedGroup):
    __defaults__ = merge_dicts(InlineGroup.__defaults__, AttributedGroup.__defaults__)


class UnattributedInlineGroup(InlineGroup, UnattributedGroup):
    __defaults__ = merge_dicts(InlineGroup.__defaults__, UnattributedGroup.__defaults__)


class Struct(AttributedGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="struct", *args, **kwargs)


class InlineStruct(AttributedInlineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="struct", *args, **kwargs)


class Union(AttributedGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="union", *args, **kwargs)


class InlineUnion(AttributedInlineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="union", *args, **kwargs)


class Enum(UnattributedGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="enum", *args, **kwargs)


class InlineEnum(UnattributedInlineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(group_name="enum", *args, **kwargs)


class GroupDefStmt(Statement, AllowedAllNode):
    __slots__ = ("group", )
    __types__ = {"group": Group}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        yield from self._lines_with_ending(self.group.whole(indent_size))


class StructDefStmt(GroupDefStmt):
    __types__ = {"group": Struct}


class UnionDefStmt(GroupDefStmt):
    __types__ = {"group": Union}


class EnumDefStmt(GroupDefStmt):
    __types__ = {"group": Enum}


"""
Control flow
"""

class ControlFlowBody(Body):
    __types__ = {"contents": [AllowedFuncBodyNode]}


class ControlFlowNode(Node, AllowedFuncBodyNode):
    pass


class If(ControlFlowNode):
    """
    If requires at least 1 condition.
    bodies is a list of lists containing Nodes.
    There must be at least 1 body for every condition.
    For n conditions, there can be either n or n+1 bodies,
    where the first n are the bodies for each respective condition,
    and the last is the else condition.

    if ({cond1}){
        {body1}
    }
    else if ({cond2}){
        {body2}
    }
    ...
    else if ({condn}){
        {bodyn}
    }
    else {
        {bodyn+1}
    }
    """

    __slots__ = ("conds", "bodies")
    __types__ = {
        "conds": [Expression],
        "bodies": [ControlFlowBody]
    }

    def lines(self):
        yield "if ({cond}){{".format(
            cond=self.conds[0]
        )
        # First body
        yield from self.bodies[0]
        yield "}"

        # Else if statements
        for i in range(1, len(self.conds)):
            yield "else if ({cond}){{".format(
                cond=self.conds[i]
            )
            yield from self.bodies[i]
            yield "}"


        if len(self.bodies) > len(self.conds):
            yield "else {"
            yield from self.bodies[len(self.conds)]
            yield "}"


class Switch(ControlFlowNode):
    """
    Similar to If
    bodies is a list of lists containing Nodes.
    There must be at least 1 body for every case.
    For n cases, there can be either n or n+1 bodies,
    where the first n are the bodies for each respective condition,
    and the last is the default case.

    switch ({cond}){
        case {case1}:
            {body1}
        case {case2}:
            {body2}
        ...
        case {casen}:
            {bodyn}
        default:
            {bodyn+1}
    }
    """

    __slots__ = ("cond", "cases", "bodies")
    __types__ = {
        "cond": Expression,
        "cases": [Expression],
        "bodies": [ControlFlowBody]
    }

    def lines(self, indent_size=BASE_INDENT_SIZE):
        yield "switch ({cond}){{".format(
            cond=self.cond
        )

        for i, case in enumerate(self.cases):
            yield " " * indent_size + "case {}:".format(case)
            for line in self.bodies[i]:
                yield " " * indent_size + line

        if len(self.bodies) > len(self.cases):
            yield " " * indent_size + "default:".format(case)
            for line in self.bodies[len(self.cases)]:
                yield " " * indent_size + line

        yield "}"


class While(ControlFlowNode):
    __slots__ = ("condition", "body")
    __types__ = {
        "condition": Expression,
        "body": ControlFlowBody
    }

    def lines(self):
        yield "while ({cond}){{".format(
            cond=self.condition
        )
        yield from self.body
        yield "}"



class DoWhile(ControlFlowNode):
    __slots__ = ("condition", "body")
    __types__ = {
        "condition": Expression,
        "body": ControlFlowBody
    }

    def lines(self):
        yield "do {"
        yield from self.body
        yield "}} while ({cond});".format(
            cond=self.condition
        )


class For(ControlFlowNode):
    __slots__ = ("start", "cond", "update", "body")
    __types__ = {
        "start": optional(VariableDefinition),
        "cond": optional(Expression),
        "update": optional((Expression, VariableAssignment)),
        "body": ControlFlowBody
    }
    __defaults__ = {
        "start": None,
        "cond": None,
        "update": None
    }

    def lines(self):
        yield "for ({start}; {cond}; {update}){{".format(
            start=self.start or "",
            cond=self.cond or "",
            update=self.update or ""
        )
        yield from self.body
        yield "}"


"""
Preprocessors
"""

class Preprocessor(Node):
    pass


class Define(Preprocessor):
    __slots__ = ("symbol", "value")
    __types__ = {"symbol": str, "value": [Node]}

    def lines(self, indent_size=BASE_INDENT_SIZE):
        lines = [line for node in self.value for line in node]
        if len(lines) == 1:
            yield "#define {} {}".format(self.symbol, lines[0])
        else:
            yield "#define {} \\".format(self.symbol)
            for i in range(len(lines) - 1):
                yield " " * indent_size + lines[i] + " \\"
            yield " " * indent_size + lines[-1]


class Include(Preprocessor):
    __slots__ = ("filename", "system")
    __types__ = {"filename": str, "system": bool}
    __defaults__ = {"system": True}

    def lines(self):
        if self.system:
            yield "#include <{}>".format(self.filename)
        else:
            yield "#include \"{}\"".format(self.filename)


