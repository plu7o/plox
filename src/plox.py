import sys
import pprint

from interpreter import Interpreter
from resolver import Resolver
from scanner import Scanner
from parser import Parser

from errors import error

DEBUG = False
interpreter = Interpreter()


class Plox:
    def run_file(self, file_path: str):
        global source_code
        with open(file_path, "r") as f:
            source = f.read()
        error.source_code = source
        self.run(source)

        if error.had_error:
            exit(65)

        if error.had_runtime_error:
            exit(70)

    def run_prompt(self):
        while True:
            line = input("plox_v0.1 $> ")
            if line == "exit":
                break
            self.run(line)
            error.had_error = False

    def run(self, source: str):
        scanner: Scanner = Scanner(source)
        tokens: list = scanner.scan_tokens()
        if DEBUG:
            print(f'\n{"-" * 20} TOKENS {"-" * 20}\n')
            self.print_tokens(tokens)

        if error.had_error:
            return

        parser: Parser = Parser(tokens, source)
        statements = parser.parse()

        if DEBUG:
            print(f'\n{"-" * 20} AST {"-" * 20}\n')
            self.print_statements(statements)

        if error.had_error:
            return

        resolver: Resolver = Resolver(interpreter)
        resolver.analyze(statements)

        if error.had_error:
            return

        if DEBUG:
            print(f'\n{"-" * 20} PROGRAM OUTPUT {"-" * 20}\n')

        interpreter.interpret(statements)

    def print_tokens(self, tokens):
        for token in tokens:
            print(token)

    def print_statements(self, statements):
        for statement in statements:
            pprint.pprint(statement, indent=4, compact=True)


def main():
    plox = Plox()

    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: plox [script]")
    elif len(args) != 0:
        plox.run_file(args[0])
    else:
        plox.run_prompt()


if __name__ == "__main__":
    main()
