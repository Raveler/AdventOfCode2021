from itertools import groupby
import re
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


cubes = []

def to_coord(idx, value):
    return {
        "idx": idx,
        "value": value,
    }


def get_dimension_coords(cubes, dim):
    coords = []
    for cube in cubes:
        coords.append(to_coord(cube["idx"], cube["min"][dim]))
        coords.append(to_coord(cube["idx"], cube["max"][dim]+1))
    coords.sort(key=lambda coord: coord["value"])
    return coords


def generate_intervals(coords):
    in_set = set()
    pp.pprint(coords)
    in_set.add(coords[0]["idx"])
    prev_value = coords[0]["value"]
    intervals = []
    for i in range(1, len(coords)):
        coord = coords[i]
        value = coord["value"]
        if value != prev_value:
            intervals.append({
                "min": prev_value,
                "max": value,
                "set": in_set.copy(),
            })
        prev_value = value
        idx = coord["idx"]
        if idx in in_set:
            in_set.remove(idx)
        else:
            in_set.add(idx)

    return intervals


def cut_cubes(cubes):

    xs = generate_intervals(get_dimension_coords(cubes, 0))
    ys = generate_intervals(get_dimension_coords(cubes, 1))
    zs = generate_intervals(get_dimension_coords(cubes, 2))

    print(xs)
    print(ys)
    print(zs)

    on_by_idx = {}
    for cube in cubes:
        on_by_idx[cube["idx"]] = cube["on"]

    split_cubes = []
    total_on = 0
    n_processed = 0
    print(f"We have {len(xs)} x {len(ys)} x {len(zs)} intervals")
    for x_interval in xs:
        for y_interval in ys:
            for z_interval in zs:
                overlap = x_interval["set"] & y_interval["set"] & z_interval["set"]
                if len(overlap) > 0:
                    min = (x_interval["min"], y_interval["min"], z_interval["min"])
                    max = (x_interval["max"], y_interval["max"], z_interval["max"])
                    #print(overlap)

                    final_on = on_by_idx[sorted(overlap)[-1]]
                    #print(f"Interval {min} -> {max} with overlap {overlap} is finally on: {final_on}")
                    if final_on:

                        dx = max[0] - min[0]
                        dy = max[1] - min[1]
                        dz = max[2] - min[2]
                        volume = dx * dy * dz
                        if volume == 0:
                            print(f"FOUND INVALID CUBE: {cube}")
                        total_on += volume

                    n_processed += 1
                    if n_processed % 100000 == 0:
                        print(f"We now have {n_processed} split cubes")
                    continue

                    split_cubes.append({
                        "on": final_on,
                        "min": min,
                        "max": max,
                        "idx": -1,
                    })

    print(f"The total on is {total_on}")
    return split_cubes, total_on



def solve():

    with open("input22-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        regexp = re.compile(r"(on|off) x=(-?[0-9]+)..(-?[0-9]+),y=(-?[0-9]+)..(-?[0-9]+),z=(-?[0-9]+)..(-?[0-9]+)")
        instructions = []
        for idx, line in enumerate(lines):
            match = regexp.match(line)
            groups = match.groups()
            instructions.append({
                "on": (groups[0] == "on"),
                "x_min": int(groups[1]),
                "x_max": int(groups[2]),
                "y_min": int(groups[3]),
                "y_max": int(groups[4]),
                "z_min": int(groups[5]),
                "z_max": int(groups[6]),
            })

            assert(int(groups[1]) < int(groups[2]))
            assert(int(groups[3]) < int(groups[4]))
            assert(int(groups[5]) < int(groups[6]))

            cubes.append({
                "on": (groups[0] == "on"),
                "min": (int(groups[1]), int(groups[3]), int(groups[5])),
                "max": (int(groups[2]), int(groups[4]), int(groups[6])),
                "idx": idx,

            })

        cut_cubes(cubes)

        grid = defaultdict(lambda: False)
        for instruction in instructions:
            pp.pprint(instruction)
            x_min = max(instruction["x_min"], -50)
            x_max = min(instruction["x_max"], 50)
            y_min = max(instruction["y_min"], -50)
            y_max = min(instruction["y_max"], 50)
            z_min = max(instruction["z_min"], -50)
            z_max = min(instruction["z_max"], 50)

            for x in range(x_min, x_max+1):
                for y in range(y_min, y_max+1):
                    for z in range(z_min, z_max+1):
                        grid[(x, y, z)] = instruction["on"]

        n_on = 0
        for x in range(-50, 50 + 1):
            for y in range(-50, 50 + 1):
                for z in range(-50, 50 + 1):
                    if grid[(x, y, z)]:
                        n_on += 1

        print(f"After initialization, {n_on} cubes are on in the [-50, 50] range.")




solve()