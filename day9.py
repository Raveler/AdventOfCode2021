
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy

def solve():
    with open("input9-2.txt") as f:
        lines = f.readlines()

        height = len(lines)
        width = len(lines[0])-1

        grid = defaultdict(lambda: {"depth": 9, "basin_found": False, "basin_id": 0})
        for y, line in enumerate(lines):
            heights = [int(c) for c in list(line.strip("\n"))]
            for x, depth in enumerate(heights):
                grid[(x,y)] = {"depth": depth, "basin_found": False, "basin_id": 0}

        # iterate over grid
        sum_risk_level = 0
        print(f"Explore grid of {width}x{height}")

        basins = []
        for x in range(0, width):
            for y in range(0, height):

                # iterate over neighbours
                depth = grid[(x,y)]["depth"]

                if depth < grid[(x-1,y)]["depth"] and depth < grid[(x+1,y)]["depth"] and depth < grid[(x,y-1)]["depth"] and depth < grid[(x,y+1)]["depth"]:
                    risk_level = depth+1
                    sum_risk_level += risk_level
                    basins.append((x,y))


        print(f"Total risk level of the grid: {sum_risk_level}")


        def flood_fill(start_pos):

            # we reached the summit
            if grid[start_pos]["depth"] == 9:
                return 0

            n = 1
            grid[start_pos]["basin_found"] = True

            left = (start_pos[0]-1, start_pos[1])
            right = (start_pos[0] + 1, start_pos[1])
            up = (start_pos[0], start_pos[1] - 1)
            down = (start_pos[0], start_pos[1] + 1)
            if not grid[left]["basin_found"]:
                n += flood_fill(left)
            if not grid[right]["basin_found"]:
                n += flood_fill(right)
            if not grid[up]["basin_found"]:
                n += flood_fill(up)
            if not grid[down]["basin_found"]:
                n += flood_fill(down)

            return n



        # for each basin, flood fill to find the basin size
        basin_sizes = []
        for basin_index, basin_pos in enumerate(basins):

            basin_size = flood_fill(basin_pos)

            print(f"Basin at {basin_pos} has size {basin_size}")
            basin_sizes.append(basin_size)

        basin_prod = numpy.prod(sorted(basin_sizes, reverse=True)[0:3])
        print(f"Three largest basins product: {basin_prod}")








solve()