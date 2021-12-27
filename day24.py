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

class Range:

    def __init__(self, min, max, vars):
        self.vars = vars
        self.min = min
        self.max = max

        # we got reduced to a constant
        if min == max:
            self.vars = set()

    def is_overlap(self, other):
        return other.min <= self.min <= other.max or self.min <= other.min <= self.max

    def is_constant(self):
        return self.min == self.max

    def is_identical_constant(self, other):
        return self.is_constant() and other.is_constant() and self.min == other.min

    def get_relevant_variables(self):
        return self.vars

    def __repr__(self):
        return f'[{self.min} -> {self.max} [{self.vars}]'


class Expression:

    var_names = ['x', 'y', 'z', 'w']

    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

        if self.arg1 not in Expression.var_names and not self.is_unknown(self.arg1):
            self.arg1 = Range(int(self.arg1), int(self.arg1), set())
        if self.arg2 not in Expression.var_names and not self.is_unknown(self.arg2):
            self.arg2 = Range(int(self.arg2), int(self.arg2), set())

    def get_relevant_variables(self):
        relevant_variables = set()
        relevant_variables = relevant_variables | self.get_relevant_variables_for_arg(self.arg1)
        relevant_variables = relevant_variables | self.get_relevant_variables_for_arg(self.arg2)
        return relevant_variables

    def get_relevant_variables_for_arg(self, arg):
        if isinstance(arg, Expression):
            return arg.get_relevant_variables()
        if isinstance(arg, int):
            return set()
        if arg[0] == 'I':
            return set([arg])

    def is_unknown(self, val):
        if isinstance(val, Expression):
            return True
        if isinstance(val, int):
            return False
        return val[0] == 'I'

    def is_raw_input(self, val):
        if isinstance(val, Expression):
            return False
        if isinstance(val, int):
            return False
        return val[0] == 'I'

    def is_range(self, val):
        return isinstance(val, Range)

    def reduce(self, data):

        arg1 = self.arg1
        arg2 = self.arg2
        if arg1 in data:
            arg1 = data[arg1]

        if arg2 in data:
            arg2 = data[arg2]

        # if isinstance(arg1, Expression):
        #     arg1 = arg1.reduce(data)
        # if isinstance(arg2, Expression):
        #     arg2 = arg2.reduce(data)

        op = self.op
        if op == 'add':
            return Range(arg1.min+arg2.min, arg1.max+arg2.max, arg1.vars|arg2.vars)

        elif op == 'mul':
            return Range(
                min(arg1.min*arg2.min, arg1.min*arg2.max, arg1.max*arg2.min, arg1.max*arg2.max),
                max(arg1.min * arg2.min, arg1.min * arg2.max, arg1.max * arg2.min, arg1.max * arg2.max),
                arg1.vars | arg2.vars)

        # in the code, div is always a positive constant
        elif op == 'div':
            if not arg2.is_constant() or arg2.min == 0:
                raise "This is not possible, arg2 should be a positive constant"

            div = arg2.min
            return Range(arg1.min // div, arg1.max // div, arg1.vars)

        # in the code, mod is always a positive constant and the input MUST also be positive!
        elif op == 'mod':
            if not arg2.is_constant() or arg2.min <= 0:
                raise "Not supported, needs to be constant"
            if arg1.min < 0:
                raise "This is not possible. Should always be positive!"

            # range falls within the first part - no modulo possible
            mod = arg2.min
            if arg1.max < mod:
                return arg1

            return Range(0, mod-1, set())

        elif op == 'eql':

            if not arg1.is_overlap(arg2):
                return Range(0, 0, set())
            elif arg1.is_identical_constant(arg2):
                return Range(1, 1, set())
            else:
                return Range(0, 1, set())

        else:
            raise "Not supported"

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
        self.data['x'] = Range(0, 0, set())
        self.data['y'] = Range(0, 0, set())
        self.data['z'] = Range(0, 0, set())
        self.data['w'] = Range(0, 0, set())
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

    def get_relevant_variables(self, arg):
        return self.data['z'].get_relevant_variables()

    def execute(self, instruction):

        op = instruction["op"]
        arg1 = instruction["arg1"]
        arg2 = instruction["arg2"]

        if op == 'inp':
            # this is from now on an unknown
            self.input_counter += 1
            self.data[arg1] = Range(1, 9, set(['I' + str(self.input_counter)]))
            return

        expression = Expression(op, arg1, arg2)
        new_value = expression.reduce(self.data)
        self.data[arg1] = new_value
        return


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

        print(relevant_digits[1:])

        print(f"State is {state}")

        relevant_variables = state.get_relevant_variables('z')
        print(relevant_variables)

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