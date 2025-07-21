from random import randint

player = {}
game_map = []
current_map = []
fog = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

SAVE_FILE_NAME = 'save{}.txt'

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

# This function converts the map data from the save file into a nested list
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(map_data, game_map, current_map):

    global MAP_WIDTH
    global MAP_HEIGHT

    game_map.clear()
    current_map.clear()
    
    for row in map_data:
        map_row = []
        for node in row:
            map_row.append(node)
        game_map.append(map_row)

    current_map.extend(game_map)
        
    MAP_WIDTH = len(game_map[0])
    MAP_HEIGHT = len(game_map)

# loads fog map from save data
def load_fog(save_data):
    fog = []
    for line in range(60,70):
        fog.append(save_data[line])
    return fog

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
    load_map(get_map(), game_map, current_map)

    # TODO: initialize fog
    create_fog(fog)
    
    # TODO: initialize player
    #   You will probably add other entries into the player dictionary
    name = prompt(message="Greetings, miner! What is your name? ")
    if name:
        player['name'] = name
    else: # default player name if nothing was entered
        player['name'] = 'Player'
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY

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
# such as the player name, day, gold and steps taken.
def save_file_details(slot_choice):
    '''
    All info to be displayed is appended into a list to be printed,
    rather than loaded into individual variables
    as this information does not need to be saved into memory for the game to run
    and will just be unneccessary fluff
    '''
    save_file = SAVE_FILE_NAME.format(slot_choice)
    save_file_info = [] 
    try: 
        with open(save_file, 'r') as save:
            save_file_info.append(save.readline().strip()) # get name
            save_file_info.append('DAY ' + save.readline().strip())
            save_file_info.append('GP: ' + save.readline().strip())
            save_file_info.append('STEPS: ' + save.readline().strip())
        return save_file_info
    except FileNotFoundError:
        return None
    
# Sundrop Caves has 5 save slots. This function will handle the selection logic.
def choose_save_slot():
    for slot in range(1,6):
        print('----- Slot {} -----'.format(slot))
        save_file_info = save_file_details(slot)
        if save_file_info:
            for info in save_file_info:
                print(info)
        else:
            print('Empty save slot')
    print('------------------')
    slot_choice = prompt(['1','2','3','4','5','x'], "Please select a save slot (X to cancel): ")
    if save_file_details(slot_choice):
        if prompt(['y','n'], 'Warning! The save slot you have chosen already contains a save file. Are you sure you want to override it? [Y/N]: ') != 'Y':
            print("Cancelling save.")
            return choose_save_slot() # Recursion until decision is made
        else:
            return slot_choice
    else:
        return slot_choice

# This function saves the game
def save_game(game_map, fog, current_map, player):
    # get save file
    
    slot_choice = choose_save_slot()
    if slot_choice == 'x':
        return
    save_file = SAVE_FILE_NAME.format(slot_choice)

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
def load_game(game_map, fog, player):
    # load player
    # load map
    # load fog
    return

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
    # TODO: Show Day
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")
    # prompt(['b','i','m','e','v','q'])

# it insists upon itself
def game():
    pass

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
def main_menu():
    show_main_menu()
    main_menu_choice = prompt(['n','l','q'])

    if main_menu_choice == 'n':
        slot_choice = choose_save_slot()
        print(slot_choice)
        if slot_choice == 'x':
            return
        save_file = SAVE_FILE_NAME.format(slot_choice)
        initialize_game(save_file, game_map, current_map, fog, player)
        game() 
    elif main_menu_choice == 'l':
        load_game()
        game()
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

main_menu()
    
