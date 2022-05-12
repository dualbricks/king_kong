import numpy as np


def get_state_for_agent(game_state, player_state, radius, string_format):
        '''
        This method returns a state for the agent. 
        It's a list of length 
        [entity at cell1, 
            ,,     cell2, 
            ,,     cell3,
            ...
            ...
            ,,     cell25],
            distance to enemy,
            contains ammo or not
        '''
        

        # Coordinate of your agent
        x_agent = player_state.location[0]  #x coordinate of agent
        y_agent = player_state.location[1]  #y cooordinate of agent

        # add visible tiles to the state
        visible_tiles = agent_tile_sense(x_agent,y_agent, radius)

        # find what objects exist at the state around your agents.
        if(string_format==True):
            training_state = get_tile_state_str(visible_tiles, game_state, player_state)
        else:
            training_state = get_tile_state_int(visible_tiles, game_state, player_state)



        # add distance to the enemy in your state
        if(string_format ==True):
            list_of_enemy = game_state.opponents(player_state.id)  # find enenmy on the board
            x_enemy = list_of_enemy[0][0] #x coordinates of enemy   
            y_enemy = list_of_enemy[0][1] #y coordinates of enemy
            dis = str(get_distance_to_enemy([x_agent, y_agent], [x_enemy, y_enemy])) # get manhattan distance to enemy
            training_state.append(dis)


            #add if ammo remaining or not
            if(player_state.ammo==0): training_state.append("0")
            else: training_state.append("1")
        else:
            list_of_enemy = game_state.opponents(player_state.id)  # find enenmy on the board
            x_enemy = list_of_enemy[0][0] #x coordinates of enemy   
            y_enemy = list_of_enemy[0][1] #y coordinates of enemy
            dis = get_distance_to_enemy([x_agent, y_agent], [x_enemy, y_enemy]) # get manhattan distance to enemy
            training_state.append(dis)


            #add if ammo remaining or not
            if(player_state.ammo==0): training_state.append(0)
            else: training_state.append(1)



        #convert list to a string
        return training_state

def get_training_state_for_Q(game_state, player_state, radius):
    training_state = get_state_for_agent(game_state=game_state, player_state=player_state, radius=radius, string_format = True)
    training_state = ''.join(training_state)
    return training_state

def get_training_state_for_Deep(game_state, player_state, radius):
    training_state = get_state_for_agent(game_state=game_state, player_state=player_state, radius=radius, string_format = False)
    return np.array(training_state)
    
def agent_tile_sense(x, y, radius):
        '''
        This method defines the eyes of the agents. The below is an example of the vision of the agent with radius 2.
        It will return a list of coordinates that defines
        
         __________________________________
        |      |      |      |      |      |
        |------ ------ ------ ------ ------|
        |      |      |      |      |      |
        |------ ------ ------ ------ ------|
        |      |      |  pos |      |      |
        |------ ------ ------ ------ ------|
        |      |      |      |      |      |
        |------ ------ ------ ------ ------|
        |      |      |      |      |      |
         ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


        '''
        diam = radius*2+1
        b = radius
        tile_sense = []
        for i in range(diam):
            a = -radius
            for j in range(diam):
                tile_sense.append((x+a,y+b))
                a+=1
            b-=1
        return tile_sense

def is_agent_safe():
    #checks whether the agent is in a safe zone or not
    pass

def manhattan_distance( start, end):
    """
    This method computes the manhattan distance between you and the enemy
    """
    distance = abs(start[0]-end[0] + abs(start[1]-end[1]))
    return distance       

def get_distance_to_enemy(self_loc, enemy_loc):
    '''
    this method returns a string value of distance. The distance is scaled to make it single digit
    '''
    distance = manhattan_distance(self_loc, enemy_loc) 
    return int((distance)*0.9)

def get_tile_state_str( visible_tiles, game_state, player_state):
    '''
    This method queries tiles visible to the agent to understand what object is present there. 
    '''
    training_state = []
    for pt in visible_tiles:
        if(not game_state.is_in_bounds(pt)):training_state.append("0")
        else:
            obs = game_state.entity_at(pt)
            if(obs==None):                  training_state.append("1") # no object foubnd
            elif(obs=="sb"):                training_state.append("2") # breakable wall
            elif(obs=="a"):                 training_state.append("3") # ammo found
            elif(obs=="b"):                 training_state.append("4") # bomb found
            elif(obs==player_state.id):     training_state.append("5") # self detected
            elif(isinstance(obs, int)):     training_state.append("6") # opponent detected
    return training_state

def get_tile_state_int( visible_tiles, game_state, player_state):
    '''
    This method queries tiles visible to the agent to understand what object is present there. 
    '''
    training_state = []
    for pt in visible_tiles:
        if(not game_state.is_in_bounds(pt)):training_state.append(0)
        else:
            obs = game_state.entity_at(pt)
            if(obs==None):                  training_state.append(1) # no object foubnd
            elif(obs=="sb"):                training_state.append(2) # breakable wall
            elif(obs=="a"):                 training_state.append(3) # ammo found
            elif(obs=="b"):                 training_state.append(4) # bomb found
            elif(obs==player_state.id):     training_state.append(5) # self detected
            elif(isinstance(obs, int)):     training_state.append(6) # opponent detected
    return training_state