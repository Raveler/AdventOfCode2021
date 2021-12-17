
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


def is_at_target(target, pos):
    return target["min"][0] <= pos[0] <= target["max"][0] and target["min"][1] <= pos[1] <= target["max"][1]

def is_done(target, pos):

    if pos[0] > target["max"][0]:
        return True
    if pos[1] < target["min"][1]:
        return True
    if is_at_target(target, pos):
        return True
    return False


def simulate(target, velocity):
    pos = (0, 0)
    n_steps = 0
    #print(f"Start with velocity {velocity}")
    max_y = pos[1]
    while not is_done(target, pos):
        pos = (pos[0] + velocity[0], pos[1] + velocity[1])
        max_y = max(max_y, pos[1])
        velocity = (velocity[0] - numpy.sign(velocity[0]), velocity[1] - 1)
        n_steps += 1
        #print(f"After {n_steps} steps, we are at {pos} with velocity {velocity}")

    return {
        "success": is_at_target(target, pos),
        "max_y": max_y
    }

def solve():
    with open("input17-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]
        regexp = re.compile(r"target area: x=(-?[0-9]+)..(-?[0-9]+), y=(-?[0-9]+)..(-?[0-9]+)")
        match = regexp.match(lines[0])
        groups = match.groups()

        target_min = (int(groups[0]), int(groups[2]))
        target_max = (int(groups[1]), int(groups[3]))
        target = {
            "min": target_min,
            "max": target_max
        }

        y = 1
        x = 1
        highest_point = 0
        highest_initial_velocity = (0, 0)
        n_successes = 0
        for y in range(target["min"][1], 1000):
            some_success = False
            for x in range(1, 130):
                velocity = (x, y)
                state = simulate(target, velocity)
                if state["success"]:
                    some_success = True
                    n_successes += 1
                if state["success"] and state["max_y"] > highest_point:
                    highest_point = state["max_y"]
                    highest_initial_velocity = velocity
                    continue
            if not some_success:
                print(f"Failed to find success at y={y}")

        print(f"The highest point we reached is {highest_point} with initial velocity {highest_initial_velocity}")
        print(f"The total number of good velocities is {n_successes}")


solve()

