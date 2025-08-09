from random import randint, seed
import pytest
from re import fullmatch
from time import time

# TODO: 
# add continue game after end
# maybe work on saving
# maybe add settings


#------------------------- GLOBAL VARIABLES -------------------------


game_seed = None
game_state = 'main'

player = {}
game_map = []
current_map = []
fog = []

MAX_SAVE_SLOTS = 5

PLAYER_DICT_SIZE = 20
PLAYER_DATA_LINES = 50
MAP_NODES = ['T', 'C', 'S', 'G', 'P']
FOG_NODES = ['?']

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 1000

PICKAXE_MAX_LEVEL = 3
BACKPACK_UPGRADE_AMOUNT = 2
TORCH_MAX_LEVEL = 3

LEADERBOARD_SIZE = 5

SAVE_FILE_NAME = 'save{}.txt'
GLOBAL_SAVE_FILE = 'global.txt'

VIEW_PADDING = 1

movement_buttons = ['w','a','s','d']
movement_map = {'w':[-1, 0], 'a':[0, -1], 's':[1, 0], 'd':[0, 1]} # [y, x]

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_prices = [0, 50, 150, None]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

drop_rates = {}
drop_rates['copper'] = (1, 5)
drop_rates['silver'] = (1, 3)
drop_rates['gold'] = (1, 2)


#---------------------------------- FUNCTIONS ----------------------------------


# This function handles all prompts. It takes in a regex expression of valid inputs and
# loops until it receives a valid input.
def prompt(valid=None, message='Your choice? '):      
    while True:
        player_input = input(message).lower()
        check = player_input.lower()
        if not valid: # empty valid array means all inputs are accepted
            return check
        elif fullmatch(valid, player_input):
            return check
        else:
            print('"{}" is not a valid input. Please try again.'.format(player_input))


# Converts text data to nested list and loads it into a variable (target)
# Also optionally cleans unwanted data
# NOTE: supersedes load_fog() function
def text_to_list(data, start_read, end_read, target, clean=[]):
    target.clear()
    for line in range(start_read, end_read):
        row = []
        for node in data[line]:
            if node in clean or not clean:
                row.append(node)
            else:
                row.append(' ')
        target.append(row)


# This function converts the map data from the save file into a nested list
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(save_data, start_read, end_read, game_map):

    global MAP_WIDTH
    global MAP_HEIGHT

    game_map.clear()
    
    text_to_list(save_data, start_read, end_read, game_map, MAP_NODES)

    MAP_WIDTH = len(game_map[0])
    MAP_HEIGHT = len(game_map)


# This function retrieves the map from a file. 
# While it is not used in the code currently, as there is a map generator in place,
# The code can be edited slightly to get a specific map from a file.
# def get_map(filename):
#     map_data = []
#     with open(filename, 'r') as map_file:
#         for line in map_file:
#             map_data.append(line)
#     return map_data


# checks how far one node is from certain nodes or node types
# parameter searchfor can be the y and x coordinates of a specific node or a string of node types
# there is also avoid mode, which calculates distance from any node not in searchfor
def distance_from(searchfor, node, map_struct, avoid=False):
    distance = None
    node_row, node_col = node

    for row in range(len(map_struct)):
        for col in range(len(map_struct[0])):
            cell = map_struct[row][col]

            if avoid:
                if cell in searchfor:
                    continue
            else:
                if type(searchfor) == str:
                    if cell not in searchfor:
                        continue
                else:  
                    return ((searchfor[0] - node_row) ** 2 + (searchfor[1] - node_col) ** 2) ** 0.5

            d = ((row - node_row) ** 2 + (col - node_col) ** 2) ** 0.5
            if distance is None or d < distance:
                distance = d
    if distance == None:
        return 100000000 # not found will return as very far away
    else:
        return distance 


# returns an array of the ore types surrounding a node:
def neighbour_nodes(map_struct, node, checkfor):
    nodes = []

    # check if node is within +-1 x AND +-1 y
    for row in range(node[0] - 1, node[0] + 2):
        for col in range(node[1] - 1, node[1] + 2):
            if row < len(map_struct) and col < len(map_struct[0]): # dodge index error

                # check if node is the type that we are searchijng for and is not the center node
                if map_struct[row][col] in checkfor and [row, col] != node: 
                    nodes.append(map_struct[row][col])

    return nodes


# randomly generates a new game map given certain parameters
def generate_map(map_width, map_height, spread, min_density, max_density): 
    while True:
        map_struct = [[' ' for x in range(map_width)] for y in range(map_height)]
        map_struct[0][0] = 'T'
        max_distance = distance_from('T', [map_height - 1, map_width - 1], map_struct)

        # random map generation logic is based off neighbouring nodes
        # i.e if a node is surrounded by many copper nodes, it is likely to become a copper node itself
        # the first iteration over the map will place various ores to start this process
        # and then the rest of the map will be populated based off those starting nodes
        # this strategy allows clusters of ores to form, similarly to the provided map
        
        # first iteration to go place "seed" nodes
        for row in range(map_height):
            for col in range(map_width):
                if map_struct[row][col] == ' ':
                    # beginner area shall only contain copper, also immediate surrounding area from T is empty
                    if distance_from('T', [row, col], map_struct) <= 1.5:
                        continue

                    elif distance_from('T', [row, col], map_struct) < 0.15 * max_distance:
                        if randint(1,2) == 1:              
                            # cannot put ores too close together -> will result in very large and dense clusters
                            if distance_from(' T', [row, col], map_struct, True) > spread:
                                map_struct[row][col] = 'C'
                    
                    # main area will contain all ores
                    elif distance_from('T', [row, col], map_struct) < 0.90 * max_distance:
                        chance = randint(1,16)
                        if chance == 1:
                            if distance_from(' ', [row, col], map_struct, True) > spread:
                                map_struct[row][col] = 'C'
                        elif chance <= 3:
                            if distance_from(' ', [row, col], map_struct, True) > spread:
                                map_struct[row][col] = 'S'
                        elif chance == 4:
                            if distance_from(' ', [row, col], map_struct, True) > spread:
                                map_struct[row][col] = 'G'
                    
                    # farthest corner will contain gold
                    else:
                        if randint(1,3) == 1:
                            if distance_from(' ', [row, col], map_struct, True) > spread:
                                map_struct[row][col] = 'G'
        
        # place more ore nodes sprouting off the "seed" nodes
        # populate map to desired density
        while True:
            for row in range(map_height):
                for col in range(map_width):
                    if map_struct[row][col] == ' ':
                        if distance_from('T', [row, col], map_struct) <= 1.5:
                            continue
                        nearby_nodes = neighbour_nodes(map_struct, [row, col], ' CSG')
                        if nearby_nodes: # just in case
                            # node becomes a random node from its 8 surrounding nodes 
                            chosen = randint(0, len(nearby_nodes) - 1)
                            map_struct[row][col] = nearby_nodes[chosen]

            ore_count = 0
            copper_count = 0
            silver_count = 0
            gold_count = 0
            for row in range(map_height):
                for col in range(map_width):
                    ore = map_struct[row][col]
                    if ore in 'CSG':
                        ore_count += 1
                        if ore == 'C':
                            copper_count += 1
                        elif ore == 'S':
                            silver_count += 1
                        else:
                            gold_count += 1

            if ore_count > min_density * map_height * map_width:
                break

        # NOTE: this algorithm is likely to overshoot the desired density, as once there are enough ores
        # the rate of ore placement speeds up very quickly, i.e. a density of 0.33 is likely to result in maps that are 45% filled
        # therefore, a maximum density check is in place to prevent a map that is too full of ores.

        if ore_count < max_density * map_height * map_width:
            if copper_count >= 20 and silver_count >= 20 and gold_count >= 20: # ensure sufficient ore for the player
                break

    return map_struct


# creates a new fog map
def create_fog(fog):
    fog.clear()
    for y in range(MAP_HEIGHT):
        fog_row = []
        for x in range(MAP_WIDTH):
            if y <= 1 and x <= 1: # clear out fog surrounding town
                fog_row.append(' ')
            else:
                fog_row.append('?')
        fog.append(fog_row)


# sets up empty save file for new game
def initialize_game(save_file, game_map, fog, current_map, player):

    global game_seed
    global game_state
    global MAP_HEIGHT
    global MAP_WIDTH

    # use random seeds to prevent players from repeatedly quitting and restarting to get better luck
    # also allows for players to do repeated runs with the same random seed to eliminate randomness
    game_seed = time()
    seed(game_seed)

    game_state = 'town'
    MAP_HEIGHT = 10
    MAP_WIDTH = 30

    # initialize map
    game_map.clear()
    current_map.clear()

    game_map.extend(generate_map(MAP_WIDTH, MAP_HEIGHT, 4, 0.33, 0.5))

    # copies game map row by row to make 2 seperate maps that will not affect each other
    current_map.extend([row[:] for row in game_map]) 

    # initialize fog
    create_fog(fog)
    
    # initialize player
    # key info
    name = prompt(message="Greetings, miner! What is your name? ")
    if name:
        player['name'] = name
    else: # default player name if nothing was entered
        player['name'] = 'Player'
    print('Pleased to meet you, {}. Welcome to Sundrop Town!'.format(name))
    player['day'] = 1
    player['GP'] = 0
    player['steps'] = 0

    # other info
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['turns'] = TURNS_PER_DAY
    player['pickaxe_level'] = 1
    player['backpack_capacity'] = 10
    player['torch_level'] = 1
    player['portal_x'] = 0
    player['portal_y'] = 0
    player['copper_price'] = randint(prices['copper'][0], prices['copper'][1])
    player['silver_price'] = randint(prices['silver'][0], prices['silver'][1])
    player['gold_price'] = randint(prices['gold'][0], prices['gold'][1])
    player['warehouse_level'] = 1
    player['warehouse'] = ''

    save_game(save_file, game_map, fog, current_map, player)


# This function draws the entire map, covered by the fog
def draw_map(current_map, fog):

    global game_state

    print()
    map_view = '+' + '-' * MAP_WIDTH + '+\n'
    
    for row in range(MAP_HEIGHT):
        map_row = []
        for col in range(MAP_WIDTH):
            if [row, col] == [0, 0] and game_state == 'town':
                map_row.append('M')
            elif player['y'] == row and player['x'] == col and game_state == 'mine':
                map_row.append('M')
            elif [row, col] == [0, 0] and game_state != 'town':
                map_row.append('T')
            elif fog[row][col] == '?':
                map_row.append('?')
            else:
                map_row.append(current_map[row][col])
        map_view += '|' + ''.join(map_row) + '|\n'

    map_view += '+' + '-' * MAP_WIDTH + '+'
    return map_view


# returns an array of all the nodes coordinates surrounding a center nodes, including the center node
def get_surrounding_nodes(center, search_area):
    nodes = []
    # check if center node is within +-search_area x AND +-search_area y
    for row in range(center[0] - search_area, center[0] + search_area + 1):
        for col in range(center[1] - search_area, center[1] + search_area + 1):
            nodes.append([row, col])
    return nodes


# This function clears the fog of war at the 3x3 square around the player
def clear_fog(fog, nodes):
    for node in nodes:
        row = node[0]
        col = node[1]
        if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
            fog[row][col] = ' '


# This function draws the 3x3 viewport
def draw_view(current_map, player, nodes):
    view_size = 2 * player['torch_level'] + 1 
    view = '+' + '-' * view_size + '-' * (view_size + 1) * VIEW_PADDING + '+\n|' + ' ' * VIEW_PADDING
    pos = 1
    for node in nodes:
        row = node[0]
        col = node[1]
        
        if node == [player['y'], player['x']]:
            view += 'M'
        elif -1 < row < MAP_HEIGHT and -1 < col < MAP_WIDTH: # In bounds
            view += current_map[row][col]
        elif ((row == -1  or row == MAP_HEIGHT) and -1 <= col <= MAP_WIDTH) or ((col == -1 or col == MAP_WIDTH) and -1 <= row <= MAP_HEIGHT): # Border
            view += '#'
        else: # Out of bounds
            view += ' '

        if pos < view_size:
            view += VIEW_PADDING * ' '
            pos += 1
        elif node == nodes[-1]:
            view += ' ' * VIEW_PADDING + '|\n'
        else:
            view += ' ' * VIEW_PADDING + '|\n|' + ' ' * VIEW_PADDING
            pos = 1

    view += '+' + '-' * view_size + '-' * (view_size + 1) * VIEW_PADDING + '+' 
    return view


# displays player inventory
def show_backpack(player):
    print("-------------- Backpack --------------")
    valid = '['
    for mineral in minerals:
        if player[mineral]:
            spacing = max([len(mineral) + 2 for mineral in minerals])
            ore_name = '(' + mineral[0].upper() + ')' + mineral[1:]
            print("{:<} | x{:<}".format(ore_name + ' ' * (spacing - len(ore_name)), player[mineral]))
            valid += mineral[0]
    valid += 'q]'
    print("--------------------------------------")
    return valid


# handles selection of ores from backpack
# mode will equal 'sell' or 'store'
def choose_backpack_ore(player, mode):
    
    print()
    valid = show_backpack(player)

    while True:
        player_input = prompt(valid, "Choose a mineral to {} (Q to cancel): ".format(mode))
        if player_input.upper() in mineral_names.keys():
            chosen_ore = player_input.upper()
            ore_count = prompt(r'\d+|a',"How much {} would you like to {}? ".format(mineral_names[chosen_ore], mode))
            if ore_count == 'a': # intuitive that 'a' means sell all, since that applies to other prompts
                ore_count = player[mineral_names[chosen_ore]]
            return [chosen_ore, int(ore_count)]
        else:
            return 'q'
            

# handles selection of ores to sell from warehouse
def choose_warehouse_ore(player, valid):
    while True:
        player_input = prompt(valid, "Choose a mineral to sell (A to sell all, Q to cancel): ")
        if player_input.upper() in mineral_names.keys():
            chosen_ore = player_input.upper()
            ore_count = prompt(r'\d+|a',"How much {} would you like to sell? ".format(mineral_names[chosen_ore]))
            if ore_count == 'a':  # intuitive that 'a' means sell all, since that applies to other prompts
                ore_count = player['warehouse'].count(chosen_ore)
            return [chosen_ore, int(ore_count)]
        elif player_input == 'a':
            return 'a'
        else:
            return 'q'
        

# displays player information
def show_information(player):
    print()
    print("--------- Player Information ---------")
    print("Name:", player['name'])
    print("Portal position: ({}, {})".format(player['portal_x'], player['portal_y']))
    print("Pickaxe level: {} ({})".format(player['pickaxe_level'], minerals[player['pickaxe_level'] - 1]))
    
    if sum([player[mineral] for mineral in minerals]) != 0:
        show_backpack(player)
    else:
        print("--------------------------------------")

    print("Load: {} / {}".format(sum([player[mineral] for mineral in minerals]), player['backpack_capacity']))
    print("--------------------------------------")
    print("GP:", player['GP'])
    print("Steps taken:", player['steps'])
    print("--------------------------------------")


# This function reads key information from a save file for temporary display, 
# such as the player name, day, gold and steps taken, and returns it as a list of strings to be printed
def save_file_details(save_file):
    save_file_info = [] 
    try: 
        with open(save_file, 'r') as save:
            save.readline() # skip seed
            save.readline() # skip game state
            save_file_info.append(save.readline().strip().split(',',1)[1]) # get name
            save_file_info.append(save.readline().strip().split(',')[1]) # get day
            save_file_info.append(save.readline().strip().split(',')[1]) # get GP
            save_file_info.append(save.readline().strip().split(',')[1]) # get steps
        return save_file_info
    except FileNotFoundError:
        return None


# Sundrop Caves has multiple save slots. This function will handle the selection logic.
def choose_save_slot(saving=True):
    while True:
        print()
        print('---------------------------- SAVE SLOTS -----------------------------')
        for slot in range(1, MAX_SAVE_SLOTS + 1):
            save_file_info = save_file_details(SAVE_FILE_NAME.format(slot))
            if save_file_info:
                name = save_file_info[0]
                day = save_file_info[1]
                GP = save_file_info[2]
                steps = save_file_info[3]
                print(' {:<33} {:>33} '.format('SLOT ' + str(slot),'DAY ' + day))
                if len(name) <= 33:
                    print(' {:<33} {:>33} '.format(name, 'STEPS: ' + steps))
                    print(' {:>67} '.format('GP: ' + GP))
                else:
                    split_name = []
                    for n in range(int(len(name)/33)):
                        split_name.append(name[n*33:(n+1)*33])
                    if len(name) > (n+1) * 33:
                        split_name.append(name[(n+1)*33:])

                    print(' {:<33} {:>33} '.format(split_name.pop(0), 'STEPS: ' + steps))
                    print(' {:<33} {:>33} '.format(split_name.pop(0), 'GP: ' + GP))
                    for part in split_name:
                        print(' {:<33}'.format(part))
            else:
                print(' {:<33} {:>33} '.format('SLOT ' + str(slot),'EMPTY'))
                print()
                print()
            print('---------------------------------------------------------------------')

        valid = '[1-' + str(MAX_SAVE_SLOTS) + ']|[q]'

        save_file = SAVE_FILE_NAME.format(prompt(valid, "Please select a save slot (Q to close): "))
        if 'q' in save_file:
            return save_file
        elif save_file_details(save_file) and saving:
            if prompt('[yn]', 'Warning! The save slot you have chosen already contains a save file. Are you sure you want to override it? [Y/N]: ') != 'y':
                print("Cancelling save.")
                continue
            else:
                return save_file
        elif not save_file_details(save_file) and not saving:
            print('The save slot you chose is empty. Please try again')
            continue
        else:
            return save_file


# saves game data into a save file
def save_game(save_file, game_map, fog, current_map, player):

    global game_seed
    global game_state

    save_data = []
    save_data.append(str(game_seed))
    save_data.append(game_state)
    
    # save player 
    # saves key alongside value for flexibility
    for key in player:
        save_data.append('{},{}'.format(key, player[key]))

    # padding
    save_data.append('\n' * (((2 + PLAYER_DATA_LINES) - len(save_data)) - 1))

    # save game map
    for row in game_map:
        save_data.append(''.join(row))
    # save fog
    for row in fog:
        save_data.append(''.join(row))
    # save current map
    for row in current_map:
        save_data.append(''.join(row))
    
    with open(save_file, 'w') as save_file:
        save_file.write('\n'.join(save_data))
    print('Game saved.')


# adds scores into global save
# places score in the correct position such that the list is sorted
def add_high_score(player):
    try:
        global_save = open(GLOBAL_SAVE_FILE, 'r')
    except FileNotFoundError:
        # creates empty global save file
        global_save = open(GLOBAL_SAVE_FILE, 'w')
        global_save.close()
        global_save = open(GLOBAL_SAVE_FILE, 'r')
        
    data = global_save.read()
    global_save.close()
    
    new_score = ','.join([player['name'], str(player['day']), str(player['steps']), str(player['GP'])])

    if data:
        data = data.split('\n')
        new_score_info = new_score.split(',')

        for score_pos in range(0, len(data)):
            score_info = data[score_pos].split(',')

            # go through the list until there is a score worse than the current one
            # read from right to left to dodge player name inteference
            # i.e. comma in player name
            if int(new_score_info[-3]) < int(score_info[-3]): # sort by days
                break
            elif int(new_score_info[-3]) == int(score_info[-3]):
                if int(new_score_info[-2]) < int(score_info[-2]): # sort by steps
                    break
                elif int(new_score_info[-2]) == int(score_info[-2]): 
                    if int(new_score_info[-1]) >= int(score_info[-1]): # sort by GP
                        break
        
        else: # only runs if for loop reaches the end
            score_pos = len(data) # put score at the end if it is worse than all other scores

        # rewrite data list, but with the appended data in the correct position
        new_data = []
        for item in range(score_pos):
            new_data.append(data[item])
        
        new_data.append(new_score)

        for item in range(score_pos, len(data)):
            new_data.append(data[item])

        if score_pos < LEADERBOARD_SIZE:
            print('Congratulations! You have a new high score on the leaderboard!')

        global_save = open(GLOBAL_SAVE_FILE, 'w')
        
        for score_pos in range(len(new_data)):
            if score_pos == len(new_data) - 1:
                global_save.write(new_data[score_pos])
            else:
                global_save.write(new_data[score_pos] + '\n')

    else:
        global_save = open(GLOBAL_SAVE_FILE, 'w')

        global_save.write(new_score)
    
        print('Congratulations! You have a new high score on the leaderboard!')

    global_save.close()


# returns the appropriate suffix for a number
# e.g. returns 'st' if number = 1
def number_suffix(number):
    last_digit = int(str(number)[-1])
    suffixes = ['st','nd','rd','th']
    if last_digit > 4 or 11 <= number <= 13:
        last_digit = 4
    return suffixes[last_digit - 1] # note that it returns 'th' if 0, which is correct.
        

# displays the top scores from the scores list
def show_high_scores():
    with open(GLOBAL_SAVE_FILE, 'r') as global_save:
        data = global_save.read().split('\n')
        if len(data[0]) != 0:
            rank = 1
            print()
            print("--------------------- HIGH SCORES ---------------------")
            for score_pos in range(LEADERBOARD_SIZE):
                if score_pos == len(data):
                    break
                high_score = data[score_pos].split(',')

                # high score is processed like this so commas in the name will not interfere
                day = high_score.pop(-3)
                steps = high_score.pop(-2)
                GP = high_score.pop(-1)
                name = ','.join(high_score)

                print(" {:<5} {:>47}".format(str(rank) + number_suffix(rank), 'DAY ' + day))

                if len(name) <= 26:
                    print(" {:<26} {:>26}".format(name, 'STEPS: ' + steps))
                    print(" {:>53}".format('GP: ' + GP))
                else:
                    split_name = []
                    for n in range(int(len(name)/26)):
                        split_name.append(name[n*26:(n+1)*26])
                    if len(name) > (n+1) * 26:
                        split_name.append(name[(n+1)*26:])

                    print(" {:<26} {:>26}".format(split_name.pop(0), 'STEPS: ' + steps))
                    print(" {:<26} {:>26}".format(split_name.pop(0), 'GP: ' + GP))
                    
                    for part in split_name:
                        print(" {:<26}".format(part))

                print("-------------------------------------------------------")
                rank += 1
        else:
            print('There are no high scores as you have not won the game yet.')


# loads game data from a save file
def load_game(save_file, game_map, fog, current_map, player):
    save_file = open(save_file, 'r')
    save_data = save_file.read().split('\n')

    global game_state
    global game_seed

    game_seed = float(save_data[0])
    seed(game_seed)

    game_state = save_data[1]

    # load player
    for line in range(2, PLAYER_DATA_LINES + 2):
        if save_data[line]:
            info = save_data[line].split(',', 1)
            if info[1].isdigit():
                data = int(info[1])
            elif '[' in info[1]:
                data = info[1].strip('[]').replace("'", "").replace('"', "").split(',')
                if data == ['']:
                    data.clear()
            else:
                data = info[1]
            player[info[0]] = data
        else:
            break

    # load game map
    load_map(save_data, PLAYER_DATA_LINES + 2, PLAYER_DATA_LINES + 12, game_map)
            
    # load fog
    text_to_list(save_data, PLAYER_DATA_LINES + 12, PLAYER_DATA_LINES + 22,fog, FOG_NODES)

    # load current map
    text_to_list(save_data, PLAYER_DATA_LINES + 22, PLAYER_DATA_LINES + 32, current_map, MAP_NODES)

    try:
        error_detect = 'Missing player data.'
        assert len(player) >= PLAYER_DICT_SIZE
        error_detect = 'Extra player data'
        assert len(player) == PLAYER_DICT_SIZE
        error_detect = 'Map size mismatch'
        assert len(fog[0]) == MAP_WIDTH and len(fog) == MAP_HEIGHT
        assert len(current_map[0]) == MAP_WIDTH and len(current_map) == MAP_HEIGHT
    except AssertionError:
        print("Error in save data.", error_detect)
        quit()


# draws the warehouse and the ores it contains
def draw_warehouse(player):
    print()
    print('Warehouse')
    size = 2 + player['warehouse_level']
    print('+' + '-' * size + '-' * (size + 1) * VIEW_PADDING + '+')

    view_row = ''
    for node in range(size ** 2):
        if node < len(player['warehouse']):
            view_row += player['warehouse'][node]
        else:
            view_row += ' '
        
        view_row += VIEW_PADDING * ' '

        if len(view_row) == size + size * VIEW_PADDING:
            print('|' + VIEW_PADDING * ' ' + view_row + '|')
            view_row = ''

    print('+' + '-' * size + '-' * (size + 1) * VIEW_PADDING + '+')
    print('Level: {} ({}x{})'.format(player['warehouse_level'], size, size))


# display warehouse menu and determine valid inputs and upgrade price
def show_warehouse_menu(player):

    draw_warehouse(player)

    upgrade_price = 5 + player['warehouse_level'] * 25

    valid = '['
    if player['warehouse'] == (2 + player['warehouse_level']) ** 2:
        print('The warehouse is full!')
    elif sum([player[mineral] for mineral in minerals]) > 0:
        valid += 'sa'
        print('(S)tore ores, Store (A)ll')
    else:
        print('Your backpack is empty!')

    if player['warehouse']:
        print('Sell (W)arehouse ores')
        valid += 'w'
    print('(U)pgrade storage ({} GP), (L)eave'.format(upgrade_price))
    valid += 'ul]'

    return upgrade_price, valid


# automatically store as many ores as possible from player backpack
def store_all_ores(player):
    ores_to_be_stored = ''.join([player[mineral_names[mineral]] * mineral for mineral in mineral_names.keys()])
    ores_to_be_stored = ores_to_be_stored[:(2 + player['warehouse_level'])**2]
    
    storage_dict = {}
    for mineral in mineral_names.keys():
        if mineral in ores_to_be_stored:
            storage_dict[mineral] = ores_to_be_stored.count(mineral)
            player[mineral_names[mineral]] -= ores_to_be_stored.count(mineral) 
    
    for mineral in storage_dict.keys():
        print('You stored {} {}!'.format(storage_dict[mineral], mineral_names[mineral]))
        player['warehouse'] += storage_dict[mineral] * mineral 


# manage navigation of warehouse menu and upgrades
def warehouse_menu(player):

    global game_state

    game_state = 'warehouse'

    while True:
        price, valid = show_warehouse_menu(player)

        player_input = prompt(valid)

        if player_input == 's':
            selection = choose_backpack_ore(player, 'store')
            if selection != 'q':
                ore = selection[0]
                count = selection[1]
                if count > (2 + player['warehouse_level'])**2 - len(player['warehouse']):
                    count = (2 + player['warehouse_level'])**2 - len(player['warehouse'])
                player['warehouse'] += ore * count
                print('You stored {} {}!'.format(count, mineral_names[ore]))
        elif player_input == 'a':
            store_all_ores(player)
        elif player_input == 'w':
            sell_from_warehouse(player)
        elif player_input == 'u':
            if player['GP'] >= price:
                player['warehouse_level'] += 1
                size = 2 + player['warehouse_level']
                print('Congratulations! Your warehouse is now level {} ({}x{})!'.format(player['warehouse_level'], size, size))
                player['GP'] -= price
            else:
                print('You do not have enough GP for this upgrade!')
        else:
            game_state = 'town'

        if game_state != 'warehouse':
            break


# allows the player to sell the ores stored in their warehouse through the sell menu
def sell_from_warehouse(player):

    valid = '['
    for mineral in player['warehouse']:
        if mineral.lower() not in valid:
            valid += mineral.lower()
    valid += 'aq]'

    if len(player['warehouse']) > 0:
        selection = choose_warehouse_ore(player, valid)

        if selection == 'a':
            for ore in mineral_names.keys():
                ore_name = mineral_names[ore]
                if ore in player['warehouse']:
                    ore_count = player['warehouse'].count(ore)
                    earned = ore_count * player[ore_name + '_price']
                    print("You sell {} {} ore for {} GP.".format(ore_count, ore_name, earned))
                    player['GP'] += earned

            print("You now have {} GP!".format(player['GP']))
            player['warehouse'] = ''

        elif selection != 'q':
            ore = selection[0]
            ore_name = mineral_names[ore]
            count = selection[1]

            if count > player['warehouse'].count(ore):
                count = player['warehouse'].count(ore)

            earned = count * player[ore_name + '_price']
            print("You sell {} {} ore for {} GP.".format(count, ore_name, earned))
            player['GP'] += earned
            player['warehouse'] = player['warehouse'].replace(selection[0],'',selection[1])
            print("You now have {} GP!".format(player['GP']))
    else:
        print("The warehouse is empty!")


# displays sell menu and returns valid player choices
def show_sell_menu(player):
    
    valid = '['

    print()
    print('-------- Prices --------')
    for mineral in minerals:
        spacing = max([len(mineral) for mineral in minerals])
        print("{:<} - {:>2} GP".format(mineral.capitalize() + ' ' * (spacing - len(mineral)), player[mineral + '_price']))
    print('------------------------')

    if sum([player[mineral] for mineral in minerals]) == 0:
        print('You have no ores!')
    else:
        print('Choose from (B)ackpack')
        valid += 'b'
        print('Sell (A)ll')
        valid += 'a'

    print('Choose from (W)arehouse')
    valid += 'w'

    print('(L)eave sell menu')
    valid += 'l]'
    print('------------------------')

    return valid


def sell_ore(player, selection):
    ore_name = mineral_names[selection[0]]
    count = selection[1]

    if count > player[ore_name]:
        count = player[ore_name]
    
    earned = player[ore_name] * player[ore_name + '_price']
    print("You sell {} {} ore for {} GP.".format(player[ore_name], ore_name, earned))
    player['GP'] += earned
    player[ore_name] = 0


# Sells all player ores
def sell_all_ores(player):

    if player['copper']:
        sell_ore(player, ['C', player['copper']])

    if player['silver']:
        sell_ore(player, ['S', player['silver']])

    if player['gold']:
        sell_ore(player, ['G', player['gold']])

    print("You now have {} GP!".format(player['GP']))
    

# manage selling of ores
def sell_menu(player):

    global game_state

    game_state = 'sell'

    while True:
        valid = show_sell_menu(player)
        player_input = prompt(valid)

        if player_input == 'b':
            selection = choose_backpack_ore(player, mode='sell')
            if selection != 'q':
                sell_ore(player, selection)
                print("You now have {} GP!".format(player['GP']))
        elif player_input == 'w':
            draw_warehouse(player)
            sell_from_warehouse(player)
        elif player_input == 'a':
            sell_all_ores(player)
        else:
            print('Bye! See you again!')
            game_state = 'town'
        
        if player['GP'] >= WIN_GP:   
            game_state = "win"
        
        if game_state != 'sell':
            break


# display shop menu and calculate prices
def show_shop_menu():
    pickaxe_level = player['pickaxe_level']
    backpack_capacity = player['backpack_capacity']
    accepted_inputs = '['
    print()
    print('----------------------- Shop Menu -------------------------')
    if player['pickaxe_level'] == PICKAXE_MAX_LEVEL:
        print('Your pickaxe cannot be upgraded any further!')
    else:
        print('(P)ickaxe upgrade to Level {} to mine {} ore for {} GP'.format(pickaxe_level + 1, minerals[pickaxe_level], pickaxe_prices[pickaxe_level]))
        accepted_inputs += 'p'

    print('(B)ackpack upgrade to carry {} items for {} GP'.format(backpack_capacity + BACKPACK_UPGRADE_AMOUNT, backpack_capacity * 2))
    accepted_inputs += 'b'

    if player['torch_level'] == TORCH_MAX_LEVEL:
        print('Your torch cannot be enchanted any more!')
    else:
        view_size = 1 + (player['torch_level'] + 1) * 2
        print('(T)orch enchantment to increase view size to {}x{} for {} GP'.format(view_size, view_size, player['torch_level'] * 100))
        accepted_inputs += 't'

    print('(L)eave shop')
    accepted_inputs += 'l]'

    print('-----------------------------------------------------------')
    print('GP:', player['GP'])
    print('-----------------------------------------------------------')
    return pickaxe_prices[pickaxe_level], backpack_capacity * 2, player['torch_level'] * 100, accepted_inputs


# manages purchasing upgrades
def shop_menu(player):
    while True:
        pickaxe_price, backpack_price, torch_price, accepted_inputs = show_shop_menu()
        choice = prompt(accepted_inputs)
        if choice == 'p':
            if pickaxe_price > player['GP']:
                print("You don't have enough money for this upgrade!")
            else:
                print("Congratulations! You can now mine {}!".format(minerals[player['pickaxe_level']]))
                player['pickaxe_level'] += 1
                player['GP'] -= pickaxe_price
            continue
        elif choice == 'b':
            if backpack_price > player['GP']:
                print("You don't have enough money for this upgrade!")
            else:
                player['backpack_capacity'] += BACKPACK_UPGRADE_AMOUNT
                print("Congratulations! You can now carry {} items!".format(player['backpack_capacity']))
                player['GP'] -= backpack_price
            continue           
        elif choice == 't':
            if torch_price > player['GP']:
                print("You don't have enough money for this enchantment!")
            else:
                player['torch_level'] += 1
                view_size = 1 + player['torch_level'] * 2
                print('Congratulations, your view size has increased to {}x{}!'.format(view_size, view_size))
                player['GP'] -= torch_price
            continue
        else:
            print('Bye! See you again!')
            break


# display the mine menu
def show_mine_menu(current_map, player):
    print()
    print('DAY', player['day'])
    nodes = get_surrounding_nodes([player['y'], player['x']], player['torch_level'])
    viewport = draw_view(current_map, player, nodes)
    print(viewport)
    print('Turns left: {:<5} Load: {} / {}    Steps: {}'.format(player['turns'], sum([player[mineral] for mineral in minerals]), player['backpack_capacity'], player['steps']))
    print('(WASD) to move')
    print('(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu')


# determines the amount of ore again
def mine_ore(ore):
    ore_name = mineral_names[ore]
    amount_mined = randint(drop_rates[ore_name][0], drop_rates[ore_name][1])
    return amount_mined


# determines what happens when a player steps on a node
def interact_node(current_map, player, node_coords):
    node = current_map[node_coords[0]][node_coords[1]]

    if node in mineral_names.keys():
        current_map[node_coords[0]][node_coords[1]] = ' '
        amount_mined = mine_ore(node)
        print('You mined {} piece(s) of {}.'.format(amount_mined, mineral_names[node]))
        
        backpack_load = sum([player[mineral] for mineral in minerals]) + amount_mined
        if backpack_load > player['backpack_capacity']:
            amount_mined -= backpack_load - player['backpack_capacity']
            print('...but you can only carry {} more piece(s)!'.format(amount_mined))
        
        player[mineral_names[node]] += amount_mined
                   
    elif node == 'T' or node == 'P':
        if prompt('[yn]', "Would you like to return to town? [Y/N]: ") == 'y':
            return_to_town(player)

    player['steps'] += 1        
    player['turns'] -= 1
    if player['turns'] == 0:
        print("You are exhausted.")
        portal_stone(player, current_map)
 

# handles player movement
def attempt_move(player_action, player, current_map):
    print()
    print('-----------------------------------------------------')
    test_y = player['y'] + movement_map[player_action][0]
    test_x = player['x'] + movement_map[player_action][1]

    # movement rules; kept seperate from return logic for organisation
    if -1 < test_y < MAP_HEIGHT and -1 < test_x < MAP_WIDTH:
        out_of_bounds = False
    else:
        out_of_bounds = True
    
    if out_of_bounds: # return here to avoid current map index error
        print("That's a wall, you can't go that way.")
        return player['y'], player['x'], False

    if sum([player[mineral] for mineral in minerals]) == player['backpack_capacity'] and current_map[test_y][test_x] in mineral_names.keys():
        backpack_full = True
    else:
        backpack_full = False
    
    if current_map[test_y][test_x] in mineral_names.keys():
        if player['pickaxe_level'] - 1 < minerals.index(mineral_names[current_map[test_y][test_x]]):
            pickaxe_level_too_low = True
        else:
            pickaxe_level_too_low = False
    else:
        pickaxe_level_too_low = False

    # determine movement validity
    if pickaxe_level_too_low:
        print('Your pickaxe is not good enough to mine {}.'.format(mineral_names[current_map[test_y][test_x]]))
        return player['y'], player['x'], False
    elif backpack_full:
        print("You can't carry any more, so you can't go that way.")
        return player['y'], player['x'], False
    else:
        return test_y, test_x, True


# handles sell prices and new day
def return_to_town(player):

    global game_state

    game_state = 'town'

    player['copper_price'] = randint(prices['copper'][0], prices['copper'][1])
    player['silver_price'] = randint(prices['silver'][0], prices['silver'][1])
    player['gold_price'] = randint(prices['gold'][0], prices['gold'][1])
    
    player['day'] += 1
    player['turns'] = TURNS_PER_DAY


# the script that runs when the game is won
def win_game(save_file, game_map, fog, current_map, player):

    global game_state

    print()
    print('-------------------------------------------------------------')
    print('Woo-hoo! Well done, {}, you have {} GP! '.format(player['name'], player['GP']))
    print('You now have enough to retire and play video games every day.')
    print('And it only took you {} days and {} steps! You win!'.format(player['day'], player['steps']))
    print('-------------------------------------------------------------')

    save_game(save_file, game_map, fog, current_map, player)
    
    add_high_score(player)

    game_state = 'main'


# handles using portal stone
def portal_stone(player, current_map):
    if player['y'] == 0 and player['x'] == 0:
        print('You return to town.')
    else:
        if not (player['portal_y'] == 0 and player['portal_x'] == 0):
            current_map[player['portal_y']][player['portal_x']] = ' '
        player['portal_y'] = player['y']
        player['portal_x'] = player['x']
        current_map[player['portal_y']][player['portal_x']] = 'P'
        print('You place your portal stone here and zap back to town.')

    return_to_town(player)


# has a chance to restore mined ores when entering mine
def replenish_nodes(game_map, current_map):
    nodes_were_replenished = False
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if game_map[row][col] in mineral_names.keys() and current_map[row][col] == ' ':
                
                # gets an array of the node types surrounding the node
                # with these parameters, it checks current map for empty spaces or ore nodes
                nearby_node_types = neighbour_nodes(current_map, [row, col], ' CSG')

                # boosts chance of replenishing to 50% if node is isolated
                if game_map[row][col] not in nearby_node_types:
                    chance = 2
                else:
                    chance = 5
                
                if randint(1, chance) == 1:
                    current_map[row][col] = game_map[row][col]
                    nodes_were_replenished = True
    
    if nodes_were_replenished:
        print("Peering into the cave, you notice that some nodes were replenished!")


# manages all mine related code
def mine(save_file, game_map, fog, current_map, player):

    global game_state

    game_state = 'mine'

    replenish_nodes(game_map, current_map)

    print()
    print('---------------------------------------------------')
    print('{:^51}'.format('DAY ' + str(player['day'])))
    print('---------------------------------------------------')
    valid = '[mipq' + ''.join(movement_buttons) + ']'

    while True:
        show_mine_menu(current_map, player)
        
        player_action = prompt(valid, "Action? ")
        if player_action in movement_buttons:
            player['y'], player['x'], successful_move = attempt_move(player_action, player, current_map)
            if successful_move:
                node = [player['y'], player['x']]
                nodes = get_surrounding_nodes([player['y'], player['x']], player['torch_level'])
                clear_fog(fog, nodes)
                interact_node(current_map, player, node)
        elif player_action == 'm':
            mine_map = draw_map(current_map, fog)
            print(mine_map)
        elif player_action == 'i':
            show_information(player)
        elif player_action == 'p':
            print()
            print('-----------------------------------------------------')
            portal_stone(player, current_map)
        else:
            save_or_not = prompt('[yn]',"Would you like to save before quitting? Unsaved data will be lost otherwise. [Y/N]: ")
            if save_or_not == 'y':
                save_game(save_file, game_map, fog, current_map, player)
            game_state = 'main'

        if game_state != 'mine':
            break


# display town menu
def show_town_menu():
    print()
    print("DAY", player['day'])
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("(S)ell ores")
    print("Go to (W)arehouse")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")


# manages all town related decisions
def town(save_file, game_map, fog, current_map, player):

    global game_state
    
    while True:
        show_town_menu()
        player_action = prompt('[bswimevq]')
        if player_action == 'b':
            shop_menu(player)
        elif player_action == 's':
            sell_menu(player)
        elif player_action == 'w':
            warehouse_menu(player)
        elif player_action == 'i':
            show_information(player)
        elif player_action == 'm':
            mine_map = draw_map(current_map, fog)
            print(mine_map)
        elif player_action == 'e':
            mine(save_file, game_map, fog, current_map, player)
        elif player_action == 'v':
            save_game(save_file, game_map, fog, current_map, player)
        else:
            save_or_not = prompt('[yn]',"Would you like to save before quitting? Unsaved data will be lost otherwise. [Y/N]: ")
            if save_or_not == 'y':
                save_game(save_file, game_map, fog, current_map, player)
            game_state = 'main'
            break
            
        if game_state != 'town':
            break


# runs the appropriate function based on game state
def game(save_file, game_map, fog, current_map, player):

    global game_state

    while True:
        if game_state == 'town':
            town(save_file, game_map, fog, current_map, player)
        elif game_state == 'mine':
            mine(save_file, game_map, fog, current_map, player)
        elif game_state == 'main':
            break
        elif game_state == 'win':
            win_game(save_file, game_map, fog, current_map, player)
            break


# display main menu
def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")


# manage main menu navigation
def main_menu(game_map, fog, current_map, player):

    global game_state

    while True:
        show_main_menu()
        main_menu_choice = prompt('[nlhq]')

        if main_menu_choice == 'n':
            save_file = choose_save_slot()
            if 'q' in save_file:
                continue
            initialize_game(save_file, game_map, fog, current_map, player)
            game(save_file, game_map, fog, current_map, player) 
        elif main_menu_choice == 'l':
            save_file = choose_save_slot(False)
            if 'q' in save_file:
                continue
            load_game(save_file, game_map, fog, current_map, player)
            game(save_file, game_map, fog, current_map, player)
        elif main_menu_choice == 'h':
            show_high_scores()
        else:
            break


def main():
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.")
    print()
    print("How quickly can you get the 1000 GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")

    main_menu(game_map, fog, current_map, player)


#--------------------------- MAIN GAME ---------------------------
if __name__ == "__main__":
    main()

