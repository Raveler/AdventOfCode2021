
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
from collections import Counter


def solve(repeats):
    with open("input15-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        original_width = len(lines[0])
        original_height = len(lines)
        width = original_width * repeats
        height = original_height * repeats
        print(f"Original w/h: {original_width},{original_height}")

        grid = {}
        for y in range(0, height):
            for x in range(0, width):
                value = int(lines[y % original_height][x % original_width]) + (x // original_width) + (y // original_height)
                if value > 9:
                    value -= 9
                grid[(x, y)] = value

        dist = {}
        prev = {}
        vertices = []
        explored_vertices = []
        processed = {}
        for x in range(0, width):
            for y in range(0, height):
                dist[(x, y)] = math.inf
                prev[(x, y)] = False
                vertices.append((x, y))
                processed[(x,y)] = False

        dist[(0, 0)] = 0

        def get_neighbours(pos):
            if pos[0] > 0:
                yield (pos[0]-1, pos[1])
            if pos[1] > 0:
                yield (pos[0], pos[1]-1)
            if pos[0] < width-1:
                yield (pos[0]+1, pos[1])
            if pos[1] < height-1:
                yield (pos[0], pos[1]+1)

        def find_next_vertex():
            lowest = math.inf
            next_pos = (0, 0)
            for pos in explored_vertices:
                if processed[pos]:
                    continue
                if dist[pos] < lowest:
                    lowest = dist[pos]
                    next_pos = pos

            processed[next_pos] = True
            explored_vertices.remove(next_pos)
            return next_pos

        print(f"Start with {len(vertices)} vertices")
        total_processed = 0
        explored_vertices.append((0, 0))
        while total_processed < width*height:
            #print(dict(filter(lambda elem: dist[elem[0]] != math.inf, dist.items())))
            pos = find_next_vertex()
            total_processed += 1

            if total_processed % 100 == 0:
                print(f"We now have {total_processed} processed vertices and {len(explored_vertices)} in the open list")
            #print(f"Visit {pos}")

            if pos == (width-1, height-1):
                break

            for neighbour in get_neighbours(pos):
                alt = dist[pos] + grid[neighbour]
                if alt < dist[neighbour]:
                    dist[neighbour] = alt
                    prev[neighbour] = pos

                if neighbour not in explored_vertices and not processed[neighbour]:
                    explored_vertices.append(neighbour)

        pos = (width-1, height-1)
        path_cost = dist[pos]
        print(f"The shortest path cost is {path_cost}")


solve(5)