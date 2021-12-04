
from itertools import groupby

board_size = 5


class Board:

    def __init__(self, lines):

        self.board = {}
        self.marked = {}

        for y in range(0, board_size):
            split = lines[y].split()
            for x in range(0, board_size):
                self.board[(x,y)] = int(split[x])
                self.marked[(x,y)] = False
        print(self.board)

    def mark(self, number):
        for x in range(0, board_size):
            for y in range(0, board_size):
                if self.board[(x,y)] == number:
                    self.marked[(x,y)] = True

    def is_done(self):

        for i in range(0, board_size):

            horizontal_marked = 0
            vertical_marked = 0
            for j in range(0, board_size):
                if self.marked[(i,j)]:
                    horizontal_marked += 1

                if self.marked[(j,i)]:
                    vertical_marked += 1

            if horizontal_marked == board_size or vertical_marked == board_size:
                return True

        return False

    def get_score(self):
        score = 0
        for x in range(0, board_size):
            for y in range(0, board_size):
                if not self.marked[(x,y)]:
                    score += self.board[(x,y)]
        return score

    def print(self):
        s = ""
        for y in range(0, board_size):
            for x in range(0, board_size):
                s = s + str(self.board[(x, y)])
                if self.marked[(x, y)]:
                    s += "[X]"
                s += " "
            s += "\n"
        print(s)



def part_1():
    with open("input4-2.txt") as f:
        lines = f.readlines()

        print(lines)
        print(lines[0].split(","))
        numbers = list(map(int, lines[0].split(",")))
        print(numbers)

        boards = []
        for i in range(2, len(lines), board_size+1):
            print(f"Create board for lines {i}")
            print(lines[i:i+board_size])
            board = Board(lines[i:i+board_size])
            boards.append(board)
            print(board)

        print(f"There are {len(boards)} boards!")

        done = False

        for i in range(0, len(numbers)):
            print(f"DRAW {numbers[i]}:")
            for board_index in range(0, len(boards)):
                board = boards[board_index]
                board.mark(numbers[i])
                if board.is_done():
                    print(f"Board {board_index} is done after {i} numbers were drawn (last number: {numbers[i]})...")
                    score = board.get_score()
                    final_score = score * numbers[i]

                    print(f"FINAL SCORE FOR BOARD: {final_score}")
                    board.print()
                    done = True
            if done:
                return


def part_2():
    with open("input4-2.txt") as f:
        lines = f.readlines()

        print(lines)
        print(lines[0].split(","))
        numbers = list(map(int, lines[0].split(",")))
        print(numbers)

        boards = []
        for i in range(2, len(lines), board_size + 1):
            print(f"Create board for lines {i}")
            print(lines[i:i + board_size])
            board = Board(lines[i:i + board_size])
            boards.append(board)
            print(board)

        print(f"There are {len(boards)} boards!")

        done = False

        n_won = 0
        for i in range(0, len(numbers)):
            for board_index in range(0, len(boards)):
                board = boards[board_index]
                if board.is_done():
                    continue

                board.mark(numbers[i])
                if board.is_done():
                    print(f"Board {board_index} is done after {i} numbers were drawn (last number: {numbers[i]})...")
                    score = board.get_score()
                    final_score = score * numbers[i]

                    print(f"FINAL SCORE FOR BOARD: {final_score}")
                    board.print()
                    n_won += 1

                    if n_won == len(boards):
                        print("This was the last board!")
                        done = True
            if done:
                return


part_2()




