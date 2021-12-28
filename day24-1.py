from itertools import groupby, repeat
import re
import math
import pprint
import functools

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
import itertools
import random
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

    def __init__(self, min, max, step, vars):
        self.vars = vars
        self.min = min
        self.max = max
        self.step = step

        # we got reduced to a constant
        if min == max:
            self.vars = set()

    def includes(self, value):
        if (value - self.min) % self.step != 0:
            return False
        return self.min <= value <= self.max

    def is_overlap(self, other):
        return other.min <= self.min <= other.max or self.min <= other.min <= self.max

    def is_constant(self):
        return self.min == self.max

    def is_identical_constant(self, other):
        return self.is_constant() and other.is_constant() and self.min == other.min

    def get_relevant_variables(self):
        return self.vars

    def __repr__(self):
        return f'[{self.min} -> {self.max} with step {self.step} [{self.vars}]'

class Num:

    def __init__(self, value, vars):
        self.value = value
        self.vars = vars


class Expression:

    var_names = ['x', 'y', 'z', 'w']

    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

        if self.arg1 not in Expression.var_names and not self.is_unknown(self.arg1):
            self.arg1 = int(self.arg1)
        if self.arg2 not in Expression.var_names and not self.is_unknown(self.arg2):
            self.arg2 = int(self.arg2)

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
        if isinstance(val, set):
            return False
        if isinstance(val, Range):
            return False
        return val[0] == 'I'

    def is_range(self, val):
        return isinstance(val, Range)

    def get_range(self, data):

        if self.op == 'inp':
            return Range(1, 9, 1, set([self.arg1]))

        arg1 = self.arg1
        arg2 = self.arg2

        if arg1 in data:
            arg1 = data[arg1]

        if arg2 in data:
            arg2 = data[arg2]

        if isinstance(arg1, Expression):
             arg1 = arg1.get_range(data)
        if isinstance(arg2, Expression):
             arg2 = arg2.get_range(data)

        if isinstance(arg1, int):
            arg1 = Range(arg1, arg1, 1, set())
        if isinstance(arg2, int):
            arg2 = Range(arg2, arg2, 1, set())

        if self.is_raw_input(arg1):
            arg1 = Range(1, 9, 1, set([arg1]))
        if self.is_raw_input(arg2):
            arg2 = Range(1, 9, 1, set([arg2]))


        op = self.op

        if op == 'add':
            add_range = Range(arg1.min+arg2.min, arg1.max+arg2.max, 1, arg1.vars|arg2.vars)
            if arg1.step == arg2.step:
                add_range.step = arg1.step
            elif arg1.is_constant():
                add_range.step = arg1.step
            elif arg2.is_constant():
                add_range.step = arg2.step
            return add_range

        elif op == 'mul':
            mul_range = Range(
                min(arg1.min * arg2.min, arg1.min * arg2.max, arg1.max * arg2.min, arg1.max * arg2.max),
                max(arg1.min * arg2.min, arg1.min * arg2.max, arg1.max * arg2.min, arg1.max * arg2.max),
                arg1.step * arg2.step,
                arg1.vars | arg2.vars)

            if arg1.is_constant() and arg2.is_constant():
                mul_range.vars = set()
                mul_range.step = 1
            elif arg1.is_constant():
                mul_range.step = arg1.min
            elif arg2.is_constant():
                mul_range.step = arg2.min

            return mul_range

        # in the code, div is always a positive constant
        elif op == 'div':
            if not arg2.is_constant() or arg2.min == 0:
                raise "This is not possible, arg2 should be a positive constant"

            div = arg2.min
            return Range(arg1.min // div, arg1.max // div, arg1.step // div, arg1.vars)

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

            # use the steps to deduce the REAL definitive value if it matches
            if arg1.step % mod == 0:
                return Range(arg1.min, arg1.min, 1, set())

            return Range(0, mod-1, 1, set())

        elif op == 'eql':

            if not arg1.is_overlap(arg2):
                return Range(0, 0, 1, set())
            elif arg1.is_identical_constant(arg2):
                return Range(1, 1, 1, set())
            else:
                return Range(0, 1, 1, set())

        else:
            raise "Not supported"


    def get_numerical_range(self, data):

        if self.op == 'inp':
            return set(range(1, 10))

        arg1 = self.arg1
        arg2 = self.arg2

        if arg1 in data:
            arg1 = data[arg1]

        if arg2 in data:
            arg2 = data[arg2]

        if isinstance(arg1, Expression):
             arg1 = arg1.get_numerical_range(data)
        if isinstance(arg2, Expression):
             arg2 = arg2.get_numerical_range(data)

        if isinstance(arg1, int):
            arg1 = set([arg1])
        if isinstance(arg2, int):
            arg2 = set([arg2])

        if self.is_raw_input(arg1):
            arg1 = set(range(1, 10))
        if self.is_raw_input(arg2):
            arg2 = set(range(1, 10))

        op = self.op

        if op == 'add':
            return set([x + y for (x, y) in itertools.product(arg1, arg2)])
            full_range = set()
            for num in arg1:
                full_range |= numpy.add(arg2, num)
            return full_range

        elif op == 'mul':
            return set([x * y for (x, y) in itertools.product(arg1, arg2)])

        # in the code, div is always a positive constant
        elif op == 'div':
            full_range = set()

            if len(arg2) != 1 or min(arg2) == 0:
                raise "This is not possible, arg2 should be a positive constant"

            div = min(arg2)
            return set([x // div for x in arg1])

        # in the code, mod is always a positive constant and the input MUST also be positive!
        elif op == 'mod':
            if len(arg2) != 1 or min(arg2) <= 0:
                raise "Not supported, needs to be constant"
            if min(arg1) < 0:
                raise "This is not possible. Should always be positive!"

            # range falls within the first part - no modulo possible
            mod = min(arg2)
            return set([x % mod for x in arg1])

        elif op == 'eql':

            # the two sets are identical constants
            if len(arg1) == len(arg2) == 1:
                if len(arg1 & arg2) == 1:
                    return set([1])
                else:
                    return set([0])
            else:
                if len(arg1 & arg2) > 0:
                    return set([0, 1])
                else:
                    return set([0])

        else:
            raise "Not supported"

    def get_allowed_values(self, allowed_range):

        arg1 = self.arg1
        arg2 = self.arg2
        op = self.op
        print("HMZ")
        print(op)
        print(arg1)
        print(arg2)

        if op == 'add':
            pass


        elif op == 'mul':
            pass


        elif op == 'div':
            pass


        elif op == 'mod':
            pass

        elif op == 'eql':
            pass

        else:
            raise "Not supported"


    def reduce(self, data):

        # get our range - if it is a constant, we return that one!
        #range = self.get_range(data)
        range = self.get_numerical_range(data)
        #print(f"Range for {self}:")
        #print(range)
        #print(range)
        #if range.is_constant():
        #    return range.min
        if len(range) == 1:
            return min(range)

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
            if self.is_unknown(arg1) and self.is_unknown(arg2):
                return Expression(op, arg1, arg2)
            elif self.is_unknown(arg1):
                if arg2 == 0:
                    return arg1
                else:
                    return Expression(op, arg1, arg2)
            elif self.is_unknown(arg2):
                if arg1 == 0:
                    return arg2
                else:
                    return Expression(op, arg1, arg2)
            return arg1 + arg2

        elif op == 'mul':
            if self.is_unknown(arg1) and self.is_unknown(arg2):
                return Expression(op, arg1, arg2)
            elif self.is_unknown(arg1):
                if arg2 == 1:
                    return arg1
                elif arg2 == 0:
                    return 0
                else:
                    return Expression(op, arg1, arg2)
            elif self.is_unknown(arg2):
                if arg1 == 1:
                    return arg2
                elif arg1 == 0:
                    return 0
                else:
                    return Expression(op, arg1, arg2)

            if self.is_unknown(arg1) or self.is_unknown(arg2):
                if arg1 == 0 or arg2 == 0:
                    return 0
                else:
                    return Expression(op, arg1, arg2)
            return arg1 * arg2

        elif op == 'div':
            if arg2 == 1:
                return arg1
            if self.is_unknown(arg1) or self.is_unknown(arg2):
                return Expression(op, arg1, arg2)
            return arg1 // arg2

        elif op == 'mod':
            if self.is_unknown(arg1) or self.is_unknown(arg2):
                return Expression(op, arg1, arg2)
            return arg1 % arg2

        elif op == 'eql':
            if self.is_unknown(arg1) and self.is_unknown(arg2):
                return Expression(op, arg1, arg2)
            elif self.is_unknown(arg1):
                if self.is_raw_input(arg1) and arg2 < 1 or arg2 > 9:
                    return 0
                else:
                    return Expression(op, arg1, arg2)
            elif self.is_unknown(arg2):
                if self.is_raw_input(arg2) and arg1 < 1 or arg1 > 9:
                    return 0
                else:
                    return Expression(op, arg1, arg2)
            return 1 if arg1 == arg2 else 0

        else:
            raise "Not supported"

    def __repr__(self):
        if self.op == 'inp':
            return f'IN {self.arg1}'

        s = ""
        if isinstance(self.arg1, Expression):
            s += f"({str(self.arg1)})"
        else:
            s += str(self.arg1)
        s += " " + self.get_op_string() + " "
        if isinstance(self.arg2, Expression):
            s += f"({str(self.arg2)})"
        else:
            s += str(self.arg2)
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

    def get_relevant_variables(self, arg):
        return self.data['z'].get_relevant_variables()

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

    with open("input24-2.txt") as f:


        def eql(val1, val2):
            return 1 if val1 == val2 else 0

        def validate_input(input):
            x = 0
            y = 0
            z = 0
            w = 0

            divs = [1, 1, 1, 1, 26, 1, 1, 26, 1, 26, 26, 26, 26, 26]
            x_adds = [12, 11, 10, 10, -16, 14, 12, -4, 15, -7, -8, -4, -15, -8]
            y_adds = [6, 12, 5, 10, 7, 0, 4, 12, 14, 13, 10, 11, 9, 9]

            for i in range(len(input)):

                div = divs[i]
                x_add = x_adds[i]
                y_add = y_adds[i]

                w = input[i]
                x = ((z % 26) + x_add)
                z = z // div
                #if x != w:
                #    return False

                x = eql(eql(x, w), 0)

                #if x != 0:
                #    return False

                y = (25 * x) + 1
                z = z * y
                y = (w + y_add) * x

                #print(f"x = {x}, y = {y}, w = {w}")

                z = z + y
                #print(z)

                # if we are in a /26 phase, we NEED to make sure that z is flipped to 0, otherwise it will never become 0 again
                if x_add < 0 and x == 1 and z >= 26:
                    return False


            return len(input) < 14 or z == 0

        input = [9]
        digit_index = 0

        while len(input) > 0:

            # try to validate the current input
            print(f"Try to validate {input}")
            if validate_input(input):

                # we reached a valid one!
                if len(input) == 14:
                    print(f"The first valid input is {''.join([str(i) for i in input])}")
                    break

                digit_index += 1
                input.append(9)

            # invalid - reset to next
            else:
                input[digit_index] -= 1
                while digit_index >= 0 and input[digit_index] == 0:
                    input.pop()
                    digit_index -= 1
                    if digit_index >= 0:
                        input[digit_index] -= 1

        input = [1]
        digit_index = 0

        while len(input) > 0:

            # try to validate the current input
            #print(f"Try to validate {input}")
            if validate_input(input):

                # we reached a valid one!
                if len(input) == 14:
                    print(f"The first valid input is {''.join([str(i) for i in input])}")
                    break

                digit_index += 1
                input.append(1)

            # invalid - reset to next
            else:
                input[digit_index] += 1
                while digit_index >= 0 and input[digit_index] == 10:
                    input.pop()
                    digit_index -= 1
                    if digit_index >= 0:
                        input[digit_index] += 1


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
            instructions.append(instruction)

            # if this is an input digit, we check if it is relevant
            if instruction["op"] == "inp":
                relevant_digits.append(state.is_unknown())

            #print(f"Add instruction {instruction}")
            #state.execute(instruction)
            #print(f"State is {state}")

        def to_digit_list(num):
            return [int(x) for x in str(num)]

        def run_program(input):

            state = State(input)
            for instruction in instructions:
                success = state.execute(instruction["op"], instruction["arg1"], instruction["arg2"])
                if not success:
                    return 1

            return state.data["z"]

        print(f"The result for 99894989191967 is {run_program(to_digit_list(99894989191967))}")

        # print(relevant_digits[1:])
        #
        #print(f"State is {state}")
        return
        #
        # relevant_variables = state.get_relevant_variables('z')
        # print(relevant_variables)
        # state.data['x'].get_allowed_values(Range(0, 0, 1, set()))
        #print(f"{expression.target} = {expression}")

        results_per_input = {}
        for idx in range(len(input)):

            results_per_input[idx] = set()

            for attempt in range(0, 10):
                outputs = set()
                for shuffle_index in range(len(input)):
                    if shuffle_index == idx:
                        continue
                    input[shuffle_index] = random.randrange(1, 10)

                for idx_value in range(1, 10):
                    input[idx] = idx_value
                    out = run_program(input.copy())
                    print(out)
                    outputs.add(out)

                results_per_input[idx].add(len(outputs))

        pp.pprint(results_per_input)



        input = to_digit_list(99999999999999)

        while run_program(input.copy()) != 0:
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