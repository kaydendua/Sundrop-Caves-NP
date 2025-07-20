from random import randint

player = {}
game_map = []
fog = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(filename, map_struct):
    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT
    
    map_struct.clear()
    
    # TODO: Add your map loading code here
    
    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()

# This function clears the fog of war at the 3x3 square around the player
def clear_fog(fog, player):
    return

def initialize_game(game_map, fog, player):
    # initialize map
    load_map("level1.txt", game_map)

    # TODO: initialize fog
    
    # TODO: initialize player
    #   You will probably add other entries into the player dictionary
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 0
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY

    clear_fog(fog, player)
    
# This function draws the entire map, covered by the fof
def draw_map(game_map, fog, player):
    return

# This function draws the 3x3 viewport
def draw_view(game_map, fog, player):
    return

# This function shows the information for the player
def show_information(player):
    return

# This function reads key information from a save file for display, 
# such as the player name, day, gold and steps taken.
def save_file_details(filename):
    '''
    All info to be displayed is appended into a list to be printed,
    rather than loaded into individual variables
    as this information does not need to be saved into memory for the game to run
    and will just be unneccessary fluff
    '''
    save_file_info = [] 
    try: 
        with open(filename, 'r') as save:
            save_file_info.append(save.readline().strip()) # get name
            save_file_info.append('DAY ' + save.readline().strip())
            save_file_info.append('GP: ' + save.readline().strip())
            save_file_info.append('STEPS: ' + save.readline().strip())
        return save_file_info
    except FileNotFoundError:
        return None
    
# Sundrop Caves has 5 save slots. This function will handle the selection logic.
def save_file_slots():
    for slot in range(1,6):
        print('----- Slot {} -----'.format(slot))
        save_file_info = save_file_details('save{}.txt'.format(slot))
        if save_file_info:
            for info in save_file_info:
                print(info)
        else:
            print('Empty save slot')
    print('------------------')
    return


# This function saves the game
def save_game(game_map, fog, player):
    # save map
    # save fog
    # save player
    return
        
# This function loads the game
def load_game(game_map, fog, player):
    # load map
    # load fog
    # load player
    return

# This function handles all prompts. It takes in a list of valid inputs and
# loops until it receives a valid input.
def prompt(valid, message='Your choice? '):      
    while True:
        player_input = input(message).lower()
        if player_input in valid:
            return player_input     
        else:
            print('"{}" is not a valid input. Please try again.'.format(player_input))

def main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
#    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")
    return prompt(['n','l','q'])

def town_menu():
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
    return prompt(['b','i','m','e','v','q'])

# it insists upon itself
def game():
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

player_input = main_menu()
save_file_slots()
    
