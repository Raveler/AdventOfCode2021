
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy


class Cave:

    def __init__(self, c):
        self.connections = []
        self.big = c.isupper() or c == 'end'
        self.name = c;

    def add_connection(self, cave):
        self.connections.append(cave)
        cave.connections.append(self)



def solve():
    with open("input13-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        width = 0
        height = 0
        grid = set()
        instructions = []

        def print_grid():
            for y in range(0, height):
                ss = ""
                for x in range(0, width):
                    if (x,y) in grid:
                        ss += "#"
                    else:
                        ss += "."
                print(ss)


        dotting = True
        regex = re.compile(r"fold along (x|y)=([0-9]+)")
        for line in lines:

            if len(line) == 0:
                dotting = False

            elif dotting:
                split = line.split(",")
                x = int(split[0])
                y = int(split[1])
                grid.add((x,y))
                width = max(x+1, width)
                height = max(y+1, height)

            else:
                match = regex.match(line)
                groups = match.groups()
                instructions.append(groups)


        # execute
        for instruction in instructions:
            d = int(instruction[1])

            if instruction[0] == 'x':
                for x in range(0, d):
                    for y in range(0, height):
                        if (d+(d-x), y) in grid:
                            grid.add((x, y))
                width = width // 2

            else:
                for y in range(0, d):
                    for x in range(0, width):
                        if (x, d+(d-y)) in grid:
                            grid.add((x, y))
                height = height // 2

        # count
        dots = 0
        for x in range(0, width):
            for y in range(0, height):
                if (x,y) in grid:
                    dots += 1

        print(f"After {len(instructions)} folds, we have {dots} dots remaining.")

        print_grid()





solve()