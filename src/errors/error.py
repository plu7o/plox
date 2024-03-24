import os
from values.tokens import Token

from errors.exceptions import PloxRuntimeError

had_error = False
had_runtime_error = False
source_code = ""


def scanner_error(line: int, where: tuple, message: str):
    global had_error
    report("SYNTAX_ERROR", line, get_position(*where), message)
    had_error = True


def parse_error(token: Token, message: str):
    global had_error
    report("ERROR", token.position.line, get_token_position(token), message)
    had_error = True


def resolver_error(token: Token, message: str):
    global had_error
    report("WARNING", token.position.line, get_token_position(token), message)


def runtime_error(error: PloxRuntimeError):
    global had_runtime_error
    report(
        "RUNTIME_ERROR",
        error.token.position.line,
        get_token_position(error.token),
        error.message,
    )
    had_runtime_error = True


def report(error_type: str, line: int, where: tuple, message: str):
    global had_error
    code, line, column, length = where
    cursor = f'{"^" * length}' if length > 1 else "^"
    location = f"[line {line}:{column}]"
    term_size = os.get_terminal_size().columns
    print(f'{"-" * term_size}')
    print(f"{location} {error_type}: {message}")
    print(
        f'{line:>{len(location) + 2}} | {code}\n{" " * ((column - length) + len(location) + 5)}{cursor}'
    )
    print(f'{"-" * term_size}')


def get_token_position(token: Token):
    code = [line for line in source_code.split("\n")][token.position.line - 1]
    return code, token.position.line, token.position.column, token.length


def get_position(line, line_start, start, current):
    code = [line for line in source_code.split("\n")][line - 1]
    column = current - line_start
    text = source_code[start:current]
    return code, line, column, len(text)
