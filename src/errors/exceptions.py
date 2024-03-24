from values.tokens import Token


class ParseError(Exception):
    pass


class PloxRuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        self.message = message
        self.token = token
