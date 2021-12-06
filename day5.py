
from itertools import groupby
import re


class Line:

    def __init__(self, p1, p2):
        self.p1 = p1;
        self.p2 = p2;

    def is_perpendicular(self):
        return self.p1[0] == self.p2[0] or self.p1[1] == self.p2[1]


def parse_line(text):
    m = re.search(r"([0-9]+),([0-9]+) -> ([0-9]+),([0-9]+)", text)
    values = m.group(1,2,3,4)
    return Line((int(values[0]), int(values[1])), (int(values[2]), int(values[3])))

def part_1():
    with open("input5-2.txt") as f:
        file_lines = f.readlines()

        lines = [parse_line(line) for line in file_lines]

        grid = {}
        dangerous_spots = 0
        for line in lines:

            if not line.is_perpendicular():
                continue

            for x in range(min(line.p1[0], line.p2[0]), max(line.p1[0], line.p2[0])+1):
                for y in range(min(line.p1[1], line.p2[1]), max(line.p1[1], line.p2[1])+1):
                    if not (x,y) in grid:
                        grid[(x,y)] = 0
                    grid[(x,y)] += 1
                    if grid[(x,y)] == 2:
                        dangerous_spots += 1

        print(grid)
        print(f"There are {dangerous_spots} dangerous spots.")


def sign(val):
    if val < 0:
        return -1
    elif val > 0:
        return 1
    else:
        return 0


def part_2():
    with open("input5-2.txt") as f:
        file_lines = f.readlines()

        lines = [parse_line(line) for line in file_lines]

        grid = {}
        dangerous_spots = 0
        for line in lines:

            dir = (sign(line.p2[0] - line.p1[0]), sign(line.p2[1] - line.p1[1]))

            pos = line.p1
            while pos != (line.p2[0] + dir[0], line.p2[1] + dir[1]):
                if not pos in grid:
                    grid[pos] = 0
                grid[pos] += 1
                if grid[pos] == 2:
                    dangerous_spots += 1

                pos = (pos[0] + dir[0], pos[1] + dir[1])

        print(grid)
        print(f"There are {dangerous_spots} dangerous spots.")


#part_1()
part_2()




