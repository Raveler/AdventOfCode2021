from itertools import groupby, repeat
import re
import math
import pprint
import functools

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


class State:

    def __init__(self, input):
        self.data = {}
        self.data['x'] = 0
        self.data['y'] = 0
        self.data['z'] = 0
        self.data['w'] = 0
        self.input = input

    def get_value(self, arg):
        if arg in self.data:
            return self.data[arg]
        else:
            return int(arg)

    def execute(self, op, arg1, arg2):

        if op == 'inp':
            value = self.input.pop(0)
            self.data[arg1] = value

        elif op == 'add':
            self.data[arg1] += self.get_value(arg2)

        elif op == 'mul':
            self.data[arg1] *= self.get_value(arg2)

        elif op == 'div':
            arg2 = self.get_value(arg2)
            if arg2 == 0:
                return False
            self.data[arg1] //= arg2

        elif op == 'mod':
            arg2 = self.get_value(arg2)
            if self.data[arg1] < 0 or arg2 <= 0:
                return False
            self.data[arg1] %= arg2

        elif op == 'eql':
            self.data[arg1] = 1 if self.data[arg1] == self.get_value(arg2) else 0

        else:
            raise "Not supported"

        return True

class Expression:

    var_names = ['x', 'y', 'z', 'w']

    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

        if self.arg1 not in Expression.var_names:
            self.arg1 = int(self.arg1)
        if self.arg2 not in Expression.var_names:
            self.arg2 = int(self.arg2)

    def reduce(self, data):

        if self.arg1 in data:
            self.arg1 = data[self.arg1]
            if isinstance(self.arg1, Expression):

        if self.arg2 in data:
            self.arg2 = data[self.arg2]

        if self.arg1 == '?' or self.arg2 == '?':
            return self

        op = self.op
        if op == 'add':
            return self.arg1 + self.arg2

        elif op == 'mul':
            self.data[arg1] *= self.get_value(arg2)

        elif op == 'div':
            arg2 = self.get_value(arg2)
            if arg2 == 0:
                return False
            self.data[arg1] //= arg2

        elif op == 'mod':
            arg2 = self.get_value(arg2)
            if self.data[arg1] < 0 or arg2 <= 0:
                return False
            self.data[arg1] %= arg2

        elif op == 'eql':
            self.data[arg1] = 1 if self.data[arg1] == self.get_value(arg2) else 0

        else:
            raise "Not supported"


    def replace(self, expression):
        if self.arg1 == expression.target:
            self.arg1 = Expression(expression.op, expression.arg1, expression.arg2)
        elif isinstance(self.arg1, Expression):
            self.arg1.replace(expression)
            self.arg1 = self.arg1.reduce()

        if self.arg2 == expression.target:
            self.arg2 = Expression(expression.op, expression.arg1, expression.arg2)
        elif isinstance(self.arg2, Expression):
            self.arg2.replace(expression)
            self.arg2 = self.arg2.reduce()

    def reduce(self):
        op = self.op

        # reduce the children
        if isinstance(self.arg1, Expression):
            self.arg1 = self.arg1.reduce()
        if isinstance(self.arg2, Expression):
            self.arg2 = self.arg2.reduce()

        if op == 'mul' and (self.arg1 == 0 or self.arg2 == 0):
            return 0

        if op == 'add' and self.arg1 == 0:
            return self.arg2

        if op == 'add' and self.arg2 == 0:
            return self.arg1

        return self

    def __repr__(self):
        if self.op == 'inp':
            return f'IN {self.arg1}'
        s = "("
        s += str(self.arg1)
        s += " " + self.get_op_string() + " "
        s += str(self.arg2)
        s += ")"
        return s

    def get_op_string(self):
        op = self.op

        if op == 'add':
            return "+"

        elif op == 'mul':
            return "*"

        elif op == 'div':
            return "/"

        elif op == 'mod':
            return "%"

        elif op == 'eql':
            return "=="

        elif op == 'inp':
            return "IN"


class ExpressionState:

    def __init__(self):
        self.data = {}
        self.data['x'] = 0
        self.data['y'] = 0
        self.data['z'] = 0
        self.data['w'] = 0
        self.input_counter = 0

    def is_unknown(self):
        return self.data['x'] == '?' or self.data['y'] == '?' or self.data['z'] == '?'


    def get_value(self, arg):
        if arg in self.data:
            val = self.data[arg]
            if val == '?':
                return '?'
            else:
                return val
        else:
            return int(arg)

    def execute(self, instruction):

        op = instruction["op"]
        arg1 = instruction["arg1"]
        arg2 = instruction["arg2"]

        if op == 'inp':
            # this is from now on an unknown
            self.input_counter += 1
            self.data[arg1] = 'I' + str(self.input_counter)
            return

        expression = Expression(op, arg1, arg2)
        new_value = expression.reduce(self.data)
        self.data[arg1] = new_value


        arg2v = self.get_value(arg2)
        arg1v = self.data[arg1]

        if op == 'add':
            if arg1v == '?' or arg2v == '?':
                self.data[arg1] = '?'
            else:
                self.data[arg1] += arg2v

        elif op == 'mul':
            if arg1v == 0 or arg2v == 0:
                self.data[arg1] = 0
            elif arg1v == '?' or arg2v == '?':
                self.data[arg1] = '?'
            else:
                self.data[arg1] *= arg2v

        elif op == 'div':

            if arg1v == '?' or arg2v == '?':
                self.data[arg1] = '?'
            else:
                self.data[arg1] //= arg2v

        elif op == 'mod':

            if arg1v == '?' or arg2v == '?':
                self.data[arg1] = '?'
            else:
                self.data[arg1] %= arg2v

        elif op == 'eql':
            if arg2v == '?':
                self.data[arg1] = '?' if 1 <= arg1v <= 9 else 0
            else:
                self.data[arg1] = 1 if arg1v == arg2v else 0

        else:
            raise "Not supported"

    def __repr__(self):

        return f"x = {self.data['x']}, y = {self.data['y']}, z = {self.data['z']}, w = {self.data['w']}"


def solve():

    with open("input24-1.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]
        #lines.reverse()
        regexp = re.compile(r"(inp|add|mul|div|mod|eql) ([xyzw]) ?([xyzw]|[-0-9]+)?")

        instructions = []
        expression = None
        state = ExpressionState()
        relevant_digits = []
        for line in lines:
            match = regexp.match(line)
            groups = match.groups()

            instruction = {
                "op": groups[0],
                "arg1": groups[1],
                "arg2": groups[2] if len(groups) > 2 else None
            }

            # if this is an input digit, we check if it is relevant
            if instruction["op"] == "inp":
                relevant_digits.append(state.is_unknown())

            print(f"Add instruction {instruction}")
            state.execute(instruction)
            print(f"State is {state}")
            #
            # new_expression = Expression(instruction["op"], instruction["arg1"], instruction["arg2"])
            # if expression == None:
            #     expression = new_expression
            # else:
            #     expression.replace(new_expression)
            # instructions.append(instruction)
            # print(f"{expression.target} = {expression}")

        print(relevant_digits[1:])

        return
        print(f"{expression.target} = {expression}")
        return

        def run_program(input):

            state = State(input)
            for instruction in instructions:
                success = state.execute(instruction["op"], instruction["arg1"], instruction["arg2"])
                if not success:
                    return 0

            return state.data["z"]

        def to_digit_list(num):
            return [int(x) for x in str(num)]

        input = to_digit_list(99999999999999)
        while run_program(input.copy()) != 1:
            idx = 13
            input[idx] -= 1
            while input[idx] == 0:
                input[idx] = 9
                idx -= 1
                input[idx] -= 1

                if idx == 9:
                    print(f"Now trying input {input}")

        print(f"The first input to have a positive result is {input}")





solve()