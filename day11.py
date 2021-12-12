
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy



def solve(steps):
    with open("input11-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        grid = {}
        flashed = {}
        width = len(lines[0])
        height = len(lines)
        for y in range(0, height):
            for x in range(0, width):
                grid[(x,y)] = int(lines[y][x])
                flashed[(x,y)] = False

        def flash(x, y):
            flashed[(x,y)] = True
            for dx in range(max(0, x-1), min(width, x+2)):
                for dy in range(max(0, y-1), min(height, y+2)):
                    grid[(dx,dy)] += 1



        total_flashes = 0
        for step in range(0, steps):
            step_flash_count = 0

            # increase by one
            for (x,y) in grid:
                grid[(x, y)] += 1
                flashed[(x,y)] = False

            # flash
            something_flashed = True
            while something_flashed:
                something_flashed = False
                for y in range(0, height):
                    for x in range(0, width):
                        if grid[(x,y)] > 9 and not flashed[(x,y)]:
                            flash(x, y)
                            step_flash_count += 1
                            something_flashed = True
                            total_flashes += 1

            # reset to zero
            for y in range(0, height):
                for x in range(0, width):
                    if flashed[(x,y)]:
                        grid[(x,y)] = 0
                        flashed[(x,y)] = False

            print(f"After {step+1} steps, there are {total_flashes} flashes")

            # SYNC
            if step_flash_count == width*height:
                print(f"The octopi are synched after step {step+1}!")
                break












solve(1000000)