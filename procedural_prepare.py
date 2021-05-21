# The first script prepares your save by adding up to 100,000 seeds to it.
# Usage: python procedural_prepare.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_SEEDS_ITERATIONS]

import sys
import json
import copy
from collections import OrderedDict

# region const

ITEMS_FREIGHTER = [
    'UP_FRHYP',
    'UP_FRSPE',
    'UP_FRFUE',
    'UP_FRCOM',
    'UP_FRTRA',
    'UP_FREXP',
    'UP_FRMIN',
]
ITEMS_PRODUCT = [
    'PROC_LOOT',
    'PROC_HIST',
    'PROC_BIO',
    'PROC_FOSS',
    'PROC_PLNT',
    'PROC_TOOL',
    'PROC_FARM',
    'PROC_SEA',
    'PROC_FEAR',
    'PROC_SALV',
    'PROC_BONE',
    'PROC_DARK',
    'PROC_STAR',
]
ITEMS_SHIP = [
    'UP_PULSE',
    'UP_LAUN',
    'UP_HYP',
    'UP_S_SHL',
    'UP_SGUN',
    'UP_SLASR',
    'UP_SSHOT',
    'UP_SMINI',
    'UP_SBLOB',
]
ITEMS_SHIP_LIVING = [
    'UA_PULSE',
    'UA_LAUN',
    'UA_HYP',
    'UA_S_SHL',
    'UA_SGUN',
    'UA_SLASR',
]
ITEMS_SUIT = [
    'UP_ENGY',
    'UP_HAZ',
    'UP_JET',
    'UP_SHLD',
    'UP_UNW',
    'UP_RAD',
    'UP_TOX',
    'UP_COLD',
    'UP_HOT',
]
ITEMS_VEHICLE = [
    'UP_EXGUN',
    'UP_EXLAS',
    'UP_BOOST',
    'UP_EXENG',
]
ITEMS_VEHICLE_MECH = [
    'UP_MCLAS',
    'UP_MCGUN',
    'UP_MCENG',
]
ITEMS_VEHICLE_SUBMARINE = [
    'UP_EXSUB',
    'UP_SUGUN',
]
ITEMS_WEAPON = [
    'UP_LASER',
    'UP_SCAN',
    'UP_BOLT',
    'UP_GREN',
    'UP_TGREN',
    'UP_RAIL',
    'UP_SHOT',
    'UP_SMG',
]

ITEMS = [
    ITEMS_FREIGHTER,
    ITEMS_PRODUCT,
    ITEMS_SHIP,
    ITEMS_SHIP_LIVING,
    ITEMS_SUIT,
    ITEMS_VEHICLE,
    ITEMS_VEHICLE_MECH,
    ITEMS_VEHICLE_SUBMARINE,
    ITEMS_WEAPON,
]
MAX_SEED = 99999
TOTAL_SEEDS = 100000
TYPES = OrderedDict([
    ('freighter', 'Freighter'),
    ('product', 'Product'),
    ('ship', 'Starship 0: Normal'),
    ('living', 'Starship 1: Living'),
    ('suit', 'Exosuit'),
    ('vehicle', 'Exocraft 2: Colossus'),
    ('submarine', 'Exocraft 5: Nautilon'),
    ('mech', 'Exocraft 6: Minotaur'),
    ('weapon', 'Weapon 0'),
])

# endregion


# region method


def iter_slot(inventory, item, starting_seed, nec_iter):
    """
    Add as much as possible procedural items to an inventory.

    @param inventory: inventory object of a save where to add the items
    @param item: id of the procedural item to add
    @param starting_seed: starting seed for the item
    @param nec_iter: number of necessary iterations (should be an even number)
    """
    if starting_seed > MAX_SEED:
        return

    width = 8  # max visible in-game
    height = int(TOTAL_SEEDS / nec_iter / width)  # as much as possible

    inventory["=Tb"] = width
    inventory["N9>"] = height

    # use object of first procedural item as template
    template = None
    for slot in inventory[':No']:
        if '#' in slot['b2n']:
            template = copy.deepcopy(slot)
            break

    if not template:
        return

    # add item with seeds based on the passed arguments
    inventory[':No'] = []
    for i in range(width * height):
        if starting_seed > MAX_SEED:
            break

        duplicate = copy.deepcopy(template)
        duplicate['3ZH']['>Qh'] = i % width
        duplicate['3ZH']['XJ>'] = int(i / width)
        duplicate['b2n'] = f'^{item}#{starting_seed}'
        inventory[':No'].append(duplicate)

        starting_seed += 1

# endregion

# region input

if len(sys.argv) < 3:
    print('ERROR: Not enough arguments! Usage: python procedural_prepare.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_SEEDS_ITERATIONS]')
    exit()

f_name = sys.argv[1]
intruction = {
    'item': sys.argv[2],
    'iteration': int(sys.argv[3]) if len(sys.argv) >= 5 else 1,
    'iteration_necessary': int(sys.argv[4]) if len(sys.argv) >= 5 else 1,
}

item = intruction['item'][:-1]
type_identifier = None

# determine where to put the item
for t, l in zip(TYPES.keys(), ITEMS):
    if item in l:
        type_identifier = t

if not type_identifier:
    print(f'ERROR: Unknown item ({intruction["item"]})')
    exit()

# endregion

# region algorithm

with open(f_name, 'r') as f:
    print('Read')
    save = json.loads(f.read()[:-1])

counting_seed = int(TOTAL_SEEDS / intruction['iteration_necessary'])

starting_seed = (intruction['iteration'] - 1) * counting_seed


def call_iter(inventory):
    iter_slot(inventory, intruction['item'], starting_seed, intruction['iteration_necessary'])


print(f'Update {TYPES[type_identifier]} with {intruction["item"]} ({starting_seed} - {starting_seed + counting_seed - 1})')

inventory = {
    'freighter': save['6f=']['8ZP'],
    'product': save['6f='][';l5'],
    'ship': save['6f=']['@Cs'][0][';l5'],
    'living': save['6f=']['@Cs'][1][';l5'],
    'suit': save['6f='][';l5'],
    'vehicle': save['6f=']['P;m'][2][';l5'],
    'submarine': save['6f=']['P;m'][5][';l5'],
    'mech': save['6f=']['P;m'][6][';l5'],
    'weapon': save['6f=']['SuJ'][0]['OsQ'],
}
call_iter(inventory[type_identifier])

with open(f_name, 'w') as f:
    print('Write')
    json.dump(save, f, separators=(',', ':'))
    f.write('\x00')

# endregion
