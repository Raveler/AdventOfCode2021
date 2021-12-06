
from itertools import groupby
import re
import math

cache = {}


def get_offspring_count(fish, start_day, n_days):

    if (fish, start_day, n_days) in cache:
        return cache[(fish, start_day, n_days)]

    #print(f"Find total offspring for {fish} starting at day {start_day} with {n_days} days total")
    day = start_day + fish + 1
    total_offspring = 0

    while day <= n_days:
        child_offspring = get_offspring_count(8, day, n_days)
        total_offspring += child_offspring
        day += 7

    # ourselves
    total_offspring += 1
    cache[(fish, start_day, n_days)] = total_offspring

    return total_offspring


def run(n_days):
    with open("input6-2.txt") as f:
        lines = f.readlines()
        fishes = [int(val) for val in lines[0].split(",")]
        #fishes = [1]

        fish_per_starting_count = {}
        for initial_fish_age in range(1, 6):
            total_offspring = get_offspring_count(initial_fish_age, 0, n_days)
            fish_per_starting_count[initial_fish_age] = total_offspring
            print(f"Total offspring for starting age {initial_fish_age} is {total_offspring}")


        total_fishes = 0
        for fish in fishes:
            #print(f"Fish {fish} produces {fish_per_starting_count[fish]} total offspring")
            total_fishes += fish_per_starting_count[fish]

        print(f"Total fishes: {total_fishes}")

        print(f"There are now {len(fishes)} fishes after {n_days} days!")

#run(80)
run(256)




