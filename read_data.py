# This script iterates over all loaded items and reads the values.
# Usage: python read_data.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]

import csv
import pymem
import re
import sys
from datetime import datetime

# region const

STEPS = 10000
TOTAL_SEEDS = 100000

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
        TRANSLATION[line[0]][0]: line + (TRANSLATION[line[0]][1], TRANSLATION[line[0]][2])
        for line in data
    }


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

# endregion

# region stats


pattern_int_lightyear = re.compile("^[0-9]{2,3} ly$")
pattern_int_percent = re.compile("^[-+][0-9]{1,3}%$")
pattern_int_percent_thousand = re.compile("^\+[0-9]{1,2},[0-9]{3}%$")
pattern_float = re.compile("^\+[0-9]{1,2}\.[0-9]$")

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

TRANSLATION = {
    # region Exocraft

    'Vehicle_GunDamage': ('Damage', extract_int_percent, pattern_int_percent),
    'Vehicle_GunRate': ('Rate of Fire', extract_int_percent, pattern_int_percent),
    'Vehicle_GunHeatTime': ('Weapon Power Efficiency', extract_int_percent, pattern_int_percent),

    'Vehicle_LaserDamage': ('Mining Laser Power', extract_int_percent, pattern_int_percent),
    'Vehicle_LaserHeatTime': ('Mining Laser Efficiency', extract_int_percent, pattern_int_percent),

    # endregion

    # region Ship

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

    # TODO: values of stats below not displayed

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

    # region Weapon

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
    'Weapon_Projectile_Rate': ('Fire Rate', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_ReloadTime': ('Reload Time', extract_int_percent, pattern_int_percent),
    'Weapon_Projectile_BurstCap': ('Shots Per Burst', extract_float, pattern_float),

    'Weapon_Scan_Discovery_Creature': ('Fauna Analysis Rewards', extract_int_percent_thousand, pattern_int_percent_thousand),
    'Weapon_Scan_Discovery_Flora': ('Flora Analysis Rewards', extract_int_percent_thousand, pattern_int_percent_thousand),
    'Weapon_Scan_Radius': ('Scan Radius', extract_int_percent, pattern_int_percent),

    # endregion

    # region TODO
    # 'Vehicle_BoostSpeed': ('Boost Power', extract_int_percent, pattern_int_percent),
    # 'Vehicle_BoostTanks': ('Boost Tank Size', extract_int_percent, pattern_int_percent),
    # 'Vehicle_EngineFuelUse': ('Fuel Usage', extract_int_percent, pattern_int_percent),
    # 'Vehicle_EngineTopSpeed': ('Top Speed', extract_int_percent, pattern_int_percent),
    # 'Vehicle_SubBoostSpeed': ('Acceleration', extract_int_percent, pattern_int_percent),
    # 'Ship_Launcher_AutoCharge': ('Automatic Recharging', extract_int_percent, pattern_int_percent),
    # 'Freighter_Hyperdrive_JumpDistance': ('Hyperdrive Range', extract_int_percent, pattern_int_percent),
    # 'Freighter_Hyperdrive_JumpsPerCell': ('Warp Cell Efficiency', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Speed': ('Expedition Speed', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Fuel': ('Expedition Efficiency', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Combat': ('Expedition Defenses', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Trade': ('Expedition Trade Ability', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Explore': ('Expedition Scientific Ability', extract_int_percent, pattern_int_percent),
    # 'Freighter_Fleet_Mine': ('Expedition Mining Ability', extract_int_percent, pattern_int_percent),
    # endregion
}

# In the mapping below, the values are composed as follows:
# * meta: type used by the game, min value, max value
# * number: max possible stats
DATA = {
    # region Weapon (8x2)

    'UP_LASER': {
        '1': {
            'meta': [
                ('Weapon_Laser_Mining_Speed', 6, 10),
                ('Weapon_Laser_HeatTime', 5, 15),
                ('Weapon_Laser_Drain', 1, 10),
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
                ('Weapon_Laser_Drain', 1, 25),
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
                ('Weapon_Projectile_Rate', 1, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 1, 5),
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
                ('Weapon_Projectile_Rate', 1, 20),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 1, 20),
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

    # endregion

    # ! TODO
    # region Suit (9x1)

    'UP_ENGY': {
        '1': {
            'meta': [
                ('Suit_Energy', 5, 19),
                ('Suit_Energy_Regen', 1, 10),
            ],
            'number': 2,  # 0 (Suit_Energy_Regen with 0)
        },
        '2': {
            'meta': [
                ('Suit_Energy', 20, 49),
                ('Suit_Energy_Regen', 1, 25),
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
                ('Suit_Energy_Regen', 1, 75),
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
                ('Suit_Stamina_Recovery', 1, 10),
                ('Suit_Jetpack_Drain', 6, 10),
                ('Suit_Jetpack_Refill', 1, 5),
            ],
            'number': 4,  # 1 (AlwaysChoose x1 but Suit_Stamina_Recovery and Suit_Jetpack_Refill with 0)
        },
        '2': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 149),
                ('Suit_Stamina_Strength', 10, 29),
                ('Suit_Stamina_Recovery', 11, 20),
                ('Suit_Jetpack_Drain', 11, 15),
                ('Suit_Jetpack_Ignition', 1, 5),
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
                ('Suit_Jetpack_Ignition', 1, 5),
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
                ('Suit_Jetpack_Ignition', 1, 15),
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

    # ! TODO values not displayed (as of 3.4)
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

    # ! TODO values not displayed (as of 3.4)
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

    # ! TODO values not displayed (as of 3.4)
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

    # ! TODO values not displayed (as of 3.4)
    'UP_COLD': {
        '1': {
            'meta': [
                ('Suit_Protection_Cold', (180, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (0, 5, extract_int_percent)),
            ],
            'number': 2,  # 2
        },
        '2': {
            'meta': [
                ('Suit_Protection_Cold', (200, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (5, 15, extract_int_percent)),
            ],
            'number': 2,  # 2
        },
        '3': {
            'meta': [
                ('Suit_Protection_Cold', (220, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (10, 20, extract_int_percent)),
            ],
            'number': 2,  # 2
        },
    },

    # ! TODO values not displayed (as of 3.4)
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
                ('Ship_Boost', 1, 1),
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
                ('Ship_Boost', 1, 10),
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

    # TODO
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

    # TODO verify values
    'UP_BOOST': {
        '1': {
            'meta': [
                ('Vehicle_BoostSpeed', 10, 20),
                ('Vehicle_BoostTanks', 10, 20),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_BoostSpeed', 20, 35),
                ('Vehicle_BoostTanks', 15, 30),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_BoostSpeed', 35, 55),
                ('Vehicle_BoostTanks', 30, 50),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_BoostSpeed', 55, 70),
                ('Vehicle_BoostTanks', 50, 60),
            ],
            'number': 2,  # 2
        },
    },

    # TODO verify values
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
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_EngineTopSpeed', 8, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 10, 15),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # TODO
    # region Submarine (2)

    # TODO verify values
    'UP_EXSUB': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5),
                ('Vehicle_EngineTopSpeed', 1, 3),
                ('Vehicle_SubBoostSpeed', 10, 20),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
                ('Vehicle_SubBoostSpeed', 20, 35),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_EngineTopSpeed', 8, 15),
                ('Vehicle_SubBoostSpeed', 35, 55),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 10, 15),
                ('Vehicle_SubBoostSpeed', 55, 70),
            ],
            'number': 3,  # 3
        },
    },

    # TODO verify values
    'UP_SUGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 5, 10),
                ('Vehicle_GunRate', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30),
                ('Vehicle_GunRate', 10, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # TODO
    # region Mech (3)

    # TODO verify values
    'UP_MCLAS': {
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 10, 20),
                ('Vehicle_LaserHeatTime', 5, 10),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 20, 30),
                ('Vehicle_LaserHeatTime', 10, 15),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 30, 40),
                ('Vehicle_LaserHeatTime', 15, 20),
            ],
            'number': 2,  # 2
        },
    },

    # TODO verify values
    'UP_MCGUN': {
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20),
                ('Vehicle_GunHeatTime', 5, 10),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 3,  # 2
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30),
                ('Vehicle_GunHeatTime', 10, 15),
                ('Vehicle_GunRate', 10, 15),
            ],
            'number': 3,  # 3
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40),
                ('Vehicle_GunHeatTime', 15, 20),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 3,  # 3
        },
    },

    # TODO verify values
    'UP_MCENG': {
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_BoostTanks', 10, 15),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_BoostTanks', 15, 25),
            ],
            'number': 2,  # 1
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_BoostTanks', 25, 30),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # TODO
    # region AlienShip (6)

    # TODO verify values
    'UA_PULSE': {
        '1': {
            # TODO verify values
            # UA_PULSE1#0 // # # // XXXX ABC, XXXX
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 10),
                ('Ship_Boost', 0, 5),
                ('Ship_BoostManeuverability', 0, 5),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,  # 2 (AlwaysChoose x1)
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 10, 15),
                ('Ship_Boost', 5, 10),
                ('Ship_BoostManeuverability', 0, 10),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,  # 3 (AlwaysChoose x1)
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20),
                ('Ship_Boost', 5, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 4,  # 3 (AlwaysChoose x1)
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20),
                ('Ship_Boost', 10, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 4,  # 4 (AlwaysChoose x1)
        },
    },

    # TODO verify values
    'UA_LAUN': {
        '1': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 5, 10),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 10, 15),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 15, 20),
            ],
            'number': 1,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 20, 20),
                ('Ship_Launcher_AutoCharge', 1, 1),
            ],
            'number': 2,  # 2
        },
    },

    # TODO verify values
    'UA_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,  # 2
        },
    },

    # TODO verify values
    'UA_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 10, 20),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 20, 20),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UA_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 16),
                ('Ship_Weapons_Guns_Rate', 0.1, 1.1),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 1.0),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 12, 20),
                ('Ship_Weapons_Guns_Rate', 0.6, 1.6),
                ('Ship_Weapons_Guns_HeatTime', 1.0, 2.0),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 16, 24),
                ('Ship_Weapons_Guns_Rate', 1.6, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 2.0, 3.0),
            ],
            'number': 3,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 20, 28),
                ('Ship_Weapons_Guns_Rate', 2.1, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 3.0, 3.0),
            ],
            'number': 3,  # 3
        },
    },

    # TODO verify values
    'UA_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 35),
                ('Ship_Weapons_Lasers_Damage', 30, 40),
            ],
            'number': 2,  # 1
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 35, 55),
                ('Ship_Weapons_Lasers_Damage', 40, 50),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75),
                ('Ship_Weapons_Lasers_Damage', 50, 60),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95),
                ('Ship_Weapons_Lasers_Damage', 60, 70),
            ],
            'number': 2,  # 2
        },
    },

    # endregion

    # TODO
    # region Freighter (7)

    # TODO verify values
    'UP_FRHYP': {
        '1': {
            # TODO verify values
            # UP_FRHYP1#0 // # # // XXXX ABC, XXXX
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 150, 200),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 200, 250),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,  # 2
        },
    },

    # TODO verify values
    'UP_FRSPE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Speed', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Speed', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Speed', 10, 14),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Speed', 15, 15),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UP_FRFUE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Fuel', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Fuel', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Fuel', 10, 15),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Fuel', 15, 20),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UP_FRCOM': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Combat', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Combat', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Combat', 10, 14),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Combat', 15, 15),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UP_FRTRA': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Trade', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Trade', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Trade', 10, 14),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Trade', 15, 15),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UP_FREXP': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Explore', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Explore', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Explore', 10, 14),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Explore', 15, 15),
            ],
            'number': 1,  # 1
        },
    },

    # TODO verify values
    'UP_FRMIN': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Mine', 1, 5),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Mine', 5, 10),
            ],
            'number': 1,  # 1
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Mine', 10, 14),
            ],
            'number': 1,  # 1
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Mine', 15, 15),
            ],
            'number': 1,  # 1
        },
    },

    # endregion
}

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

    tech_name = module[:hashtag_index - 1]  # 'UP_HAZ'
    tech_class = module[hashtag_index - 1:hashtag_index]  # 'X'

    if tech_name not in DATA or tech_class not in DATA[tech_name]:
        print(f'ERROR: Your procedural item ({tech_name}{tech_class}) is not configured')
        exit()

    tech_stats = DATA[tech_name][tech_class]

    high_number = tech_stats['number']

    addr_stats = addr_stats[:high_number]

    if len(addr_stats) != high_number:
        print(f'ERROR: Your number of memory addresses ({len(addr_stats)}) does not match the max number of stats ({len(tech_stats)})')
        exit()

    tech_stats['meta'] = init_meta(tech_stats['meta'])

    addr_off = addr_id_seed + hashtag_index + 1
    fieldnames = ['Seed', 'Name', 'Perfection'] + [value[0] for value in tech_stats['meta'].values()]
    key_possibilities = tech_stats['meta'].keys()
    middle = start
    pattern = re.compile('(?<=<STELLAR>)[A-Z a-z]+(?=<>)')
    round_digits = 3
    static_description = tech_stats['description'] if 'description' in tech_stats else ''
    static_value = tech_stats['value'] if 'value' in tech_stats else []

    begin = int(pm.read_string(addr_off, byte=16))
    count = int(TOTAL_SEEDS / iteration_necessary)

    iteration_stop = TOTAL_SEEDS
    for i in range(1, iteration_necessary + 1):
        iteration_stop = i * count
        if begin < iteration_stop:
            break

    stop = max(0, min(begin + count, iteration_stop))

    f_name = fr'{tech_name}{tech_class}_{begin}_{stop - 1}.csv'
    with open(f_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel-tab')
        writer.writeheader()
        print('Item  ', tech_name, tech_class)
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
                    (description.startswith('UPGRADE_0') or '<STELLAR>' in description and description.endswith('.'))
                    and title != ''
                ):
                    # Then extract stat names from the description and make sure it's fully loaded
                    # with the complete name of a possible stat and its value.
                    # Some seeds produce an empty description starting with UPGRADE_0 and have no stats (displayed).
                    keys = pattern.findall(description)[:high_number]
                    if (
                        all(key in key_possibilities and tech_stats['meta'][key][4].match(values[index]) for index, key in enumerate(keys))
                        or description.startswith('UPGRADE_0')
                    ):
                        break

            if i_next < stop:
                pm.write_string(addr_off, str(i_next))

            # Set to \0 to avoid duplicates in next while True
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
                meta = tech_stats['meta'][key]

                row.update({meta[0]: values[index]})

                extract_method = meta[3]

                value = extract_method(values[index])

                p = 1.0
                if meta[2] - meta[1] > 0:
                    p -= (meta[2] - value) / (meta[2] - meta[1])
                perfection.append(p)

            perfection = round(sum(perfection) / high_number, round_digits) if perfection else 0

            row.update({
                'Name': title,
                'Perfection': perfection,
                'Seed': i,
            })

            writer.writerow(row)
            if (i - (STEPS - 1)) % STEPS == 0:
                middle_next = datetime.now()
                print(f'{i:>6} ({middle_next - middle}) ({middle_next})')
                middle = middle_next
                f.flush()
        else:
            # 7 = tech_class (1) + # (1) + 99999 (5)
            pm.write_string(addr_id_seed, f'{tech_name}{tech_class}#{begin}'.ljust(len(tech_name) + 7, '\0'))

    end = datetime.now()

    print(f'{stop - begin:>6} module(s) added to {f_name} in {end - start}')

    # endregion
