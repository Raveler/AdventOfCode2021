from itertools import groupby
import re
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter

class Scanner:

    def __init__(self, beacons, offset = (0, 0, 0)):
        self.beacons = beacons
        self.offset = offset
        self.sets = self.generate_sets()

    def find_relative_position_of_other(self, other):

        beacons = self.beacons
        offsets_tried = set()
        for beacon in beacons:

            # try to match this world beacon no each beacon in the other set
            for other_set in other.sets:
                for other_root_beacon in other_set["set"]:

                    offset = (beacon[0] - other_root_beacon[0], beacon[1] - other_root_beacon[1], beacon[2] - other_root_beacon[2])

                    if offset in offsets_tried:
                        continue

                    offsets_tried.add(offset)
                    n_found = 0
                    other_beacon_indices = []
                    for other_index, other_beacon in enumerate(other_set["set"]):
                        other_beacon = (other_beacon[0] + offset[0], other_beacon[1] + offset[1], other_beacon[2] + offset[2])

                        if other_beacon in beacons:
                            n_found += 1
                            other_beacon_indices.append(other_index)

                    if n_found >= 12:

                        print("FOUND A MATCH")

                        # rotate the other beacon back to world coordinates, not relative ones
                        print(f"Found {len(other_beacon_indices)} matching beacons")

                        print("RELATIVE BEACON SET:")
                        world_beacons = []
                        print(f"Offset is {offset}")
                        print(other.beacons)
                        for beacon in other.beacons:
                            beacon = other.rotate(beacon, other_set["x_rotations"], other_set["y_rotations"], other_set["z_rotations"], False)
                            world_beacons.append((beacon[0] + offset[0], beacon[1] + offset[1], beacon[2] + offset[2]))
                        print(world_beacons)

                        return Scanner(world_beacons, offset)

        return None

    def generate_sets(self):

        sets = []
        for x_rotations in range(0, 4):
            for y_rotations in range(0, 4):
                for z_rotations in range(0, 4):

                    # generate the set
                    set = self.generate_set(x_rotations, y_rotations, z_rotations)

                    # make sure the set is not a copy of an old one
                    if not self.is_copy_of_existing_set(set, sets):
                        sets.append({
                            "x_rotations": x_rotations,
                            "y_rotations": y_rotations,
                            "z_rotations": z_rotations,
                            "set": set,
                        })

        return sets

    def is_copy_of_existing_set(self, set, prev_sets):
        for prev_set in prev_sets:

            copy_found = True
            for beacon in prev_set:
                if beacon not in set:
                    copy_found = False

            if copy_found:
                return True

        return False

    def generate_set(self, x_rotations, y_rotations, z_rotations, inverted = False):

        new_beacons = []
        sign = -1 if inverted else 1
        for beacon in self.beacons:
            new_beacons.append(self.rotate(beacon, x_rotations, y_rotations, z_rotations, inverted))

        return new_beacons

    def rotate(self, beacon, x_rotations, y_rotations, z_rotations, inverted):

        sign = -1 if inverted else 1
        new_beacon = beacon

        for i in range(0, x_rotations):
            new_beacon = (new_beacon[0], sign*-new_beacon[2], sign*new_beacon[1])

        for i in range(0, y_rotations):
            new_beacon = (sign*-new_beacon[2], new_beacon[1], sign*new_beacon[0])

        for i in range(0, z_rotations):
            new_beacon = (sign*-new_beacon[1], sign*new_beacon[0], new_beacon[2])

        return new_beacon





def solve():

    with open("input19-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        scanners = []
        beacons = []
        for line in lines:
            if line[0:2] == '--':

                if len(beacons) > 0:
                    print(beacons)
                    scanners.append(Scanner(beacons))

                beacons = []

            elif len(line) > 0:
                split = line.split(",")
                beacons.append((int(split[0]), int(split[1]), int(split[2])))

        if len(beacons) > 0:
            print(beacons)
            scanners.append(Scanner(beacons))


        def is_all_done():
            for scanner in scanners:
                if not scanner.is_all_identified():
                    return False
            return True

        world_rotated_scanners = [scanners[0]]
        unfixed_scanners = scanners[1:]
        print(unfixed_scanners)

        def step():
            print(f"Try to match {len(world_rotated_scanners)} world scanners to {len(unfixed_scanners)} unfixed ones")
            for idx in range(0, len(world_rotated_scanners)):
                for other_idx in range(0, len(unfixed_scanners)):
                    scanner = world_rotated_scanners[idx]
                    other_scanner = unfixed_scanners[other_idx]
                    world_scanner = scanner.find_relative_position_of_other(other_scanner)
                    if world_scanner is not None:
                        print(f"Found overlap between scanner {idx} and {other_idx}, rotate the scanner to world coordinates...")
                        world_rotated_scanners.append(world_scanner)
                        unfixed_scanners.pop(other_idx)
                        return True
            return False

        while step():
            print("Step done!")

        world_beacons = {}
        for scanner in world_rotated_scanners:
            for beacon in scanner.beacons:
                world_beacons[str(beacon)] = True

        print(f"Found {len(world_beacons)} unique beacons")

        max_distance = 0
        for scanner in world_rotated_scanners:
            for other_scanner in world_rotated_scanners:
                max_distance = max(max_distance, abs(scanner.offset[0] - other_scanner.offset[0]) + abs(scanner.offset[1] - other_scanner.offset[1]) + abs(scanner.offset[2] - other_scanner.offset[2]))

        print(f"The max manhattan distance is {max_distance}")


        print("DONE")

solve()
