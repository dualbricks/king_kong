'''
TEMPLATE for creating your own Agent to compete in
'Dungeons and Data Structures' at the Coder One AI Sports Challenge 2020.
For more info and resources, check out: https://bit.ly/aisportschallenge

BIO:
Floth - The fastest ~Sloth~ (The Three toes Assassin!)
Use A* Search approach to find the shortest path from agent to the target tile
- Heuristic function used Manhattan Distance (City Block)
- But just A* Search is not enough since there are many scenarios and targets
- Calculate the score of each tiles in the game to determine the targets
- Kill the slow starter and Assassinate when there is a chance!!!!

    FFFFFFFFFFFFFFFFFFFFFFlllllll                           tttt         hhhhhhh
    F::::::::::::::::::::Fl:::::l                        ttt:::t         h:::::h
    F::::::::::::::::::::Fl:::::l                        t:::::t         h:::::h
    FF::::::FFFFFFFFF::::Fl:::::l                        t:::::t         h:::::h
      F:::::F       FFFFFF l::::l    ooooooooooo   ttttttt:::::ttttttt    h::::h hhhhh
      F:::::F              l::::l  oo:::::::::::oo t:::::::::::::::::t    h::::hh:::::hhh
      F::::::FFFFFFFFFF    l::::l o:::::::::::::::ot:::::::::::::::::t    h::::::::::::::hh
      F:::::::::::::::F    l::::l o:::::ooooo:::::otttttt:::::::tttttt    h:::::::hhh::::::h
      F:::::::::::::::F    l::::l o::::o     o::::o      t:::::t          h::::::h   h::::::h
      F::::::FFFFFFFFFF    l::::l o::::o     o::::o      t:::::t          h:::::h     h:::::h
      F:::::F              l::::l o::::o     o::::o      t:::::t          h:::::h     h:::::h
      F:::::F              l::::l o::::o     o::::o      t:::::t    tttttth:::::h     h:::::h
    FF:::::::FF           l::::::lo:::::ooooo:::::o      t::::::tttt:::::th:::::h     h:::::h
    F::::::::FF           l::::::lo:::::::::::::::o      tt::::::::::::::th:::::h     h:::::h
    F::::::::FF           l::::::l oo:::::::::::oo         tt:::::::::::tth:::::h     h:::::h
    FFFFFFFFFFF           llllllll   ooooooooooo             ttttttttttt  hhhhhhh     hhhhhhh
'''


import numpy as np
from heapq import heapify, heappush, heappop
from collections import deque, defaultdict


class Agent:

    def __init__(self):
        self.name = "Floth"
        self.rows = 7
        self.cols = 7
        self.bomb_tick = 20
        self.prev_tick = 0
        self.prev_action = 0
        self.prev_position = None
        self.player_position = (0, 0)
        self.player_id = 0
        self.bomb_dict = {}
        self.exploded_bomb_dict = {}
        self.ore_dict = {}
        self.init_ore_dict = True
        self.queue_action = ""
        self.lag = False
        self.board_mapping = {
            0: 0,
            1: 1,
            "0": 0,
            "1": 1,
            "sb": 2,
            "ib": 3,
            "ob": 4,
            "b": 5,
            "a": 6,
            "t": 7,
            None: 8
        }
        self.not_block = [0, 1, 6, 7, 8]
        self.opponent_position = (0, 0)
        self.opponent_moved = False

    def get_surrounding_tiles(self, tile):
        if tile[1] > 0:
            yield (tile[0], tile[1] - 1), "d"
        if tile[1] < self.rows - 1:
            yield (tile[0], tile[1] + 1), "u"
        if tile[0] > 0:
            yield (tile[0] - 1, tile[1]), "l"
        if tile[0] < self.cols - 1:
            yield (tile[0] + 1, tile[1]), "r"

    def get_bomb_range_tiles(self, board, tile, current=False):
        if current:
            yield  tile
        if tile[1] > 0:
            yield (tile[0], tile[1] - 1)
        if tile[1] < self.rows - 1:
            yield (tile[0], tile[1] + 1)
        if tile[0] > 0:
            yield (tile[0] - 1, tile[1])
        if tile[0] < self.cols - 1:
            yield (tile[0] + 1, tile[1])
        if tile[1] > 1 and board[(tile[0], tile[1] - 1)] in self.not_block:
            yield (tile[0], tile[1] - 2)
        if tile[1] < self.rows - 2 and board[(tile[0], tile[1] + 1)] in self.not_block:
            yield (tile[0], tile[1] + 2)
        if tile[0] > 1 and board[(tile[0] - 1, tile[1])] in self.not_block:
            yield (tile[0] - 2, tile[1])
        if tile[0] < self.cols - 2 and board[(tile[0] + 1, tile[1])] in self.not_block:
            yield (tile[0] + 2, tile[1])

    def get_surrounding_n_tiles(self, tile, n=1):
        for i in range(n):
            if tile[1] > i:
                yield (tile[0], tile[1] - 1 - i), "d"
            if tile[1] < self.rows - 1 - i:
                yield (tile[0], tile[1] + 1 + i), "u"
            if tile[0] > i:
                yield (tile[0] - 1 - i, tile[1]), "l"
            if tile[0] < self.cols - 1 - i:
                yield (tile[0] + 1 + i, tile[1]), "r"

    def astar(self, impassable_positions, end, exploding_tiles):
        start_node = Node(None, self.player_position, None)
        end_node = Node(None, end, None)
        open_set = [start_node]
        heapify(open_set)
        closed_set = set()

        while open_set:
            current = heappop(open_set)
            closed_set.add(current.position)
            if current == end_node:
                path = deque()
                while current:
                    path.appendleft(current)
                    current = current.parent
                return list(path)
            for tile, action in self.get_surrounding_tiles(current.position):
                if tile in impassable_positions or tile in closed_set or tile in exploding_tiles[current.g]:
                    continue
                neighbour = Node(current, tile, action)
                neighbour.g = current.g + 1
                neighbour.h = abs(tile[0] - end_node.position[0]) + abs(tile[1] - end_node.position[1])
                neighbour.f = neighbour.g + neighbour.h
                if neighbour not in open_set:
                    heappush(open_set, neighbour)

    def path_to_target_tile(self, impassable_positions, score_dict, exploding_tiles):
        action = ""
        for score in sorted(score_dict, reverse=True):
            max_path_score = 0
            for target in score_dict[score]:
                path = self.astar(impassable_positions, target, exploding_tiles)
                if path:
                    path_score = self.rows + self.cols - len(path)
                    if path_score > max_path_score:
                        max_path_score = path_score
                        action = "".join(node.action for node in path[1:4])
                        if not action and score >= 0.4:
                            action = "p"
            if action:
                return action
        return ""

    def not_in_bomb_range(self, board, position):
        for tile in self.get_bomb_range_tiles(board, position):
            if board[tile] == 5:
                return False
        return True

    def place_bomb(self, board, player_state, score_dict):
        if player_state.ammo:
            for score in sorted(score_dict, reverse=True)[:5]:
                if score <= 0.4:
                    continue
                for tile, action in self.get_surrounding_tiles(self.player_position):
                    if board[tile] < 6:
                        continue
                    if tile in score_dict[score] and self.player_position not in score_dict[score]:
                        return action
                if self.player_position in score_dict[score]:
                    return "p"
        return ""

    def update_state_dict(self, board, bombs):
        for bomb in bombs:
            if bomb in self.bomb_dict:
                self.bomb_dict[bomb] -= 1
            else:
                self.bomb_dict[bomb] = self.bomb_tick
                for tile in self.get_bomb_range_tiles(board, bomb):
                    self.bomb_dict[bomb] = min(self.bomb_dict[bomb], self.bomb_dict.get(tile, self.bomb_tick) + 1)
                blocked = set()
                for tile, action in self.get_surrounding_n_tiles(bomb, 2):
                    if action in blocked:
                        continue
                    if 2 <= board[tile] <= 3:
                        blocked.add(action)
                    elif tile in self.ore_dict:
                        if action == "u" and tile[1] > 0 and (bomb[0], bomb[1] - 1) in self.bomb_dict:
                            continue
                        if action == "d" and tile[1] < self.rows - 1 and (bomb[0], bomb[1] + 1) in self.bomb_dict:
                            continue
                        if action == "r" and tile[0] > 0 and (bomb[0] - 1, bomb[1]) in self.bomb_dict:
                            continue
                        if action == "l" and tile[0] < self.cols - 1 and (bomb[0] + 1, bomb[1]) in self.bomb_dict:
                            continue
                        self.ore_dict[tile] -= 1
                        if self.ore_dict[tile] <= 0:
                            del self.ore_dict[tile]
                        blocked.add(action)

        for bomb in list(self.bomb_dict.keys()):
            if bomb not in bombs:
                self.bomb_dict[bomb] -= 1
                if self.bomb_dict[bomb] <= 0:
                    del self.bomb_dict[bomb]

    def calculate_tile_score(self, board, player_state, position):
        score = 0

        # no ammo
        if player_state.ammo == 0:
            state = board[position]
            if state == self.player_id:
                score += 0.1
            elif state == 5:
                score += -100
            elif state == 6:
                score += 50
            elif state == 7:
                score += 2
            elif state == 8:
                score += 0.1

            blocked = set()
            for tile, action in self.get_surrounding_n_tiles(position, 2):
                if action in blocked:
                    continue
                state = board[tile]
                if state == self.player_id:
                    score += 0.1
                elif state == 2:
                    score += -0.1
                    blocked.add(action)
                elif state == 3:
                    score += -0.3
                    blocked.add(action)
                elif state == 4:
                    score += -0.2
                    blocked.add(action)
                elif state == 5:
                    score += -5
                    blocked.add(action)
                elif state == 8:
                    score += 0.1
        else:
            state = board[position]
            if state == self.player_id:
                score += 0.1
            elif state == 5:
                score += -100
            elif state == 6:
                score += 5
            elif state == 7:
                score += 1
            elif state == 8:
                score += 0.1

            blocked = set()
            for tile, action in self.get_surrounding_n_tiles(position, 2):
                if action in blocked:
                    continue
                state = board[tile]
                if state == self.player_id:
                    score += 0.1
                elif state == 2:
                    if self.not_in_bomb_range(board, tile):
                        score += 2.5
                    blocked.add(action)
                elif state == 3:
                    blocked.add(action)
                elif state == 4:
                    if self.ore_dict.get(tile) == 1:
                        score += 10
                    else:
                        score += 1
                    blocked.add(action)
                elif state == 5:
                    score += -25
                    blocked.add(action)
                elif state == 8:
                    score += 0.1
        return score

    def strategy1(self, board, player_state, impassable_positions):
        # initialize
        exploding_tiles = defaultdict(set)
        score_dict = defaultdict(list)

        # calculate the score of each tile
        for x in range(self.cols):
            for y in range(self.rows):
                position = (x, y)
                # populate tiles in bomb range
                if position in self.bomb_dict:
                    for tile in self.get_bomb_range_tiles(board, position, current=True):
                        if board[tile] in self.not_block:
                            for i in range(5 - player_state.hp):
                                exploding_tiles[max(0, self.bomb_dict[position] - i - 1)].add(tile)
                score_dict[self.calculate_tile_score(board, player_state, position)].append(position)

        # kill slow starter and trap opponent
        count = 0
        window_size = 0
        for x in range(self.opponent_position[0] - 1, self.opponent_position[0] + 2, 1):
            for y in range(self.opponent_position[1] - 1, self.opponent_position[1] + 2, 1):
                if x < 0 or x > self.cols - 1 or y < 0 or y > self.rows - 1:
                    continue
                window_size += 1
                if board[(x, y)] not in self.not_block:
                    count += 1
        if player_state.ammo > 0 and (not self.opponent_moved or count >= window_size / 3):
            for tile in self.get_bomb_range_tiles(board, self.opponent_position):
                if board[tile] != 5 and self.not_in_bomb_range(board, tile):
                    dis = abs(tile[0] - self.opponent_position[0]) + abs(tile[1] - self.opponent_position[1])
                    score_dict[30 / dis].append(tile)

        return self.place_bomb(board, player_state, score_dict) or self.path_to_target_tile(impassable_positions, score_dict, exploding_tiles)

    def next_move(self, game_state, player_state):
        players = []
        board = []
        for x in range(self.cols):
            row = []
            for y in range(self.rows):
                position = (x, y)
                entity = game_state.entity_at(position)
                if isinstance(entity, int):
                    players.append(position)
                row.append(self.board_mapping[entity])
            board.append(row)
        board = np.array(board)
        # init ore block hp
        if self.init_ore_dict:
            for ore_block in game_state.ore_blocks:
                self.ore_dict[ore_block] = 3
            self.init_ore_dict = False
            self.player_id = player_state.id
            self.opponent_position = game_state.opponents(self.player_id)[0]
        # kill slow starter opponent
        if self.prev_tick < 50:
            if game_state.opponents(self.player_id)[0] != self.opponent_position:
                self.opponent_moved = True
        else:
            self.opponent_moved = True
        self.opponent_position = game_state.opponents(self.player_id)[0]
        # update bomb timer in memory
        self.update_state_dict(board, game_state.bombs)

        # workaround for game_state lag
        if self.prev_position and self.prev_action and not self.lag:
            flag = False
            if self.prev_action == "d" and self.prev_position[1] <= player_state.location[1]:
                flag = True
            elif self.prev_action == "u" and self.prev_position[1] >= player_state.location[1]:
                flag = True
            elif self.prev_action == "l" and self.prev_position[0] <= player_state.location[0]:
                flag = True
            elif self.prev_action == "r" and self.prev_position[0] >= player_state.location[0]:
                flag = True
            elif self.prev_action == "p" and game_state.entity_at(player_state.location) != "b":
                flag = True
            if flag:
                self.lag = True
                if len(self.queue_action) > 1:
                    self.prev_action, self.queue_action = self.queue_action[0], self.queue_action[1:]
                else:
                    self.prev_action, self.queue_action = self.queue_action, ""

                self.prev_position = player_state.location
                return self.prev_action
        elif self.lag:
            if len(self.queue_action) > 1:
                self.prev_action, self.queue_action = self.queue_action[0], self.queue_action[1:]
            else:
                self.prev_action, self.queue_action = self.queue_action, ""
            if not self.prev_action:
                self.lag = False
            return self.prev_action

        self.player_position = (player_state.location[0], player_state.location[1])
        action = self.strategy1(board, player_state, game_state.all_blocks + game_state.bombs + players)
        if len(action) > 1:
            action, self.queue_action = action[0], action[1:]
        else:
            self.queue_action = ""
        self.prev_position = player_state.location
        self.prev_action = action
        self.prev_tick = game_state.tick_number
        return action


class Node:

    def __init__(self, parent=None, position=None, action=None):
        self.parent = parent
        self.position = position
        self.action = action
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f