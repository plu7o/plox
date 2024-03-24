from objects.callable import PloxCallable
import time


class PloxTime(PloxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, arguments: list):
        return time.time()

    def __str__(self) -> str:
        return "<Native Fn>"

    def __repr__(self) -> str:
        return "<Native Fn>"


class PloxPrint(PloxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, arguments: list):
        return print(*arguments)

    def __str__(self) -> str:
        return "<Native Fn>"

    def __repr__(self) -> str:
        return "<Native Fn>"
