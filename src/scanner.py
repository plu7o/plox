from values.tokens import Position, Token, TokenType

from errors.error import scanner_error


class Scanner:

    def __init__(self, source: str):
        self.source: str = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.line_start = 0
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fn": TokenType.FN,
            "if": TokenType.IF,
            "none": TokenType.NONE,
            "or": TokenType.OR,
            "echo": TokenType.ECHO,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "self": TokenType.SELF,
            "true": TokenType.TRUE,
            "let": TokenType.LET,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(
            Token(
                TokenType.EOF,
                "",
                None,
                Position(self.line, self.line_start, self.current, self.current),
                0,
            )
        )
        return self.tokens

    def scan_token(self):
        c: str = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "?":
                self.add_token(TokenType.QUESTION_MARK)
            case "%":
                self.add_token(TokenType.MODULO)
            case "*":
                self.add_token(
                    TokenType.STAR_ASSIGN if self.match("=") else TokenType.STAR
                )
            case "+":
                if self.match("+"):
                    self.add_token(TokenType.PLUS_PLUS)
                elif self.match("="):
                    self.add_token(TokenType.PLUS_ASSIGN)
                else:
                    self.add_token(TokenType.PLUS)
            case "-":
                if self.match("-"):
                    self.add_token(TokenType.MINUS_MINUS)
                elif self.match("="):
                    self.add_token(TokenType.MINUS_ASSIGN)
                elif self.match(">"):
                    self.add_token(TokenType.RIGHT_ARROW)
                else:
                    self.add_token(TokenType.MINUS)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                if self.match("="):
                    self.add_token(TokenType.LESS_EQUAL)
                elif self.match("<"):
                    self.add_token(TokenType.LEFT_SHIFT)
                elif self.match("-"):
                    self.add_token(TokenType.LEFT_ARROW)
                else:
                    self.add_token(TokenType.LESS)
            case ">":
                if self.match("="):
                    self.add_token(TokenType.GREATER_EQUAL)
                elif self.match(">"):
                    self.add_token(TokenType.RIGHT_SHIFT)
                else:
                    self.add_token(TokenType.GREATER)
            case ":":
                self.add_token(
                    TokenType.DOUBLE_COLON if self.match(":") else TokenType.COLON
                )
            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                elif self.match("*"):
                    while (
                        not self.match("*")
                        and self.peek() != "/"
                        and not self.is_at_end()
                    ):
                        if self.peek() == "\n":
                            self.line += 1
                            self.line_start = self.current
                        self.advance()
                    self.advance()
                elif self.match("="):
                    self.add_token(TokenType.SLASH_ASSIGN)
                else:
                    self.add_token(TokenType.SLASH)
            case "\r" | "\t" | " ":
                ...
            case "\n":
                self.line += 1
                self.line_start = self.current
            case "'":
                self.string()
            case '"':
                self.multiline_string()
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    scanner_error(
                        self.line,
                        (self.line, self.line_start, self.start, self.current),
                        f"Unexpected character: '{c}'",
                    )

    def get_position(self):
        code: str = self.source[self.line_start : self.current].strip("\n")
        column = self.current - self.line_start
        text = self.source[self.start : self.current]
        return code, self.line, column, len(text)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text: str = self.source[self.start : self.current]
        _type: TokenType | None = self.keywords.get(text)
        if _type is None:
            _type = TokenType.IDENTIFIER
        self.add_token(_type)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def string(self):
        while self.peek() != "'" and not self.is_at_end():
            if self.peek() == "\n" or self.peek() == ";":
                # Error if string is not terminated before end of line
                scanner_error(
                    self.line,
                    (self.line, self.line_start, self.start, self.current),
                    "Unterminated string. Missing ' at end.",
                )
                return
            self.advance()

        if self.is_at_end():
            # Error if string is not terminated before end of file
            scanner_error(
                self.line,
                (self.line, self.line_start, self.start, self.current),
                "String never terminated. Missing ' at end.",
            )
            return

        self.advance()

        value: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def multiline_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
                self.line_start = self.current
            self.advance()

        if self.is_at_end():
            # Error if string is not terminated before end of file
            scanner_error(
                self.line,
                (self.line, self.line_start, self.start, self.current),
                'Unterminated multiline string. Missing " at end.',
            )
            return

        self.advance()

        value: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_alpha(self, char: str) -> bool:
        # return char >= 'a' and char <= 'z' or char >= 'A' and char <= 'Z' or char == '_'
        return char.isalpha()

    def is_alpha_numeric(self, char: str) -> bool:
        # return self.is_alpha(char) or self.is_digit(char)
        return char.isalnum()

    def is_digit(self, char: str) -> bool:
        # return char >= '0' and char <= '9'
        return char.isdigit()

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        next = self.current
        self.current += 1
        return self.source[next]

    def add_token(self, _type: TokenType, literal: object = None):
        text: str = self.source[self.start : self.current]
        column = self.current - self.line_start
        self.tokens.append(
            Token(
                _type,
                text,
                literal,
                Position(
                    line=self.line,
                    line_start=self.line_start,
                    offset=self.current,
                    column=column,
                ),
                len(text),
            )
        )
