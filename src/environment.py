from typing import Any

from values.tokens import Token

from errors.exceptions import PloxRuntimeError


class Env:
    def __init__(self, enclosing=None):
        self.values: dict[str, Any] = {}
        self.enclosing = enclosing

    def get(self, name: Token):
        if name.symbol in self.values:
            return self.values.get(name.symbol)

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise PloxRuntimeError(name, f"Undefined variable '{name.symbol}'.")

    def assign(self, name: Token, value):
        if name.symbol in self.values:
            self.values[name.symbol] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise PloxRuntimeError(name, f"Undefined variable '{name.symbol}'.")

    def define(self, name: str, value):
        self.values[name] = value

    def ancestor(self, distance: int):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.symbol] = value
