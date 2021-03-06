# This script iterates over all stored seeds and recomputes the perfection.
# Usage: python recompute_perfection.py

import csv
import os
import shutil
from datetime import datetime

from read_data import get_has_class, get_high_number, get_high_number_perfection, get_is_configured, get_item_stats, get_key_possibilities, get_perfection
from read_data import TRANSLATION

# region methods


def init_meta(data):
    """
    Convert and enrich list of stats to dictionary.
    """
    is_used = lambda name: not (len(TRANSLATION[name]) >= 4 and TRANSLATION[name][3])

    weighting = [(stat[2] - stat[1] + 1 if is_used(stat[0]) else 0) for stat in data]
    weighting_min = min(weight for weight in weighting if weight)

    return {
        stat[0]: stat + ((weighting[i] / weighting_min,) if weighting[i] else (0,)) + TRANSLATION[stat[0]][1:]
        for i, stat in enumerate(data)
    }

# endregion


if __name__ == '__main__':
    f_list = [
        # region Weapon

        # 'Weapon\\UP_LASER1.csv',
        # 'Weapon\\UP_LASER2.csv',
        # 'Weapon\\UP_LASER3.csv',
        # 'Weapon\\UP_LASER4.csv',
        # 'Weapon\\UP_LASERX.csv',

        # 'Weapon\\UP_SCAN1.csv',
        # 'Weapon\\UP_SCAN2.csv',
        # 'Weapon\\UP_SCAN3.csv',
        # 'Weapon\\UP_SCAN4.csv',
        # 'Weapon\\UP_SCANX.csv',

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

        # 'Weapon\\UP_TGREN1.csv',
        # 'Weapon\\UP_TGREN2.csv',
        # 'Weapon\\UP_TGREN3.csv',
        # 'Weapon\\UP_TGREN4.csv',
        # 'Weapon\\UP_TGRENX.csv',

        # 'Weapon\\UP_RAIL1.csv',
        # 'Weapon\\UP_RAIL2.csv',
        # 'Weapon\\UP_RAIL3.csv',
        # 'Weapon\\UP_RAIL4.csv',
        # 'Weapon\\UP_RAILX.csv',

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

        # 'Weapon\\UP_CANN1.csv',
        # 'Weapon\\UP_CANN2.csv',
        # 'Weapon\\UP_CANN3.csv',
        # 'Weapon\\UP_CANN4.csv',
        # 'Weapon\\UP_CANNX.csv',

        # 'Weapon\\UP_SENGUN.csv',

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

        # 'Suit\\UP_SNSUIT.csv',

        # endregion

        # region Ship

        # 'Ship\\UP_PULSE1.csv',
        # 'Ship\\UP_PULSE2.csv',
        # 'Ship\\UP_PULSE3.csv',
        # 'Ship\\UP_PULSE4.csv',
        # 'Ship\\UP_PULSEX.csv',

        # 'Ship\\UP_LAUN1.csv',
        # 'Ship\\UP_LAUN2.csv',
        # 'Ship\\UP_LAUN3.csv',
        # 'Ship\\UP_LAUN4.csv',
        # 'Ship\\UP_LAUNX.csv',

        # 'Ship\\UP_HYP1.csv',
        # 'Ship\\UP_HYP2.csv',
        # 'Ship\\UP_HYP3.csv',
        # 'Ship\\UP_HYP4.csv',
        # 'Ship\\UP_HYPX.csv',

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

        # 'Ship\\UP_SBLOB1.csv',
        # 'Ship\\UP_SBLOB2.csv',
        # 'Ship\\UP_SBLOB3.csv',
        # 'Ship\\UP_SBLOB4.csv',
        # 'Ship\\UP_SBLOBX.csv',

        # endregion

        # region Exocraft

        # 'Exocraft\\UP_EXGUN1.csv',
        # 'Exocraft\\UP_EXGUN2.csv',
        # 'Exocraft\\UP_EXGUN3.csv',
        # 'Exocraft\\UP_EXGUN4.csv',

        # 'Exocraft\\UP_EXLAS1.csv',
        # 'Exocraft\\UP_EXLAS2.csv',
        # 'Exocraft\\UP_EXLAS3.csv',
        # 'Exocraft\\UP_EXLAS4.csv',

        # 'Exocraft\\UP_BOOST1.csv',
        # 'Exocraft\\UP_BOOST2.csv',
        # 'Exocraft\\UP_BOOST3.csv',
        # 'Exocraft\\UP_BOOST4.csv',

        # 'Exocraft\\UP_EXENG1.csv',
        # 'Exocraft\\UP_EXENG2.csv',
        # 'Exocraft\\UP_EXENG3.csv',
        # 'Exocraft\\UP_EXENG4.csv',

        # endregion

        # region Submarine

        # 'Submarine\\UP_EXSUB1.csv',
        # 'Submarine\\UP_EXSUB2.csv',
        # 'Submarine\\UP_EXSUB3.csv',
        # 'Submarine\\UP_EXSUB4.csv',

        # 'Submarine\\UP_SUGUN1.csv',
        # 'Submarine\\UP_SUGUN2.csv',
        # 'Submarine\\UP_SUGUN3.csv',
        # 'Submarine\\UP_SUGUN4.csv',

        # endregion

        # region Mech

        # 'Mech\\UP_MCLAS2.csv',
        # 'Mech\\UP_MCLAS3.csv',
        # 'Mech\\UP_MCLAS4.csv',

        # 'Mech\\UP_MCGUN2.csv',
        # 'Mech\\UP_MCGUN3.csv',
        # 'Mech\\UP_MCGUN4.csv',

        # 'Mech\\UP_MCENG2.csv',
        # 'Mech\\UP_MCENG3.csv',
        # 'Mech\\UP_MCENG4.csv',

        # endregion

        # region AlienShip

        # 'AlienShip\\UA_PULSE1.csv',
        # 'AlienShip\\UA_PULSE2.csv',
        # 'AlienShip\\UA_PULSE3.csv',
        # 'AlienShip\\UA_PULSE4.csv',

        # 'AlienShip\\UA_LAUN1.csv',
        # 'AlienShip\\UA_LAUN2.csv',
        # 'AlienShip\\UA_LAUN3.csv',
        # 'AlienShip\\UA_LAUN4.csv',

        # 'AlienShip\\UA_HYP1.csv',
        # 'AlienShip\\UA_HYP2.csv',
        # 'AlienShip\\UA_HYP3.csv',
        # 'AlienShip\\UA_HYP4.csv',

        # 'AlienShip\\UA_S_SHL1.csv',
        # 'AlienShip\\UA_S_SHL2.csv',
        # 'AlienShip\\UA_S_SHL3.csv',
        # 'AlienShip\\UA_S_SHL4.csv',

        # 'AlienShip\\UA_SGUN1.csv',
        # 'AlienShip\\UA_SGUN2.csv',
        # 'AlienShip\\UA_SGUN3.csv',
        # 'AlienShip\\UA_SGUN4.csv',

        # 'AlienShip\\UA_SLASR1.csv',
        # 'AlienShip\\UA_SLASR2.csv',
        # 'AlienShip\\UA_SLASR3.csv',
        # 'AlienShip\\UA_SLASR4.csv',

        # endregion

        # region Freighter

        # 'Freighter\\UP_FRHYP1.csv',
        # 'Freighter\\UP_FRHYP2.csv',
        # 'Freighter\\UP_FRHYP3.csv',
        # 'Freighter\\UP_FRHYP4.csv',

        # 'Freighter\\UP_FRSPE1.csv',
        # 'Freighter\\UP_FRSPE2.csv',
        # 'Freighter\\UP_FRSPE3.csv',
        # 'Freighter\\UP_FRSPE4.csv',

        # 'Freighter\\UP_FRFUE1.csv',
        # 'Freighter\\UP_FRFUE2.csv',
        # 'Freighter\\UP_FRFUE3.csv',
        # 'Freighter\\UP_FRFUE4.csv',

        # 'Freighter\\UP_FRCOM1.csv',
        # 'Freighter\\UP_FRCOM2.csv',
        # 'Freighter\\UP_FRCOM3.csv',
        # 'Freighter\\UP_FRCOM4.csv',

        # 'Freighter\\UP_FRTRA1.csv',
        # 'Freighter\\UP_FRTRA2.csv',
        # 'Freighter\\UP_FRTRA3.csv',
        # 'Freighter\\UP_FRTRA4.csv',

        # 'Freighter\\UP_FREXP1.csv',
        # 'Freighter\\UP_FREXP2.csv',
        # 'Freighter\\UP_FREXP3.csv',
        # 'Freighter\\UP_FREXP4.csv',

        # 'Freighter\\UP_FRMIN1.csv',
        # 'Freighter\\UP_FRMIN2.csv',
        # 'Freighter\\UP_FRMIN3.csv',
        # 'Freighter\\UP_FRMIN4.csv',

        # endregion

        # region Product

        # 'Product\\PROC_LOOT.csv',
        # 'Product\\PROC_HIST.csv',
        # 'Product\\PROC_BIO.csv',
        # 'Product\\PROC_FOSS.csv',
        # 'Product\\PROC_PLNT.csv',
        # 'Product\\PROC_TOOL.csv',
        # 'Product\\PROC_FARM.csv',
        # 'Product\\PROC_SEA.csv',
        # 'Product\\PROC_FEAR.csv',
        # 'Product\\PROC_SALV.csv',
        # 'Product\\PROC_BONE.csv',
        # 'Product\\PROC_DARK.csv',
        # 'Product\\PROC_STAR.csv',

        # endregion
    ]

    # region algorithm

    for f_original in f_list:
        start = datetime.now()

        f_original = f'Pi\\{f_original}'
        f_backup = f'{f_original[:-4]}.tmp.csv'

        shutil.copyfile(f_original, f_backup)

        module = f_original.split('\\')[-1][:-4]
        if module.startswith('PROC'):
            item_name, item_class = module.split('_')
            round_digits = 5
        else:
            has_class = get_has_class(module)

            item_name = module[:-1] if has_class else module  # 'UP_HAZ'
            item_class = module[-1] if has_class else ''  # 'X'
            round_digits = 3

        if get_is_configured(item_name, item_class):
            print(f'ERROR: Your procedural item ({item_name}{item_class}) is not configured')
            continue

        item_stats = get_item_stats(item_name, item_class)

        item_stats['meta'] = init_meta(item_stats['meta'])

        count = 0
        key_possibilities = get_key_possibilities(item_stats)

        high_number_perfection = get_high_number_perfection(get_high_number(item_stats), key_possibilities, item_stats)

        with open(f_backup, 'r', newline='') as backup:
            backup.readline()  # skip first line with delimiter indicator
            reader = csv.DictReader(backup, dialect='excel')
            with open(f_original, 'w', newline='') as original:
                original.write('sep=,\r\n')
                writer = csv.DictWriter(original, fieldnames=reader.fieldnames, dialect='excel')
                writer.writeheader()

                for row in reader:
                    count += 1
                    perfection = []
                    weighting_total = sum(item_stats['meta'][key][3] for key in key_possibilities if row[key])

                    # Get actual values of the current item.
                    for key in key_possibilities:
                        meta = item_stats['meta'][key]

                        extract_method = meta[4]
                        value = row[key]
                        weighting = meta[3]

                        if len(meta) >= 7 and meta[6]:
                            continue

                        if value:
                            value = extract_method(value)

                            p = 1.0
                            if meta[2] - meta[1] > 0:
                                p -= (meta[2] - value) / (meta[2] - meta[1])
                            p *= weighting
                            perfection.append(p)

                    row.update({
                        'Perfection': get_perfection(perfection, weighting_total, high_number_perfection, round_digits),
                    })

                    writer.writerow(row)

        os.remove(f_backup)

        end = datetime.now()

        print(f'{count:>6} module(s) perfection for {module} recomputed in {end - start}')

    # endregion
