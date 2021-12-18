from itertools import groupby
import re
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


class Number:
    pass


class LiteralNumber(Number):

    def __init__(self, value):
        self.value = value
        self.literal = True

    def try_explode(self):
        return False

    def try_split(self):
        if self.value >= 10:
            #print("SPLIT:")
            self.parent.split(self)
            return True
        return False

    def add_to_child(self, value, index):
        self.value += value

    def get_magnitude(self):
        return self.value

    def __repr__(self):
        return str(self.value)


literal_regexp = re.compile(r"\[([0-9]+),([0-9]+)\]")
class PairNumber(Number):

    def __init__(self, number1, number2):
        self.pair = [number1, number2]
        self.set_child(0, number1)
        self.set_child(1, number2)
        self.parent = None
        self.literal = False

    def set_child(self, index, child):
        self.pair[index] = child
        child.parent = self

    def add(self, other):
        return PairNumber(self, other)

    def get_depth(self):
        depth = 0
        parent = self.parent
        while parent is not None:
            depth += 1
            parent = parent.parent
        return depth

    def reduce(self):

        # check for explosions and then splits
        donezo = False
        while not donezo:
            donezo = True

            if self.try_explode():
                donezo = False
            elif self.try_split():
                donezo = False

    def try_explode(self):

        # if both our children are literals, we see if we need to explode
        if self.pair[0].literal and self.pair[1].literal:

            if self.get_depth() > 3:
                #print("EXPLODE")
                self.explode()
                return True

        # otherwise, check our children
        if self.pair[0].try_explode():
            return True

        if self.pair[1].try_explode():
            return True

        return False

    def try_split(self):

        if self.pair[0].try_split():
            return True
        if self.pair[1].try_split():
            return True
        return False

    def explode(self):
        left_literal_value = self.pair[0].value
        right_literal_value = self.pair[1].value

        # we keep going up the tree as long as we're the left child
        child = self
        while child.parent is not None and child == child.parent.pair[0]:
            child = child.parent

        # add to the parent if we have one
        if child.parent is not None:
            child.parent.pair[0].add_to_child(left_literal_value, 1)

        # we keep going up the tree as long as we're the left child
        child = self
        while child.parent is not None and child == child.parent.pair[1]:
            child = child.parent

        # add to the parent if we have one
        if child.parent is not None:
            child.parent.pair[1].add_to_child(right_literal_value, 0)

        # now update ourselves
        if self.parent.pair[0] == self:
            self.parent.set_child(0, LiteralNumber(0))
        else:
            self.parent.set_child(1, LiteralNumber(0))

    def split(self, literal_child):
        value = literal_child.value
        new_number = PairNumber(LiteralNumber(value // 2), LiteralNumber((value // 2) + (value % 2)))
        if literal_child == self.pair[0]:
            self.set_child(0, new_number)
        else:
            self.set_child(1, new_number)

    def add_to_child(self, value, index):
        self.pair[index].add_to_child(value, index)

    def get_magnitude(self):
        return self.pair[0].get_magnitude() * 3 + self.pair[1].get_magnitude() * 2

    def __repr__(self):
        return f"[{self.pair[0]},{self.pair[1]}]"


def convert_to_numbers(arr):

    if isinstance(arr, list):
        return PairNumber(convert_to_numbers(arr[0]), convert_to_numbers(arr[1]))

    else:
        return LiteralNumber(int(arr))


def solve():
    with open("input18-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]
        #numbers = [PairNumber(line) for line in lines]

        numbers = []
        arrays = []
        for line in lines:

            arr = []
            root = arr
            parents = []

            for c in line:
                if c == '[':
                    arr.append([])
                    parents.append(arr)
                    arr = arr[-1]
                elif c == ']':
                    arr = parents[-1]
                    parents = parents[:-1]
                elif c == ',':
                    pass
                else:
                    arr.append(int(c))

            arr = arr[0]
            number = convert_to_numbers(arr)
            arrays.append(arr)
            print(line)
            print(number)
            print()
            numbers.append(number)

        result = numbers[0]
        for i in range(1, len(numbers)):
            print("ADD:")
            result = result.add(numbers[i])
            result.reduce()
            print(result)

        print(result)
        print(f"Magnitude of result is {result.get_magnitude()}")

        largest_magnitude = 0
        for i in range(0, len(numbers)):
            for j in range(0, len(numbers)):
                if i == j:
                    continue

                # since reduce is mutable, we need to re-parse them every time :p
                sum = convert_to_numbers(arrays[i]).add(convert_to_numbers(arrays[j]))
                sum.reduce()
                largest_magnitude = max(sum.get_magnitude(), largest_magnitude)
                sum = convert_to_numbers(arrays[j]).add(convert_to_numbers(arrays[i]))
                sum.reduce()
                largest_magnitude = max(sum.get_magnitude(), largest_magnitude)

        print(f"The largest possible magnitude is {largest_magnitude}")



solve()
