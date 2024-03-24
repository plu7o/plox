from typing import Any

from objects.callable import PloxCallable
from objects.klass import PloxClass, PloxInstance
from objects.function import PloxAnonymFunction, PloxFunction
from objects.returns import Returns

from values.tokens import Token, TokenType
from values import expr
from values import stmt

from environment import Env
from stdlib.plox_time import PloxTime, PloxPrint

from errors.exceptions import PloxRuntimeError
from errors.error import runtime_error


class Interpreter(expr.Visitor, stmt.Visitor):
    def __init__(self):
        self.globals = Env()
        self.env: Env = self.globals
        self.locals: dict[expr.Expr, int] = {}

        self.globals.define("time", PloxTime())
        self.globals.define("print", PloxPrint())

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except PloxRuntimeError as error:
            runtime_error(error)

    def evaluate(self, expression: expr.Expr):
        return expression.accept(self)

    def execute(self, statement: stmt.Stmt):
        statement.accept(self)

    def resolve(self, expression: expr.Expr, depth: int):
        self.locals[expression] = depth

    def execute_block(self, statements: list[stmt.Stmt], env: Env):
        previous: Env = self.env
        try:
            self.env = env

            for statement in statements:
                self.execute(statement)
        finally:
            self.env = previous

    def visit_block_stmt(self, statement: stmt.Block) -> Any:
        self.execute_block(statement.statements, Env(self.env))

    def visit_class_stmt(self, statement: stmt._Class) -> Any:
        superclass = None
        if statement.superclass:
            superclass = self.evaluate(statement.superclass)
            if not isinstance(superclass, PloxClass):
                raise RuntimeError(
                    statement.superclass.name, "superclass must be a class."
                )

        self.env.define(statement.name.symbol, None)

        if statement.superclass:
            self.env = Env(self.env)
            self.env.define("super", superclass)

        methods = {}
        for method in statement.methods:
            function = PloxFunction(method, self.env, method.name.symbol == "init")
            methods[method.name.symbol] = function
        klass = PloxClass(statement.name.symbol, methods, superclass)
        if superclass:
            self.env = self.env.enclosing

        self.env.assign(statement.name, klass)

    def visit_function_stmt(self, statement: stmt.Function) -> Any:
        function: PloxFunction = PloxFunction(statement, self.env, False)
        self.env.define(statement.name.symbol, function)

    def visit_if_stmt(self, statement: stmt.If) -> Any:
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then)
        elif statement.els is not None:
            self.execute(statement.els)

    def visit_var_stmt(self, statement: stmt.Var) -> Any:
        value = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)

        self.env.define(statement.name.symbol, value)

    def visit_return_stmt(self, statement: stmt.Return) -> Any:
        value = None
        if statement.value is not None:
            value = self.evaluate(statement.value)

        raise Returns(value)

    def visit_while_stmt(self, statement: stmt.While) -> Any:
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)

    def visit_expression_stmt(self, statement: stmt.Expression) -> Any:
        self.evaluate(statement.expression)

    def visit_echo_stmt(self, statement: stmt.Echo) -> Any:
        value = self.evaluate(statement.expression)
        print(self.stringify(value))

    def visit_super_expr(self, expression: expr.Super) -> Any:
        distance = self.locals[expression]
        superclass = self.env.get_at(distance, "super")
        obj = self.env.get_at(distance - 1, "self")
        method = superclass.find_method(expression.method.symbol)

        if method is None:
            raise RuntimeError(
                expression.method, f"undefined property '{expression.method.symbol}'."
            )
        return method.bind(obj)

    def visit_set_expr(self, expression: expr.Set) -> Any:
        obj = self.evaluate(expression.obj)

        if not isinstance(obj, PloxInstance):
            raise RuntimeError(expression.name, "Only instances have fields.")

        value = self.evaluate(expression.value)
        obj.set(expression.name, value)
        return value

    def visit_get_expr(self, expression: expr.Get) -> Any:
        obj = self.evaluate(expression.obj)
        if isinstance(obj, PloxInstance):
            return obj.get(expression.name)
        raise RuntimeError(expression.name, "Only instances have properties.")

    def visit_anonym_func_expr(self, expression: expr.Anonym) -> Any:
        function: PloxAnonymFunction = PloxAnonymFunction(expression, self.env)
        return function

    def visit_call_expr(self, expression: expr.Call) -> Any:
        callee = self.evaluate(expression.callee)

        arguments = []
        for arg in expression.arguments:
            arguments.append(self.evaluate(arg))

        if not isinstance(callee, PloxCallable):
            raise PloxRuntimeError(
                expression.paren, "Can only call functions and classes."
            )

        function: PloxCallable = callee
        if len(arguments) != function.arity():
            raise PloxRuntimeError(
                expression.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )

        return function.call(self, arguments)

    def visit_assign_expr(self, expression: expr.Assign) -> Any:
        value = self.evaluate(expression.value)
        distance = self.locals.get(expression)
        if distance is not None:
            self.env.assign_at(distance, expression.name, value)
        else:
            self.globals.assign(expression.name, value)

        return value

    def visit_ternary_expr(self, expression: expr.Ternary) -> Any:
        condition = self.evaluate(expression.condition)
        if self.is_truthy(condition):
            return self.evaluate(expression.expression_true)
        else:
            return self.evaluate(expression.expression_false)

    def visit_logical_expr(self, expression: expr.Logical) -> Any:
        left = self.evaluate(expression.left)

        if expression.operator._type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expression.right)

    def visit_binary_expr(self, expression: expr.Binary) -> Any:
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        match expression.operator._type:
            case TokenType.MINUS:
                self.check_number_operands(expression.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                raise PloxRuntimeError(
                    expression.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.SLASH:
                self.check_number_operands(expression.operator, left, right)
                if float(left) == 0 or float(right) == 0:
                    raise PloxRuntimeError(
                        expression.operator, "Trying to devide by Zero."
                    )
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expression.operator, left, right)
                return float(left) * float(right)
            case TokenType.MODULO:
                self.check_number_operands(expression.operator, left, right)
                return float(left) % float(right)
            case TokenType.GREATER:
                self.check_number_operands(expression.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expression.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.PLUS_ASSIGN:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to assign to a literal value"
                    )
                self.check_number_operands(expression.operator, left, right)
                self.env.assign(expression.left.name, left + right)
                return left + right
            case TokenType.MINUS_ASSIGN:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to assign to a literal value"
                    )
                self.check_number_operands(expression.operator, left, right)
                self.env.assign(expression.left.name, left - right)
                return left - right
            case TokenType.STAR_ASSIGN:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to assign to a literal value"
                    )
                self.check_number_operands(expression.operator, left, right)
                self.env.assign(expression.left.name, left * right)
                return left * right
            case TokenType.SLASH_ASSIGN:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to assign to a literal value"
                    )
                self.check_number_operands(expression.operator, left, right)
                if float(left) == 0 or float(right) == 0:
                    raise PloxRuntimeError(
                        expression.operator, "Trying to devide by Zero."
                    )
                self.env.assign(expression.left.name, left / right)
                return left / right

    def visit_unary_expr(self, expression: expr.Unary) -> Any:
        # Evaluate operand expression
        right = self.evaluate(expression.right)

        # Apply unary operator
        match expression.operator._type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expression.operator, right)
                return -float(right)

    def visit_prefix_expr(self, expression: expr.Prefix) -> Any:
        right = self.evaluate(expression.right)

        match expression.operator._type:
            case TokenType.MINUS_MINUS:
                if not isinstance(expression.right, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to decrement a literal value"
                    )
                self.check_number_operand(expression.operator, right)
                self.env.assign(expression.right.name, right - 1)
                return float(right - 1)
            case TokenType.PLUS_PLUS:
                if not isinstance(expression.right, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to increment a literal value"
                    )
                self.check_number_operand(expression.operator, right)
                self.env.assign(expression.right.name, right + 1)
                return float(right + 1)

    def visit_postfix_expr(self, expression: expr.Postfix) -> Any:
        left = self.evaluate(expression.left)

        match expression.operator._type:
            case TokenType.MINUS_MINUS:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to decrement a literal value"
                    )
                self.check_number_operand(expression.operator, left)
                self.env.assign(expression.left.name, left - 1)
                return float(left)
            case TokenType.PLUS_PLUS:
                if not isinstance(expression.left, expr.Variable):
                    raise PloxRuntimeError(
                        expression.operator, "attempting to increment a literal value"
                    )
                self.check_number_operand(expression.operator, left)
                self.env.assign(expression.left.name, left + 1)
                return float(left)

    def visit_grouping_expr(self, expression: expr.Grouping) -> Any:
        return self.evaluate(expression.expression)

    def visit_variable_expr(self, expression: expr.Variable) -> Any:
        a = self.look_up_variable(expression.name, expression)
        return a

    def visit_self_expr(self, expression: expr.Self) -> Any:
        return self.look_up_variable(expression.keyword, expression)

    def visit_literal_expr(self, expression: expr.Literal) -> Any:
        return expression.value

    def look_up_variable(self, name: Token, expression: expr.Expr):
        distance = self.locals.get(expression)
        if distance is not None:
            return self.env.get_at(distance, name.symbol)
        else:
            return self.globals.get(name)

    def check_number_operand(self, operator: Token, operand):
        if isinstance(operand, float):
            return
        raise PloxRuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: Token, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise PloxRuntimeError(operator, "Operands must be numbers")

    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return bool(obj)
        return True

    def is_equal(self, a, b) -> bool:
        return a == b

    def stringify(self, obj):
        if obj is None:
            return "none"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[0 : len(text) - 2]
            return text

        return str(obj)
