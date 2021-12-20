from itertools import groupby
import re
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter



def solve():

    with open("input20-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        algorithm = lines[0]

        grid = defaultdict(lambda: False)
        width = len(lines)-2
        height = len(lines[2])
        for y in range(0, height):
            line = lines[y+2]
            for x in range(0, width):
                grid[(x,y)] = (line[x] == '#')

        min_x = 0
        max_x = width-1
        min_y = 0
        max_y = height-1
        background_value = False

        def print_grid(grid):
            s = ""
            for y in range(min_y, max_y+1):
                for x in range(min_x, max_x+1):
                    s += "#" if grid[(x, y)] else "."
                s += "\n"
            print(s)

        def enhance(grid):
            new_grid = defaultdict(lambda: background_value)
            for x in range(min_x, max_x+1):
                for y in range(min_y, max_y+1):

                    value = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            num = 1 if grid[(x+dx, y+dy)] else 0
                            value = value * 2 + num

                    new_grid[(x,y)] = True if algorithm[value] == '#' else False

            return new_grid





        iterations = 50
        for iteration in range(0, iterations):
            min_x -= 1
            max_x += 1
            min_y -= 1
            max_y += 1
            grid = enhance(grid)
            background_value = (algorithm[0] == '#') if not background_value else (algorithm[511] == '#')
            print(f"Default background value from ({min_x},{min_y}) to ({max_x},{max_y}) now {background_value}")

            print(f"Value at far away is {grid[(500000, 50000000)]}")
            #print_grid(grid)


        n_lit = 0
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if grid[(x,y)]:
                    n_lit += 1

        print(f"There are {n_lit} lit pixels")

solve()
