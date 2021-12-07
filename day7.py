
from itertools import groupby
import re
import math


accumulated_distance = {}

def get_distance_funky(crab, target):
    distance = abs(crab - target)
    return accumulated_distance[distance]

def get_distance(crab, target):
    return abs(crab - target)

def get_distance_sum(crabs, target, get_distance):
    return sum([get_distance(crab, target) for crab in crabs])

def part_1(get_distance):

    with open("input7-2.txt") as f:

        lines = f.readlines()
        crabs = list(map(int, lines[0].split(",")))
        print(crabs)

        min_target = min(crabs)
        max_target = max(crabs)
        print(f"Go from {min_target} to {max_target}")

        accumulated_distance.clear()
        sum = 0
        for distance in range(0, abs(max_target-min_target)+1):
            sum += distance
            accumulated_distance[distance] = sum

        print(accumulated_distance)



        lowest_sum = 100000000
        for target in range(min_target, max_target+1):
            #print(f"Try target {target}")
            sum = get_distance_sum(crabs, target, get_distance)
            if sum > lowest_sum:
                continue
            if sum < lowest_sum:
                lowest_sum = sum

        print(f"The lowest fuel we can spend is {lowest_sum}")


part_1(get_distance)
part_1(get_distance_funky)