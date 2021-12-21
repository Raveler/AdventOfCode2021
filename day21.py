from itertools import groupby
import re
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


class PlayerNormal:

    def __init__(self, pos):
        self.pos = pos
        self.score = 0

    def step(self, die):
        spaces = die+(die+1)+(die+2)
        self.pos = (self.pos + spaces) % 10
        self.score += self.pos+1
        #print(f"We are at pos {self.pos} with die {die} and score {self.score}")
        return die+3

    def is_done(self):
        return self.score >= 21


def solve():

    with open("input21-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        regexp = re.compile(r"Player [0-9] starting position: ([0-9]+)")

        p1 = int(regexp.match(lines[0]).groups()[0])-1
        p2 = int(regexp.match(lines[1]).groups()[0])-1
        players = [
            PlayerNormal(p1),
            PlayerNormal(p2)
        ]

        turn = 0
        die = 1
        while True:
            die = players[turn].step(die)
            if players[turn].is_done():
                break
            turn = 1-turn

        loser = 1-turn
        die_rolls = die-1
        print(f"Player {loser+1} has won after {die_rolls} die rolls with a score of {players[loser].score}")
        print(f"The result is {die_rolls*players[loser].score}")
        print(die)

class Player:

    def __init__(self, pos, score):
        self.pos = pos
        self.score = score

    def calculate_step_count(self):
        step_count = {}
        self.calculate_step_count_internal(step_count)

    def calculate_step_count_internal(self, pos, score, step_count):
        pos = (self.pos + 1) % 10
        yield Player(pos, self.score + pos + 1)
        pos = (pos + 1) % 10
        yield Player(pos, self.score + pos + 1)
        pos = (pos + 1) % 10
        yield Player(pos, self.score + pos + 1)

    def is_done(self):
        return self.score >= 21


def calculate_step_count(distribution, pos, score, steps, step_count, times):
    if score >= 21:
        #print(f"After {steps} steps, we are at {pos} with score {score}")
        step_count[steps] += times
        return

    if steps > 5000:
        return

    for roll in distribution:
        times_multiplier = distribution[roll]
        new_pos = (pos + roll) % 10
        calculate_step_count(distribution, new_pos, score + new_pos + 1, steps + 1, step_count, times * times_multiplier)


def calculate_winner(distribution, players, scores, turn, times, winners, depth = 0):

    if scores[turn] >= 21:
        winners[turn] += times
        return

    if depth == 15:
        print(f"Entering depth {depth} after {times} times")

    turn = 1-turn

    for roll in distribution:
        times_multiplier = distribution[roll]
        new_players = players.copy()
        new_scores = scores.copy()
        new_players[turn] = (players[turn] + roll) % 10
        new_scores[turn] = scores[turn] + new_players[turn] + 1
        calculate_winner(distribution, new_players, new_scores, turn, times * times_multiplier, winners, depth + 1)

def solve_dirac():

    with open("input21-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        regexp = re.compile(r"Player [0-9] starting position: ([0-9]+)")

        p1 = int(regexp.match(lines[0]).groups()[0])-1
        p2 = int(regexp.match(lines[1]).groups()[0])-1

        # calculate the distribution of rolling 3 times 3 dice
        distribution = defaultdict(lambda: 0)
        for x in range(1, 4):
            for y in range(1, 4):
                for z in range(1, 4):
                    distribution[x+y+z] += 1

        winners = defaultdict(lambda: 0)
        calculate_winner(distribution, [p1, p2], [0, 0], 1, 1, winners)
        print(winners)




solve_dirac()
