# -*- coding: utf-8 -*-

import cast.utils as utils
import cast.base_node as base_node
import cast.expressions as expressions
import cast.bodies as bodies
import cast.definitions as definitions


class ControlFlowBody(bodies.Body):
    __types__ = bodies.FunctionBody.__types__


class If(base_node.Node):
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

    __slots__ = ("conditions", "bodies")
    __types__ = {
        "conditions": [Expression],
        "bodies": [[Node]]
    }

    def lines(self):
        yield "if ({cond}){{".format(
            cond=self.conditions[0]
        )
        # First body
        yield from self._body_lines(self.bodies[0])
        yield "}"

        # Else if statements
        for i in range(1, len(self.conditions)):
            yield "else if ({cond}){{".format(
                cond=self.conditions[i]
            )
            yield from self._body_lines(self.bodies[i])
            yield "}"


        if len(self.bodies) > len(self.conditions):
            yield "else {"
            yield from self._body_lines(self.bodies[len(self.conditions)])
            yield "}"


class While(Node):
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



class DoWhile(Node):
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


class For(base_node.Node):
    __slots__ = ("start", "condition", "update", "body")
    __types__ = {
        "start": utils.optional(definitions.VariableDefinition),
        "condition": utils.optional(expressions.Expression),
        "update": utils.optional(base_node.Node),
        "body": ControlFlowBody
    }
    __defaults__ = {
        "start": None,
        "condition": None,
        "update": None
    }

    def lines(self):
        yield "for ({start}; {cond}; {update}){{".format(
            start=self.start,
            cond=self.condition,
            update=self.update
        )
        yield from self._body_lines(body)
        yield "}"


