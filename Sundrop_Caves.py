from random import randint

# it deeply upsets me that i cannot use classes

# TODO:
# high score leaderboard
# replenishing nodes
# show inventory
# warehouse and selling 
# random events
# travelling merchant (appears every 5 days, has 3 random items)
#   magic torch
#   super torch (unlocked after magic torch)
#   steel blade
#   special key (dragon)
#   ore package (random amount of ores sold at minimum price)
#   miner's watch (replenish all nodes)
#   hard hat (less random events)
#   four-leaf clover (more random events)
#   red vial (burns enemies, heals player)
#
# 2nd mine and bossfight


player = {}
game_map = []
current_map = []
fog = []

MAX_SAVE_SLOTS = 5

PLAYER_DICT_SIZE = 16
PLAYER_DATA_LINES = 50
MAP_NODES = ['T', 'C', 'S', 'G', 'P']
FOG_NODES = ['?']

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

PICKAXE_MAX_LEVEL = 3
BACKPACK_UPGRADE_AMOUNT = 2

SAVE_FILE_NAME = 'save{}.txt'

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

# This function handles all prompts. It takes in a list of valid inputs and
# loops until it receives a valid input.
def prompt(valid=[], message='Your choice? '):      
    while True:
        player_input = input(message).lower()
        check = player_input.lower()
        if not valid: # empty valid array means all inputs are accepted
            return check
        elif check in valid:
            return check
        else:
            print('"{}" is not a valid input. Please try again.'.format(player_input))

# Converts text data to nested list and loads it into a variable (target)
# Also optionally cleans unwanted data
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
# searchfor can be the y and x coordinates of a specific node or a string of node types
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
                if map_struct[row][col] in checkfor and [row, col] != node:
                    nodes.append(map_struct[row][col])
    return nodes


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
            for node in range(map_width):
                if map_struct[row][node] == ' ':
                    # beginner area shall only contain copper, also immediate surrounding area from T is empty
                    if distance_from('T', [row, node], map_struct) <= 1.5:
                        continue

                    elif distance_from('T', [row, node], map_struct) < 0.15 * max_distance:
                        if randint(1,2) == 1:
                            # cannot put ores too close together
                            if distance_from(' T', [row, node], map_struct, True) > spread:
                                map_struct[row][node] = 'C'
                    
                    # main area will contain all ores
                    elif distance_from('T', [row, node], map_struct) < 0.90 * max_distance:
                        chance = randint(1,16)
                        if chance == 1:
                            if distance_from(' ', [row, node], map_struct, True) > spread:
                                map_struct[row][node] = 'C'
                        elif chance <= 3:
                            if distance_from(' ', [row, node], map_struct, True) > spread:
                                map_struct[row][node] = 'S'
                        elif chance == 4:
                            if distance_from(' ', [row, node], map_struct, True) > spread:
                                map_struct[row][node] = 'G'
                    
                    # farthest corner will contain gold
                    else:
                        if randint(1,3) == 1:
                            if distance_from(' ', [row, node], map_struct, True) > spread:
                                map_struct[row][node] = 'G'
        
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
            if copper_count >= 15 and silver_count >= 10 and gold_count >= 10: # ensure sufficient ore for the player
                break

    return map_struct

# Creates a new fog map
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

def initialize_game(save_file, game_map, fog, current_map, player):

    global game_state
    global MAP_HEIGHT
    global MAP_WIDTH

    game_state = 'town'
    MAP_HEIGHT = 10
    MAP_WIDTH = 31

    # initialize map
    game_map.clear()
    current_map.clear()

    game_map.extend(generate_map(MAP_WIDTH, MAP_HEIGHT, 4, 0.33, 0.5))

    # copies game map row by row to make 2 seperate maps that will not affect each other
    current_map.extend([row[:] for row in game_map]) 

    # initialize fog
    create_fog(fog)
    
    # initialize player
    #   You will probably add other entries into the player dictionary

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
    player['backpack_storage'] = []
    
    save_game(save_file, game_map, fog, current_map, player)
    
# This function draws the entire map, covered by the fog
def draw_map(current_map, fog):

    global game_state

    map_view = '+' + '-' * MAP_WIDTH + '+\n'
    
    for row in range(MAP_HEIGHT):
        map_row = []
        for node in range(MAP_WIDTH):
            if [row, node] == [0, 0] and game_state == 'town':
                map_row.append('M')
            elif player['y'] == row and player['x'] == node and game_state == 'mine':
                map_row.append('M')
            elif fog[row][node] == '?':
                map_row.append('?')
            else:
                map_row.append(current_map[row][node])
        map_view += '|' + ''.join(map_row) + '|\n'

    map_view += '+' + '-' * MAP_WIDTH + '+'
    return map_view

# This function returns an array of all the nodes surrounding the player
def get_surrounding_nodes(player):
    nodes = []
    # check if node is within +-1 x AND +-1 y
    for row in range(player['y'] - player['torch_level'], player['y'] + player['torch_level'] + 1):
        for node in range(player['x'] - player['torch_level'], player['x'] + player['torch_level'] + 1):
            nodes.append([row, node])
    return nodes

# This function clears the fog of war at the 3x3 square around the player
def clear_fog(fog, nodes):
    for node in nodes:
        row = node[0]
        col = node[1]
        if 0 <= row < MAP_HEIGHT and 0 <= col < MAP_WIDTH:
            fog[row][col] = ' '

# This function draws the 3x3 viewport
def draw_view(current_map, player, nodes, view_padding):
    view_size = 2 * player['torch_level'] + 1 
    view = '+' + '-' * view_size * (view_padding + 1) + '-' * view_padding + '+\n|' + ' ' * view_padding
    pos = 1
    for node in nodes:
        row = node[0]
        col = node[1]
        
        if node == [player['y'], player['x']]:
            view += 'M'
        elif -1 < row < MAP_HEIGHT and -1 < col < MAP_WIDTH: # In bounds
            try:
                view += current_map[row][col]
            except:
                print(row, col)
                print(game_map)
                print(current_map)
                quit()
        elif ((row == -1  or row == MAP_HEIGHT) and -1 <= col <= MAP_WIDTH) or ((col == -1 or col == MAP_WIDTH) and -1 <= row <= MAP_HEIGHT): # Border
            view += '#'
        else: # Out of bounds
            view += ' '

        if pos < view_size:
            view += view_padding * ' '
            pos += 1
        elif node == nodes[-1]:
            view += ' ' * view_padding + '|\n'
        else:
            view += ' ' * view_padding + '|\n|' + ' ' * view_padding
            pos = 1

    view += '+' + '-' * view_size * (view_padding + 1) + '-' * view_padding + '+' 
    return view

# This function shows the information for the player
def show_information(player):
    print()
    print("----- Player Information -----")
    print("Name:", player['name'])
    print("Portal position: ({}, {})".format(player['portal_x'], player['portal_y']))
    print("Pickaxe level: {} ({})".format(player['pickaxe_level'], minerals[player['pickaxe_level'] - 1]))
    print("------------------------------")
    print(player['backpack_storage'])
    print("Load: {} / {}".format(len(player['backpack_storage']), player['backpack_capacity']))
    print("------------------------------")
    print("GP:", player['GP'])
    print("Steps taken:", player['steps'])
    print("------------------------------")

# This function reads key information from a save file for temporary display, 
# such as the player name, day, gold and steps taken, and returns it as a list of strings to be printed
def save_file_details(save_file):
    save_file_info = [] 
    try: 
        with open(save_file, 'r') as save:
            save.readline()
            save_file_info.append(save.readline().strip().split(',')[1]) # get name
            save_file_info.append('DAY ' + save.readline().strip().split(',')[1])
            save_file_info.append('GP: ' + save.readline().strip().split(',')[1])
            save_file_info.append('STEPS: ' + save.readline().strip().split(',')[1])
        return save_file_info
    except FileNotFoundError:
        return None
    
# Sundrop Caves has 5 save slots. This function will handle the selection logic.
def choose_save_slot(saving=True):
    while True:
        print()
        for slot in range(1, MAX_SAVE_SLOTS + 1):
            print('----- Slot {} -----'.format(slot))
            save_file = SAVE_FILE_NAME.format(slot)
            save_file_info = save_file_details(save_file)
            if save_file_info:
                for info in save_file_info:
                    print(info)
            else:
                print('Empty save slot')
        print('------------------')

        save_file = SAVE_FILE_NAME.format(prompt(['1','2','3','4','5','q'], "Please select a save slot (Q to close): "))
        if 'q' in save_file:
            return save_file
        elif save_file_details(save_file) and saving:
            if prompt(['y','n'], 'Warning! The save slot you have chosen already contains a save file. Are you sure you want to override it? [Y/N]: ') != 'y':
                print("Cancelling save.")
                continue
            else:
                return save_file
        elif not save_file_details(save_file) and not saving:
            print('The save slot you chose is empty. Please try again')
            continue
        else:
            return save_file

# This function saves the game
def save_game(save_file, game_map, fog, current_map, player):

    global game_state

    save_data = []

    save_data.append(game_state)
    
    # save player 
    # saves key alongside value for flexibility
    for key in player:
        save_data.append('{},{}'.format(key, player[key]))

    # padding
    save_data.append('\n' * (((1 + PLAYER_DATA_LINES) - len(save_data)) - 1))

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

# saves winning runs to a global save file
def global_save():
    # TODO: high score save file
    pass

# displays the top scores
def show_high_scores():
    # TODO: display high scores
    pass

# This function loads the game
def load_game(save_file, game_map, fog, current_map, player):
    save_file = open(save_file, 'r')
    save_data = save_file.read().split('\n')

    global game_state

    game_state = save_data[0]

    # load player
    for line in range(1, PLAYER_DATA_LINES + 1):
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
    load_map(save_data, PLAYER_DATA_LINES + 1, PLAYER_DATA_LINES + 11, game_map)
            
    # load fog
    text_to_list(save_data, PLAYER_DATA_LINES + 11, PLAYER_DATA_LINES + 21,fog, FOG_NODES)

    # load current map
    text_to_list(save_data, PLAYER_DATA_LINES + 21, PLAYER_DATA_LINES + 31, current_map, MAP_NODES)

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



# Display town menu
def show_town_menu():
    print()
    print("DAY", player['day'])
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")

# Display shop menu and calculate prices
def show_shop_menu():
    pickaxe_level = player['pickaxe_level']
    backpack_capacity = player['backpack_capacity']
    accepted_inputs = []
    print()
    print('----------------------- Shop Menu -------------------------')
    if player['pickaxe_level'] == PICKAXE_MAX_LEVEL:
        print('Your pickaxe cannot be upgraded any further!')
    else:
        print('(P)ickaxe upgrade to Level {} to mine {} ore for {} GP'.format(pickaxe_level + 1, minerals[pickaxe_level], pickaxe_prices[pickaxe_level]))
        accepted_inputs.append('p')

    print('(B)ackpack upgrade to carry {} items for {} GP'.format(backpack_capacity + BACKPACK_UPGRADE_AMOUNT, backpack_capacity * 2))
    accepted_inputs.append('b')

    print('(L)eave shop ')
    accepted_inputs.append('l')

    print('-----------------------------------------------------------')
    print('GP:', player['GP'])
    print('-----------------------------------------------------------')
    return pickaxe_prices[pickaxe_level], backpack_capacity * 2, accepted_inputs

# Manages purchasing upgrades
def shop_menu(player):
    while True:
        pickaxe_price, backpack_price, accepted_inputs = show_shop_menu()
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
        else:
            break

def show_mine_menu(current_map, player):
    print()
    print('DAY', player['day'])
    nodes = get_surrounding_nodes(player)
    viewport = draw_view(current_map, player, nodes, VIEW_PADDING)
    print(viewport)
    print('Turns left: {:<5} Load: {} / {}    Steps: {}'.format(player['turns'], len(player['backpack_storage']), player['backpack_capacity'], player['steps']))
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

        for pieces in range(amount_mined):
            player['backpack_storage'].append(node)
            if len(player['backpack_storage']) > player['backpack_capacity']:
                player['backpack_storage'].pop(0)
                print('...but you can only carry {} more piece(s)!'.format(pieces))
                break

    elif node == 'T' or node == 'P':
        if prompt(['y','n'], "Would you like to return to town? [Y/N]:") == 'y':
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
        return player['y'], player['x']

    if len(player['backpack_storage']) == player['backpack_capacity'] and current_map[test_y][test_x] in mineral_names.keys():
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

# handles selling and new day
def return_to_town(player):

    global game_state

    game_state = 'town'

    copper_price = randint(prices['copper'][0], prices['copper'][1])
    silver_price = randint(prices['silver'][0], prices['silver'][1])
    gold_price = randint(prices['gold'][0], prices['gold'][1])

    copper_sold = 0
    silver_sold = 0
    gold_sold = 0
    
    for item in range(len(player['backpack_storage'])):
        item = player['backpack_storage'].pop(0)
        if item == 'C':
            copper_sold += 1
        elif item == 'S':
            silver_sold += 1
        elif item == 'G':
            gold_sold += 1
        # add more ores?
        else:
            print(item)
    
    earned = 0
    if copper_sold:
        earned = copper_sold * copper_price
        print("You sell {} copper ore for {} GP.".format(copper_sold, earned))
        player['GP'] += earned
    if silver_sold:
        earned = silver_sold * silver_price
        print("You sell {} silver ore for {} GP.".format(silver_sold, earned))
        player['GP'] += earned
    if gold_sold:
        earned = gold_sold * gold_price
        print("You sell {} gold ore for {} GP.".format(gold_sold, earned))
        player['GP'] += earned
    if earned:
        print("You now have {} GP!".format(player['GP']))
    
    if player['GP'] >= WIN_GP:
        win_game(player)
    else:
        player['day'] += 1
        player['turns'] = TURNS_PER_DAY

def win_game(player):

    global game_state

    print('-------------------------------------------------------------')
    print('Woo-hoo! Well done, {}, you have {} GP! '.format(player['name'], player['GP']))
    print('You now have enough to retire and play video games every day.')
    print('And it only took you {} days and {} steps! You win!'.format(player['day'], player['steps']))
    print('-------------------------------------------------------------')
    game_state = 'main'

# handles using portal stone
def portal_stone(player, current_map):
    current_map[player['portal_y']][player['portal_x']] = ' '
    player['portal_y'] = player['y']
    player['portal_x'] = player['x']
    current_map[player['portal_y']][player['portal_x']] = 'P'
    print('You place your portal stone here and zap back to town.')
    return_to_town(player)

# manages all mine related code
def mine(save_file, game_map, fog, current_map, player):

    global game_state

    game_state = 'mine'

    player['turns'] = TURNS_PER_DAY
    print()
    print('---------------------------------------------------')
    print('{:^51}'.format('DAY ' + str(player['day'])))
    print('---------------------------------------------------')
    valid = ['m', 'i', 'p', 'q']
    valid.extend(movement_buttons)

    while True:
        show_mine_menu(current_map, player)
        
        player_action = prompt(valid, "Action? ")
        if player_action in movement_buttons:
            player['y'], player['x'], successful_move = attempt_move(player_action, player, current_map)
            if successful_move:
                node = [player['y'], player['x']]
                nodes = get_surrounding_nodes(player)
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
            save_or_not = prompt(['y','n'],"Would you like to save before quitting? Unsaved data will be lost otherwise. [Y/N]: ")
            if save_or_not == 'y':
                save_game(save_file, game_map, fog, current_map, player)
            game_state = 'main'

        if game_state != 'mine':
            break

# it insists upon itself
def game(save_file, game_map, fog, current_map, player):

    global game_state

    while True:
        if game_state == 'town':
            town(save_file, game_map, fog, current_map, player)
        elif game_state == 'mine':
            mine(save_file, game_map, fog, current_map, player)
        elif game_state == 'main':
            break

# manages all town related decisions
def town(save_file, game_map, fog, current_map, player):

    global game_state
    
    while True:
        show_town_menu()
        player_action = prompt(['b','i','m','e','v','q'])
        if player_action == 'b':
            shop_menu(player)
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
            save_or_not = prompt(['y','n'],"Would you like to save before quitting? Unsaved data will be lost otherwise. [Y/N]: ")
            if save_or_not == 'y':
                save_game(save_file, game_map, fog, current_map, player)
            game_state = 'main'
            break
            
        if game_state == 'main':
            break

# Display main menu
def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
#    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")

# Manage main menu navigation
def main_menu(game_map, fog, current_map, player):

    global game_state

    while True:
        show_main_menu()
        main_menu_choice = prompt(['n','l','q'])

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
        else:
            break

#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print("How quickly can you get the 1000 GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

main_menu(game_map, fog, current_map, player)
