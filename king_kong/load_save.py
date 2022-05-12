import pickle

def setup_episode(EPISODE_NAME):
    '''
    This method loads episode number from file memory if it exists. Otherwise, it creates an instance of the game number and saves it to file
    '''
    try:
        with open(EPISODE_NAME, 'rb') as f:
            return pickle.load(f)
    except:
            with open(EPISODE_NAME,"wb") as f:
                pickle.dump(0, f)    
                return 0


def setup_QTable(Q_NAME):
    '''
    If the agent already has a QTable, it will use that. Else, it will create an empty q table dictionary.
    '''
    try:
        with open(Q_NAME, 'rb') as f:
            return pickle.load(f)
    except:
            Q_Table = dict()
            with open(Q_NAME,"wb") as f:
                pickle.dump(Q_Table, f)
            return Q_Table

def setup_epsilon(EPSILON_NAME, STARTING_EPSILON):
    '''
    If agent already has an epsilon value stored in memory, it will use that. Else, it will create new epsilon value, as asked by the user.
    '''
    try:
        with open(EPSILON_NAME, 'rb') as f:
            return pickle.load(f)
    except:
        with open(EPSILON_NAME,"wb") as f:
            pickle.dump(STARTING_EPSILON, f)
            return STARTING_EPSILON

def store_progress(Q_Table, episode_number, epsilon, Q_NAME, EPISODE_NAME, EPSILON_NAME):
    '''
    This stores agent progress in a file.
    '''
    with open(Q_NAME,"wb") as Q_table:
            pickle.dump(Q_Table, Q_table)
    with open(EPISODE_NAME, "wb") as f:
            pickle.dump(episode_number, f)
    with open(EPSILON_NAME, "wb") as f:
            pickle.dump(epsilon, f)