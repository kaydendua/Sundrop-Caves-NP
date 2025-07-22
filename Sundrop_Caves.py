from random import randint

player = {}
game_map = []
current_map = []
fog = []

MAX_SAVE_SLOTS = 5

PLAYER_DICT_SIZE = 12
MAP_NODES = ['T', 'C', 'S', 'G', 'P']
FOG_NODES = ['?']

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

PICKAXE_MAX_LEVEL = 2

SAVE_FILE_NAME = 'save{}.txt'

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_prices = [0, 50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

drop_rates = {}
drop_rates['copper'] = (1, 5)
drop_rates['silver'] = (1, 3)
drop_rates['gold'] = (1, 2)

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

# loads fog map from save data
# def load_fog(save_data, fog):
#     fog.clear()
#     for line in range(60,70):
#         fog_row = []
#         for node in save_data[line]:
#             fog_row.append(node)
#         fog.append(fog_row)

# This function retrieves the map from the level1.txt file. It will be replaced with a map generator.
def get_map():
    map_data = []
    with open('level1.txt', 'r') as map_file:
        for line in map_file:
            map_data.append(line)
    return map_data

# Creates a new fog map
def create_fog(fog):
    fog.clear()
    for y in range(MAP_HEIGHT):
        fog_row = []
        for x in range(MAP_WIDTH):
            fog_row.append('?')
        fog.append(fog_row)

# This function clears the fog of war at the 3x3 square around the player
def clear_fog(fog, player):
    return

def initialize_game(save_file, game_map, fog, current_map, player):
    # initialize map
    load_map(get_map(), 0, 10, game_map)
    current_map.extend(game_map)

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

    save_game(save_file, game_map, fog, current_map, player)

    return game_map, current_map, fog, player
    
# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):
    return

# This function draws the 3x3 viewport
def draw_view(game_map, fog, player):
    return

# This function shows the information for the player
def show_information(player):
    return

# This function reads key information from a save file for temporary display, 
# such as the player name, day, gold and steps taken, and returns it as a list of strings to be printed
def save_file_details(slot_choice):
    save_file = SAVE_FILE_NAME.format(slot_choice)
    save_file_info = [] 
    try: 
        with open(save_file, 'r') as save:
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
        for slot in range(1, MAX_SAVE_SLOTS + 1):
            print('----- Slot {} -----'.format(slot))
            save_file_info = save_file_details(slot)
            if save_file_info:
                for info in save_file_info:
                    print(info)
            else:
                print('Empty save slot')
        print('------------------')

        save_file = SAVE_FILE_NAME.format(prompt(['1','2','3','4','5','q'], "Please select a save slot (Q to cancel): "))
        if save_file_details(save_file) and saving:
            if prompt(['y','n'], 'Warning! The save slot you have chosen already contains a save file. Are you sure you want to override it? [Y/N]: ') != 'Y':
                print("Cancelling save.")
                continue
            else:
                return save_file
        elif not save_file_details and not saving:
            print('The save slot you chose is empty. Please try again')
            continue
        else:
            return save_file

# This function saves the game
def save_game(save_file, game_map, fog, current_map, player):

    save_data = []

    # save player 
    # saves key alongside value for flexibility
    for key in player:
        save_data.append('{},{}'.format(key, player[key]))

    # padding
    save_data.append('\n' * ((50 - len(save_data)) - 1))

    # save game map
    for row in game_map:
        save_data.append('\n'.join(row))
    # save fog
    for row in fog:
        save_data.append('\n'.join(row))
    # save current map
    for row in current_map:
        save_data.append('\n'.join(row))
    
    with open(save_file, 'w') as save_file:        
        save_file.write('\n'.join(save_data))
    print('Game saved.')
        
# This function loads the game
def load_game(save_file, game_map, fog, current_map, player):
    save_file = open(save_file, 'r')
    save_data = save_file.read().split('\n')
    # load player
    for line in range(0,50):
        if save_data[line]:
            info = save_data[line].split(',')
            player[info[0]] = info[1]
        else:
            break

    # load game map
    load_map(save_data, 50, 60, game_map)
            
    # load fog
    text_to_list(save_data, 60, 70,fog, FOG_NODES)

    # load current map
    text_to_list(save_data, 70, 80, current_map, MAP_NODES)

    try:
        error_detect = 'Missing player data.'
        assert len(player) == PLAYER_DICT_SIZE
        error_detect = 'Map size mismatch'
        assert len(fog[0]) == MAP_WIDTH and len(fog) == MAP_HEIGHT
        assert len(current_map[0]) == MAP_WIDTH and len(current_map) == MAP_HEIGHT
    except AssertionError:
        print("Error in save data.", error_detect)
        quit()


# This function handles all prompts. It takes in a list of valid inputs and
# loops until it receives a valid input.
def prompt(valid=[], message='Your choice? '):      
    while True:
        player_input = input(message).lower()
        if not valid: # empty valid array means all inputs are accepted
            return player_input
        elif player_input in valid:
            return player_input     
        else:
            print('"{}" is not a valid input. Please try again.'.format(player_input))

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

def show_shop_menu():
    pickaxe_level = player['pickaxe_level']
    backpack_capacity = player['backpack_capacity']
    accepted_inputs = []
    print()
    print('----------------------- Shop Menu -------------------------')
    if player['pickaxe_level'] == PICKAXE_MAX_LEVEL:
        print('Your pickaxe cannot be upgraded any further!')
    else:
        print('(P)ickaxe upgrade to Level {} to mine {} ore for {} GP', pickaxe_level + 1, minerals[pickaxe_level], pickaxe_prices[pickaxe_level])
        accepted_inputs.append('p')

    print('(B)ackpack upgrade to carry {} items for {} GP'.format(backpack_capacity + 2, backpack_capacity * 2))
    accepted_inputs.append('b')

    print('(L)eave shop ')
    accepted_inputs.append('l')

    print('-----------------------------------------------------------')
    print('GP:', player['GP'])
    print('-----------------------------------------------------------')
    return pickaxe_prices[pickaxe_level], backpack_capacity * 2
    
# it insists upon itself
def game(save_file, game_map, fog, current_map, player):
    show_town_menu(player)
    player_action = prompt(['b','i','m','e','v','q'])
    if player_action == 'b':
        shop_menu(player)

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
            pass

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
