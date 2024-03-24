from dataclasses import dataclass
from enum import Enum, auto
from collections import namedtuple


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    QUESTION_MARK = auto()
    MODULO = auto()

    # One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    PLUS = auto()
    PLUS_PLUS = auto()
    PLUS_ASSIGN = auto()
    MINUS = auto()
    MINUS_MINUS = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()
    LEFT_ARROW = auto()
    RIGHT_ARROW = auto()
    DOUBLE_COLON = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FN = auto()
    FOR = auto()
    IF = auto()
    NONE = auto()
    OR = auto()
    ECHO = auto()
    RETURN = auto()
    SUPER = auto()
    SELF = auto()
    TRUE = auto()
    LET = auto()
    WHILE = auto()

    EOF = auto()


Position = namedtuple("Position", ["line", "line_start", "offset", "column"])


@dataclass
class Token:
    _type: TokenType
    symbol: str
    literal: object
    position: Position
    length: int

    def __str__(self) -> str:
        return rf"[{self._type: <23} | {self.symbol: ^5}]"

    def __eq__(self, __value) -> bool:
        return (
            isinstance(__value, Token)
            and self._type == __value._type
            and self.symbol == self.symbol
        )

    def __repr__(self) -> str:
        return rf"[{self._type: <23} | {self.symbol: ^5} | {str(self.literal): ^5} | {self.position.line}:{self.position.column} ]"

    def __hash__(self) -> int:
        return hash(str(self))
