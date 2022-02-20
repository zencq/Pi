# This script iterates over all loaded items and reads the values.
# Usage: python read_data.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]

import csv
import pymem
import re
import sys
from datetime import datetime

pattern_product_age = re.compile("^([0-9]+)")
pattern_product_value = re.compile(".*(?<=<STAT>)([0-9,]+) Units(?=<>)")


# region preamble

# region const

STEPS = 10000
TOTAL_SEEDS = 100000

# In the mapping below, the values are composed as follows:
# * meta: type used by the game, min value, max value
# * number: max possible stats
DATA = {
    # region Weapon (10x2)

    'UP_LASER': {
        '1': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 6, 10),
                ('Weapon_Laser_HeatTime', 5, 15),
                ('Weapon_Laser_Drain', 0, 10),
                ('Weapon_Laser_ReloadTime', 6, 10),
            ],
            'number': 2,  # 0 (Weapon_Laser_Drain with 0)
        },
        '2': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 6, 15),
                ('Weapon_Laser_HeatTime', 15, 20),
                ('Weapon_Laser_Drain', 11, 15),
                ('Weapon_Laser_ReloadTime', 11, 15),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 11, 20),
                ('Weapon_Laser_HeatTime', 21, 40),
                ('Weapon_Laser_Drain', 15, 20),
                ('Weapon_Laser_ReloadTime', 11, 15),
            ],
            'number': 4,  # 3
        },
        '4': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 15, 20),
                ('Weapon_Laser_HeatTime', 40, 50),
                ('Weapon_Laser_Drain', 21, 21),
                ('Weapon_Laser_ReloadTime', 15, 20),
            ],
            'number': 4,  # 4
        },
        'X': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 6, 20),
                ('Weapon_Laser_HeatTime', 5, 55),
                ('Weapon_Laser_Drain', 0, 25),
                ('Weapon_Laser_ReloadTime', 6, 25),
            ],
            'number': 3,  # 0 (Weapon_Laser_Drain with 0)
        },
    },

    'UP_SCAN': {
        '1': {
            'meta': [
                ('Weapon_Scan_Radius', 5, 10),
                ('Weapon_Scan_Discovery_Creature', 1000, 1999),
                ('Weapon_Scan_Discovery_Flora', 1000, 1999),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Scan_Radius', 11, 20),
                ('Weapon_Scan_Discovery_Creature', 2500, 4999),
                ('Weapon_Scan_Discovery_Flora', 2500, 4999),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Weapon_Scan_Radius', 21, 30),
                ('Weapon_Scan_Discovery_Creature', 5004, 9999),
                ('Weapon_Scan_Discovery_Flora', 5004, 9999),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Weapon_Scan_Radius', 30, 40),
                ('Weapon_Scan_Discovery_Creature', 6500, 9999),
                ('Weapon_Scan_Discovery_Flora', 6500, 9999),
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Weapon_Scan_Radius', 5, 50),
                ('Weapon_Scan_Discovery_Creature', 1000, 10999),
                ('Weapon_Scan_Discovery_Flora', 1000, 10999),
            ],
            'number': 3,  # 1
        },
    },

    'UP_BOLT': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 6, 10),
                ('Weapon_Projectile_ClipSize', 2, 2),
                ('Weapon_Projectile_Rate', 0, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 0, 5),
            ],
            'number': 3,  # 1 (AlwaysChoose x1 but Weapon_Projectile_Rate and Weapon_Projectile_BurstCooldown with 0)
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 11, 15),
                ('Weapon_Projectile_ClipSize', 4, 4),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 6, 10),
            ],
            'number': 4,  # 3 (AlwaysChoose x1)
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 11, 20),
                ('Weapon_Projectile_ClipSize', 6, 6),
                ('Weapon_Projectile_Rate', 11, 15),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 11, 15),
            ],
            'number': 4,  # 4 (AlwaysChoose x1)
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 11, 20),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 11, 15),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 15, 15),
            ],
            'number': 4,  # 4 (AlwaysChoose x1)
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 6, 25),
                ('Weapon_Projectile_ClipSize', 2, 10),
                ('Weapon_Projectile_Rate', 0, 20),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 0, 20),
            ],
            'number': 4,  # 1 (AlwaysChoose x1 but Weapon_Projectile_Rate and Weapon_Projectile_BurstCooldown with 0)
        },
    },

    'UP_GREN': {
        '1': {
            'meta': [
                ('Weapon_Grenade_Damage', 10, 19),
                ('Weapon_Grenade_Bounce', 33, 33),
                ('Weapon_Grenade_Radius', 1, 5),
                ('Weapon_Grenade_Speed', 100, 199),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Grenade_Damage', 20, 29),
                ('Weapon_Grenade_Bounce', 33, 66),
                ('Weapon_Grenade_Radius', 6, 10),
                ('Weapon_Grenade_Speed', 100, 299),
            ],
            'number': 3,  # 1
        },
        '3': {
            'meta': [
                ('Weapon_Grenade_Damage', 30, 39),
                ('Weapon_Grenade_Bounce', 66, 99),
                ('Weapon_Grenade_Radius', 5, 10),
                ('Weapon_Grenade_Speed', 100, 299),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Weapon_Grenade_Damage', 35, 39),
                ('Weapon_Grenade_Bounce', 100, 100),
                ('Weapon_Grenade_Radius', 11, 15),
                ('Weapon_Grenade_Speed', 200, 299),
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Weapon_Grenade_Damage', 10, 44),
                ('Weapon_Grenade_Bounce', 33, 133),
                ('Weapon_Grenade_Radius', 1, 20),
                ('Weapon_Grenade_Speed', 100, 399),
            ],
            'number': 3,  # 1
        },
    },

    'UP_TGREN': {
        '1': {
            'meta': [
                ('Weapon_Grenade_Damage', 10, 19),
                ('Weapon_Grenade_Radius', 11, 20),
                ('Weapon_Grenade_Speed', 100, 199),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Grenade_Damage', 20, 39),
                ('Weapon_Grenade_Radius', 32, 30),
                ('Weapon_Grenade_Speed', 100, 299),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Weapon_Grenade_Damage', 30, 39),
                ('Weapon_Grenade_Radius', 30, 50),
                ('Weapon_Grenade_Speed', 100, 299),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Weapon_Grenade_Damage', 35, 39),
                ('Weapon_Grenade_Radius', 40, 50),
                ('Weapon_Grenade_Speed', 200, 299),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Weapon_Grenade_Damage', 10, 44),
                ('Weapon_Grenade_Radius', 11, 60),
                ('Weapon_Grenade_Speed', 100, 399),
            ],
            'number': 2,  # 1
        },
    },

    'UP_RAIL': {
        '1': {
            'meta': [
                ('Weapon_Laser_Damage', 2, 2),
                ('Weapon_Laser_ChargeTime', 6, 10),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Laser_Damage', 2, 3),
                ('Weapon_Laser_ChargeTime', 11, 15),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Weapon_Laser_Damage', 3, 3),
                ('Weapon_Laser_ChargeTime', 11, 20),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Weapon_Laser_Damage', 4, 4),
                ('Weapon_Laser_ChargeTime', 11, 20),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Weapon_Laser_Damage', 2, 5),
                ('Weapon_Laser_ChargeTime', 6, 25),
            ],
            'number': 2,  # 1
        },
    },

    'UP_SHOT': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 6, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
            ],
            'number': 3,  # 2 (AlwaysChoose x1)
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 11, 15),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 1, 5),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 6, 10),
            ],
            'number': 4,  # 3 (AlwaysChoose x1)
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 15, 20),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 11, 15),
            ],
            'number': 4,  # 4 (AlwaysChoose x1)
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 3),
                ('Weapon_Projectile_ReloadTime', 20, 25),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 11, 15),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 16, 20),
            ],
            'number': 4,  # 4 (AlwaysChoose x1)
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 3),
                ('Weapon_Projectile_ReloadTime', 6, 30),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 1, 20),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 6, 25),
            ],
            'number': 4,  # 2 (AlwaysChoose x1)
        },
    },

    'UP_SMG': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 3),
                ('Weapon_Projectile_Rate', 1, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 6),
                ('Weapon_Projectile_Rate', 1, 10),
                ('Weapon_Projectile_ReloadTime', 1, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 3,  # 1
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 9),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_ReloadTime', 1, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,  # 3
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 6, 9),
                ('Weapon_Projectile_Rate', 11, 15),
                ('Weapon_Projectile_ReloadTime', 6, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,  # 4
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 13),
                ('Weapon_Projectile_Rate', 1, 20),
                ('Weapon_Projectile_ReloadTime', 1, 15),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,  # 1
        },
    },

    'UP_CANN': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 5),
                ('Weapon_Projectile_MaximumCharge', 1, 1),
                ('Weapon_ChargedProjectile_Charge', 5, 10),
                ('Weapon_ChargedProjectile_Extras', 5, 10),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 5, 6),
                ('Weapon_Projectile_MaximumCharge', 1, 1),
                ('Weapon_ChargedProjectile_Charge', 11, 15),
                ('Weapon_ChargedProjectile_Extras', 5, 8),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 7, 9),
                ('Weapon_Projectile_MaximumCharge', 1, 1),
                ('Weapon_ChargedProjectile_Charge', 11, 20),
                ('Weapon_ChargedProjectile_Extras', 8, 11),
            ],
            'number': 4,  # 3
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 10, 10),
                ('Weapon_Projectile_MaximumCharge', 1, 1),
                ('Weapon_ChargedProjectile_Charge', 11, 20),
                ('Weapon_ChargedProjectile_Extras', 11, 13),
            ],
            'number': 4,  # 4
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 5, 14),
                ('Weapon_Projectile_MaximumCharge', 1, 1),
                ('Weapon_ChargedProjectile_Charge', 6, 25),
                ('Weapon_ChargedProjectile_Extras', 2, 13),
            ],
            'number': 4,  # 1
        },
    },

    'UP_SENGUN': {
        'meta': [
            ('Weapon_Projectile_Damage', 1, 2),
            ('Weapon_Projectile_ReloadTime', 1, 15),
            ('Weapon_Projectile_Rate', 1, 20),
        ],
        'number': 3,  # 1
    },

    # endregion

    # region Suit (10x1)

    'UP_ENGY': {
        '1': {
            'meta': [
                ('Suit_Energy', 5, 19),
                ('Suit_Energy_Regen', 0, 10),
            ],
            'number': 2,  # 0 (Suit_Energy_Regen with 0)
        },
        '2': {
            'meta': [
                ('Suit_Energy', 20, 49),
                ('Suit_Energy_Regen', 0, 25),
            ],
            'number': 2,  # 1 (Suit_Energy_Regen with 0)
        },
        '3': {
            'meta': [
                ('Suit_Energy', 50, 99),
                ('Suit_Energy_Regen', 25, 50),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Suit_Energy', 5, 109),
                ('Suit_Energy_Regen', 0, 75),
            ],
            'number': 2,  # 0 (Suit_Energy_Regen with 0)
        },
    },

    'UP_HAZ': {
        'X': {
            'meta': [
                 ('Suit_Protection_ColdDrain', 1, 10),
                 ('Suit_Protection_HeatDrain', 1, 10),
                 ('Suit_Protection_RadDrain', 1, 10),
                 ('Suit_Protection_ToxDrain', 1, 10),
            ],
            'number': 4,  # 4
        },
    },

    'UP_JET': {
        '1': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 149),
                ('Suit_Stamina_Strength', 10, 19),
                ('Suit_Stamina_Recovery', 0, 10),
                ('Suit_Jetpack_Drain', 6, 10),
                ('Suit_Jetpack_Refill', 0, 5),
            ],
            'number': 4,  # 1 (AlwaysChoose x1 but Suit_Stamina_Recovery and Suit_Jetpack_Refill with 0)
        },
        '2': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 149),
                ('Suit_Stamina_Strength', 10, 29),
                ('Suit_Stamina_Recovery', 11, 20),
                ('Suit_Jetpack_Drain', 11, 15),
                ('Suit_Jetpack_Ignition', 0, 5),
                ('Suit_Jetpack_Refill', 5, 10),
            ],
            'number': 4,  # 2 (AlwaysChoose x1 but Suit_Jetpack_Ignition with 0)
        },
        '3': {
            'meta': [
                ('Suit_Jetpack_Tank', 150, 199),
                ('Suit_Stamina_Strength', 20, 49),
                ('Suit_Stamina_Recovery', 21, 30),
                ('Suit_Jetpack_Drain', 11, 20),
                ('Suit_Jetpack_Ignition', 0, 5),
                ('Suit_Jetpack_Refill', 11, 15),
            ],
            'number': 4,  # 3 (AlwaysChoose x1 but Suit_Jetpack_Ignition with 0)
        },
        '4': {
            'meta': [
                ('Suit_Jetpack_Tank', 200, 224),
                ('Suit_Stamina_Strength', 40, 49),
                ('Suit_Stamina_Recovery', 30, 50),
                ('Suit_Jetpack_Drain', 11, 20),
                ('Suit_Jetpack_Ignition', 5, 10),
                ('Suit_Jetpack_Refill', 15, 25),
            ],
            'number': 4,  # 4 (AlwaysChoose x2)
        },
        'X': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 229),
                ('Suit_Stamina_Strength', 10, 59),
                ('Suit_Stamina_Recovery', 1, 60),
                ('Suit_Jetpack_Drain', 6, 25),
                ('Suit_Jetpack_Ignition', 0, 15),
                ('Suit_Jetpack_Refill', 5, 30),
            ],
            'number': 4,  # 3 (AlwaysChoose x2 but Suit_Jetpack_Ignition with 0)
        },
    },

    'UP_SHLD': {
        '1': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 90, 95),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 85, 90),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 80, 89),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 80, 90),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 75, 95),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,  # 1
        },
    },

    # ! TODO values not displayed (as of 3.81)
    'UP_UNW': {
        '1': {
            'meta': [
                ('Suit_Underwater', 60, 85),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Suit_Underwater', 75, 105),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Suit_Underwater', 95, 105),
            ],
            'number': 1,  # 1
        },
    },

    # ! TODO values not displayed (as of 3.81)
    'UP_RAD': {
        '1': {
            'meta': [
                ('Suit_Protection_Radiation', 180, 265),
                ('Suit_DamageReduce_Radiation', 0, 5),
            ],
            'number': 2,  # 2
        },
        '2': {
            'meta': [
                ('Suit_Protection_Radiation', 200, 265),
                ('Suit_DamageReduce_Radiation', 5, 15),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Suit_Protection_Radiation', 220, 265),
                ('Suit_DamageReduce_Radiation', 10, 20),
            ],
            'number': 2,  # 2
        },
    },

    # ! TODO values not displayed (as of 3.81)
    'UP_TOX': {
        '1': {
            'meta': [
                ('Suit_Protection_Toxic', 180, 265),
                ('Suit_DamageReduce_Toxic', 0, 5),
            ],
            'number': 2,  # 2
        },
        '2': {
            'meta': [
                ('Suit_Protection_Toxic', 200, 265),
                ('Suit_DamageReduce_Toxic', 5, 15),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Suit_Protection_Toxic', 220, 265),
                ('Suit_DamageReduce_Toxic', 10, 20),
            ],
            'number': 2,  # 2
        }, },

    # ! TODO values not displayed (as of 3.81)
    'UP_COLD': {
        '1': {
            'meta': [
                ('Suit_Protection_Cold', 180, 265),
                ('Suit_DamageReduce_Cold', 0, 5),
            ],
            'number': 2,  # 2
        },
        '2': {
            'meta': [
                ('Suit_Protection_Cold', 200, 265),
                ('Suit_DamageReduce_Cold', 5, 15),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Suit_Protection_Cold', 220, 265),
                ('Suit_DamageReduce_Cold', 10, 20),
            ],
            'number': 2,  # 2
        },
    },

    # ! TODO values not displayed (as of 3.81)
    'UP_HOT': {
        '1': {
            'meta': [
                ('Suit_Protection_Heat', 180, 265),
                ('Suit_DamageReduce_Heat', 0, 5),
            ],
            'number': 2,  # 2
        },
        '2': {
            'meta': [
                ('Suit_Protection_Heat', 200, 265),
                ('Suit_DamageReduce_Heat', 5, 15),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Suit_Protection_Heat', 220, 265),
                ('Suit_DamageReduce_Heat', 10, 20),
            ],
            'number': 2,  # 2
        },
    },

    'UP_SNSUIT': {
        'meta': [
            ('Suit_Armour_Shield_Strength', 10, 35),
            ('Suit_Armour_Health', 33, 33),
            ('Suit_Energy', 5, 109),
            ('Suit_Energy_Regen', 1, 75),
            ('Suit_Jetpack_Drain', 6, 25),
            ('Suit_Stamina_Strength', 10, 59),
        ],
        'number': 4,  # 1
    },

    # endregion

    # region Ship (9x2)

    'UP_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 6, 10),
                ('Ship_Boost', 1, 5),
                ('Ship_BoostManeuverability', 1, 5),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 11, 15),
                ('Ship_Boost', 5, 10),
                ('Ship_BoostManeuverability', 1, 10),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20),
                ('Ship_Boost', 5, 15),
                ('Ship_BoostManeuverability', 5, 12),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20),
                ('Ship_Boost', 11, 15),
                ('Ship_BoostManeuverability', 5, 12),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 6, 25),
                ('Ship_Boost', 1, 20),
                ('Ship_BoostManeuverability', 1, 14),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 3,  # 1
        },
    },

    'UP_LAUN': {
        '1': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 6, 10),
                ('Ship_Boost', 0, 1),
            ],
            'number': 2,  # 1 (AlwaysChoose x1 but Ship_Boost with 0)
        },
        '2': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 11, 15),
                ('Ship_Boost', 2, 5),
            ],
            'number': 2,  # 2 (AlwaysChoose x1)
            'description': 'A substantial upgrade to the Launch Thruster, offering significant improvements to <STELLAR>Launch Cost<> and <STELLAR>Boost<>.',
        },
        '3': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 15, 20),
                ('Ship_Boost', 5, 8),
            ],
            'number': 2,  # 2 (AlwaysChoose x1)
            'description': 'A powerful upgrade module for the Launch Thruster, with the potential to drastically improve <STELLAR>Launch Cost<> and <STELLAR>Boost<>.',
        },
        '4': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 20, 20),
                ('Ship_Boost', 9, 10),
            ],
            'number': 2,  # 2 (AlwaysChoose x1)
            'description': 'An almost total rework of the Launch Thruster, this upgrade module brings unparalleled improvements to <STELLAR>Launch Cost<> and <STELLAR>Boost<>.',
        },
        'X': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 6, 25),
                ('Ship_Boost', 0, 10),
            ],
            'number': 2,  # 1 (AlwaysChoose x1 but Ship_Boost with 0)
        },
    },

    'UP_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,  # 1
            'description': 'Upgrades the Hyperdrive, improving <STELLAR>Hyperdrive Range<>.',
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,  # 1
            'description': 'A substantial upgrade to the Hyperdrive, offering significant improvements to <STELLAR>Hyperdrive Range<>.',
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200),
                ('Ship_Hyperdrive_JumpsPerCell', 100, 100),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250),
                ('Ship_Hyperdrive_JumpsPerCell', 100, 100),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 300),
                ('Ship_Hyperdrive_JumpsPerCell', 100, 100),
            ],
            'number': 2,  # 1
        },
    },

    'UP_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 7, 15),
            ],
            'number': 1,  # 1
            'description': 'Upgrades the Deflector Shield, improving <STELLAR>Shield Strength<>.',
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 7, 15),
            ],
            'number': 1,  # 1
            'description': 'A substantial upgrade to the Deflector Shield, offering significant improvements to <STELLAR>Shield Strength<>.',
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 15, 30),
            ],
            'number': 1,  # 1
            'description': 'A powerful upgrade module for the Deflector Shield, drastically improving <STELLAR>Shield Strength<>.',
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 30, 30),
            ],
            'number': 1,  # 1
            'description': 'An almost total rework of the Deflector Shield, this upgrade module brings unparalleled improvements to <STELLAR>Shield Strength<>.',
            'value': ['+30%'],
        },
        'X': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 7, 38),
            ],
            'number': 1,  # 1
            'description': 'Bypassing nearly every galactic standard for workmanship and safety, this upgrade module affects <STELLAR>Shield Strength<>.',
        },
    },

    'UP_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 4),
                ('Ship_Weapons_Guns_Rate', 1, 2),
                ('Ship_Weapons_Guns_HeatTime', 1, 1),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 3, 6),
                ('Ship_Weapons_Guns_Rate', 1, 2),
                ('Ship_Weapons_Guns_HeatTime', 1, 2),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 5, 7),
                ('Ship_Weapons_Guns_Rate', 2, 3),
                ('Ship_Weapons_Guns_HeatTime', 2, 3),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 6, 8),
                ('Ship_Weapons_Guns_Rate', 3, 3),
                ('Ship_Weapons_Guns_HeatTime', 3, 3),
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 9),
                ('Ship_Weapons_Guns_Rate', 1, 3),
                ('Ship_Weapons_Guns_HeatTime', 1, 4),
            ],
            'number': 3,  # 1
        },
    },

    'UP_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 11, 35),
                ('Ship_Weapons_Lasers_Damage', 12, 15),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 36, 55),
                ('Ship_Weapons_Lasers_Damage', 16, 19),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75),
                ('Ship_Weapons_Lasers_Damage', 20, 23),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95),
                ('Ship_Weapons_Lasers_Damage', 24, 27),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 11, 100),
                ('Ship_Weapons_Lasers_Damage', 12, 31),
            ],
            'number': 2,  # 1
        },
    },

    'UP_SSHOT': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 2),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 1, 5),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 3),
                ('Ship_Weapons_Guns_Rate', 11, 14),
                ('Ship_Weapons_Guns_HeatTime', 5, 10),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 3),
                ('Ship_Weapons_Guns_Rate', 14, 15),
                ('Ship_Weapons_Guns_HeatTime', 11, 15),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 3, 3),
                ('Ship_Weapons_Guns_Rate', 15, 15),
                ('Ship_Weapons_Guns_HeatTime', 15, 15),
            ],
            'number': 3,  # 3
            'description': 'An almost total rework of the Positron Ejector, this upgrade module brings unparalleled improvements to <STELLAR>Damage<>, <STELLAR>Fire Rate<> and <STELLAR>Heat Dispersion<>.',
            'value': ['+3%', '+15%', '+15%'],
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 4),
                ('Ship_Weapons_Guns_Rate', 5, 20),
                ('Ship_Weapons_Guns_HeatTime', 1, 20),
            ],
            'number': 3,  # 1
        },
    },

    'UP_SMINI': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 3),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 1, 3),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 3, 5),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 5, 7),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 5, 7),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 6, 7),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 8, 9),
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 8),
                ('Ship_Weapons_Guns_Rate', 1, 15),
                ('Ship_Weapons_Guns_HeatTime', 1, 13),
            ],
            'number': 3,  # 1
        },
    },

    'UP_SBLOB': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 1),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 11, 20),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 1),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 21, 25),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 1),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 25, 30),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 1),
                ('Ship_Weapons_Guns_Rate', 11, 15),
                ('Ship_Weapons_Guns_HeatTime', 30, 35),
            ],
            'number': 3,  # 3
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 1, 2),
                ('Ship_Weapons_Guns_Rate', 1, 20),
                ('Ship_Weapons_Guns_HeatTime', 11, 40),
            ],
            'number': 3,  # 1
        },
    },

    # endregion

    # region Exocraft (4x1)

    'UP_EXGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 1, 3),
                ('Vehicle_GunHeatTime', 1, 5),
                ('Vehicle_GunRate', 1, 5),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 3, 7),
                ('Vehicle_GunHeatTime', 6, 10),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 7, 10),
                ('Vehicle_GunHeatTime', 11, 15),
                ('Vehicle_GunRate', 11, 15),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 10, 14),
                ('Vehicle_GunHeatTime', 15, 20),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 3,  # 3
        },
    },

    'UP_EXLAS': {
        '1': {
            'meta': [
                ('Vehicle_LaserDamage', 6, 12),
                ('Vehicle_LaserHeatTime', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 12, 24),
                ('Vehicle_LaserHeatTime', 6, 10),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 25, 37),
                ('Vehicle_LaserHeatTime', 11, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 37, 49),
                ('Vehicle_LaserHeatTime', 15, 20),
            ],
            'number': 2,  # 2
        },
    },

    'UP_BOOST': {
        '1': {
            'meta': [
                ('Vehicle_BoostSpeed', 10, 19),
                ('Vehicle_BoostTanks', 10, 19),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_BoostSpeed', 20, 34),
                ('Vehicle_BoostTanks', 15, 29),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_BoostSpeed', 35, 54),
                ('Vehicle_BoostTanks', 30, 49),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_BoostSpeed', 55, 69),
                ('Vehicle_BoostTanks', 50, 59),
            ],
            'number': 2,  # 2
        },
    },

    'UP_EXENG': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5),
                ('Vehicle_EngineTopSpeed', 1, 3),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 6, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 11, 15),
                ('Vehicle_EngineTopSpeed', 9, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 11, 15),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # region Submarine (2x1)

    'UP_EXSUB': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5),
                ('Vehicle_EngineTopSpeed', 1, 3),
                ('Vehicle_SubBoostSpeed', 10, 19),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 6, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
                ('Vehicle_SubBoostSpeed', 20, 34),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 11, 15),
                ('Vehicle_EngineTopSpeed', 9, 15),
                ('Vehicle_SubBoostSpeed', 35, 54),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 11, 15),
                ('Vehicle_SubBoostSpeed', 55, 69),
            ],
            'number': 3,  # 3
        },
    },

    'UP_SUGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 1, 3),
                ('Vehicle_GunRate', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 3, 7),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 7, 10),
                ('Vehicle_GunRate', 11, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 10, 14),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # region Mech (3x1)

    'UP_MCLAS': {
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 12, 24),
                ('Vehicle_LaserHeatTime', 6, 10),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 25, 37),
                ('Vehicle_LaserHeatTime', 11, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 37, 49),
                ('Vehicle_LaserHeatTime', 15, 20),
            ],
            'number': 2,  # 2
        },
    },

    'UP_MCGUN': {
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 3, 7),
                ('Vehicle_GunHeatTime', 6, 10),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 7, 10),
                ('Vehicle_GunHeatTime', 11, 15),
                ('Vehicle_GunRate', 11, 15),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 10, 14),
                ('Vehicle_GunHeatTime', 15, 20),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 3,  # 3
        },
    },

    'UP_MCENG': {
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 6, 10),
                ('Vehicle_BoostTanks', 10, 14),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 11, 15),
                ('Vehicle_BoostTanks', 15, 24),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_BoostTanks', 25, 29),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # region AlienShip (6x2)

    'UA_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 6, 10),
                ('Ship_Boost', 0, 5),
                ('Ship_BoostManeuverability', 0, 5),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 2,  # 0 (Ship_Boost and Ship_BoostManeuverability with 0)
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 11, 15),
                ('Ship_Boost', 5, 10),
                ('Ship_BoostManeuverability', 0, 10),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 2,  # 1 (Ship_BoostManeuverability with 0)
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20),
                ('Ship_Boost', 5, 15),
                ('Ship_BoostManeuverability', 5, 12),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20),
                ('Ship_Boost', 11, 15),
                ('Ship_BoostManeuverability', 5, 12),
                # ('Ship_Maneuverability'),  # AlwaysChoose x1 but hidden and ALWAYS the same
            ],
            'number': 3,  # 3
        },
    },

    'UA_LAUN': {
        '1': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 6, 10),
            ],
            'number': 1,  # 1
            'description': 'This growth improves <STELLAR>Launch Cost<>.',
        },
        '2': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 11, 15),
            ],
            'number': 1,  # 1
            'description': 'A substantial ceullar expansion, improving <STELLAR>Launch Cost<>.',
        },
        '3': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 16, 20),
            ],
            'number': 1,  # 1
            'description': 'Emeshes itself with the Neural Assembly, drastically improving <STELLAR>Launch Cost<>.',
        },
        '4': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 20, 20),
                ('Ship_Launcher_AutoCharge', 1, 1),
            ],
            'number': 2,  # 2
            'description': 'A sprawling, pulsating extension of the Neural Assembly, this new growth brings unparalleled improvements to <STELLAR>Launch Cost<> and <STELLAR>Automatic Recharging<>.',
            'value': ['-20%', 'Enabled'],
        },
    },

    'UA_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,  # 1
            'description': 'This growth improves <STELLAR>Hyperdrive Range<>.',
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,  # 1
            'description': 'A substantial ceullar expansion, improving <STELLAR>Hyperdrive Range<>.',
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200),
                ('Ship_Hyperdrive_JumpsPerCell', 100, 100),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250),
                ('Ship_Hyperdrive_JumpsPerCell', 100, 100),
            ],
            'number': 2,  # 2
        },
    },

    'UA_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 7, 15),
            ],
            'number': 1,  # 1
            'description': 'This growth improves <STELLAR>Shield Strength<>.',
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 7, 15),
            ],
            'number': 1,  # 1
            'description': 'A substantial ceullar expansion, improving <STELLAR>Shield Strength<>.',
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 15, 30),
            ],
            'number': 1,  # 1
            'description': 'Emeshes itself with the Neural Assembly, drastically improving <STELLAR>Shield Strength<>.',
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 30, 30),
            ],
            'number': 1,  # 1
            'description': 'A sprawling, pulsating extension of the Scream Suppressor, this new growth brings unparalleled improvements to <STELLAR>Shield Strength<>.',
            'value': ['+30%'],
        },
    },

    'UA_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 4),
                ('Ship_Weapons_Guns_Rate', 1, 2),
                ('Ship_Weapons_Guns_HeatTime', 1, 1),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 3, 6),
                ('Ship_Weapons_Guns_Rate', 1, 2),
                ('Ship_Weapons_Guns_HeatTime', 1, 2),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 5, 7),
                ('Ship_Weapons_Guns_Rate', 2, 3),
                ('Ship_Weapons_Guns_HeatTime', 2, 3),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 6, 8),
                ('Ship_Weapons_Guns_Rate', 3, 3),
                ('Ship_Weapons_Guns_HeatTime', 3, 3),
            ],
            'number': 3,  # 3
        },
    },

    'UA_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 11, 35),
                ('Ship_Weapons_Lasers_Damage', 12, 15),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 36, 55),
                ('Ship_Weapons_Lasers_Damage', 16, 19),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75),
                ('Ship_Weapons_Lasers_Damage', 20, 23),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95),
                ('Ship_Weapons_Lasers_Damage', 24, 27),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # region Freighter (7x2)

    'UP_FRHYP': {
        '1': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>hyperdrive range<> and efficiency.',
        },
        '2': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>hyperdrive range<> and efficiency.',
        },
        '3': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 150, 200),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,  # 2
            'description': 'The unit offers improvements to <STELLAR>hyperdrive range<> and <STELLAR>efficiency<>.',
        },
        '4': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 200, 250),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,  # 2
            'description': 'The unit offers improvements to <STELLAR>hyperdrive range<> and <STELLAR>efficiency<>.',
        },
    },

    'UP_FRSPE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Speed', 1, 5),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition speed<>.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Speed', 5, 10),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition speed<>.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Speed', 11, 14),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition speed<>.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Speed', 15, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition speed<>.',
            'value': ['+15%'],
        },
    },

    'UP_FRFUE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Fuel', 2, 6),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition fuel efficiency<>.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Fuel', 6, 11),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition fuel efficiency<>.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Fuel', 11, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition fuel efficiency<>.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Fuel', 16, 20),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to <STELLAR>expedition fuel efficiency<>.',
        },
    },

    'UP_FRCOM': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Combat', 1, 5),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>combat and defense abilities<> of all expeditions.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Combat', 5, 10),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>combat and defense abilities<> of all expeditions.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Combat', 11, 14),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>combat and defense abilities<> of all expeditions.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Combat', 15, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>combat and defense abilities<> of all expeditions.',
            'value': ['+15%'],
        },
    },

    'UP_FRTRA': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Trade', 1, 5),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>trade abilities<> of all expeditions.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Trade', 5, 10),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>trade abilities<> of all expeditions.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Trade', 11, 14),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>trade abilities<> of all expeditions.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Trade', 15, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>trade abilities<> of all expeditions.',
            'value': ['+15%'],
        },
    },

    'UP_FREXP': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Explore', 1, 5),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>exploration and scientific abilities<> of all expeditions.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Explore', 5, 10),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>exploration and scientific abilities<> of all expeditions.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Explore', 11, 14),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>exploration and scientific abilities<> of all expeditions.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Explore', 15, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>exploration and scientific abilities<> of all expeditions.',
            'value': ['+15%'],
        },
    },

    'UP_FRMIN': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Mine', 1, 5),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>industrial abilities<> of all expeditions.',
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Mine', 5, 10),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>industrial abilities<> of all expeditions.',
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Mine', 11, 14),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>industrial abilities<> of all expeditions.',
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Mine', 15, 15),
            ],
            'number': 1,  # 1
            'description': 'The unit offers improvements to the <STELLAR>industrial abilities<> of all expeditions.',
            'value': ['+15%'],
        },
    },

    # endregion

    # region Product (13x1)

    'PROC': {
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'LOOT': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'HIST': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'BIO': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'FOSS': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'PLNT': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 4 - 2
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/2000000
        # 0442-A
        'TOOL': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2299932),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 10 - 6 - 1
        # 2  /5   100000/200000 - 6  /11   400000/700000 - 14  /30    800000/1200000
        # 1061-A
        'FARM': {
            'meta': [
                ('Product_Age', 2, 30),
                ('Product_Basevalue', 115000, 1379978),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 10 - 6 - 1
        # 200/500 100000/200000 - 600/1100 400000/700000 - 1400/3000  800000/1200000
        # 1061-A
        'SEA': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 1379978),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 10 - 6 - 1
        # 20 /50  100000/250000 - 60 /110  300000/600000 - 140 /300   900000/1200000
        # 1061-B
        'FEAR': {
            'meta': [
                ('Product_Age', 20, 300),
                ('Product_Basevalue', 115000, 1379983),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 4 - 2 - 1
        # 200/500 100000/300000 - 600/1100 400000/850000 - 1400/3000 1100000/2400000
        # 0421-A
        'SALV': {
            'meta': [
                ('Product_Age', 200, 3000),
                ('Product_Basevalue', 115000, 2759926),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 20 - 5 - 1
        # 250/500  50000/110000 - 600/1100 200000/600000 - 1400/3000  700000/1700000
        # 2051-A
        'BONE': {
            'meta': [
                ('Product_Age', 250, 3000),
                ('Product_Basevalue', 57500, 1954943),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 10 - 6 - 1
        # 20 /50  100000/250000 - 60 /110  300000/600000 - 140 /300   900000/1200000
        # 1061-B
        'DARK': {
            'meta': [
                ('Product_Age', 20, 300),
                ('Product_Basevalue', 115000, 1379983),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
        # 20 - 5 - 1
        # 250/500  50000/110000 - 600/1100 200000/600000 - 1400/3000  700000/1200000
        # 2051-B
        'STAR': {
            'meta': [
                ('Product_Age', 25000, 300000),
                ('Product_Basevalue', 57500, 1379972),
            ],
            'number': 2,
            'description': '<STELLAR>Age<> and <STELLAR>Value<>.',
        },
    },

    # endregion
}
# List of items without a subclass:
ITEMS_WITHOUT_CLASS = [
    'UP_SENGUN',
    'UP_SNSUIT',
]

# endregion

# region methods


def init_cheatengine_address(address):
    """
    Convert a single or list of address strings to integer.
    """
    if isinstance(address, list):
        return [init_cheatengine_address(addr) for addr in address]

    return int(f'0x{address}', 16)


def init_meta(data):
    """
    Convert and enrich list of stats to dictionary.
    """
    return {
        TRANSLATION[line[0]][0]: line + TRANSLATION[line[0]][1:]
        for line in data
    }


def extract_bool(data):
    """
    Convert string value to bool.
    """
    return data == 'Enabled'


def extract_float(data):
    """
    Convert string value to float.
    """
    return float(data[1:])


def extract_int_lightyear(data):
    """
    Convert string with lightyear (ly) to integer.
    """
    return int(data[:-3])


def extract_int_percent(data):
    """
    Convert string percent value to integer.
    """
    return int(data[1:-1])


def extract_int_percent_thousand(data):
    """
    Convert string percent value with thousand separator to integer.
    """
    return extract_int_percent(data.replace(',', ''))


def extract_int_product_age(data):
    """
    Convert string ... to integer.
    """
    result = pattern_product_age.findall(data)
    if result:
        result = result[0]
    else:
        result = data
    return int(result)


def extract_int_product_value(data):
    """
    Convert string ... to integer.
    """
    result = pattern_product_value.findall(data)
    if result:
        result = result[0].replace(',', '')
    else:
        result = data
    return int(result)


def get_has_class(module):
    return not any(module.startswith(item) for item in ITEMS_WITHOUT_CLASS)


def get_high_number(item_stats):
    return item_stats['number']


def get_high_number_perfection(high_number, key_possibilities, item_stats):
    return high_number - len([key for key in key_possibilities if len(item_stats['meta'][key]) >= 6 and item_stats['meta'][key][5]])


def get_key_possibilities(item_stats):
    return item_stats['meta'].keys()


def get_is_configured(item_name, item_class):
    return item_name not in DATA or (item_class and item_class not in DATA[item_name])


def get_item_stats(item_name, item_class):
    return DATA[item_name][item_class] if item_class else DATA[item_name]


def get_perfection(perfection, high_number_perfection, round_digits):
    return round(sum(perfection) / high_number_perfection, round_digits) if perfection else 0

# endregion

# region translation composition

pattern_bool = re.compile("^Enabled$")
pattern_float = re.compile("^\+[0-9]{1,2}\.[0-9]$")
pattern_int_lightyear = re.compile("^[0-9]{2,3} ly$")
pattern_int_percent = re.compile("^[-+][0-9]{1,3}%$")
pattern_int_percent_thousand = re.compile("^\+[0-9]{1,2},[0-9]{3}%$")

# C1 improving <STELLAR><>.
# C2 improving <STELLAR><> and <STELLAR><>.
# C3 improving <STELLAR><>, <STELLAR><> and
# C4 improving <STELLAR><>, <STELLAR><>,

# B1 to <STELLAR><>.
# B2 to <STELLAR><> and <STELLAR><>.
# B3 to <STELLAR><>, <STELLAR><> and
# B4 to <STELLAR><>, <STELLAR><>,

# A1 improving <STELLAR><>.
# A2 improve <STELLAR><> and <STELLAR><>.
# A3 improve <STELLAR><>, <STELLAR><> and
# A4 improve <STELLAR><>, <STELLAR><>,

# S1 to <STELLAR><>.
# S2 to <STELLAR><> and <STELLAR><>.
# S3 to <STELLAR><>, <STELLAR><> and
# S4 to <STELLAR><>, <STELLAR><>,

# X1 affects <STELLAR><>.
# X2 targets <STELLAR><> and <STELLAR><>.
# X3 targets <STELLAR><>, <STELLAR><> and
# X4 affects <STELLAR><>, <STELLAR><>,

# Q1 targeting <STELLAR><>.
# Q2 targeting <STELLAR><> and <STELLAR><>.
# Q3 targeting <STELLAR><>, <STELLAR><> and
# Q4 targeting <STELLAR><>, <STELLAR><>,

TRANSLATION = {
    # region Freighter

    'Freighter_Hyperdrive_JumpDistance': ('hyperdrive range', extract_int_lightyear, pattern_int_lightyear),  # Hyperdrive Range
    'Freighter_Hyperdrive_JumpsPerCell': ('efficiency', extract_int_percent, pattern_int_percent),  # Warp Cell Efficiency

    'Freighter_Fleet_Speed': ('expedition speed', extract_int_percent, pattern_int_percent),  # Expedition Speed

    'Freighter_Fleet_Fuel': ('expedition fuel efficiency', extract_int_percent, pattern_int_percent),  # Expedition Efficiency

    'Freighter_Fleet_Combat': ('combat and defense abilities', extract_int_percent, pattern_int_percent),  # Expedition Defenses

    'Freighter_Fleet_Trade': ('trade abilities', extract_int_percent, pattern_int_percent),  # Expedition Trade Ability

    'Freighter_Fleet_Explore': ('exploration and scientific abilities', extract_int_percent, pattern_int_percent),  # Expedition Scientific Ability

    'Freighter_Fleet_Mine': ('industrial abilities', extract_int_percent, pattern_int_percent),  # Expedition Mining Ability

    # endregion

    # region Product

    'Product_Age': ('Age', extract_int_product_age, pattern_product_age, True),
    'Product_Basevalue': ('Value', extract_int_product_value, pattern_product_value),

    # endregion

    # region Ship

    'Ship_Launcher_AutoCharge': ('Automatic Recharging', extract_bool, pattern_bool),
    'Ship_Boost': ('Boost', extract_int_percent, pattern_int_percent),
    'Ship_Launcher_TakeOffCost': ('Launch Cost', extract_int_percent, pattern_int_percent),
    'Ship_BoostManeuverability': ('Maneuverability', extract_int_percent, pattern_int_percent),
    'Ship_Maneuverability': ('Maneuverability', extract_int_percent, pattern_int_percent),  # hidden but ALWAYS the same
    'Ship_PulseDrive_MiniJumpFuelSpending': ('Pulse Drive Fuel Efficiency', extract_int_percent, pattern_int_percent),

    'Ship_Hyperdrive_JumpDistance': ('Hyperdrive Range', extract_int_lightyear, pattern_int_lightyear),
    'Ship_Hyperdrive_JumpsPerCell': ('Warp Cell Efficiency', extract_int_percent, pattern_int_percent),

    'Ship_Armour_Shield_Strength': ('Shield Strength', extract_int_percent, pattern_int_percent),

    'Ship_Weapons_Guns_Damage': ('Damage', extract_int_percent, pattern_int_percent),
    'Ship_Weapons_Guns_Rate': ('Fire Rate', extract_int_percent, pattern_int_percent),
    'Ship_Weapons_Guns_HeatTime': ('Heat Dispersion', extract_int_percent, pattern_int_percent),

    'Ship_Weapons_Lasers_Damage': ('Damage', extract_int_percent, pattern_int_percent),
    'Ship_Weapons_Lasers_HeatTime': ('Heat Dispersion', extract_int_percent, pattern_int_percent),

    # endregion

    # region Suit

    'Suit_Armour_Shield_Strength': ('Shield Strength', extract_int_percent, pattern_int_percent),
    'Suit_Armour_Health': ('Core Health', extract_int_percent, pattern_int_percent),

    'Suit_Energy': ('Life Support Tanks', extract_int_percent, pattern_int_percent),
    'Suit_Energy_Regen': ('Solar Panel Power', extract_int_percent, pattern_int_percent),

    'Suit_Jetpack_Drain': ('Fuel Efficiency', extract_int_percent, pattern_int_percent),
    'Suit_Jetpack_Ignition': ('Initial Boost Power', extract_int_percent, pattern_int_percent),
    'Suit_Jetpack_Tank': ('Jetpack Tanks', extract_int_percent, pattern_int_percent),
    'Suit_Jetpack_Refill': ('Recharge Rate', extract_int_percent, pattern_int_percent),
    'Suit_Stamina_Strength': ('Sprint Distance', extract_int_percent, pattern_int_percent),
    'Suit_Stamina_Recovery': ('Sprint Recovery Time', extract_int_percent, pattern_int_percent),

    'Suit_Protection_ColdDrain': ('Cold Resistance', extract_int_percent, pattern_int_percent),
    'Suit_Protection_HeatDrain': ('Heat Resistance', extract_int_percent, pattern_int_percent),
    'Suit_Protection_RadDrain': ('Radiation Resistance', extract_int_percent, pattern_int_percent),
    'Suit_Protection_ToxDrain': ('Toxic Resistance', extract_int_percent, pattern_int_percent),

    # ! TODO: values below not displayed (as of 3.81)

    'Suit_DamageReduce_Cold': ('Cold Damage Shielding', extract_int_percent, pattern_int_percent),
    'Suit_Protection_Cold': ('Cold Protection', extract_int_percent, pattern_int_percent),

    'Suit_DamageReduce_Heat': ('Heat Damage Shielding', extract_int_percent, pattern_int_percent),
    'Suit_Protection_Heat': ('Heat Protection', extract_int_percent, pattern_int_percent),

    'Suit_DamageReduce_Radiation': ('Radiation Damage Shielding', extract_int_percent, pattern_int_percent),
    'Suit_Protection_Radiation': ('Radiation Protection', extract_int_percent, pattern_int_percent),

    'Suit_DamageReduce_Toxic': ('Toxic Damage Shielding', extract_int_percent, pattern_int_percent),
    'Suit_Protection_Toxic': ('Toxic Protection', extract_int_percent, pattern_int_percent),

    'Suit_Underwater': ('Oxygen Tank', extract_int_percent, pattern_int_percent),

    # endregion

    # region Vehicle

    'Vehicle_GunDamage': ('Damage', extract_int_percent, pattern_int_percent),
    'Vehicle_GunRate': ('Rate of Fire', extract_int_percent, pattern_int_percent),
    'Vehicle_GunHeatTime': ('Weapon Power Efficiency', extract_int_percent, pattern_int_percent),

    'Vehicle_LaserDamage': ('Mining Laser Power', extract_int_percent, pattern_int_percent),
    'Vehicle_LaserHeatTime': ('Mining Laser Efficiency', extract_int_percent, pattern_int_percent),

    'Vehicle_SubBoostSpeed': ('Acceleration', extract_int_percent, pattern_int_percent),
    'Vehicle_BoostSpeed': ('Boost Power', extract_int_percent, pattern_int_percent),
    'Vehicle_BoostTanks': ('Boost Tank Size', extract_int_percent, pattern_int_percent),
    'Vehicle_EngineFuelUse': ('Fuel Usage', extract_int_percent, pattern_int_percent),
    'Vehicle_EngineTopSpeed': ('Top Speed', extract_int_percent, pattern_int_percent),

    # endregion

    # region Weapon

    'Weapon_ChargedProjectile_Charge': ('Charging Speed', extract_int_percent, pattern_int_percent),
    'Weapon_ChargedProjectile_Extras': ('Ion Sphere Speed', extract_int_percent, pattern_int_percent),

    'Weapon_Grenade_Bounce': ('Bounce Potential', extract_int_percent, pattern_int_percent),
    'Weapon_Grenade_Damage': ('Damage', extract_int_percent, pattern_int_percent),
    'Weapon_Grenade_Radius': ('Explosion Radius', extract_int_percent, pattern_int_percent),
    'Weapon_Grenade_Speed': ('Projectile Velocity', extract_int_percent, pattern_int_percent),

    'Weapon_Laser_Damage': ('Damage', extract_int_percent, pattern_int_percent),
    'Weapon_Laser_Drain': ('Fuel Efficiency', extract_int_percent, pattern_int_percent),
    'Weapon_Laser_HeatTime': ('Heat Dispersion', extract_int_percent, pattern_int_percent),
    'Weapon_Laser_Mining_Speed': ('Mining Speed', extract_int_percent, pattern_int_percent),
    'Weapon_Laser_ReloadTime': ('Overheat Downtime', extract_int_percent, pattern_int_percent),
    'Weapon_Laser_ChargeTime': ('Time to Full Power', extract_int_percent, pattern_int_percent),

    'Weapon_Projectile_BurstCooldown': ('Burst Cooldown', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_ClipSize': ('Clip Size', extract_float, pattern_float),
    'Weapon_Projectile_Damage': ('Damage', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_MaximumCharge': ('Ion Spheres Created', extract_float, pattern_float),
    'Weapon_Projectile_Rate': ('Fire Rate', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_ReloadTime': ('Reload Time', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_BurstCap': ('Shots Per Burst', extract_float, pattern_float),

    'Weapon_Scan_Discovery_Creature': ('Fauna Analysis Rewards', extract_int_percent_thousand, pattern_int_percent_thousand),
    'Weapon_Scan_Discovery_Flora': ('Flora Analysis Rewards', extract_int_percent_thousand, pattern_int_percent_thousand),
    'Weapon_Scan_Radius': ('Scan Radius', extract_int_percent, pattern_int_percent),

    # endregion
}

# endregion

# endregion

if __name__ == '__main__':
    # region input

    if len(sys.argv) < 5:
        print('ERROR: Not enough arguments! Usage: python read_data.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]')
        exit()

    addr_id_seed = init_cheatengine_address(sys.argv[2])
    addr_description = init_cheatengine_address(sys.argv[3])
    addr_stats = init_cheatengine_address(sys.argv[5:])
    addr_title = init_cheatengine_address(sys.argv[4])
    iteration_necessary = int(sys.argv[1])

    # endregion

    # region algorithm

    start = datetime.now()

    exe = 'NMS.exe'

    pm = pymem.Pymem(exe)

    module_game = pymem.process.module_from_name(pm.process_handle, exe).lpBaseOfDll
    module = pm.read_string(addr_id_seed, byte=16)

    hashtag_index = module.index('#')

    if module.startswith('PROC'):
        item_name, item_class = module[:hashtag_index].split('_')
        round_digits = 5
    else:
        has_class = get_has_class(module)

        item_name = module[:hashtag_index - 1] if has_class else module[:hashtag_index]  # 'UP_HAZ'
        item_class = module[hashtag_index - 1:hashtag_index] if has_class else ''  # 'X'
        round_digits = 3

    if get_is_configured(item_name, item_class):
        print(f'ERROR: Your procedural item ({item_name}{item_class}) is not configured')
        exit()

    item_stats = get_item_stats(item_name, item_class)

    high_number = get_high_number(item_stats)

    addr_stats = addr_stats[:high_number]

    if len(addr_stats) != high_number:
        print(f'ERROR: Your number of memory addresses ({len(addr_stats)}) does not match the max number of stats ({len(item_stats)})')
        exit()

    item_stats['meta'] = init_meta(item_stats['meta'])

    addr_off = addr_id_seed + hashtag_index + 1
    fieldnames = ['Seed', 'Name', 'Perfection'] + [value[0] for value in item_stats['meta'].values()]
    key_possibilities = get_key_possibilities(item_stats)
    middle = start
    pattern = re.compile('(?<=<STELLAR>)[A-Z a-z]+(?=<>)')
    static_description = item_stats['description'] if 'description' in item_stats else ''
    static_value = item_stats['value'] if 'value' in item_stats else []

    begin = int(pm.read_string(addr_off, byte=16))
    count = int(TOTAL_SEEDS / iteration_necessary)
    high_number_perfection = get_high_number_perfection(high_number, key_possibilities, item_stats)

    iteration_stop = TOTAL_SEEDS
    for i in range(1, iteration_necessary + 1):
        iteration_stop = i * count
        if begin < iteration_stop:
            break

    stop = max(0, min(begin + count, iteration_stop))

    f_name = fr'{module[:hashtag_index]}_{begin}_{stop - 1}.csv'
    with open(f_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        print('Item  ', item_name, item_class)
        print('Range ', begin, '-', stop - 1)
        for i in range(begin, stop):
            i_next = i + 1

            # Loops until all data is fully loaded.
            while True:
                description = static_description or pm.read_string(addr_description, byte=512)
                title = pm.read_string(addr_title, byte=64)

                values = static_value or [pm.read_string(a) for a in addr_stats]

                # First check that description and title are loaded.
                if (
                    (description.startswith('UPGRADE_0') or description.startswith('BIO_UPGRADE_0') or '<STELLAR>' in description and description.endswith('.'))
                    and title != ''
                ):
                    # Then extract stat names from the description and make sure it's fully loaded
                    # with the complete name of a possible stat and its value.
                    # Some seeds produce an empty description starting with UPGRADE_0 and have no stats (displayed).
                    keys = pattern.findall(description)[:high_number]
                    # UP_FRHYP is a special snowflake with a not machting description.
                    if item_name == 'UP_FRHYP' and 'ly' not in values[0]:
                        values.reverse()
                    if (
                        all(key in key_possibilities and item_stats['meta'][key][4].match(values[index]) for index, key in enumerate(keys))
                        or description.startswith('UPGRADE_0')
                        or description.startswith('BIO_UPGRADE_0')
                    ):
                        break

            if i_next < stop:
                pm.write_string(addr_off, str(i_next))

            # Set to \0 to avoid duplicates in next iteration
            pm.write_uchar(addr_title, 0)
            if not static_description:
                pm.write_uchar(addr_description, 0)
            if not static_value:
                for a in addr_stats:
                    pm.write_uchar(a, 0)

            perfection = []
            row = {}

            # Get actual values of the current item.
            for index, key in enumerate(keys):
                meta = item_stats['meta'][key]

                row.update({meta[0]: values[index]})

                extract_method = meta[3]

                value = extract_method(values[index])
                if item_name == 'PROC':
                    row.update({meta[0]: value})

                if len(meta) >= 6 and meta[5]:
                    continue

                p = 1.0
                if meta[2] - meta[1] > 0:
                    p -= (meta[2] - value) / (meta[2] - meta[1])
                perfection.append(p)

            row.update({
                'Name': title,
                'Perfection': get_perfection(perfection, high_number_perfection, round_digits),
                'Seed': i,
            })

            writer.writerow(row)
            if (i - (STEPS - 1)) % STEPS == 0:
                middle_next = datetime.now()
                print(f'{i:>6} ({middle_next - middle}) ({middle_next})')
                middle = middle_next
                f.flush()
        else:
            # 6 = # (1) + 99999 (5)
            pm.write_string(addr_id_seed, f'{module[:hashtag_index]}#{begin}'.ljust(len(module[:hashtag_index]) + 6, '\0'))

    end = datetime.now()

    print(f'{stop - begin:>6} item(s) added to {f_name} in {end - start}')

    # endregion
