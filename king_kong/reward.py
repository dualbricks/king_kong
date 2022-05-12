def get_reward_for_agent(occurred_event, 
                        DESTROY_SOFTBLOCK, 
                        DO_DAMAGE,
                        TAKE_DAMAGE,         
                        EARN_AMMO,
                        COLLIDE_WITH_WALLS,  
                        DAMAGE_ITSELF,  
                        NO_DESTRUCTION,           
                        NO_KILL,          
                        PLACING_BOMBS_WITH_NO_AMMO,          
                        PLACING_BOMB_ON_TOP_OF_BOMB,        
                        BOMB_IN_RANGE, 
                        EXIST_PENALTY,
                        player_state,
                        game_state
                        ):
        '''
        This method calculate the reward for a tick of the game. It checks the occurrence of an event, and then effectively adds or subtracts reward from the total reward.
        '''
        reward = 0
        if(occurred_event[0] >0):         reward+=DESTROY_SOFTBLOCK*occurred_event[0]
        if(occurred_event[1]==1):         reward+=DO_DAMAGE
        if(occurred_event[2]==1):         reward+=TAKE_DAMAGE
        if(occurred_event[3]==1):         reward+=EARN_AMMO
        if(occurred_event[4]==1):         reward+=COLLIDE_WITH_WALLS
        if(occurred_event[5]==1):         reward+=DAMAGE_ITSELF   #it's own bomb explodes on itself
        if(occurred_event[6]==1):         reward+=NO_DESTRUCTION #  bomb explodes without destroying any blocks
        if(occurred_event[7]==1):         reward+=NO_KILL      # bomb explodes without killing any player
        if(occurred_event[8]==1):         reward+=PLACING_BOMBS_WITH_NO_AMMO
        if(occurred_event[9]==1):         reward+=PLACING_BOMB_ON_TOP_OF_BOMB
        if(is_in_range_of_bomb_explosion(game_state, player_state)):
            reward+=BOMB_IN_RANGE

        reward = reward + EXIST_PENALTY
        return reward

def is_in_range_of_bomb_explosion(game_state, player_state):
    p_x = player_state.location[0]
    p_y = player_state.location[1]

    own = (p_x, p_y)
    fl = (p_x-2, p_y)
    nl = (p_x-1, p_y)
    ft = (p_x, p_y+2)
    nt = (p_x, p_y+1)
    fr = (p_x+2, p_y)
    nr = (p_x+1, p_y)
    fb = (p_x, p_y-2)
    nb = (p_x, p_y-1)

    danger_blocks = [own, fl,nl, ft, nt, fr, nr, fb, nb]
    for block in danger_blocks:
        if(game_state.entity_at(block)=="b"):
            return True
        else:
            return False
