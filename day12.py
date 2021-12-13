
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
    with open("input12-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        caves = {}

        def get_cave(name):
            if name not in caves.keys():
                caves[name] = Cave(name)
            return caves[name]

        for line in lines:

            cave_names = line.split("-")
            left_cave = get_cave(cave_names[0])
            right_cave = get_cave(cave_names[1])
            left_cave.add_connection(right_cave)

        print(caves)
        print(caves['start'])
        # find all paths by doing a depth-first search
        paths = []

        def explore(stack, did_double_visit):

            # we are done
            current_cave = stack[-1]

            if current_cave == 'end':
                #print(f"Reached end! we have stack {stack}")
                paths.append(stack.copy())
                return

            # explore all connections
            cave = caves[current_cave]
            for next_cave in cave.connections:

                # this is a small cave and we already visited one
                if not next_cave.big and next_cave.name in stack:

                    # allow one double visit
                    if stack.count(next_cave.name) > 1 or did_double_visit:
                        #print(f"Stack {stack} with next cave {next_cave.name} and did_double_visit {did_double_visit} is a dead end")
                        continue

                # don't go back to start
                if next_cave.name == 'start':
                    continue

                stack.append(next_cave.name)
                explore(stack, did_double_visit or (not next_cave.big and stack.count(next_cave.name) == 2))
                stack.pop()

        paths = []
        explore(['start'], True)

        print(f"We have a total of {len(paths)} legal paths")

        paths = []
        explore(['start'], False)
        print(f"When double visits are allowed, we have a total of {len(paths)} legal paths")









solve()