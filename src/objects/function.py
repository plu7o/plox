from typing import Any

from objects.callable import PloxCallable
from objects.klass import PloxInstance
from objects.returns import Returns

from values import stmt
from values import expr

from environment import Env


class PloxFunction(PloxCallable):
    def __init__(
        self, declaration: stmt.Function, closure: Env, is_initializer: bool
    ) -> None:
        self.delcaration = declaration
        self.closure: Env = closure
        self.is_initializer = is_initializer

    def arity(self) -> Any:
        return len(self.delcaration.params)

    def call(self, interpreter, arguments: list):
        env: Env = Env(self.closure)
        for i in range(len(self.delcaration.params)):
            env.define(self.delcaration.params[i].symbol, arguments[i])
        try:
            interpreter.execute_block(self.delcaration.body, env)
        except Returns as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "self")
            return return_value.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

    def bind(self, instance: PloxInstance):
        env = Env(self.closure)
        env.define("self", instance)
        return PloxFunction(self.delcaration, env, self.is_initializer)

    def __str__(self) -> str:
        return f"<fn {self.delcaration.name.symbol}>"

    def __repr__(self) -> str:
        return f"<fn {self.delcaration.name.symbol}>"


class PloxAnonymFunction(PloxCallable):
    def __init__(self, expression: expr.Anonym, closure: Env) -> None:
        self.delcaration = expression
        self.closure: Env = closure

    def arity(self) -> Any:
        return len(self.delcaration.params)

    def call(self, interpreter, arguments: list):
        env: Env = Env(self.closure)
        for i in range(len(self.delcaration.params)):
            env.define(self.delcaration.params[i].symbol, arguments[i])
        try:
            interpreter.execute_block(self.delcaration.body, env)
        except Returns as return_value:
            return return_value.value

        return None

    def __str__(self) -> str:
        return "<fn Anonymous>"

    def __repr__(self) -> str:
        return "<fn Anonymous>"
