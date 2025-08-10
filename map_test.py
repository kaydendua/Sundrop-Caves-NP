from Sundrop_Caves import generate_map, prompt
import pytest
import time

MAP_WIDTH = 30
MAP_HEIGHT = 10

def show_map(map_struct):

    print()
    map_view = '+' + '-' * MAP_WIDTH + '+\n'
    
    for row in range(MAP_HEIGHT):
        map_row = []
        for node in range(MAP_WIDTH):
            map_row.append(map_struct[row][node])
        map_view += '|' + ''.join(map_row) + '|\n'

    map_view += '+' + '-' * MAP_WIDTH + '+'
    return map_view

def calculate_density(map_struct):
    total = 0
    copper = 0
    silver = 0
    gold = 0
    diamond = 0
    for row in map_struct:
        for node in row:
            if node == "C":
                copper += 1
            elif node == "S":
                silver += 1
            elif node == "G":
                gold += 1
            elif node == 'D':
                diamond += 1
            total += 1
    
    return copper, silver, gold, diamond, total


while prompt(message="Press enter to generate map, 'Q' to stop: ") != 'q':
    timer = time.time()
    map_struct = generate_map(map_width=30, map_height=10, spread=4, min_density=0.33, max_density=0.50)
    time_taken = time.time() - timer
    
    print(show_map(map_struct))
    print("Time taken: {:.3f}".format(time_taken))

    copper, silver, gold, diamond, total = calculate_density(map_struct)
    print("Copper:", copper, "/ Silver:", silver, "/ Gold:", gold, "/ Diamond:", diamond)
    ores = copper + silver + gold + diamond
    print("Density: {}/{} = {:.3f}".format(ores, total, ores/total))
    print()