# This script iterates over all loaded items and reads the values.
# Usage: python procedural.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]

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
        TRANSLATION[line[0]][0]: line + (TRANSLATION[line[0]][1],)
        for line in data
    }


def extract_float(data):
    """
    Convert string value to float.
    """
    return float(data[1:])


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

TRANSLATION = {
    'Suit_Energy': ('Life Support Tanks', extract_int_percent),
    'Suit_Energy_Regen': ('Solar Panel Power', extract_int_percent),

    'Suit_Protection_ColdDrain': ('Cold Resistance', extract_int_percent),
    'Suit_Protection_HeatDrain': ('Heat Resistance', extract_int_percent),
    'Suit_Protection_RadDrain': ('Radiation Resistance', extract_int_percent),
    'Suit_Protection_ToxDrain': ('Toxic Resistance', extract_int_percent),

    'Weapon_Grenade_Bounce': ('Bounce Potential', extract_int_percent),
    'Weapon_Grenade_Damage': ('Damage', extract_int_percent),
    'Weapon_Grenade_Radius': ('Explosion Radius', extract_int_percent),
    'Weapon_Grenade_Speed': ('Projectile Velocity', extract_int_percent),

    'Weapon_Laser_Drain': ('Fuel Efficiency', extract_int_percent),
    'Weapon_Laser_HeatTime': ('Heat Dispersion', extract_int_percent),
    'Weapon_Laser_Mining_Speed': ('Mining Speed', extract_int_percent),
    'Weapon_Laser_ReloadTime': ('Overheat Downtime', extract_int_percent),

    'Weapon_Projectile_BurstCap': ('Shots Per Burst', extract_float),
    'Weapon_Projectile_BurstCooldown': ('Burst Cooldown', extract_int_percent),
    'Weapon_Projectile_ClipSize': ('Clip Size', extract_float),
    'Weapon_Projectile_Damage': ('Damage', extract_int_percent),
    'Weapon_Projectile_Rate': ('Fire Rate', extract_int_percent),
    'Weapon_Projectile_ReloadTime': ('Reload Time', extract_int_percent),

    'Weapon_Scan_Discovery_Creature': ('Fauna Analysis Rewards', extract_int_percent_thousand),
    'Weapon_Scan_Discovery_Flora': ('Flora Analysis Rewards', extract_int_percent_thousand),
    'Weapon_Scan_Radius': ('Scan Radius', extract_int_percent),

    # 'Weapon_Laser_Damage': ('Damage', extract_int_percent),
    # 'Weapon_Laser_ChargeTime': ('Time to Full Power', extract_int_percent),
    # 'Suit_Jetpack_Tank': ('Jetpack Tanks', extract_int_percent),
    # 'Suit_Stamina_Strength': ('Sprint Distance', extract_int_percent),
    # 'Suit_Stamina_Recovery': ('Sprint Recovery Time', extract_int_percent),
    # 'Suit_Jetpack_Drain': ('Fuel Efficiency', extract_int_percent),
    # 'Suit_Jetpack_Ignition': ('Initial Boost Power', extract_int_percent),
    # 'Suit_Jetpack_Refill': ('Recharge Rate', extract_int_percent),
    # 'Suit_Armour_Shield_Strength': ('Shield Strength', extract_int_percent),
    # 'Suit_Armour_Health': ('Core Health', extract_int_percent),
    # 'Suit_Underwater': ('Oxygen Tank', extract_int_percent),
    # 'Suit_Protection_Radiation': ('Radiation Protection', extract_int_percent),
    # 'Suit_DamageReduce_Radiation': ('Radiation Damage Shielding', extract_int_percent),
    # 'Suit_Protection_Toxic': ('Toxic Protection', extract_int_percent),
    # 'Suit_DamageReduce_Toxic': ('Toxic Damage Shielding', extract_int_percent),
    # 'Suit_Protection_Cold': ('Cold Protection', extract_int_percent),
    # 'Suit_DamageReduce_Cold': ('Cold Damage Shielding', extract_int_percent),
    # 'Suit_Protection_Heat': ('Heat Protection', extract_int_percent),
    # 'Suit_DamageReduce_Heat': ('Heat Damage Shielding', extract_int_percent),
    # 'Ship_PulseDrive_MiniJumpFuelSpending': ('Pulse Drive Fuel Efficiency', extract_int_percent),
    # 'Ship_Boost': ('Boost', extract_int_percent),
    # 'Ship_BoostManeuverability': ('Maneuverability', extract_int_percent),  # TODO: rename with mod to "Boost-Maneuverability"?
    # 'Ship_Maneuverability': ('Maneuverability', extract_int_percent),
    # 'Ship_Hyperdrive_JumpDistance': ('Hyperdrive Range', extract_int_percent),
    # 'Ship_Hyperdrive_JumpsPerCell': ('Warp Cell Efficiency', extract_int_percent),
    # 'Ship_Armour_Shield_Strength': ('Shield Strength', extract_int_percent),
    # 'Ship_Weapons_Guns_Damage': ('Damage', extract_int_percent),
    # 'Ship_Weapons_Guns_Rate': ('Fire Rate', extract_int_percent),
    # 'Ship_Weapons_Guns_HeatTime': ('Heat Dispersion', extract_int_percent),
    # 'Ship_Weapons_Lasers_HeatTime': ('Heat Dispersion', extract_int_percent),
    # 'Ship_Weapons_Lasers_Damage': ('Damage', extract_int_percent),
    # 'Vehicle_GunDamage': ('Damage', extract_int_percent),
    # 'Vehicle_GunHeatTime': ('Weapon Power Efficiency', extract_int_percent),
    # 'Vehicle_GunRate': ('Rate of Fire', extract_int_percent),
    # 'Vehicle_LaserDamage': ('Mining Laser Power', extract_int_percent),
    # 'Vehicle_LaserHeatTime': ('Mining Laser Efficiency', extract_int_percent),
    # 'Vehicle_BoostSpeed': ('Boost Power', extract_int_percent),
    # 'Vehicle_BoostTanks': ('Boost Tank Size', extract_int_percent),
    # 'Vehicle_EngineFuelUse': ('Fuel Usage', extract_int_percent),
    # 'Vehicle_EngineTopSpeed': ('Top Speed', extract_int_percent),
    # 'Vehicle_SubBoostSpeed': ('Acceleration', extract_int_percent),
    # 'Ship_Launcher_TakeOffCost': ('Launch Cost', extract_int_percent),
    # 'Ship_Launcher_AutoCharge': ('Automatic Recharging', extract_int_percent),
    # 'Freighter_Hyperdrive_JumpDistance': ('Hyperdrive Range', extract_int_percent),
    # 'Freighter_Hyperdrive_JumpsPerCell': ('Warp Cell Efficiency', extract_int_percent),
    # 'Freighter_Fleet_Speed': ('Expedition Speed', extract_int_percent),
    # 'Freighter_Fleet_Fuel': ('Expedition Efficiency', extract_int_percent),
    # 'Freighter_Fleet_Combat': ('Expedition Defenses', extract_int_percent),
    # 'Freighter_Fleet_Trade': ('Expedition Trade Ability', extract_int_percent),
    # 'Freighter_Fleet_Explore': ('Expedition Scientific Ability', extract_int_percent),
    # 'Freighter_Fleet_Mine': ('Expedition Mining Ability', extract_int_percent),
}

# In the mapping below, the values are composed as follows:
# * meta: type used by the game, min value, max value
# * number: max possible stats
data = {
    # C1 improving <STELLAR><>.
    # C2 improving <STELLAR><> and <STELLAR><>.
    # B2 to <STELLAR><> and <STELLAR><>.
    # B3 to <STELLAR><>, <STELLAR><>,
    # A2 improve <STELLAR><> and <STELLAR><>.
    # A3 improve <STELLAR><>, <STELLAR><>,
    # S2 to <STELLAR><> and <STELLAR><>.
    # S3 to <STELLAR><>, <STELLAR><>,
    # X2 targets <STELLAR><> and <STELLAR><>.
    # X3 targets <STELLAR><>, <STELLAR><>,

    # region Weapon

    'UP_LASER': {
        '1': {
            # UP_LASER1#0 // #19 #20 // ENHANCED PHOTON MIRROR, ?
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 10),
                ('Weapon_Laser_HeatTime', 5, 15),
                ('Weapon_Laser_Drain', 0, 10),
                ('Weapon_Laser_ReloadTime', 5, 10),
            ],
            'number': 2,  # 1
        },
        '2': {
            # UP_LASER2#0 // #17 #19 // FINE-TUNED PHOTON MIRROR, ?
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 15),
                ('Weapon_Laser_HeatTime', 15, 20),
                ('Weapon_Laser_Drain', 10, 15),
                ('Weapon_Laser_ReloadTime', 10, 15),
            ],
            'number': 3,  # 2
        },
        '3': {
            # UP_LASER3#0 // #17 #19 // HIGH-ENERGY PHOTON MIRROR, ?
            'meta': [
                ('Weapon_Laser_Mining_Speed', 10, 20),
                ('Weapon_Laser_HeatTime', 20, 40),
                ('Weapon_Laser_Drain', 15, 20),
                ('Weapon_Laser_ReloadTime', 10, 15),
            ],
            'number': 4,  # 3
        },
        '4': {
            # UP_LASER4#0 // BRILLIANT PHOTON MIRROR, ?
            'meta': [
                ('Weapon_Laser_Mining_Speed', 15, 20),
                ('Weapon_Laser_HeatTime', 40, 50),
                ('Weapon_Laser_Drain', 20, 20),
                ('Weapon_Laser_ReloadTime', 15, 20),
            ],
            'number': 4,  # 4
        },
        'X': {
            # UP_LASERX#0 // #22 #24 // COUNTERFEIT FINE-TUNED PHOTON MIRROR, ?
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 20),
                ('Weapon_Laser_HeatTime', 5, 55),
                ('Weapon_Laser_Drain', 0, 25),
                ('Weapon_Laser_ReloadTime', 5, 25),
            ],
            'number': 3,  # 1
        },
    },

    'UP_SCAN': {
        '1': {
            # UP_SCAN1#0 // #19 #20 // WAVEFORM DETECTOR, ?
            # UP_SCAN1#50000 // #50007 #50033 // LOW-HEAT DETECTOR, ?
            'meta': [
                ('Weapon_Scan_Radius', 5, 10),
                ('Weapon_Scan_Discovery_Creature', 1000, 2000),
                ('Weapon_Scan_Discovery_Flora', 1000, 2000),
            ],
            'number': 2,  # 1
        },
        '2': {
            # UP_SCAN2#0 // NANITE-POWERED DETECTOR, ?
            # UP_SCAN1#50000 // CALIBRATED DETECTOR, ?
            'meta': [
                ('Weapon_Scan_Radius', 10, 20),
                ('Weapon_Scan_Discovery_Creature', 2500, 5000),
                ('Weapon_Scan_Discovery_Flora', 2500, 5000),
            ],
            'number': 2,  # 2
        },
        '3': {
            # UP_SCAN3#0 // #1 #8 // FLUX DETECTOR, ?
            # UP_SCAN3#50000 // #50000 #50003 // GENOME DETECTOR, ?
            'meta': [
                ('Weapon_Scan_Radius', 20, 30),
                ('Weapon_Scan_Discovery_Creature', 5000, 10000),
                ('Weapon_Scan_Discovery_Flora', 5000, 10000),
            ],
            'number': 3,  # 2
        },
        '4': {
            # UP_SCAN4#0 // HOLOGRAPHIC DETECTOR, ?
            # UP_SCAN4#50000 // VACUUM DETECTOR, ?
            'meta': [
                ('Weapon_Scan_Radius', 30, 40),
                ('Weapon_Scan_Discovery_Creature', 6500, 10000),
                ('Weapon_Scan_Discovery_Flora', 6500, 10000),
            ],
            'number': 3,  # 3
        },
        'X': {
            # UP_SCANX#0 // #20 #22 // NANITE-POWERED DETECTOR, ?
            # UP_SCANX#50000 // #50001 #50002 // PROHIBITED CALIBRATED DETECTOR, ?
            'meta': [
                ('Weapon_Scan_Radius', 5, 50),
                ('Weapon_Scan_Discovery_Creature', 1000, 11000),
                ('Weapon_Scan_Discovery_Flora', 1000, 11000),
            ],
            'number': 3,  # 1
        },
    },

    'UP_BOLT': {
        '1': {
            # UP_BOLT1#0 // #17 #19 // BYPASS ENERGY LATTICE
            # UP_BOLT1#50000 // #50000 #50007 // WELL-CRAFTED ENERGY LATTICE
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 5, 10),
                ('Weapon_Projectile_ClipSize', 2, 2),
                ('Weapon_Projectile_Rate', 0, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 0, 5),
            ],
            'number': 3,  # 2 (AlwaysChoose + NumStats)
        },
        '2': {
            # UP_BOLT2#0 // #19 #20 // OPTICAL ENERGY LATTICE, LUMINOUS
            # UP_BOLT2#50000 // #50000 #50007 // VACUUM ENERGY LATTICE, ISOTROPIC
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 10, 15),
                ('Weapon_Projectile_ClipSize', 4, 4),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 5, 10),
            ],
            'number': 4,  # 3 (AlwaysChoose + NumStats)
        },
        '3': {
            # UP_BOLT3#0 // INCANDESCENT ENERGY LATTICE, PLATINUM
            # UP_BOLT3#50000 // RADIANT ENERGY LATTICE, DEUTERIUM
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 10, 20),
                ('Weapon_Projectile_ClipSize', 6, 6),
                ('Weapon_Projectile_Rate', 10, 15),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 10, 15),
            ],
            'number': 4,  # 4 (AlwaysChoose + NumStats)
        },
        '4': {
            # UP_BOLT4#0 // PUGNEUM ENERGY LATTICE, NEUTRINO
            # UP_BOLT4#50000 // ANCIENT ENERGY LATTICE, STARLIGHT
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 10, 20),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 10, 15),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 15, 15),
            ],
            'number': 4,  # 4
        },
        'X': {
            # UP_BOLTX#0 // #4 #8 // COUNTERFEIT OPTICAL ENERGY LATTICE, UNLICENSED
            # UP_BOLTX#50000 // #50001 #50002 // PROHIBITED VACUUM ENERGY LATTICE, FORBIDDEN
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 5, 25),
                ('Weapon_Projectile_ClipSize', 2, 10),
                ('Weapon_Projectile_Rate', 0, 20),
                ('Weapon_Projectile_BurstCap', 1, 2),
                ('Weapon_Projectile_BurstCooldown', 0, 20),
            ],
            'number': 4,  # 2 (AlwaysChoose + NumStats)
        },
    },

    'UP_GREN': {
        '1': {
            # UP_GREN1#0 // #17 #19 // SECONDARY GAS EXPANDER, TERTIARY
            # UP_GREN1#50000 // #50000 #50007 // BOOSTED GAS EXPANDER, EFFICIENT
            'meta': [
                ('Weapon_Grenade_Damage', 10, 20),
                ('Weapon_Grenade_Bounce', 33, 33),
                ('Weapon_Grenade_Radius', 0, 5),
                ('Weapon_Grenade_Speed', 100, 200),
            ],
            'number': 2,  # 1
        },
        '2': {
            # UP_GREN2#0 // #19 #33 // UNSTABLE GAS EXPANDER, LINEAR
            # UP_GREN2#50000 // #50007 #50022 // PUGNEUM GAS EXPANDER, KINETIC
            'meta': [
                ('Weapon_Grenade_Damage', 20, 30),
                ('Weapon_Grenade_Bounce', 33, 66),
                ('Weapon_Grenade_Radius', 5, 10),
                ('Weapon_Grenade_Speed', 100, 300),
            ],
            'number': 3,  # 1
        },
        '3': {
            # UP_GREN3#0 // #1 #8 // GEOMETRIC GAS EXPANDER, GYROSCOPIC
            # UP_GREN3#50000 // #50000 #50003 // SUPERCRITICAL GAS EXPANDER, GEOMETRIC
            'meta': [
                ('Weapon_Grenade_Damage', 30, 40),
                ('Weapon_Grenade_Bounce', 66, 100),
                ('Weapon_Grenade_Radius', 5, 10),
                ('Weapon_Grenade_Speed', 100, 300),
            ],
            'number': 3,  # 2
        },
        '4': {
            # UP_GREN4#0 // ANTIMATTER GAS EXPANDER, GRAVITATIONAL
            # UP_GREN4#50000 // M-FIELD GAS EXPANDER, NANO
            'meta': [
                ('Weapon_Grenade_Damage', 35, 40),
                ('Weapon_Grenade_Bounce', 100, 100),
                ('Weapon_Grenade_Radius', 10, 15),
                ('Weapon_Grenade_Speed', 200, 300),
            ],
            'number': 3,  # 3
        },
        'X': {
            # UP_GRENX#0 // #20 #37 // COUNTERFEIT UNSTABLE GAS EXPANDER, SMUGGLED
            # UP_GRENX#50000 // #50001 #50002 // PROHIBITED PUGNEUM GAS EXPANDER, FORBIDDEN
            'meta': [
                ('Weapon_Grenade_Damage', 10, 45),
                ('Weapon_Grenade_Bounce', 33, 133),
                ('Weapon_Grenade_Radius', 0, 20),
                ('Weapon_Grenade_Speed', 100, 400),
            ],
            'number': 3,  # 1
        },
    },

    'UP_TGREN': {
        '1': {
            # UP_TGREN1#0 // SECONDARY GAS EXPANDER, TERTIARY
            # UP_TGREN1#50000 // BOOSTED GAS EXPANDER, EFFICIENT
            'meta': [
                ('Weapon_Grenade_Damage', 10, 20),
                ('Weapon_Grenade_Radius', 10, 20),
                ('Weapon_Grenade_Speed', 100, 200),
            ],
            'number': 1,  # 1
        },
        '2': {
            # UP_TGREN2#0 // #17 #19 // UNSTABLE GAS EXPANDER, LINEAR
            # UP_TGREN2#50000 // #50000 #50007 // PUGNEUM GAS EXPANDER, XXXX
            'meta': [
                ('Weapon_Grenade_Damage', 20, 30),
                ('Weapon_Grenade_Radius', 20, 30),
                ('Weapon_Grenade_Speed', 100, 300),
            ],
            'number': 2,  # 1
        },
        '3': {
            # UP_TGREN3#0 // #17 #19 // GEOMETRIC UNSTABLE GAS EXPANDER, LINEAR
            # UP_TGREN3#50000 // #50000 #50007 // SUPERCRITICAL GAS EXPANDER, NANITE
            'meta': [
                ('Weapon_Grenade_Damage', 30, 40),
                ('Weapon_Grenade_Radius', 30, 50),
                ('Weapon_Grenade_Speed', 100, 300),
            ],
            'number': 2,  # 1
        },
        '4': {
            # UP_TGREN4#0 // ANTIMATTER GAS EXPANDER, GRAVITATIONAL
            # UP_TGREN4#50000 // M-FIELD GAS EXPANDER, NANO
            'meta': [
                ('Weapon_Grenade_Damage', 35, 40),
                ('Weapon_Grenade_Radius', 40, 50),
                ('Weapon_Grenade_Speed', 200, 300),
            ],
            'number': 2,  # 2
        },
        'X': {
            # UP_TGRENX#0 // #8 #16 // UNLICENSED UNSTABLE GAS EXPANDER, SMUGGLED
            # UP_TGRENX#50000 // #50001 #50010 // PROHIBITED PUGNEUM GAS EXPANDER, FORBIDDEN
            'meta': [
                ('Weapon_Grenade_Damage', 10, 45),
                ('Weapon_Grenade_Radius', 10, 60),
                ('Weapon_Grenade_Speed', 100, 400),
            ],
            'number': 2,  # 1
        },
    },

    # TODO verify values
    'UP_RAIL': {
        '1': {
            'meta': [
                ('Weapon_Laser_Damage', 300, 400),
                ('Weapon_Laser_ChargeTime', 5, 10),
            ],
            'number': 1,  # 1
        },
        '2': {
            'meta': [
                ('Weapon_Laser_Damage', 400, 500),
                ('Weapon_Laser_ChargeTime', 10, 15),
            ],
            'number': 2,  # 1
        },
        '3': {
            'meta': [
                ('Weapon_Laser_Damage', 500, 600),
                ('Weapon_Laser_ChargeTime', 10, 20),
            ],
            'number': 2,  # 2
        },
        '4': {
            'meta': [
                ('Weapon_Laser_Damage', 600, 750),
                ('Weapon_Laser_ChargeTime', 10, 20),
            ],
            'number': 2,  # 2
        },
        'X': {
            'meta': [
                ('Weapon_Laser_Damage', 300, 850),
                ('Weapon_Laser_ChargeTime', 5, 25),
            ],
            'number': 2,  # 1
        },
    },

    # TODO verify values
    'UP_SHOT': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_ReloadTime', 5, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_ReloadTime', 10, 15),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 0, 5),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 5, 10),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 4),
                ('Weapon_Projectile_ReloadTime', 15, 20),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 10, 15),
            ],
            'number': 4,
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 5),
                ('Weapon_Projectile_ReloadTime', 20, 25),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 10, 15),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 15, 20),
            ],
            'number': 4,
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 6),
                ('Weapon_Projectile_ReloadTime', 5, 30),
                ('Weapon_Projectile_ClipSize', 8, 8),
                ('Weapon_Projectile_Rate', 0, 20),
                ('Weapon_Projectile_BurstCap', 1, 1),
                ('Weapon_Projectile_BurstCooldown', 5, 25),
            ],
            'number': 4,
        },
    },

    # TODO verify values
    'UP_SMG': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1),
                ('Weapon_Projectile_Rate', 0, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2),
                ('Weapon_Projectile_Rate', 0, 10),
                ('Weapon_Projectile_ReloadTime', 0, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 3),
                ('Weapon_Projectile_Rate', 5, 10),
                ('Weapon_Projectile_ReloadTime', 0, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 3),
                ('Weapon_Projectile_Rate', 10, 15),
                ('Weapon_Projectile_ReloadTime', 5, 10),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 4),
                ('Weapon_Projectile_Rate', 0, 20),
                ('Weapon_Projectile_ReloadTime', 0, 15),
                ('Weapon_Projectile_ClipSize', 12, 12),
            ],
            'number': 4,
        },
    },

    # endregion

    # region Suit

    'UP_ENGY': {
        '1': {
            # UP_ENGY1#0 // #17 #31 // GAS PURIFIER, ?
            'meta': [
                ('Suit_Energy', 5, 20),
                ('Suit_Energy_Regen', 0, 10),
            ],
            'number': 2,
        },
        '2': {
            # UP_ENGY2#0 // HIGH-VOLUME PURIFIER, ?
            'meta': [
                ('Suit_Energy', 20, 50),
                ('Suit_Energy_Regen', 0, 25),
            ],
            'number': 2,
        },
        '3': {
            # UP_ENGY3#0 // T-GEL PURIFIER, ?
            'meta': [
                ('Suit_Energy', 50, 100),
                ('Suit_Energy_Regen', 25, 50),
            ],
            'number': 2,
        },
        'X': {
            # UP_ENGYX#0 // #4 #8 // COUNTERFEIT GAS PURIFIER, ?
            'meta': [
                ('Suit_Energy', 5, 110),
                ('Suit_Energy_Regen', 0, 75),
            ],
            'number': 2,
        },
    },

    'UP_HAZ': {
        'X': {
            # UP_HAZX#0 // COUNTERFEIT CRYOSTATIC AIR PURIFIER, ?
            'meta': [
                 ('Suit_Protection_ColdDrain', 1, 10),
                 ('Suit_Protection_HeatDrain', 1, 10),
                 ('Suit_Protection_RadDrain', 1, 10),
                 ('Suit_Protection_ToxDrain', 1, 10),
            ],
            'number': 4,
        },
    },

    # TODO verify values
    'UP_JET': {
        '1': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 50),
                ('Suit_Stamina_Strength', 10, 20),
                ('Suit_Stamina_Recovery', 0, 10),
                ('Suit_Jetpack_Drain', 5, 10),
                ('Suit_Jetpack_Refill', 0, 5),
            ],
            'number': 3,
        },
        '2': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 50),
                ('Suit_Stamina_Strength', 10, 30),
                ('Suit_Stamina_Recovery', 10, 20),
                ('Suit_Jetpack_Drain', 10, 15),
                ('Suit_Jetpack_Ignition', 0, 5),
                ('Suit_Jetpack_Refill', 0, 5),
            ],
            'number': 4,
        },
        '3': {
            'meta': [
                ('Suit_Jetpack_Tank', 50, 100),
                ('Suit_Stamina_Strength', 20, 50),
                ('Suit_Stamina_Recovery', 20, 30),
                ('Suit_Jetpack_Drain', 10, 20),
                ('Suit_Jetpack_Ignition', 0, 5),
                ('Suit_Jetpack_Refill', 10, 15),
            ],
            'number': 4,
        },
        '4': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 125),
                ('Suit_Stamina_Strength', 40, 50),
                ('Suit_Stamina_Recovery', 30, 50),
                ('Suit_Jetpack_Drain', 10, 20),
                ('Suit_Jetpack_Ignition', 5, 10),
                ('Suit_Jetpack_Refill', 15, 25),
            ],
            'number': 4,
        },
        'X': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 130),
                ('Suit_Stamina_Strength', 10, 60),
                ('Suit_Stamina_Recovery', 0, 60),
                ('Suit_Jetpack_Drain', 5, 25),
                ('Suit_Jetpack_Ignition', 0, 15),
                ('Suit_Jetpack_Refill', 5, 30),
            ],
            'number': 4,
        },
    },

    # TODO verify values
    'UP_SHLD': {
        '1': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 5, 10),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 15),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 20),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 20),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,
        },
        'X': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 5, 25),
                ('Suit_Armour_Health', 33, 33),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_UNW': {
        '1': {
            'meta': [
                ('Suit_Underwater', 60, 85),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Suit_Underwater', 75, 105),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Suit_Underwater', 95, 105),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_RAD': {
        '1': {
            'meta': [
                ('Suit_Protection_Radiation', 180, 265),
                ('Suit_DamageReduce_Radiation', 0, 5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Suit_Protection_Radiation', 200, 265),
                ('Suit_DamageReduce_Radiation', 5, 15),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Suit_Protection_Radiation', 220, 265),
                ('Suit_DamageReduce_Radiation', 10, 20),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_TOX': {
        '1': {
            'meta': [
                ('Suit_Protection_Toxic', 180, 265),
                ('Suit_DamageReduce_Toxic', 0, 5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Suit_Protection_Toxic', 200, 265),
                ('Suit_DamageReduce_Toxic', 5, 15),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Suit_Protection_Toxic', 220, 265),
                ('Suit_DamageReduce_Toxic', 10, 20),
            ],
            'number': 2,
        }, },

    # TODO verify values
    'UP_COLD': {
        '1': {
            'meta': [
                ('Suit_Protection_Cold', (180, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (0, 5, extract_int_percent)),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Suit_Protection_Cold', (200, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (5, 15, extract_int_percent)),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Suit_Protection_Cold', (220, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (10, 20, extract_int_percent)),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_HOT': {
        '1': {
            'meta': [
                ('Suit_Protection_Heat', 180, 265),
                ('Suit_DamageReduce_Heat', 0, 5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Suit_Protection_Heat', 200, 265),
                ('Suit_DamageReduce_Heat', 5, 15),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Suit_Protection_Heat', 220, 265),
                ('Suit_DamageReduce_Heat', 10, 20),
            ],
            'number': 2,
        },
    },

    # endregion

    # region Ship

    # TODO verify values
    'UP_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 10),
                ('Ship_Boost', 0, 5),
                ('Ship_BoostManeuverability', 0, 5),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 10, 15),
                ('Ship_Boost', 5, 10),
                ('Ship_BoostManeuverability', 0, 10),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20),
                ('Ship_Boost', 5, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20),
                ('Ship_Boost', 10, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,
        },
        'X': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 25),
                ('Ship_Boost', 0, 20),
                ('Ship_BoostManeuverability', 0, 14),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
        'X': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 300),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 10, 20),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 20, 20),
            ],
            'number': 1,
        },
        'X': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 25),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 16),
                ('Ship_Weapons_Guns_Rate', 0.1, 1.1),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 1.0),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 12, 20),
                ('Ship_Weapons_Guns_Rate', 0.6, 1.6),
                ('Ship_Weapons_Guns_HeatTime', 1.0, 2.0),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 16, 24),
                ('Ship_Weapons_Guns_Rate', 1.6, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 2.0, 3.0),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 20, 28),
                ('Ship_Weapons_Guns_Rate', 2.1, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 3.0, 3.0),
            ],
            'number': 3,
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 32),
                ('Ship_Weapons_Guns_Rate', 0.1, 2.6),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 3.5),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 35),
                ('Ship_Weapons_Lasers_Damage', 30, 40),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 35, 55),
                ('Ship_Weapons_Lasers_Damage', 40, 50),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75),
                ('Ship_Weapons_Lasers_Damage', 50, 60),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95),
                ('Ship_Weapons_Lasers_Damage', 60, 70),
            ],
            'number': 2,
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 100),
                ('Ship_Weapons_Lasers_Damage', 30, 80),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_SSHOT': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 1, 5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10),
                ('Ship_Weapons_Guns_Rate', 10, 13.5),
                ('Ship_Weapons_Guns_HeatTime', 5, 10),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 10),
                ('Ship_Weapons_Guns_Rate', 13.5, 15),
                ('Ship_Weapons_Guns_HeatTime', 10, 15),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 10),
                ('Ship_Weapons_Guns_Rate', 15, 15),
                ('Ship_Weapons_Guns_HeatTime', 15, 15),
            ],
            'number': 3,
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 12),
                ('Ship_Weapons_Guns_Rate', 5, 20),
                ('Ship_Weapons_Guns_HeatTime', 1, 20),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_SMINI': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 1, 3),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 3, 5),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 12),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 5, 7),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 12),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 7, 9),
            ],
            'number': 3,
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 14),
                ('Ship_Weapons_Guns_Rate', 1, 15),
                ('Ship_Weapons_Guns_HeatTime', 1, 13),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_SBLOB': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 10, 20),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10),
                ('Ship_Weapons_Guns_Rate', 1, 5),
                ('Ship_Weapons_Guns_HeatTime', 20, 25),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 12),
                ('Ship_Weapons_Guns_Rate', 5, 10),
                ('Ship_Weapons_Guns_HeatTime', 25, 30),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 12),
                ('Ship_Weapons_Guns_Rate', 10, 15),
                ('Ship_Weapons_Guns_HeatTime', 30, 35),
            ],
            'number': 3,
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 14),
                ('Ship_Weapons_Guns_Rate', 1, 20),
                ('Ship_Weapons_Guns_HeatTime', 10, 40),
            ],
            'number': 3,
        },
    },

    # endregion

    # region Vehicle

    # TODO verify values
    'UP_EXGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 5, 10),
                ('Vehicle_GunHeatTime', 1, 5),
                ('Vehicle_GunRate', 1, 5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20),
                ('Vehicle_GunHeatTime', 5, 10),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 3,
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30),
                ('Vehicle_GunHeatTime', 10, 15),
                ('Vehicle_GunRate', 10, 15),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40),
                ('Vehicle_GunHeatTime', 15, 20),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_EXLAS': {
        '1': {
            'meta': [
                ('Vehicle_LaserDamage', 5, 10),
                ('Vehicle_LaserHeatTime', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 10, 20),
                ('Vehicle_LaserHeatTime', 5, 10),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 20, 30),
                ('Vehicle_LaserHeatTime', 10, 15),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 30, 40),
                ('Vehicle_LaserHeatTime', 15, 20),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_BOOST': {
        '1': {
            'meta': [
                ('Vehicle_BoostSpeed', 10, 20),
                ('Vehicle_BoostTanks', 10, 20),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Vehicle_BoostSpeed', 20, 35),
                ('Vehicle_BoostTanks', 15, 30),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_BoostSpeed', 35, 55),
                ('Vehicle_BoostTanks', 30, 50),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_BoostSpeed', 55, 70),
                ('Vehicle_BoostTanks', 50, 60),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_EXENG': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5),
                ('Vehicle_EngineTopSpeed', 1, 3),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_EngineTopSpeed', 8, 15),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 10, 15),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_EXSUB': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5),
                ('Vehicle_EngineTopSpeed', 1, 3),
                ('Vehicle_SubBoostSpeed', 10, 20),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_EngineTopSpeed', 3, 8),
                ('Vehicle_SubBoostSpeed', 20, 35),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_EngineTopSpeed', 8, 15),
                ('Vehicle_SubBoostSpeed', 35, 55),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_EngineTopSpeed', 10, 15),
                ('Vehicle_SubBoostSpeed', 55, 70),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_SUGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 5, 10),
                ('Vehicle_GunRate', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20),
                ('Vehicle_GunRate', 5, 10),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30),
                ('Vehicle_GunRate', 10, 15),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_MCLAS': {
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 10, 20),
                ('Vehicle_LaserHeatTime', 5, 10),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 20, 30),
                ('Vehicle_LaserHeatTime', 10, 15),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 30, 40),
                ('Vehicle_LaserHeatTime', 15, 20),
            ],
            'number': 2,
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
            'number': 3,
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30),
                ('Vehicle_GunHeatTime', 10, 15),
                ('Vehicle_GunRate', 10, 15),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40),
                ('Vehicle_GunHeatTime', 15, 20),
                ('Vehicle_GunRate', 15, 20),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UP_MCENG': {
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10),
                ('Vehicle_BoostTanks', 10, 15),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15),
                ('Vehicle_BoostTanks', 15, 25),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20),
                ('Vehicle_BoostTanks', 25, 30),
            ],
            'number': 2,
        },
    },

    # endregion

    # region Living Ship

    # TODO verify values
    'UA_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 10),
                ('Ship_Boost', 0, 5),
                ('Ship_BoostManeuverability', 0, 5),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 10, 15),
                ('Ship_Boost', 5, 10),
                ('Ship_BoostManeuverability', 0, 10),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20),
                ('Ship_Boost', 5, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20),
                ('Ship_Boost', 10, 15),
                ('Ship_BoostManeuverability', 5, 12),
                ('Ship_Maneuverability', 0.5, 0.5),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UA_LAUN': {
        '1': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 5, 10),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 10, 15),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 15, 20),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 20, 20),
                ('Ship_Launcher_AutoCharge', 1, 1),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UA_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UA_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 10, 20),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 20, 20),
            ],
            'number': 1,
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
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 12, 20),
                ('Ship_Weapons_Guns_Rate', 0.6, 1.6),
                ('Ship_Weapons_Guns_HeatTime', 1.0, 2.0),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 16, 24),
                ('Ship_Weapons_Guns_Rate', 1.6, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 2.0, 3.0),
            ],
            'number': 3,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 20, 28),
                ('Ship_Weapons_Guns_Rate', 2.1, 2.1),
                ('Ship_Weapons_Guns_HeatTime', 3.0, 3.0),
            ],
            'number': 3,
        },
    },

    # TODO verify values
    'UA_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 35),
                ('Ship_Weapons_Lasers_Damage', 30, 40),
            ],
            'number': 2,
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 35, 55),
                ('Ship_Weapons_Lasers_Damage', 40, 50),
            ],
            'number': 2,
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75),
                ('Ship_Weapons_Lasers_Damage', 50, 60),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95),
                ('Ship_Weapons_Lasers_Damage', 60, 70),
            ],
            'number': 2,
        },
    },

    # endregion

    # region Freighter

    # TODO verify values
    'UP_FRHYP': {
        '1': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 50, 100),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 100, 150),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 150, 200),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
        '4': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 200, 250),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1),
            ],
            'number': 2,
        },
    },

    # TODO verify values
    'UP_FRSPE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Speed', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Speed', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Speed', 10, 14),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Speed', 15, 15),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_FRFUE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Fuel', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Fuel', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Fuel', 10, 15),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Fuel', 15, 20),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_FRCOM': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Combat', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Combat', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Combat', 10, 14),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Combat', 15, 15),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_FRTRA': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Trade', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Trade', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Trade', 10, 14),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Trade', 15, 15),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_FREXP': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Explore', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Explore', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Explore', 10, 14),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Explore', 15, 15),
            ],
            'number': 1,
        },
    },

    # TODO verify values
    'UP_FRMIN': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Mine', 1, 5),
            ],
            'number': 1,
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Mine', 5, 10),
            ],
            'number': 1,
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Mine', 10, 14),
            ],
            'number': 1,
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Mine', 15, 15),
            ],
            'number': 1,
        },
    },

    # endregion
}

# endregion

# region input

if len(sys.argv) < 5:
    print('ERROR: Not enough arguments! Usage: python procedural.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]')
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

if tech_name not in data or tech_class not in data[tech_name]:
    print(f'ERROR: Your procedural item ({tech_name}{tech_class}) is not configured')
    exit()

tech_stats = data[tech_name][tech_class]

if len(addr_stats) != tech_stats['number']:
    print(f'ERROR: Your number of memory addresses ({len(addr_stats)}) does not match the max number of stats ({len(tech_stats)})')
    exit()

tech_stats['meta'] = init_meta(tech_stats['meta'])

addr_off = addr_id_seed + hashtag_index + 1
fieldnames = ['Seed', 'Name', 'Perfection'] + [value[0] for value in tech_stats['meta'].values()]
high_number = tech_stats['number']
key_possibilities = tech_stats['meta'].keys()
middle = start
pattern = '(?<=R>).*?(?=<)'
round_digits = 2

begin = int(pm.read_string(addr_off, byte=16))
count = int(TOTAL_SEEDS / iteration_necessary)

stop = max(0, min(begin + count, TOTAL_SEEDS))

f_name = fr'{tech_name}{tech_class}_{begin}_{stop - 1}.csv'
with open(f_name, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel-tab')
    writer.writeheader()
    print('Range:', begin, '-', stop)
    for i in range(begin, stop):
        i_next = i + 1

        # Loops until all data is fully loaded.
        while True:
            description = pm.read_string(addr_description, byte=512)
            title = pm.read_string(addr_title, byte=64)

            values = [pm.read_string(a) for a in addr_stats]

            # First check that description and title are fully loaded.
            if all(text != '' for text in [description, title]):
                # Then extract stat names from the description and make sure it's fully loaded
                # and contains the complete name of a possible stat. Also ensure that
                # the current number of stats is loaded.
                # Some seeds produce an empty description starting with UPGRADE_0 and have no stats (displayed).
                keys = re.findall(pattern, description)
                if (
                    all(key in key_possibilities for key in keys) and all(value != '' for value in values[:len(keys)])
                ) or description.startswith('UPGRADE_0'):
                    break

        if i_next < stop:
            pm.write_string(addr_off, str(i_next))

        # Set to \0 to avoid duplicates in next while True
        pm.write_uchar(addr_description, 0)
        pm.write_uchar(addr_title, 0)
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

        perfection = round(sum(perfection) / high_number, round_digits) if perfection else ''
        title = title.title() \
            .replace('Ph Balancer', 'pH Balancer')  # UP_HAZ

        row.update({
            'Name': title,
            'Perfection': perfection,
            'Seed': i,
        })

        writer.writerow(row)
        if (i - (STEPS - 1)) % STEPS == 0:
            middle_next = datetime.now()
            print(f'{i:>6} ({middle_next - middle})')
            middle = middle_next
            f.flush()
    else:
        # 7 = tech_class (1) + # (1) + 99999 (5)
        pm.write_string(addr_id_seed, f'{tech_name}{tech_class}#{begin}'.ljust(len(tech_name) + 7, '\0'))

end = datetime.now()

print(f'{stop - begin} module(s) added to {f_name} in {end - start}')

# endregion
