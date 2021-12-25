from itertools import groupby, repeat
import re
import math
import pprint
import functools

pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


class Node:

    id_counter = 0

    def __init__(self, room, name, target_letter):
        self.connections = []
        self.target_letter = target_letter
        self.name = name
        self.amphipod = None
        self.id = Node.id_counter
        Node.id_counter += 1

    def add_connection(self, node, cost):
        node.connections.append({
            "node": self,
            "cost": cost
        })
        self.connections.append({
            "node": node,
            "cost": cost
        })

    def precalculate_routes(self):

        visited = set()
        open = [{
            "path": [],
            "node": self,
            "cost": 0
        }]
        routes = {}
        while len(open) > 0:
            next = open.pop()

            visited.add(next["node"])

            connections = next["node"].connections
            for connection in connections:
                if connection["node"] in visited:
                    continue

                path = next["path"].copy()
                path.append(connection["node"])
                cost = next["cost"] + connection["cost"]
                route = {
                    "path": path,
                    "node": connection["node"],
                    "cost": cost
                }
                visited.add(connection["node"])
                routes[connection["node"].id] = route
                open.append(route)

        #print(f"Routes for node {self.name}:")
        #for route in routes:
        #    pp.pprint(routes[route])

        self.routes = routes


    def __repr__(self):
        #return f"{self.name} connected to [{[conn['node'].name for conn in self.connections]}]"
        return f"{self.name}"

    def is_available(self):
        return self.amphipod is None

    def is_room(self):
        return self.target_letter is not None

    def is_valid_room(self, letter):
        return self.target_letter == letter or self.target_letter is None

    def contains_bad_amphipod(self):
        if self.amphipod is None:
            return False
        return self.amphipod.letter != self.target_letter

    def get_print(self):
        if self.amphipod == None:
            return '.'
        else:
            return str(self.amphipod.letter)


class Amphipod:

    id_counter = 0

    def __init__(self, start_node, letter, room_nodes):
        self.node = start_node
        self.letter = letter
        self.node.amphipod = self
        self.target_nodes = list(filter(lambda node: node.target_letter == letter, room_nodes))
        self.has_left_room = False
        self.id = Amphipod.id_counter
        Amphipod.id_counter += 1
        print(f"Amphipod {letter} wants to move to:")
        pp.pprint(self.target_nodes)

    def get_move_cost(self):
        return 10 ** self.letter

    def is_done(self):
        return self.node.target_letter == self.letter

    def move_to(self, target_node):
        self.node.amphipod = None
        target_node.amphipod = self
        self.node = target_node
        if not self.node.is_room():
            self.has_left_room = True

    def get_possible_moves(self):

        # we are where we want to be
        if self.is_done() and self.has_left_room:
            return []

        # if we are in the hallway, we see if we can move into the room we need to go
        node = self.node
        if not self.node.is_room():

            # order is important here - we always want to check the backside first, never moving to entrance if backside is available
            reachable_route = self.get_reachable_target_route()
            if reachable_route is not None:
                return [{
                    "from": node,
                    "had_left_room": self.has_left_room,
                    "to": reachable_route["node"],
                    "cost": reachable_route["cost"] * self.get_move_cost(),
                    "amphipod": self,
                }]
            else:
                return []

        # we are in a room - we can move anywhere, EXCEPT for the wrong room
        else:

            #print("We are in a room")
            moves = []
            for target_node in node.routes.keys():
                route = node.routes[target_node]
                if route["node"].is_room() and route["node"].target_letter == node.target_letter:
                    continue
                if self.is_valid_move_target(route["node"]) and self.is_valid_route(route):
                    moves.append({
                        "from": node,
                        "had_left_room": self.has_left_room,
                        "to": route["node"],
                        "cost": route["cost"] * self.get_move_cost(),
                        "amphipod": self,
                    })
            return moves

    def is_valid_move_target(self, node):
        if not node.is_available():
            return False

        # can always move OUTSIDE of rooms
        if not node.is_room():
            return True

        # but when we move INTO a room, we cannot block another pod or move into the wrong room
        if not node.is_valid_room(self.letter):
            return False

        for i in range(0, len(self.target_nodes)):
            if self.target_nodes[i] == node:
                break
            if self.target_nodes[i].contains_bad_amphipod():
                return False

        return True


    def is_valid_route(self, route):
        for node in route["path"]:
            if not node.is_available():
                return False
        return True

    def is_valid_route_except_last(self, route):
        for node in route["path"][0:-1]:
            if not node.is_available() and node.amphipod.letter != self.letter:
                return False
        return True

    def get_reachable_target_route(self):

        for i in range(0, len(self.target_nodes)):

            if self.target_nodes[i].is_available():

                ok = True
                for k in range(0, i):
                    if self.target_nodes[k].is_available() or self.target_nodes[k].amphipod.letter != self.target_nodes[k].target_letter:
                        ok = False
                        break

                if ok:
                    route = self.node.routes[self.target_nodes[i].id]
                    if self.is_valid_route(route):
                        return route

        if False:
            # back room is available - always go there
            if self.target_nodes[0].is_available():
                route = self.node.routes[self.target_nodes[0].id]
                if self.is_valid_route(route):
                    return route

            # entrance is available - only go there if we won't block someone in the back
            elif self.target_nodes[1].is_available() and self.target_nodes[0].amphipod.letter == self.target_nodes[0].target_letter:
                route = self.node.routes[self.target_nodes[1].id]
                if self.is_valid_route(route):
                    return route

        # don't go anywhere
        return None


    def __repr__(self):
        return f"{self.letter} at {self.node}"



global_lowest_score = 100000000000000
global_depth = 0

def solve():

    hallway_nodes = [Node(False, f"Hallway {i}", None) for i in range(0, 7)]
    room_entry_nodes = [Node(True, f"Room entrance {i}", i) for i in range(0, 4)]
    room_back_nodes = [Node(True, f"Room backside {i}", i) for i in range(0, 4)]
    room_back2_nodes = [Node(True, f"Room backside2 {i}", i) for i in range(0, 4)]
    room_back3_nodes = [Node(True, f"Room backside3 {i}", i) for i in range(0, 4)]

    # connect the different nodes
    for i in range(0, 4):
        room_back3_nodes[i].add_connection(room_back2_nodes[i], 1)
        room_back2_nodes[i].add_connection(room_back_nodes[i], 1)
        room_back_nodes[i].add_connection(room_entry_nodes[i], 1)
        room_entry_nodes[i].add_connection(hallway_nodes[i+1], 2)
        room_entry_nodes[i].add_connection(hallway_nodes[i+2], 2)
    for i in range(0, 6):
        hallway_nodes[i].add_connection(hallway_nodes[i+1], 1 if i == 0 or i == 5 else 2)

    room_nodes = room_back3_nodes + room_back2_nodes + room_back_nodes + room_entry_nodes
    #room_nodes = room_back_nodes + room_entry_nodes
    all_nodes = hallway_nodes + room_entry_nodes + room_back_nodes + room_back2_nodes + room_back3_nodes
    #all_nodes = hallway_nodes + room_entry_nodes + room_back_nodes
    for node in all_nodes:
        node.precalculate_routes()

    # EXAMPLE
    # amphipods = [
    #     Amphipod(room_entry_nodes[0], 1, room_nodes),
    #     Amphipod(room_back_nodes[0], 3, room_nodes),
    #     Amphipod(room_back2_nodes[0], 3, room_nodes),
    #     Amphipod(room_back3_nodes[0], 0, room_nodes),
    #
    #     Amphipod(room_entry_nodes[1], 2, room_nodes),
    #     Amphipod(room_back_nodes[1], 2, room_nodes),
    #     Amphipod(room_back2_nodes[1], 1, room_nodes),
    #     Amphipod(room_back3_nodes[1], 3, room_nodes),
    #
    #     Amphipod(room_entry_nodes[2], 1, room_nodes),
    #     Amphipod(room_back_nodes[2], 1, room_nodes),
    #     Amphipod(room_back2_nodes[2], 0, room_nodes),
    #     Amphipod(room_back3_nodes[2], 2, room_nodes),
    #
    #     Amphipod(room_entry_nodes[3], 3, room_nodes),
    #     Amphipod(room_back_nodes[3], 0, room_nodes),
    #     Amphipod(room_back2_nodes[3], 2, room_nodes),
    #     Amphipod(room_back3_nodes[3], 0, room_nodes),
    # ]

    # amphipods = [
    #     Amphipod(room_entry_nodes[0], 1, room_nodes),
    #     Amphipod(room_back_nodes[0], 0, room_nodes),
    #
    #     Amphipod(room_entry_nodes[1], 2, room_nodes),
    #     Amphipod(room_back_nodes[1], 3, room_nodes),
    #
    #     Amphipod(room_entry_nodes[2], 1, room_nodes),
    #     Amphipod(room_back_nodes[2], 2, room_nodes),
    #
    #     Amphipod(room_entry_nodes[3], 3, room_nodes),
    #     Amphipod(room_back_nodes[3], 0, room_nodes),
    # ]

    # EXAMPLE
    #
    # amphipods = [
    #     Amphipod(room_entry_nodes[0], 0, room_nodes),
    #     Amphipod(room_back_nodes[0], 3, room_nodes),
    #
    #     Amphipod(room_entry_nodes[1], 2, room_nodes),
    #     Amphipod(room_back_nodes[1], 0, room_nodes),
    #
    #     Amphipod(room_entry_nodes[2], 1, room_nodes),
    #     Amphipod(room_back_nodes[2], 3, room_nodes),
    #
    #     Amphipod(room_entry_nodes[3], 2, room_nodes),
    #     Amphipod(room_back_nodes[3], 1, room_nodes),
    # ]

    amphipods = [
        Amphipod(room_entry_nodes[0], 0, room_nodes),
        Amphipod(room_back_nodes[0], 3, room_nodes),
        Amphipod(room_back2_nodes[0], 3, room_nodes),
        Amphipod(room_back3_nodes[0], 3, room_nodes),

        Amphipod(room_entry_nodes[1], 2, room_nodes),
        Amphipod(room_back_nodes[1], 2, room_nodes),
        Amphipod(room_back2_nodes[1], 1, room_nodes),
        Amphipod(room_back3_nodes[1], 0, room_nodes),

        Amphipod(room_entry_nodes[2], 1, room_nodes),
        Amphipod(room_back_nodes[2], 1, room_nodes),
        Amphipod(room_back2_nodes[2], 0, room_nodes),
        Amphipod(room_back3_nodes[2], 3, room_nodes),

        Amphipod(room_entry_nodes[3], 2, room_nodes),
        Amphipod(room_back_nodes[3], 0, room_nodes),
        Amphipod(room_back2_nodes[3], 2, room_nodes),
        Amphipod(room_back3_nodes[3], 1, room_nodes),
    ]


    move_stack = []

    def apply_move(move):
        move_stack.append(move)
        amphipod = move["amphipod"]
        amphipod.move_to(move["to"])

    def undo_last_move():
        move = move_stack.pop()
        amphipod = move["amphipod"]
        amphipod.move_to(move["from"])
        amphipod.has_left_room = move["had_left_room"]

    def print_state():

        s = ""
        for i in range(0, 7):
            if 1 < i < 6:
                s += "."
            s += hallway_nodes[i].get_print()
        s += "\n"
        s += "  "
        for i in range(0, 4):
            s += room_entry_nodes[i].get_print() + " "
        s += "\n"
        s += "  "
        for i in range(0, 4):
            s += room_back_nodes[i].get_print() + " "
        s += "\n"
        s += "  "
        for i in range(0, 4):
            s += room_back2_nodes[i].get_print() + " "
        s += "\n"
        s += "  "
        for i in range(0, 4):
            s += room_back3_nodes[i].get_print() + " "
        s += "\n"
        print(s)


    def print_stack():
        copy_stack = move_stack.copy()

        while len(move_stack) > 0:
            undo_last_move()

        for move in copy_stack:
            print_state()
            print(f"Apply move {move}")
            apply_move(move)
        print_state()

    def is_deadlock():

        # go over all amphipods outside of their rooms, and see if more than 1 cannot get to their room
        n_blocked = 0
        for amphipod in amphipods:
            target_entrance = room_entry_nodes[amphipod.letter]
            node = amphipod.node
            if node == target_entrance or node.is_room():
                continue
            route = node.routes[target_entrance.id]
            if not amphipod.is_valid_route_except_last(route):
                n_blocked += 1

                if n_blocked > 1:
                    return True
        return False

    lowest_score_by_state = {}

    def get_state_hash():
        hash = []
        for amphipod in amphipods:
            hash.append(amphipod.id)
            hash.append(amphipod.node.id)
        return tuple(hash)

    @functools.lru_cache(maxsize=None)
    def get_lowest_score(state):

        global global_lowest_score

        if len(move_stack) > 50:
            print("WENT TOO DEEP")
            print_stack()
            return 100000000000000

        # see if all amphipods are done, in which case WE are done
        n_done = 0
        for amphipod in amphipods:
            if amphipod.is_done():
                n_done += 1

        if n_done == len(amphipods):

            # calculate total score and update
            total_cost = sum([move["cost"] for move in move_stack])
            if total_cost < global_lowest_score:
                global_lowest_score = total_cost
                print(f"FOUND NEW BEST SCORE:")
                print_stack()
                print(f"BEST SCORE IS {total_cost}")

            return 0

        # go over every amphipod and figure out all possible actions
        total_moves_found = 0
        lowest_cost = 100000000000000
        for amphipod in amphipods:

            #print(f"Get valid moves for {amphipod.letter} at {amphipod.node}:")
            possible_moves = amphipod.get_possible_moves()
            total_moves_found += len(possible_moves)
            for move in possible_moves:
                #print(f"At depth {depth} move {move}")

                apply_move(move)
                best_cost = move["cost"] + get_lowest_score(get_state_hash())
                lowest_cost = min(best_cost, lowest_cost)
                undo_last_move()

        return lowest_cost

    lowest_score = get_lowest_score(get_state_hash())
    print(lowest_score)










solve()