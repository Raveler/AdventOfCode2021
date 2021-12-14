
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
from collections import Counter


def solve_1():
    with open("input14-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        template = lines[0]

        regex = re.compile(r"([A-Z]+) -> ([A-Z])")
        rules = {}
        for line in lines[2:]:
            match = regex.match(line)
            groups = match.groups()
            rules[groups[0]] = groups[1]


        steps = 10
        for step in range(0, steps):
            print(f"Step {step}:")
            next_template = ""
            for i in range(0, len(template)-1):
                input = template[i:i+2]
                output = rules[input]
                next_template += input[0] + output

            next_template += template[-1]

            template = next_template

        counter = Counter(template)
        print(counter)
        sorted = counter.most_common()
        score = sorted[0][1] - sorted[-1][1]
        print(f"The final score is {score}")

def solve_2():
    with open("input14-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        template = lines[0]

        regex = re.compile(r"([A-Z]+) -> ([A-Z])")
        rules = {}
        rule_occurence = {}
        letter_occurence = {}
        for line in lines[2:]:
            match = regex.match(line)
            groups = match.groups()
            input = groups[0]
            output = groups[1]
            rules[groups[0]] = [input[0] + output, output + input[1]]
            rule_occurence[input] = template.count(input)
            letter_occurence[output] = template.count(output)

        print(rules)
        print(rule_occurence)
        print(letter_occurence)


        steps = 40
        for step in range(0, steps):
            print(f"Step {step}:")

            next_rule_occurence = rule_occurence.copy()
            for input in rule_occurence:
                n_rules_occurences = rule_occurence[input]
                if n_rules_occurences == 0:
                    continue

                outputs = rules[input]
                letter_occurence[outputs[0][1]] += rule_occurence[input]

                next_rule_occurence[input] -= n_rules_occurences
                next_rule_occurence[outputs[0]] += n_rules_occurences
                next_rule_occurence[outputs[1]] += n_rules_occurences

            rule_occurence = next_rule_occurence

        sorted = Counter(letter_occurence).most_common()
        score = sorted[0][1] - sorted[-1][1]
        print(f"The final score is {score}")









solve_2()