
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)

def part_1():
    with open("input8-2.txt") as f:
        lines = f.readlines()

        easy_digits = 0

        for line in lines:
            split = line.split("|")
            patterns = [sorted(list(pattern)) for pattern in split[0].split()]
            outputs = [sorted(list(output)) for output in split[1].split()]
            print(patterns)
            print(outputs)

            for output in outputs:
                if len(output) == 2 or len(output) == 4 or len(output) == 3 or len(output) == 7:
                    easy_digits += 1

        print(f"Total easy digits: {easy_digits}")


def get_patterns_with_count(patterns, n):
    return list(filter(lambda pattern: len(pattern) == n, patterns))


def eliminate_mappings(possible_mappings, valid_mappings):
    return list(filter(lambda c: c in valid_mappings, possible_mappings))


def filter_pattern_by_count(possible_mappings_per_signal, patterns, valid_mappings):

    # first, set the correct pattern
    pattern = get_patterns_with_count(patterns, len(valid_mappings))[0]
    for signal in pattern:
        possible_mappings_per_signal[signal] = eliminate_mappings(possible_mappings_per_signal[signal], valid_mappings)

    # then, eliminate these outputs from all other candidates
    for signal in possible_mappings_per_signal:
        if not signal in pattern:
            possible_mappings_per_signal[signal] = list(filter(lambda c: c not in valid_mappings, possible_mappings_per_signal[signal]))

    return pattern


def find_patterns_with_signals(patterns, signals, n):
    patterns = list(filter(lambda pattern: len(pattern) == n and set(signals) < set(pattern), patterns))
    return patterns


def find_mappings_with_targets(possible_mappings_per_signal, targets):
    mappings = list(filter(
        lambda signal: len(set(possible_mappings_per_signal[signal]).intersection(set(targets))) != 0,
        possible_mappings_per_signal.keys()))
    return mappings


def remove_pattern(patterns, pattern):
    return list(filter(lambda p: set(p) != set(pattern), patterns))

def part_2():
    with open("input8-2.txt") as f:
        lines = f.readlines()

        sum = 0
        for line in lines:
            split = line.split("|")
            patterns = [sorted(list(pattern)) for pattern in split[0].split()]
            outputs = split[1].split()

            # create a list of candidates

            possible_mappings_per_signal = {}
            for i in range(0, 7):
                possible_mappings_per_signal[chr(ord('a') + i)] = [chr(ord('a') + k) for k in range(0, 7)]

            # go over all patterns and eliminate the mappings we can NOT be
            one = filter_pattern_by_count(possible_mappings_per_signal, patterns, ['c', 'f'])
            seven = filter_pattern_by_count(possible_mappings_per_signal, patterns, ['a', 'c', 'f'])
            four = filter_pattern_by_count(possible_mappings_per_signal, patterns, ['b', 'c', 'd', 'f'])
            eight = filter_pattern_by_count(possible_mappings_per_signal, patterns, ['a', 'b', 'c', 'd', 'e', 'f', 'g'])

            #b_or_d = list(filter(lambda signal: 'b' in possible_mappings_per_signal[signal] or 'd' in possible_mappings_per_signal[signal], possible_mappings_per_signal.keys()))
            b_or_d = find_mappings_with_targets(possible_mappings_per_signal, ['b', 'd'])
            c_or_f = find_mappings_with_targets(possible_mappings_per_signal, ['c', 'f'])
            c_or_f_or_b_or_d = find_mappings_with_targets(possible_mappings_per_signal, ['c', 'f', 'b', 'd'])
            five = find_patterns_with_signals(patterns, b_or_d, 5)[0]
            three = find_patterns_with_signals(patterns, c_or_f, 5)[0]

            patterns = remove_pattern(patterns, one)

            patterns = remove_pattern(patterns, seven)
            patterns = remove_pattern(patterns, four)
            patterns = remove_pattern(patterns, eight)
            patterns = remove_pattern(patterns, five)
            patterns = remove_pattern(patterns, three)

            two = get_patterns_with_count(patterns, 5)[0]
            patterns = remove_pattern(patterns, two)

            nine = find_patterns_with_signals(patterns, c_or_f_or_b_or_d, 6)[0]
            patterns = remove_pattern(patterns, nine)
            six = find_patterns_with_signals(patterns, b_or_d, 6)[0]
            patterns = remove_pattern(patterns, six)

            zero = patterns[0]

            final_mapping = {
                ''.join(zero): 0,
                ''.join(one): 1,
                ''.join(two): 2,
                ''.join(three): 3,
                ''.join(four): 4,
                ''.join(five): 5,
                ''.join(six): 6,
                ''.join(seven): 7,
                ''.join(eight): 8,
                ''.join(nine): 9
            }

            number = 0
            place = 1
            for i in range(0, 4):
                digit = outputs[3-i]
                value = final_mapping[''.join(sorted(digit))]
                number += place * value
                place *= 10

            #print(f"FINAL NUMBER: {number}")
            sum += number

        print(f"FINAL SUM: {sum}")




part_2()