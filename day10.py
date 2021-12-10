
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy



def solve():
    with open("input10-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        brackets = {
            '(': ')',
            '[': ']',
            '{': '}',
            '<': '>'
        }
        points = {
            ')': 3,
            ']': 57,
            '}': 1197,
            '>': 25137
        }

        autocomplete_points = {
            ')': 1,
            ']': 2,
            '}': 3,
            '>': 4
        }

        syntax_score = 0
        autocomplete_scores = []
        for line in lines:
            stack = []
            corrupted = False
            for c in line:
                #print(stack)

                if c in brackets.keys():
                    stack.append(c)
                else:
                    if c == brackets[stack[-1]]:
                        stack = stack[:-1]

                    else:
                        corrupted = True
                        syntax_score += points[c]
                        break


            if not corrupted:
                autocomplete_score = 0
                while len(stack) > 0:
                    next_closing_char = brackets[stack[-1]]
                    autocomplete_score = autocomplete_score * 5 + autocomplete_points[next_closing_char]
                    stack = stack[:-1]
                autocomplete_scores.append(autocomplete_score)

        autocomplete_scores = sorted(autocomplete_scores)
        final_autocomplete_score = autocomplete_scores[math.floor(len(autocomplete_scores)/2)]



        print(f"The total syntax score is {syntax_score}")
        print(f"The total autocomplete score is {final_autocomplete_score}")





solve()