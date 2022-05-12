'''
BIO:
Lee Sang-hyeok (Korean: 이상혁; born May 7, 1996), better known by his in-game name FAIKER (Korean: 페이커), 
is a South Korean professional Dungeon and Data Structures player. Formerly known as GoJeonPa on the Korean server, 
he was picked up by Team Solo Bot in 2013 and has played as the team's bot laner since. He is widely considered to be 
the best Dungeon and Data Structures player of all time.

'''
# import useful packages
import time

PLAYER_1 = '0'
PLAYER_2 = '1'
METAL_BLOCK = 'ib'
WOODEN_BLOCK = 'sb'
ORE_BLOCK = 'ob'
BOMB = 'b'
AMMO = 'a'
TREASURE = 't'

MOVE_WAIT = ''
MOVE_UP = 'u'
MOVE_DOWN = 'd'
MOVE_LEFT = 'l'
MOVE_RIGHT = 'r'
MOVE_BOMB = 'p'


class agent:
    class bomb_state:
        def __init__(self, location, bomb_power):
            self.location = location
            self.bomb_timer = 10
            self.explosion_tick_counter = 2
            explosion_tiles = set()
            for x in range(-bomb_power, bomb_power):
                explosion_tiles.add((location[0] + x, location[1]))
                explosion_tiles.add((location[0], location[1] + x))
            self.explosion_tiles = explosion_tiles

    def __init__(self):
        self.bomb_states = None
        pass

    def next_move(self, game_state, player_state):
        self.game_state = game_state

        self.player_state = player_state
        self.location = player_state.location
        self.bomb_power = player_state.power
        self.update_bomb_state(game_state.bombs)
        self.opponent = 1 if self.player_state.id == 0 else 0
        return self.find_move()

    ########################
    ###     HELPERS      ###
    ########################
    def update_bomb_state(self, new_bombs):
        if self.bomb_states == None:
            self.bomb_states = []
            for bomb in new_bombs:
                self.bomb_states.append(self.bomb_state(bomb, self.bomb_power))
        else:
            bombs_to_check = set(new_bombs)
            new_bomb_states = [bomb_state for bomb_state in self.bomb_states if not bomb_state.explosion_tick_counter == 0]
            self.bomb_states = new_bomb_states
            for bomb_state in self.bomb_states:
                if not bomb_state.location in bombs_to_check:
                    bomb_state.explosion_tick_counter += -1
                bomb_state.bomb_timer += -1
            for new_bomb in new_bombs:
                already_exists = False
                for bomb_state in self.bomb_states:
                    if bomb_state.location == new_bomb:
                        already_exists = True
                        break
                if not already_exists:
                    self.bomb_states.append(self.bomb_state(new_bomb, self.bomb_power))
                    
     
    # returns the manhattan distance between two tiles, calculated as:
    # 	|x1 - x2| + |y1 - y2|
    def manhattan_distance(self, start, end):

        distance = abs(start[0] - end[0]) + abs(start[1] - end[1])

        return distance

    # given a location as an (x,y) tuple and the bombs on the map
    # we'll return a list of the bomb positions that are nearby
    def get_bombs_in_range(self, location, bombs):

        # empty list to store our bombs that are in range of us
        bombs_in_range = []

        # loop through all the bombs placed in the game
        for bomb in bombs:

            # get manhattan distance to a bomb
            distance = self.manhattan_distance(location, bomb)

            # set to some arbitrarily high distance
            if distance <= 10:
                bombs_in_range.append(bomb)

        return bombs_in_range

    # given a tile location as an (x,y) tuple, this function
    # will return the surrounding tiles up, down, left and to the right as a list
    # (i.e. [(x1,y1), (x2,y2),...])
    # as long as they do not cross the edge of the map
    def get_surrounding_tiles(self, location):

        # find all the surrounding tiles relative to us
        # location[0] = col index; location[1] = row index
        tile_up = (location[0], location[1]+1)
        tile_down = (location[0], location[1]-1)
        tile_left = (location[0]-1, location[1])
        tile_right = (location[0]+1, location[1])

        # combine these into a list
        all_surrounding_tiles = [tile_up, tile_down, tile_left, tile_right]

        # we'll need to remove tiles that cross the border of the map
        # start with an empty list to store our valid surrounding tiles
        valid_surrounding_tiles = []

        # loop through our tiles
        for tile in all_surrounding_tiles:
            # check if the tile is within the boundaries of the game
            if self.game_state.is_in_bounds(tile):
                # if yes, then add them to our list
                valid_surrounding_tiles.append(tile)

        return valid_surrounding_tiles

    # given a list of tiles
    # return the ones which are actually empty
    def get_empty_tiles(self, tiles):
        explosion_tiles = self.get_explosion_tiles(0, True)
        # empty list to store our empty tiles
        empty_tiles = []

        for tile in tiles:
            neighbors = self.get_surrounding_tiles_to_move_to(
                tile, self.ENTITIES_YOU_CANT_MOVE_TO, explosion_tiles)
            if not self.game_state.is_occupied(tile) and not tile in explosion_tiles and len(neighbors) > 0:
                # the tile isn't occupied, so we'll add it to the list
                empty_tiles.append(tile)

        return empty_tiles

    # given a list of tiles and bombs
    # find the tile that's safest to move to
    def get_safest_tile(self, tiles, bombs):

        # which bomb is closest to us?
        bomb_distance = 10  # some arbitrary high distance
        closest_bomb = bombs[0]

        for bomb in bombs:
            new_bomb_distance = self.manhattan_distance(bomb, self.location)
            if new_bomb_distance < bomb_distance:
                bomb_distance = new_bomb_distance
                closest_bomb = bomb

        safe_dict = {}
        # now we'll figure out which tile is furthest away from that bomb
        for tile in tiles:
            # get the manhattan distance
            distance = self.manhattan_distance(closest_bomb, tile)
            # store this in a dictionary
            safe_dict[tile] = distance

        # return the tile with the furthest distance from any bomb
        safest_tile = max(safe_dict, key=safe_dict.get)

        return safest_tile

    # given an adjacent tile location, move us there
    def move_to_tile(self, location, tile):

        # see where the tile is relative to our current location
        diff = tuple(x-y for x, y in zip(self.location, tile))

        # return the action that moves in the direction of the tile
        if diff == (0, 1):
            action = 'd'
        elif diff == (1, 0):
            action = 'l'
        elif diff == (0, -1):
            action = 'u'
        elif diff == (-1, 0):
            action = 'r'
        else:
            action = ''

        return action

    ENTITIES_YOU_CANT_MOVE_TO = set([METAL_BLOCK, BOMB])
    TILES_YOU_CANT_MOVE_TO_EXCLUDING_BOMBS = set([METAL_BLOCK])
    DESTRUCTIBLE_BLOCKS = set([WOODEN_BLOCK, ORE_BLOCK])
    CENTRE_TILE = (3,3)

    def calculate_bomb_value(self, bomb_location):
        destructibles = 0
        # left
        for x in range(1, self.bomb_power + 1):
            tile = (bomb_location[0] + x, bomb_location[1])
            if self.game_state.entity_at(tile) in self.DESTRUCTIBLE_BLOCKS:
                destructibles += 50
                break
        # right
        for x in range(1, self.bomb_power + 1):
            tile = (bomb_location[0] - x, bomb_location[1])
            if self.game_state.entity_at(tile) in self.DESTRUCTIBLE_BLOCKS:
                destructibles += 50
                break
        # up
        for x in range(1, self.bomb_power + 1):
            tile = (bomb_location[0], bomb_location[1] + x)
            if self.game_state.entity_at(tile) in self.DESTRUCTIBLE_BLOCKS:
                destructibles += 50
                break
        # down
        for x in range(1, self.bomb_power + 1):
            tile = (bomb_location[0], bomb_location[1] - x)
            if self.game_state.entity_at(tile) in self.DESTRUCTIBLE_BLOCKS:
                destructibles += 50
                break
            
        return destructibles

    def get_explosion_tiles(self, ticks_passed = 0, respect_ticks = True):
        all_explosion_tiles = set()
        for bomb in self.bomb_states:
            if bomb.bomb_timer - ticks_passed <= 0 or not respect_ticks:
                for explosion_tile in bomb.explosion_tiles:
                    all_explosion_tiles.add(explosion_tile)
        return all_explosion_tiles

    def get_surrounding_tiles_to_move_to(self, location, entities_to_exclude, tiles_to_exclude):

        # find all the surrounding tiles relative to us
        # location[0] = col index; location[1] = row index
        tile_up = (location[0], location[1]+1)
        tile_down = (location[0], location[1]-1)
        tile_left = (location[0]-1, location[1])
        tile_right = (location[0]+1, location[1])

        # combine these into a list
        all_surrounding_tiles = [tile_up, tile_down, tile_left, tile_right]

        # we'll need to remove tiles that cross the border of the map
        # start with an empty list to store our valid surrounding tiles
        valid_surrounding_tiles = []
        # loop through our tiles
        for tile in all_surrounding_tiles:
            # check if the tile is within the boundaries of the game
            entity = self.game_state.entity_at(tile)
            if self.game_state.is_in_bounds(tile) and not entity in entities_to_exclude and not tile in tiles_to_exclude:
                # if yes, then add them to our list
                valid_surrounding_tiles.append(tile)

        return valid_surrounding_tiles

    class move_data:
        def __init__(self):
            self.path = []
            self.move = None
            self.score = 0

        def move_str(self, location, tile):
            # see where the tile is relative to our current location
            diff = tuple(x-y for x, y in zip(location, tile))

            # return the action that moves in the direction of the tile
            if diff == (0, 1):
                action = 'D '
            elif diff == (1, 0):
                action = 'L '
            elif diff == (0, -1):
                action = 'U '
            elif diff == (-1, 0):
                action = 'R '
            else:
                action = ''
            return action       

        def to_string(self):
            path_str = ""
            from_tile = None
            for tile in self.path:
                if not from_tile == None:
                    path_str += self.move_str(from_tile, tile)
                from_tile = tile
                
            return f"""
Path as actions: {path_str}
Move: {self.move}
Score: {self.score}
            """

    def find_move(self):
        all_moves = []
        visited = set()
        queue = []
        first = self.move_data()
        first.path.append(self.location)
        queue.append(first)
        immediate_explosion_tiles_ticks_ignored = self.get_explosion_tiles(0, False)
        immediate_explosion_tiles_ticks_respected = self.get_explosion_tiles(0, True)
        currently_on_explosion_tile = self.location in immediate_explosion_tiles_ticks_respected
        while queue:
            move_data = queue.pop(0)
            move_data.score += -10
            node = move_data.path[-1]
            path_length = len(move_data.path)
            explosion_tiles = self.get_explosion_tiles(path_length - 1)
            neighbors = self.get_surrounding_tiles_to_move_to(
                node, self.ENTITIES_YOU_CANT_MOVE_TO, explosion_tiles)
            entity = self.game_state.entity_at(node)
            
            if len(neighbors) == 0:
                visited.add(node)
                continue
            
            if entity in self.DESTRUCTIBLE_BLOCKS:
                if path_length == 2:
                    move_data.move = MOVE_BOMB
                else:
                    move_data.move = self.move_to_tile(self.location, move_data.path[1])

                if self.player_state.ammo == 0 or node in immediate_explosion_tiles_ticks_ignored:
                    continue
                else:
                    move_data.score += self.calculate_bomb_value(node)
                all_moves.append(move_data)
            elif entity == AMMO:
                if self.player_state.ammo == 0:
                    move_data.score += 10
                move_data.score += 10
                move_data.move = self.move_to_tile(self.location, move_data.path[1])
                all_moves.append(move_data)
            elif entity == TREASURE:
                move_data.move = self.move_to_tile(self.location, move_data.path[1])
                move_data.score += 20
                all_moves.append(move_data)
            # Add empty tiles as movement options if we're on an explosion tile and we're out of ammo
            elif currently_on_explosion_tile and not self.game_state.is_occupied(node):
                # This has more value the further away it is from a bomb.
                move_data.move = self.move_to_tile(self.location, move_data.path[1])
                if node in explosion_tiles:
                    move_data.score += -100
                move_data.score += 2
                all_moves.append(move_data)
            elif entity == self.opponent:
                if path_length == 2:
                    move_data.move = MOVE_BOMB
                else:
                    move_data.move = self.move_to_tile(self.location, move_data.path[1])

                no_blocks_left = len(self.game_state.soft_blocks) == 0 and len(self.game_state.ore_blocks) == 0 
                if self.player_state.ammo == 0 or node in explosion_tiles or not no_blocks_left:
                    continue
                else:
                    move_data.score += 50
                all_moves.append(move_data)
            elif node not in visited:
                for neighbor in neighbors:
                    new_path = move_data.path.copy()
                    new_path.append(neighbor)
                    new_move_data = self.move_data()
                    new_move_data.path = new_path
                    new_move_data.score = move_data.score
                    queue.append(new_move_data)
                visited.add(node)
        if len(all_moves) == 0:
            surrounding_tiles = self.get_surrounding_tiles(self.location)
            empty_tiles = self.get_empty_tiles(surrounding_tiles)
            if empty_tiles:
                # If we have no moves, lets go back to the middle of the map.
                closest_tile = empty_tiles[0]
                closest_tile_distance = 34 #werwe 
                for tile in empty_tiles:
                    distance = self.manhattan_distance(tile, self.CENTRE_TILE)
                    if distance < closest_tile_distance:
                        closest_tile = tile
                        closest_tile_distance = distance
                return self.move_to_tile(self.location, closest_tile)
            else:
                return ''
        all_moves.sort(key=lambda x: x.score, reverse=True)        
        best_move = all_moves[0]
        return best_move.move
   