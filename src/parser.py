from values.tokens import Token, TokenType
from values import expr
from values import stmt

from errors.exceptions import ParseError
from errors.error import parse_error


class Parser:

    def __init__(self, tokens: list[Token], source: str):
        self.tokens = tokens
        self.source = source
        self.current: int = 0

    def parse(self) -> list[stmt.Stmt | None]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self) -> stmt.Stmt | None:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FN):
                return self.function("function")
            if self.match(TokenType.LET):
                return self.var_declaration()

            return self.statement()
        except ParseError:
            self.sync()
            return None

    def class_declaration(self) -> stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        super_class = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            super_class = expr.Variable(self.previous())
            self.consume(TokenType.GREATER, "Expect '>' after superclass.")

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return stmt._Class(name, methods, super_class)

    def var_declaration(self) -> stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.ECHO):
            return self.echo()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())

        return self.expression_statement()

    def for_statement(self):
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.LET):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        body: stmt.Stmt = self.statement()

        if increment is not None:
            body = stmt.Block([body, stmt.Expression(increment)])

        if condition is None:
            condition = expr.Literal(True)

        body = stmt.While(condition, body)

        if initializer is not None:
            body = stmt.Block([initializer, body])

        return body

    def if_statement(self) -> stmt.Stmt:
        condition: expr.Expr = self.expression()

        self.consume(TokenType.COLON, "Expected ':' after condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return stmt.If(condition, then_branch, else_branch)

    def echo(self) -> stmt.Stmt:
        value: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return stmt.Echo(value)

    def return_statement(self) -> stmt.Stmt:
        keyword: Token = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return stmt.Return(keyword, value)

    def while_statement(self):
        condition: expr.Expr = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after condition.")
        body: stmt.Stmt = self.statement()
        return stmt.While(condition, body)

    def expression_statement(self) -> stmt.Stmt:
        expression: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return stmt.Expression(expression)

    def function(self, kind: str) -> stmt.Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name.")

        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    parse_error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expected parameter name")
                )

                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, "Expected '{' before" + kind + "body")
        body: list[stmt.Stmt] = self.block()

        return stmt.Function(name, parameters, body)

    def block(self) -> list[stmt.Stmt]:
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def expression(self) -> expr.Expr:
        return self.assignment()

    def assignment(self) -> expr.Expr:
        expression: expr.Expr = self.ternary()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: expr.Expr = self.assignment()

            if isinstance(expression, expr.Variable):
                name: Token = expression.name
                return expr.Assign(name, value)
            elif isinstance(expression, expr.Get):
                return expr.Set(expression.obj, expression.name, value)

            parse_error(equals, "Invalid assignment target.")

        return expression

    def ternary(self) -> expr.Expr:
        expression: expr.Expr = self._or()

        while self.match(TokenType.QUESTION_MARK):
            if_operator: Token = self.previous()
            expression_true: expr.Expr = self.ternary()
            self.consume(
                TokenType.COLON,
                "Expected ':' after ? in ternary expression (condition ? true: false).",
            )
            or_operator: Token = self.previous()
            expression_false: expr.Expr = self.ternary()
            expression = expr.Ternary(
                expression, if_operator, expression_true, or_operator, expression_false
            )

        return expression

    def _or(self) -> expr.Expr:
        expression: expr.Expr = self._and()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: expr.Expr = self._and()
            expression = expr.Logical(expression, operator, right)

        return expression

    def _and(self) -> expr.Expr:
        expression: expr.Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: expr.Expr = self.equality()
            expression = expr.Logical(expression, operator, right)

        return expression

    def equality(self) -> expr.Expr:
        expression: expr.Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: expr.Expr = self.comparison()
            expression = expr.Binary(expression, operator, right)

        return expression

    def comparison(self) -> expr.Expr:
        expression: expr.Expr = self.assign_operators()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: expr.Expr = self.assign_operators()
            expression = expr.Binary(expression, operator, right)

        return expression

    def assign_operators(self):
        expression: expr.Expr = self.term()

        while self.match(
            TokenType.PLUS_ASSIGN,
            TokenType.MINUS_ASSIGN,
            TokenType.STAR_ASSIGN,
            TokenType.SLASH_ASSIGN,
        ):
            operator: Token = self.previous()
            right: expr.Expr = self.term()
            expression = expr.Binary(expression, operator, right)

        return expression

    def term(self) -> expr.Expr:
        expression: expr.Expr = self.modulo()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: expr.Expr = self.modulo()
            expression = expr.Binary(expression, operator, right)

        return expression

    def modulo(self) -> expr.Expr:
        expression: expr.Expr = self.factor()

        while self.match(TokenType.MODULO):
            operator: Token = self.previous()
            right: expr.Expr = self.factor()
            expression = expr.Binary(expression, operator, right)

        return expression

    def factor(self) -> expr.Expr:
        expression: expr.Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            expression = expr.Binary(expression, operator, right)

        return expression

    def unary(self) -> expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            return expr.Unary(operator, right)

        return self.increment()

    def increment(self) -> expr.Expr:
        if self.match(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            operator: Token = self.previous()
            right: expr.Expr = self.increment()
            return expr.Prefix(operator, right)

        expression: expr.Expr = self.call()
        if self.match(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            operator: Token = self.previous()
            expression = expr.Postfix(expression, operator)

        return expression

    def call(self):
        expression: expr.Expr = self.anonym()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'"
                )
                expression = expr.Get(expression, name)
            else:
                break

        return expression

    def finish_call(self, callee: expr.Expr) -> expr.Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    parse_error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")
        return expr.Call(callee, paren, arguments)

    def anonym(self):
        if not self.match(TokenType.FN):
            return self.primary()

        kind = "anonymous"
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    parse_error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expected parameter name")
                )

                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before" + kind + "body")
        body: list[stmt.Stmt] = self.block()

        expression = expr.Anonym(parameters, body)
        return expression

    def primary(self) -> expr.Expr:
        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        if self.match(TokenType.TRUE):
            return expr.Literal(True)
        if self.match(TokenType.NONE):
            return expr.Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOUBLE_COLON, "Expect '::' after 'super'")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name")
            return expr.Super(keyword, method)
        if self.match(TokenType.SELF):
            return expr.Self(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression: expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return expr.Grouping(expression)

        token = self.peek() if self.peek()._type != TokenType.EOF else self.previous()
        raise self.error(token, "Expected expression.")

    def match(self, *types: TokenType) -> bool:
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        return False

    def consume(self, _type: TokenType, message: str):
        if self.check(_type):
            return self.advance()

        raise self.error(self.previous(), message)

    def check(self, _type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek()._type == _type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek()._type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str):
        parse_error(token, message)
        return ParseError

    def sync(self):
        self.advance()

        while not self.is_at_end():
            if self.previous()._type == TokenType.SEMICOLON:
                return

            match self.peek()._type:
                case TokenType.CLASS:
                    return
                case TokenType.FN:
                    return
                case TokenType.LET:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.ECHO:
                    return
                case TokenType.RETURN:
                    return
                case TokenType.CLASS:
                    return

            self.advance()
