from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from values.tokens import Token
from values import expr


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


@dataclass
class Expression(Stmt):
    expression: expr.Expr

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


@dataclass
class _Class(Stmt):
    name: Token
    methods: list[Function]
    superclass: expr.Variable | None = None

    def accept(self, visitor):
        return visitor.visit_class_stmt(self)


@dataclass
class If(Stmt):
    condition: expr.Expr
    then: Stmt
    els: Stmt | None

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


@dataclass
class Echo(Stmt):
    expression: expr.Expr

    def accept(self, visitor):
        return visitor.visit_echo_stmt(self)


@dataclass
class Return(Stmt):
    keyword: Token
    value: expr.Expr | None

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: expr.Expr | None

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


@dataclass
class While(Stmt):
    condition: expr.Expr
    body: Stmt

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


class Visitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, statement: Block) -> Any:
        pass

    @abstractmethod
    def visit_class_stmt(self, statement: _Class) -> Any:
        pass

    @abstractmethod
    def visit_expression_stmt(self, statement: Expression) -> Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, statement: Function) -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, statement: If) -> Any:
        pass

    @abstractmethod
    def visit_echo_stmt(self, statement: Echo) -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, statement: Return) -> Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, statement: Var) -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, statement: While) -> Any:
        pass
