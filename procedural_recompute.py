# This script iterates over all stored seeds and recomputes the perfection.
# Usage: python procedural_recompute.py

import csv
import os
import shutil
from datetime import datetime

from procedural import DATA, TRANSLATION

# region methods


def init_meta(data):
    """
    Convert and enrich list of stats to dictionary.
    """
    return {
        line[0]: line + (TRANSLATION[line[0]][1], TRANSLATION[line[0]][2])
        for line in data
    }

# endregion


if __name__ == '__main__':
    f_list = [
        # region Ship

        # 'Ship\\UP_HYP1.csv',
        # 'Ship\\UP_HYP2.csv',
        # 'Ship\\UP_HYP3.csv',
        # 'Ship\\UP_HYP4.csv',
        # 'Ship\\UP_HYPX.csv',

        # 'Ship\\UP_LAUN1.csv',
        # 'Ship\\UP_LAUN2.csv',
        # 'Ship\\UP_LAUN3.csv',
        # 'Ship\\UP_LAUN4.csv',
        # 'Ship\\UP_LAUNX.csv',

        # 'Ship\\UP_PULSE1.csv',
        # 'Ship\\UP_PULSE2.csv',
        # 'Ship\\UP_PULSE3.csv',
        # 'Ship\\UP_PULSE4.csv',
        # 'Ship\\UP_PULSEX.csv',

        # 'Ship\\UP_S_SHL1.csv',
        # 'Ship\\UP_S_SHL2.csv',
        # 'Ship\\UP_S_SHL3.csv',
        # 'Ship\\UP_S_SHL4.csv',
        # 'Ship\\UP_S_SHLX.csv',

        # 'Ship\\UP_SGUN1.csv',
        # 'Ship\\UP_SGUN2.csv',
        # 'Ship\\UP_SGUN3.csv',
        # 'Ship\\UP_SGUN4.csv',
        # 'Ship\\UP_SGUNX.csv',

        # 'Ship\\UP_SLASR1.csv',
        # 'Ship\\UP_SLASR2.csv',
        # 'Ship\\UP_SLASR3.csv',
        # 'Ship\\UP_SLASR4.csv',
        # 'Ship\\UP_SLASRX.csv',

        # 'Ship\\UP_SSHOT1.csv',
        # 'Ship\\UP_SSHOT2.csv',
        # 'Ship\\UP_SSHOT3.csv',
        # 'Ship\\UP_SSHOT4.csv',
        # 'Ship\\UP_SSHOTX.csv',

        # 'Ship\\UP_SMINI1.csv',
        # 'Ship\\UP_SMINI2.csv',
        # 'Ship\\UP_SMINI3.csv',
        # 'Ship\\UP_SMINI4.csv',
        # 'Ship\\UP_SMINIX.csv',

        # endregion

        # region Suit

        # 'Suit\\UP_ENGY1.csv',
        # 'Suit\\UP_ENGY2.csv',
        # 'Suit\\UP_ENGY3.csv',
        # 'Suit\\UP_ENGYX.csv',

        # 'Suit\\UP_HAZX.csv',

        # 'Suit\\UP_JET1.csv',
        # 'Suit\\UP_JET2.csv',
        # 'Suit\\UP_JET3.csv',
        # 'Suit\\UP_JET4.csv',
        # 'Suit\\UP_JETX.csv',

        # 'Suit\\UP_SHLD1.csv',
        # 'Suit\\UP_SHLD2.csv',
        # 'Suit\\UP_SHLD3.csv',
        # 'Suit\\UP_SHLD4.csv',
        # 'Suit\\UP_SHLDX.csv',

        # endregion

        # region Weapon

        # 'Weapon\\UP_BOLT1.csv',
        # 'Weapon\\UP_BOLT2.csv',
        # 'Weapon\\UP_BOLT3.csv',
        # 'Weapon\\UP_BOLT4.csv',
        # 'Weapon\\UP_BOLTX.csv',

        # 'Weapon\\UP_GREN1.csv',
        # 'Weapon\\UP_GREN2.csv',
        # 'Weapon\\UP_GREN3.csv',
        # 'Weapon\\UP_GREN4.csv',
        # 'Weapon\\UP_GRENX.csv',

        # 'Weapon\\UP_LASER1.csv',
        # 'Weapon\\UP_LASER2.csv',
        # 'Weapon\\UP_LASER3.csv',
        # 'Weapon\\UP_LASER4.csv',
        # 'Weapon\\UP_LASERX.csv',

        # 'Weapon\\UP_RAIL1.csv',
        # 'Weapon\\UP_RAIL2.csv',
        # 'Weapon\\UP_RAIL3.csv',
        # 'Weapon\\UP_RAIL4.csv',
        # 'Weapon\\UP_RAILX.csv',

        # 'Weapon\\UP_SCAN1.csv',
        # 'Weapon\\UP_SCAN2.csv',
        # 'Weapon\\UP_SCAN3.csv',
        # 'Weapon\\UP_SCAN4.csv',
        # 'Weapon\\UP_SCANX.csv',

        # 'Weapon\\UP_SHOT1.csv',
        # 'Weapon\\UP_SHOT2.csv',
        # 'Weapon\\UP_SHOT3.csv',
        # 'Weapon\\UP_SHOT4.csv',
        # 'Weapon\\UP_SHOTX.csv',

        # 'Weapon\\UP_SMG1.csv',
        # 'Weapon\\UP_SMG2.csv',
        # 'Weapon\\UP_SMG3.csv',
        # 'Weapon\\UP_SMG4.csv',
        # 'Weapon\\UP_SMGX.csv',

        # 'Weapon\\UP_TGREN1.csv',
        # 'Weapon\\UP_TGREN2.csv',
        # 'Weapon\\UP_TGREN3.csv',
        # 'Weapon\\UP_TGREN4.csv',
        # 'Weapon\\UP_TGRENX.csv',

        # endregion
    ]
    round_digits = 3

    # region algorithm

    for f_original in f_list:
        start = datetime.now()

        f_backup = f'{f_original[:-4]}.tmp.csv'

        shutil.copyfile(f_original, f_backup)

        item = f_original.split('\\')[1][:-4]
        item_name = item[:-1]  # 'UP_HAZ'
        item_class = item[-1]  # 'X'

        if item_name not in DATA or item_class not in DATA[item_name]:
            print(f'ERROR: Your procedural item ({item_name}{item_class}) is not configured')
            continue

        item_stats = DATA[item_name][item_class]

        item_stats['meta'] = init_meta(item_stats['meta'])

        count = 0
        high_number = item_stats['number']
        keys = item_stats['meta'].keys()

        with open(f_backup, 'r', newline='') as backup:
            reader = csv.DictReader(backup, dialect='excel-tab')
            with open(f_original, 'w', newline='') as original:
                writer = csv.DictWriter(original, fieldnames=reader.fieldnames, dialect='excel-tab')
                writer.writeheader()

                for row in reader:
                    count += 1
                    perfection = []

                    # Get actual values of the current item.
                    for key in keys:
                        meta = item_stats['meta'][key]

                        extract_method = meta[3]
                        value = row[key]

                        if value:
                            value = extract_method(value)

                            p = 1.0
                            if meta[2] - meta[1] > 0:
                                p -= (meta[2] - value) / (meta[2] - meta[1])
                            perfection.append(p)

                    perfection = round(sum(perfection) / high_number, round_digits) if perfection else 0

                    row.update({
                        'Perfection': perfection,
                    })

                    writer.writerow(row)

        os.remove(f_backup)

        end = datetime.now()

        print(f'{count:>6} module(s) perfection for {item} recomputed in {end - start}')

    # endregion
