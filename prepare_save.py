# The first script prepares your save by adding up to 100,000 seeds to it.
# Usage: python prepare_save.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_ITERATIONS]

import copy
import json
import lz4.block as lz4
import os
import struct
import sys

from read_data import get_has_class
from read_data import ITEMS, TOTAL_SEEDS, TYPES

# region const

MAX_SEED = TOTAL_SEEDS - 1  # starts at 0
SLICE = 524288

# endregion


# region method


def compress_file(data):
    """
    Adapted from https://github.com/UNOWEN-OwO/NMS-Save-Parser/blob/main/convert.py#L42
    """

    result = b''
    while block := data[:SLICE]:
        data = data[SLICE:]

        block += b'\x00' if len(block) < SLICE and block[-1] != b'\x00' else b''
        compressed_block = lz4.compress(block, store_size=False)
        result += b'\xE5\xA1\xED\xFE' + struct.pack('i', len(compressed_block)) + struct.pack('i', len(block)) + (b'\x00' * 4) + compressed_block

    return result


def iter_slot(inventory, item, seed, nec_iter):
    """
    Add as much as possible procedural items to an inventory.

    @param inventory: inventory object of a save where to add the items
    @param item: id of the procedural item to add
    @param starting_seed: starting seed for the item
    @param nec_iter: number of necessary iterations (should be an even number)
    """
    if seed > MAX_SEED:
        return

    width = 10
    height = int(TOTAL_SEEDS / nec_iter / width)  # as much as possible
    template = {
        'Vn8': {
            'elv': 'Technology',
        },
        'b2n': None,  # set below
        '1o9': -1,
        'F9q': 100,
        'eVk': 0.0,
        'b76': True,
        '3ZH': {
            '>Qh': None,  # set below
            'XJ>': None,  # set below
        }
    }

    # prepare inventory size
    inventory["=Tb"] = width
    inventory["N9>"] = height

    # add item with seeds based on the passed arguments
    for i in range(width * height):
        if seed > MAX_SEED:
            break

        duplicate = copy.deepcopy(template)
        duplicate['3ZH']['>Qh'] = i % width  # X
        duplicate['3ZH']['XJ>'] = int(i / width)  # Y
        duplicate['b2n'] = f'^{item}#{seed}'
        inventory[':No'].append(duplicate)

        seed += 1


def load_file(filepath):
    """
    Adapted from https://github.com/UNOWEN-OwO/NMS-Save-Parser/blob/main/convert.py#L53
    """
    with open(filepath, 'rb') as f:
        print('Read')
        mode = None
        uncompressed = b''

        while f.read(4) == b'\xE5\xA1\xED\xFE':
            block_size = struct.unpack('i', f.read(4))[0]
            uncompressed_size = struct.unpack('i', f.read(4))[0]
            f.read(4)
            uncompressed += lz4.decompress(f.read(block_size), uncompressed_size=uncompressed_size)

        if f.read(1):
            f.seek(0)
            uncompressed = f.read().rstrip(b'\x00')
            mode = 0
        else:
            uncompressed = uncompressed.rstrip(b'\x00')
            mode = 1

        return json.loads(uncompressed), mode


# endregion


if __name__ == '__main__':
    # region input

    if len(sys.argv) < 3:
        print('ERROR: Not enough arguments! Usage: python prepare_save.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_SEEDS_ITERATIONS]')
        exit()

    f_filepath = sys.argv[1]
    intruction = {
        'item': sys.argv[2].upper(),
        'iteration': int(sys.argv[3]) if len(sys.argv) >= 5 else 1,
        'iteration_necessary': int(sys.argv[4]) if len(sys.argv) >= 5 else 1,
    }

    module = intruction['item']
    if not module.startswith('PROC_') and get_has_class(module):
        module = module[:-1]
    type_identifier = None

    # determine where to put the item
    for t, l in zip(TYPES.keys(), ITEMS):
        if module in l:
            type_identifier = t

    if not type_identifier:
        print(f'ERROR: Unknown item ({intruction["item"]})')
        exit()

    # endregion

    # region algorithm

    save, is_compressed = load_file(f_filepath)

    counting_seed = int(TOTAL_SEEDS / intruction['iteration_necessary'])
    starting_seed = (intruction['iteration'] - 1) * counting_seed

    print(f'Update {TYPES[type_identifier]} with {intruction["item"]} ({starting_seed} - {starting_seed + counting_seed - 1})')

    inventories = {
        'Freighter': save['6f=']['0wS'],
        'Product': save['6f='][';l5'],
        'Ship': save['6f=']['@Cs'][0]['PMT'],
        'AlienShip': save['6f=']['@Cs'][0]['PMT'],
        'Suit': save['6f=']['PMT'],
        'Exocraft': save['6f=']['P;m'][2]['PMT'],
        'Submarine': save['6f=']['P;m'][5]['PMT'],
        'Mech': save['6f=']['P;m'][6]['PMT'],
        'Weapon': save['6f=']['SuJ'][0]['OsQ'],
    }
    # clear all slots of all inventories to avoid multiple 100k entires in a file
    for inventory in inventories.values():
        inventory[':No'] = inventory[':No'][:1]  # keep one or weapon will be corrupted

    # fill one of the inventories with the selected item
    iter_slot(inventories[type_identifier], intruction['item'], starting_seed, intruction['iteration_necessary'])

    # automatically use the selected ship/vehicle
    if type_identifier == 'Ship':
        base_stat_values = [
            base_stat_value
            for base_stat_value in save['6f=']['@Cs'][0][';l5']['@bB']
            if base_stat_value['QL1'] != '^ALIEN_SHIP'
        ]

        save['6f=']['@Cs'][0]['NTx']['93M'] = 'MODELS/COMMON/SPACECRAFT/FIGHTERS/FIGHTER_PROC.SCENE.MBIN'
        save['6f=']['@Cs'][0][';l5']['@bB'] = save['6f=']['@Cs'][0]['gan']['@bB'] = save['6f=']['@Cs'][0]['PMT']['@bB'] = base_stat_values
    elif type_identifier == 'AlienShip':
        base_stat_values = save['6f=']['@Cs'][0][';l5']['@bB']
        base_stat_values.append({
            'QL1': '^ALIEN_SHIP',
            '>MX': 1.0,
        })

        save['6f=']['@Cs'][0]['NTx']['93M'] = 'MODELS/COMMON/SPACECRAFT/S-CLASS/BIOPARTS/BIOSHIP_PROC.SCENE.MBIN'
        save['6f=']['@Cs'][0][';l5']['@bB'] = save['6f=']['@Cs'][0]['gan']['@bB'] = save['6f=']['@Cs'][0]['PMT']['@bB'] = base_stat_values
    elif type_identifier == 'Exocraft':
        save['6f=']['5sx'] = 2
    elif type_identifier == 'Submarine':
        save['6f=']['5sx'] = 5
    elif type_identifier == 'Mech':
        save['6f=']['5sx'] = 6

    with open(f_filepath, 'wb') as f:
        print('Write')

        json_dumps = json.dumps(save, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

        if is_compressed:
            json_dumps = compress_file(json_dumps)

        f.write(json_dumps)
        f.write(b'\x00')

    # endregion
