from objects.callable import PloxCallable
from values.tokens import Token


class PloxClass(PloxCallable):
    def __init__(self, name: str, methods: dict, superclass) -> None:
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def __repr__(self) -> str:
        return f"<PloxClass {self.name}>"

    def call(self, interpreter, arguments: list):
        instance = PloxInstance(self)

        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None


class PloxInstance:
    def __init__(self, klass: PloxClass) -> None:
        self.klass = klass
        self.fields = dict()

    def __repr__(self) -> str:
        return f"[{self.klass} instance]"

    def get(self, name: Token):
        if name.symbol in self.fields:
            return self.fields[name.symbol]
        method = self.klass.find_method(name.symbol)
        if method:
            return method.bind(self)

        raise RuntimeError(name, f"undefined property '{name.symbol}'.")

    def set(self, name: Token, value):
        self.fields[name.symbol] = value
