from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from values.tokens import Token


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor) -> Any:
        pass

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor):
        return visitor.visit_super_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Set(Expr):
    obj: Expr
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_set_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Get(Expr):
    obj: Expr
    name: Token

    def accept(self, visitor):
        return visitor.visit_get_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor):
        return visitor.visit_call_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Ternary(Expr):
    condition: Expr
    if_operator: Token
    expression_true: Expr
    or_operator: Token
    expression_false: Expr

    def accept(self, visitor):
        return visitor.visit_ternary_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Prefix(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_prefix_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Postfix(Expr):
    left: Expr
    operator: Token

    def accept(self, visitor):
        return visitor.visit_postfix_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Self(Expr):
    keyword: Token

    def accept(self, visitor):
        return visitor.visit_self_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Anonym(Expr):
    params: list[Token]
    body: list

    def accept(self, visitor):
        return visitor.visit_anonym_func_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

    def __hash__(self) -> int:
        return hash((str(self)))


class Visitor(ABC):
    @abstractmethod
    def visit_literal_expr(self, expression: Literal) -> Any:
        pass

    @abstractmethod
    def visit_self_expr(self, expression: Self) -> Any:
        pass

    @abstractmethod
    def visit_variable_expr(self, expression: Variable) -> Any:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expression: Grouping) -> Any:
        pass

    @abstractmethod
    def visit_prefix_expr(self, expression: Prefix) -> Any:
        pass

    @abstractmethod
    def visit_postfix_expr(self, expression: Postfix) -> Any:
        pass

    @abstractmethod
    def visit_unary_expr(self, expression: Unary) -> Any:
        pass

    @abstractmethod
    def visit_binary_expr(self, expression: Binary) -> Any:
        pass

    @abstractmethod
    def visit_logical_expr(self, expression: Logical) -> Any:
        pass

    @abstractmethod
    def visit_ternary_expr(self, expression: Ternary) -> Any:
        pass

    @abstractmethod
    def visit_assign_expr(self, expression: Assign) -> Any:
        pass

    @abstractmethod
    def visit_call_expr(self, expression: Call) -> Any:
        pass

    @abstractmethod
    def visit_anonym_func_expr(self, expression: Anonym) -> Any:
        pass

    @abstractmethod
    def visit_get_expr(self, expression: Get) -> Any:
        pass

    @abstractmethod
    def visit_set_expr(self, expression: Set) -> Any:
        pass

    @abstractmethod
    def visit_super_expr(self, expression: Super) -> Any:
        pass
