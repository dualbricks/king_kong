AGENT_NAME                  =       "king kong"
TEAM_NAME                   =       "Dualbricks"

    
# These are algorithm parameters. You need to change this
DELTA                       =      0.1              #   How much should the epsilon shift by in every game
LR                          =      0.01           #   This is the learning rate. High learning rate means faster learning"                     
GAMMA                       =      0.6            #   gamma = discount factor. High gamma value means focus on future rewards "
STARTING_EPSILON            =      1.0

#These are the reward parameters. You need to change this. Refer to the guide to know what each means in detail
DESTROY_SOFTBLOCK           =      200      
DO_DAMAGE                   =      500
TAKE_DAMAGE                 =      -100     
EARN_AMMO                   =      20
COLLIDE_WITH_WALLS          =      -10
DAMAGE_ITSELF               =      -100        
NO_DESTRUCTION              =      -50                
NO_KILL                     =      -30             
PLACING_BOMBS_WITH_NO_AMMO  =      -200
BOMB_IN_RANGE               =      -100
PLACING_BOMB_ON_TOP_OF_BOMB =      -50
EXIST_PENALTY               =      -0.5



RL_ALGORITHM_TYPE           =       "SARSA"    # "SARSA"  ,   "Q_LEARNING",   "DEEPQ"
RADIUS                      =       2   


from coachPangolin import Agent as coachPango
from coachLizard import agent as coachLizzie

COACH                       =       coachPango()                # choose between coachPango, coachLizzie, coachSiss
GUIDANCE                    =       0.4                        # 1 means the agent copies exactly as the coach. 0 means that the agent makes random moves Should be between 1 and 0


Q_NAME                      =       AGENT_NAME + "_" +"QTable" + "_"+TEAM_NAME
EPISODE_NAME                =       AGENT_NAME + "_"+"G_Number"+ "_"+TEAM_NAME
EPSILON_NAME                =       AGENT_NAME + "_"+"epsilon" + "_"+TEAM_NAME






#Modules required. These provide extra functions so that we can do more operations
import random           #  to generate random numbers
from sre_parse import State           #  to load and save python data in files
import numpy as np      #  to do fast and efficient computation on data


#Import coaches
#import coachSnake
#import coachHornbill
from load_save import *
from state import *
from reward import *
# These are algorithm parameters. You need to change this


class Agent:
    """
    This class defines the agent that plays your game.
    """
    def __init__(self):
        '''
        Place any initialization code for your agent here (if any)
        '''
        self.cumulative_reward = 0                     # this stores sum total reward in every iteration
        # These attributes store the agent's previous state and action. These values are important for the QTable
        self.old_state = None                   
        self.old_action = None     
        self.scores= []
        # The following attributes contain data that the agent should remember for each move 
        self.episode_number = setup_episode(EPISODE_NAME=EPISODE_NAME)                 #  match number
        self.Q_Table = setup_QTable(Q_NAME=Q_NAME)                     #  Q Table
        self.epsilon = setup_epsilon(EPSILON_NAME=EPSILON_NAME, STARTING_EPSILON=STARTING_EPSILON)         #  EPSILON



    def next_move(self, game_state, player_state):
        '''
        This is the main method. It's called by the game to understand what's the agent's next move at every single tick.
        '''
        if(game_state.tick_number==0):
            self.old_state = get_training_state_for_Q(game_state, player_state, radius=RADIUS)
            ac = self.get_action(self.old_state, game_state, player_state)
            self.old_action = ac.index(1)
            ac = ['','u','d','l','r','p'][ac.index(1)]
            return ac
        #---------------------------------------------------------------- LEARNING-----------------------------------------------------------
        reward =    get_reward_for_agent(game_state._occurred_event, DESTROY_SOFTBLOCK, 
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
                        game_state)  #reward collected from the previous action
        new_state = get_training_state_for_Q(game_state, player_state, radius=RADIUS)  #new state transitioned into after implementing the previous action
        new_action = self.get_action(new_state, game_state, player_state).index(1)  
        self.cumulative_reward+=reward             # update return_sum for calculating cumulative reward
        self.learn(state = self.old_state, state2 = new_state, reward = reward, action = self.old_action, action2 = new_action) #learn method to learn from the state
        #-------------------------------------------------------------------------------------------------------------------------------------

        # Compute if the state is over
        done = (game_state.is_over) or (player_state.hp==0) or (game_state.tick_number==1800)
        if(done):
            print("----------------\t\t"    +   RL_ALGORITHM_TYPE   +   "\t\t------------------------------")
            if(player_state.hp==0):     print("LOST")
            else:                       print("WIN")

            self.increment_episode()                        #Increase the game numer
            self.shift_epsilon(DELTA)                       #Change epsilon value by DELTA

            # store the information from the agent
            self.scores.append(player_state.reward)      
            store_progress(self.Q_Table, self.episode_number, self.epsilon, Q_NAME=Q_NAME, EPISODE_NAME=EPISODE_NAME, EPSILON_NAME=EPSILON_NAME)
            self.display_agent_result()     
            self.cumulative_reward = 0


        #Store new_action as old acction and new_state as old_state. 
        self.old_action = new_action
        self.old_state = new_state

        #Return new action
        new_action = ['','u','d','l','r','p'][new_action]
        return new_action

    def learn(self, state, state2, reward, action, action2):
        """
        This method defines how the QTable needs to be updated
        """
        ls_check = ["SARSA", "Q_LEARNING", "DEEPQ" ]
        if(RL_ALGORITHM_TYPE not in ls_check):
            print("Error in the RL_ALGORITHM_TYPE ENTERED")
            return
        if(RL_ALGORITHM_TYPE =="SARSA"):
            action = action                      #old action
            action2 = action2                      #new action
            #If the agent is exploring an already existing state, then the entry must already be in the QTable
            #Otherwise, we need to create new entry into the QTable.
            if(state not in self.Q_Table):              self.Q_Table[state] = np.zeros(6)
            if(state2 not in self.Q_Table):             self.Q_Table[state2] = np.zeros(6)
            # We assume that value inside the QTable is the best one that we have.
            predict = self.Q_Table[state][action].item()  # this gets you the particular value
            target = reward + GAMMA * self.Q_Table[state2][action2].item()
            #This is the self.Q_Table
            self.Q_Table[state][action] = self.Q_Table[state][action].item() + LR * (target - predict)
        elif(RL_ALGORITHM_TYPE == "Q_LEARNING"):
            action = action     # convert old action from list([0,0,1,0,0,0]) to index number
            action2 = action2   # convert new action from list([0,0,1,0,0,0]) to index number
            # if state already in Q table, then it means that particlar state has been explored, otherwise, new entry is added to the table
            if(state not in self.Q_Table):                     
                self.Q_Table[state] = np.random.uniform(0,1,6)
            if(state2 not in self.Q_Table):
                self.Q_Table[state2] = np.random.uniform(0,1,6)
            # calculate predict and target
            predict = self.Q_Table[state][action].item()      # valuee for particular state and action given by the state
            target = reward + GAMMA * np.argmax(self.Q_Table[state2]).item()     # optimal value
            #update the q value for the particular state and action 
            self.Q_Table[state][action] = self.Q_Table[state][action].item() + LR * (target - predict) #updating the self.q_value
        
        elif(RL_ALGORITHM_TYPE=="DEEPQ"):
            pass



    def increment_episode(self):
        '''
        Called when match is over to increase game number
        '''
        self.episode_number+=1


    def shift_epsilon(self, delta):
        '''
        Change epsilon as per the participant's function
        '''
        self.epsilon+=delta



    def get_action(self, state, game_state, player_state):
        '''
        This method implements epsilon greedy strategy to choose action taken by the agent
        a random number is generated between 0 and 1. 
        if it's smaller than epsilon, then a random move is implemented
        else action is taken from the q table
        '''
        final_move = [0,0,0,0,0,0]
        if(self.choose_action()):
            move = self.explore(state, game_state, player_state)
        else:
            move = self.exploit(state)
        final_move[move]=1
        return final_move
        
    def choose_action(self):
        '''
        This method decides whether the agent should explore or not
        TRUE = exploration
        FALSE = exploitation
        '''
        final_move = [0,0,0,0,0,0]
        if np.random.uniform(0,1)< self.epsilon: return True
        else: return False

    def explore(self, state, game_state, player_state):
        '''
        This method returns a random move. We have decreased the probability of agent placing bombs. So that it doesn't kill itself very often. 
        '''
        #implements epsilon greedy 
        y = random.random()
        if(y<GUIDANCE):
            guided_move = COACH.next_move(game_state, player_state)
            return  ['','u','d','l','r','p'].index(guided_move)
        else:
            x = random.random()
            if(x>0.99):     return  5
            else:           return random.randint(0, 4)


    def exploit(self, state):
        '''
        This method chooses the best move as learned by the QTable
        '''
        if(state not in self.Q_Table): return random.randint(0, 5)
        return np.argmax(self.Q_Table[state])

    def display_agent_result(self):
        print("Game Number \t \t : \t", self.episode_number)
        print("Reward Earned \t \t : \t", self.cumulative_reward)
        print("Epsilon \t \t : \t", self.epsilon)
        print("_____________________________________________________________________________________________________")

