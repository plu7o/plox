from values import expr


class AstPrinter(expr.Visitor):
    def visit_super_expr(self, expression: expr.Super):
        ...

    def visit_set_expr(self, expression: expr.Set):
        ...

    def visit_get_expr(self, expression: expr.Get):
        ...

    def visit_call_expr(self, expression: expr.Call):
        ...

    def visit_assign_expr(self, expression: expr.Assign):
        ...

    def visit_ternary_expr(self, expression: expr.Ternary):
        return self.parenthesize("ternary", expression.condition, expression.expression_true, expression.expression_false)

    def visit_logical_expr(self, expression: expr.Logical):
        ...

    def visit_binary_expr(self, expression: expr.Binary):
        return self.parenthesize(expression.operator.symbol, expression.left, expression.right)

    def visit_unary_expr(self, expression: expr.Unary):
        return self.parenthesize(expression.operator.symbol, expression.right)

    def visit_postfix_expr(self, expression: expr.Postfix):
        return self.parenthesize('postfix ' + expression.operator.symbol, expression.left)

    def visit_prefix_expr(self, expression: expr.Prefix):
        return self.parenthesize('prefix ' + expression.operator.symbol, expression.right)

    def visit_grouping_expr(self, expression: expr.Grouping):
        return self.parenthesize("group", expression.expression)

    def visit_variable_expr(self, expression: expr.Variable):
        ...

    def visit_self_expr(self, expression: expr.Self):
        ...

    def visit_literal_expr(self, expression: expr.Literal):
        if not expression.value:
            return "none"
        return str(expression.value)

    def print_ast(self, expression: expr.Expr):
        return expression.accept(self)

    def parenthesize(self, name: str, *exprs: expr.Expr):
        message = f'({name}{''.join([f' {expr.accept(self)}' for expr in exprs])} )'
        return message
