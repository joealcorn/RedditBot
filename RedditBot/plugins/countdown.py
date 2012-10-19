# -*- coding: utf-8 -*-
from RedditBot import bot

import ast
from ast import parse, NodeVisitor
from fractions import Fraction
from decimal import Decimal
from time import time
import random
import re
import os

current_game = None


class CountdownException(Exception):
    value = None

    def __init__(self, value):
        super(Exception, self).__init__()
        self.value = value

    def __str__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.value)


class IllegalNumber(CountdownException):
    pass


class IllegalOperation(CountdownException):
    def __str__(self):
        return 'IllegalOperation({0})'.format(self.value.__class__.__name__)


class IllegalNode(CountdownException):
    pass


class ResolveExpr(NodeVisitor):
    allowed_numbers = None

    def __init__(self, allowed_numbers=None):
        super(ResolveExpr, self).__init__()
        if allowed_numbers != None:
            self.allowed_numbers = [Fraction(n) for n in allowed_numbers]

    def use_number(self, n):
        if self.allowed_numbers != None:
            if n not in self.allowed_numbers:
                raise IllegalNumber(n)
            self.allowed_numbers.remove(n)
        return n

    def visit_Num(self, node):
        return self.use_number(Fraction(node.n))

    def visit_Add(self, node):
        return lambda x, y: x + y

    def visit_Sub(self, node):
        return lambda x, y: x - y

    def visit_Mult(self, node):
        return lambda x, y: x * y

    def visit_Div(self, node):
        return lambda x, y: x / y

    def visit_BinOp(self, node):
        return self.visit(node.op)(self.visit(node.left), self.visit(node.right))

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def generic_visit(self, node):
        if isinstance(node, ast.operator):
            raise IllegalOperation(node)
        else:
            raise IllegalNode(node)


def test_expr(expr, numbers=None):
    if not isinstance(expr, ast.AST):
        expr = parse(expr)
    return ResolveExpr(numbers).visit(expr)


def get_number(big=False):
    random.seed(os.urandom(1024))
    nums = ([25, 50, 75, 100] if big else range(1, 10))
    return random.choice(nums)


def exact_or_approx(f):
    if f.denominator <= 10000:
        return str(f)
    else:
        return '~' + str(f.limit_denominator())


def as_decimal(n):
    return Decimal(n.numerator) / Decimal(n.denominator)


# not really what this module is for, but we may as well include it
@bot.command('calculate')
def calc(context, make_decimal=False):
    '''.calculate <expression>'''
    if not context.args:
        return calc.__doc__
    node = parse(context.args)
    try:
        result = test_expr(node)
        if make_decimal and Fraction(as_decimal(result)) == result:
            result = as_decimal(result).normalize()
    except IllegalOperation as e:
        result = 'Sorry, operator \'{op}\' is not supported.'.format(op=e.value.__class__.__name__)
    except IllegalNode as e:
        result = 'Expression contains unrecognized syntax ({op})'.format(op=e.value.__class__.__name__)
    except Exception as e:
        result = str(e)
    return '{user}: {result}'.format(result=result, **context.line)


@bot.command('decimal')
def decimal(context):
    '''.decimal <expression>'''
    if not context.args:
        return decimal.__doc__
    return calc(context, make_decimal=True)


@bot.command('countdown')
def new_countdown(context):
    if context.line['sender'].lower() not in bot.config['COUNTDOWN_CHANNELS']:
        return '{0} not in countdown channel whitelist: [{1}]'.format(context.line['sender'],
                ','.join(bot.config['COUNTDOWN_CHANNELS']))
    global current_game
    if current_game and time() - current_game[2] < 30:
        return u'{user}: Please wait before starting a new round.'.format(**context.line)
    big = 2
    small = 6 - big
    use_nums = [get_number(big=True) for x in range(big)] + [get_number() for x in range(small)]
    random.seed(os.urandom(1024))
    target = Fraction(random.randint(100, 999))
    current_game = (target, use_nums, time())
    return u'Target: \x02{target}\x02. Use {numbers} and operators +, -, *, /.'.format(target=target, numbers=', '.join(map(str, use_nums)))


@bot.regex(re.compile('^[^A-Za-z]*$'))
def guess_countdown(context):
    if context.line['sender'].lower() not in bot.config['COUNTDOWN_CHANNELS']:
        return
    global current_game
    if not current_game:
        return
    print context.line.items()
    expr = context.line['regex_search'].group(0)
    try:
        print '[' + expr + ']'
        result = test_expr(expr, current_game[1])
        if result == current_game[0]:
            current_game = None
            return u'{user} wins this round.'.format(**context.line)
        elif result.denominator != 1:
            return u'{user}: {result} is not integral, try again.'.format(result=exact_or_approx(result), **context.line)
        elif abs(current_game[0] - result) <= 5:
            return u'{user} came close with {result}.'.format(result=exact_or_approx(result), **context.line)
        else:
            return u'{user}: {result} is not close to the target {target}, try again.'.format(result=exact_or_approx(result), target=current_game[0], **context.line)
    except IllegalNumber as e:
        number = e.value
        if number in current_game[1]:
            return u'{user}: Number {n} used too many times.'.format(n=number, **context.line)
        else:
            return u'{user}: Number {n} is not allowed, please find a solution using the numbers {numbers}'.format(numbers=', '.join(map(str, current_game[1])), n=number, **context.line)
    except IllegalOperation:
        return u'{user}: Only operations +, -, * and / are permitted.'.format(**context.line)
    except Exception as e:
        return

if __name__ == '__main__':
    print [str(test_expr(e)) for e in ['1 + (2 / 4)', '1 - 2', '1 * 2', '1 / 2', '3 + 4']]
