from abc import ABC, abstractmethod
from typing import Any


class PloxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list) -> Any:
        pass

    @abstractmethod
    def arity(self) -> Any:
        pass
