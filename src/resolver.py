from enum import Enum, auto
from typing import Any

from values.tokens import Token

from values import stmt
from values import expr

from errors.error import parse_error, resolver_error


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    ANON = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(expr.Visitor, stmt.Visitor):
    def __init__(self, interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.unresolved = set()
        self.resolved = set()

    def visit_class_stmt(self, statement: stmt._Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(statement.name)
        self.define(statement.name)

        if (
            statement.superclass
            and statement.name.symbol == statement.superclass.name.symbol
        ):
            resolver_error(
                statement.superclass.name, "A class can't inherit from itself."
            )

        if statement.superclass:
            self.current_class = ClassType.SUBCLASS
            self.resolve_node(statement.superclass)

        if statement.superclass:
            self.begin_scope()
            self.peek()["super"] = True

        self.begin_scope()
        self.peek()["self"] = True
        for method in statement.methods:
            declaration = FunctionType.METHOD
            if method.name.symbol == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()

        if statement.superclass:
            self.end_scope()

        self.current_class = enclosing_class

    def visit_block_stmt(self, statement: stmt.Block) -> Any:
        self.begin_scope()
        self.resolve(statement.statements)
        self.end_scope()

    def visit_expression_stmt(self, statement: stmt.Expression) -> Any:
        self.resolve_node(statement.expression)

    def visit_function_stmt(self, statement: stmt.Function) -> Any:
        self.declare(statement.name)
        self.define(statement.name)
        self.resolve_function(statement, FunctionType.FUNCTION)

    def visit_anonym_func_expr(self, expression: expr.Anonym) -> Any:
        self.resolve_function(expression, FunctionType.ANON)

    def visit_if_stmt(self, statement: stmt.If) -> Any:
        self.resolve_node(statement.condition)
        self.resolve_node(statement.then)
        if statement.els is not None:
            self.resolve_node(statement.els)

    def visit_echo_stmt(self, statement: stmt.Echo) -> Any:
        self.resolve_node(statement.expression)

    def visit_return_stmt(self, statement: stmt.Return) -> Any:
        if self.current_function == FunctionType.NONE:
            parse_error(statement.keyword, "Can't return from top-level code.")
        if statement.value:
            if self.current_function == FunctionType.INITIALIZER:
                resolver_error(
                    statement.keyword, "Can't return a value from an initializer."
                )
            self.resolve_node(statement.value)

    def visit_var_stmt(self, statement: stmt.Var) -> Any:
        self.declare(statement.name)
        if statement.initializer is not None:
            self.resolve_node(statement.initializer)
        self.define(statement.name)
        self.unresolved.add(statement.name)

    def visit_while_stmt(self, statement: stmt.While) -> Any:
        self.resolve_node(statement.condition)
        self.resolve_node(statement.body)

    def visit_self_expr(self, expression: expr.Self):
        if self.current_class == ClassType.NONE:
            resolver_error(expression.keyword, "Can't use 'self' outside of a class.")
        self.resolve_local(expression, expression.keyword)

    def visit_get_expr(self, expression: expr.Get):
        self.resolve_node(expression.obj)

    def visit_set_expr(self, expression: expr.Set):
        self.resolve_node(expression.value)
        self.resolve_node(expression.obj)

    def visit_super_expr(self, expression: expr.Super):
        if self.current_class == ClassType.NONE:
            resolver_error(expression.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            resolver_error(
                expression.keyword, "Can't use 'super' in a class with no superclass"
            )
        self.resolve_local(expression, expression.keyword)

    def visit_prefix_expr(self, expression: expr.Prefix):
        self.resolve_node(expression.right)

    def visit_postfix_expr(self, expression: expr.Postfix):
        self.resolve_node(expression.left)

    def visit_binary_expr(self, expression: expr.Binary):
        self.resolve_node(expression.left)
        self.resolve_node(expression.right)

    def visit_call_expr(self, expression: expr.Call):
        self.resolve_node(expression.callee)
        for arg in expression.arguments:
            self.resolve_node(arg)

    def visit_ternary_expr(self, expression: expr.Ternary):
        self.resolve_node(expression.condition)
        self.resolve_node(expression.expression_true)
        self.resolve_node(expression.expression_false)

    def visit_grouping_expr(self, expression: expr.Grouping):
        self.resolve_node(expression.expression)

    def visit_literal_expr(self, expression: expr.Literal):
        _ = expression
        return

    def visit_logical_expr(self, expression: expr.Logical):
        self.resolve_node(expression.left)
        self.resolve_node(expression.right)

    def visit_unary_expr(self, expression: expr.Unary):
        self.resolve_node(expression.right)

    def visit_assign_expr(self, expression: expr.Assign) -> Any:
        self.resolve_node(expression.value)
        self.resolve_local(expression, expression.name)

    def visit_variable_expr(self, expression: expr.Variable) -> Any:
        if len(self.scopes) != 0 and self.peek().get(expression.name.symbol) is False:
            parse_error(
                expression.name, "Can't read local variable in its own initilizer."
            )
        self.resolve_local(expression, expression.name)

    def analyze(self, statements: list):
        self.resolve(statements)
        unused = self.unresolved - self.resolved
        if unused:
            for name in unused:
                resolver_error(name, f"Variable '{name.symbol}' was never used.")

    def resolve(self, statements: list):
        for statement in statements:
            self.resolve_node(statement)

    def resolve_node(self, node):
        node.accept(self)

    def resolve_local(self, expression: expr.Expr, name: Token):
        self.resolved.add(name)
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.symbol in self.scopes[i]:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - i)
                return

    def resolve_function(
        self, function: stmt.Function | expr.Anonym, _type: FunctionType
    ):
        enclosing_function = self.current_function
        self.current_function = _type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop(-1)

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return

        scope = self.peek()
        if name.symbol in scope:
            parse_error(name, "Already a variable with this name is this scope")
        scope[name.symbol] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.peek()
        scope[name.symbol] = True

    def peek(self):
        return self.scopes[-1]
