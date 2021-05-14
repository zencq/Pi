# This script iterates over all loaded items and reads the values.
# Usage: python procedural.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_NAME ADDRESS_DESCRIPTION ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]

import csv
import pymem
import re
import sys
from collections import OrderedDict
from datetime import datetime

# region const

STEPS = 10000
TOTAL_SEEDS = 100000
TRANSLATION = {
    'Weapon_Laser_Mining_Speed': 'Mining Speed',
    'Weapon_Laser_HeatTime': 'Heat Dispersion',
    'Weapon_Laser_Drain': 'Fuel Efficiency',
    'Weapon_Laser_ReloadTime': 'Overheat Downtime',
    'Weapon_Scan_Radius': 'Scan Radius',
    'Weapon_Scan_Discovery_Creature': 'Fauna Analysis Rewards',
    'Weapon_Scan_Discovery_Flora': 'Flora Analysis Rewards',
    'Weapon_Projectile_Damage': 'Damage',
    'Weapon_Projectile_ReloadTime': 'Reload Time',
    'Weapon_Projectile_ClipSize': 'Clip Size',
    'Weapon_Projectile_Rate': 'Fire Rate',
    'Weapon_Projectile_BurstCap': 'Shots Per Burst',
    'Weapon_Projectile_BurstCooldown': 'Burst Cooldown',
    'Weapon_Grenade_Damage': 'Damage',
    'Weapon_Grenade_Bounce': 'Bounce Potential',
    'Weapon_Grenade_Radius': 'Explosion Radius',
    'Weapon_Grenade_Speed': 'Projectile Velocity',
    'Weapon_Laser_Damage': 'Damage',
    'Weapon_Laser_ChargeTime': 'Time to Full Power',
    'Suit_Energy': 'Life Support Tanks',
    'Suit_Energy_Regen': 'Solar Panel Power',
    'Suit_Protection_ColdDrain': 'Cold Resistance',
    'Suit_Protection_HeatDrain': 'Heat Resistance',
    'Suit_Protection_RadDrain': 'Radiation Resistance',
    'Suit_Protection_ToxDrain': 'Toxic Resistance',
    'Suit_Jetpack_Tank': 'Jetpack Tanks',
    'Suit_Stamina_Strength': 'Sprint Distance',
    'Suit_Stamina_Recovery': 'Sprint Recovery Time',
    'Suit_Jetpack_Drain': 'Fuel Efficiency',
    'Suit_Jetpack_Ignition': 'Initial Boost Power',
    'Suit_Jetpack_Refill': 'Recharge Rate',
    'Suit_Armour_Shield_Strength': 'Shield Strength',
    'Suit_Armour_Health': 'Core Health',
    'Suit_Underwater': 'Oxygen Tank',
    'Suit_Protection_Radiation': 'Radiation Protection',
    'Suit_DamageReduce_Radiation': 'Radiation Damage Shielding',
    'Suit_Protection_Toxic': 'Toxic Protection',
    'Suit_DamageReduce_Toxic': 'Toxic Damage Shielding',
    'Suit_Protection_Cold': 'Cold Protection',
    'Suit_DamageReduce_Cold': 'Cold Damage Shielding',
    'Suit_Protection_Heat': 'Heat Protection',
    'Suit_DamageReduce_Heat': 'Heat Damage Shielding',
    'Ship_PulseDrive_MiniJumpFuelSpending': 'Pulse Drive Fuel Efficiency',
    'Ship_Boost': 'Boost',
    'Ship_BoostManeuverability': 'Maneuverability',  # TODO: rename with mod to "Boost-Maneuverability"
    'Ship_Maneuverability': 'Maneuverability',
    'Ship_Hyperdrive_JumpDistance': 'Hyperdrive Range',
    'Ship_Hyperdrive_JumpsPerCell': 'Warp Cell Efficiency',
    'Ship_Armour_Shield_Strength': 'Shield Strength',
    'Ship_Weapons_Guns_Damage': 'Damage',
    'Ship_Weapons_Guns_Rate': 'Fire Rate',
    'Ship_Weapons_Guns_HeatTime': 'Heat Dispersion',
    'Ship_Weapons_Lasers_HeatTime': 'Heat Dispersion',
    'Ship_Weapons_Lasers_Damage': 'Damage',
    'Vehicle_GunDamage': 'Damage',
    'Vehicle_GunHeatTime': 'Weapon Power Efficiency',
    'Vehicle_GunRate': 'Rate of Fire',
    'Vehicle_LaserDamage': 'Mining Laser Power',
    'Vehicle_LaserHeatTime': 'Mining Laser Efficiency',
    'Vehicle_BoostSpeed': 'Boost Power',
    'Vehicle_BoostTanks': 'Boost Tank Size',
    'Vehicle_EngineFuelUse': 'Fuel Usage',
    'Vehicle_EngineTopSpeed': 'Top Speed',
    'Vehicle_SubBoostSpeed': 'Acceleration',
    'Ship_Launcher_TakeOffCost': 'Launch Cost',
    'Ship_Launcher_AutoCharge': 'Automatic Recharging',
    'Freighter_Hyperdrive_JumpDistance': 'Hyperdrive Range',
    'Freighter_Hyperdrive_JumpsPerCell': 'Warp Cell Efficiency',
    'Freighter_Fleet_Speed': 'Expedition Speed',
    'Freighter_Fleet_Fuel': 'Expedition Efficiency',
    'Freighter_Fleet_Combat': 'Expedition Defenses',
    'Freighter_Fleet_Trade': 'Expedition Trade Ability',
    'Freighter_Fleet_Explore': 'Expedition Scientific Ability',
    'Freighter_Fleet_Mine': 'Expedition Mining Ability',
}

# endregion


# region methods


def init_cheatengine_address(address):
    if isinstance(address, list):
        return [init_cheatengine_address(addr) for addr in address]

    return int(f'0x{address}', 16)


def init_meta(data):
    return OrderedDict([
        (TRANSLATION[line[0]], line)
        for line in data
    ])


def extract_float(data):
    return float(data[1:])


def extract_int_percent(data):
    return int(data[1:-1])


def extract_int_percent_thousand(data):
    return extract_int_percent(data.replace(',', ''))

# endregion

# region stats


# Stats are normally displayed as '+X%' which can be with method 'extract_int_percent'. For special formats other extraction method are needed.
# In the mapping below, the values are composed as follows:
# * meta: stats type used by the game, min value, max value, extraction method
# * number: min of possible stats, max of possible stats
data = {
    # <STELLAR><>
    # #0 // #, # // NAME, OTHER
    # #50000 // #, # // NAME, OTHER

    # region Weapon

    'UP_LASER': {
        '1': {
            # UP_LASER1#0 // #19 #20 // ENHANCED PHOTON MIRROR
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 10, extract_int_percent),
                ('Weapon_Laser_HeatTime', 5, 15, extract_int_percent),
                ('Weapon_Laser_Drain', 0, 10, extract_int_percent),
                ('Weapon_Laser_ReloadTime', 5, 10, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            # UP_LASER2#0 // #17 #19 // FINE-TUNED PHOTON MIRROR
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 15, extract_int_percent),
                ('Weapon_Laser_HeatTime', 15, 20, extract_int_percent),
                ('Weapon_Laser_Drain', 10, 15, extract_int_percent),
                ('Weapon_Laser_ReloadTime', 10, 15, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            # UP_LASER3#0 // #17 #19 // HIGH-ENERGY PHOTON MIRROR
            'meta': [
                ('Weapon_Laser_Mining_Speed', 10, 20, extract_int_percent),
                ('Weapon_Laser_HeatTime', 20, 40, extract_int_percent),
                ('Weapon_Laser_Drain', 15, 20, extract_int_percent),
                ('Weapon_Laser_ReloadTime', 10, 15, extract_int_percent),
            ],
            'number': (3, 4),
        },
        '4': {
            # UP_LASER4#0 // BRILLIANT PHOTON MIRROR
            'meta': [
                ('Weapon_Laser_Mining_Speed', 15, 20, extract_int_percent),
                ('Weapon_Laser_HeatTime', 40, 50, extract_int_percent),
                ('Weapon_Laser_Drain', 20, 20, extract_int_percent),
                ('Weapon_Laser_ReloadTime', 15, 20, extract_int_percent),
            ],
            'number': (4, 4),
        },
        'X': {
            # UP_LASERX#0 // #22 #24 // COUNTERFEIT FINE-TUNED PHOTON MIRROR
            'meta': [
                ('Weapon_Laser_Mining_Speed', 5, 20, extract_int_percent),
                ('Weapon_Laser_HeatTime', 5, 55, extract_int_percent),
                ('Weapon_Laser_Drain', 0, 25, extract_int_percent),
                ('Weapon_Laser_ReloadTime', 5, 25, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    'UP_SCAN': {
        '1': {
            # UP_SCAN1#0 // #19 #20 // WAVEFORM DETECTOR
            # UP_SCAN1#50000 // #50007 #50033 // LOW-HEAT DETECTOR
            'meta': [
                ('Weapon_Scan_Radius', 5, 10, extract_int_percent),
                ('Weapon_Scan_Discovery_Creature', 1000, 2000, extract_int_percent_thousand),
                ('Weapon_Scan_Discovery_Flora', 1000, 2000, extract_int_percent_thousand),
            ],
            'number': (1, 2),
        },
        '2': {
            # UP_SCAN2#0 // NANITE-POWERED DETECTOR
            # UP_SCAN1#50000 // CALIBRATED DETECTOR
            'meta': [
                ('Weapon_Scan_Radius', 10, 20, extract_int_percent),
                ('Weapon_Scan_Discovery_Creature', 2500, 5000, extract_int_percent_thousand),
                ('Weapon_Scan_Discovery_Flora', 2500, 5000, extract_int_percent_thousand),
            ],
            'number': (2, 2),
        },
        '3': {
            # UP_SCAN3#0 // #1 #8 // FLUX DETECTOR
            # UP_SCAN3#50000 // #50000 #50003 // GENOME DETECTOR
            'meta': [
                ('Weapon_Scan_Radius', 20, 30, extract_int_percent),
                ('Weapon_Scan_Discovery_Creature', 5000, 10000, extract_int_percent_thousand),
                ('Weapon_Scan_Discovery_Flora', 5000, 10000, extract_int_percent_thousand),
            ],
            'number': (2, 3),
        },
        '4': {
            # UP_SCAN4#0 // HOLOGRAPHIC DETECTOR
            # UP_SCAN4#50000 // VACUUM DETECTOR
            'meta': [
                ('Weapon_Scan_Radius', 30, 40, extract_int_percent),
                ('Weapon_Scan_Discovery_Creature', 6500, 10000, extract_int_percent_thousand),
                ('Weapon_Scan_Discovery_Flora', 6500, 10000, extract_int_percent_thousand),
            ],
            'number': (3, 3),
        },
        'X': {
            # UP_SCANX#0 // #20, #22 // NANITE-POWERED DETECTOR
            # UP_SCANX#50000 // #50001 #50002 // PROHIBITED CALIBRATED DETECTOR
            'meta': [
                ('Weapon_Scan_Radius', 5, 50, extract_int_percent),
                ('Weapon_Scan_Discovery_Creature', 1000, 11000, extract_int_percent_thousand),
                ('Weapon_Scan_Discovery_Flora', 1000, 11000, extract_int_percent_thousand),
            ],
            'number': (1, 3),
        },
    },

    'UP_BOLT': {
        '1': {
            # UP_BOLT1#0 // #17 #19 // BYPASS ENERGY LATTICE
            # UP_BOLT1#50000 // #50000 #50007 // WELL-CRAFTED ENERGY LATTICE
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 5, 10, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 2, 2, extract_float),
                ('Weapon_Projectile_Rate', 0, 10, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_float),
                ('Weapon_Projectile_BurstCooldown', 0, 5, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '2': {
            # UP_BOLT2#0 // #19 #20 // OPTICAL ENERGY LATTICE, LUMINOUS
            # UP_BOLT2#50000 // #50000 #50007 // VACUUM ENERGY LATTICE, ISOTROPIC
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 10, 15, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 4, 4, extract_float),
                ('Weapon_Projectile_Rate', 5, 10, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_float),
                ('Weapon_Projectile_BurstCooldown', 5, 10, extract_int_percent),
            ],
            'number': (3, 4),
        },
        '3': {
            # UP_BOLT3#0 // INCANDESCENT ENERGY LATTICE, PLATINUM
            # UP_BOLT3#50000 // RADIANT ENERGY LATTICE, DEUTERIUM
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 10, 20, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 6, 6, extract_float),
                ('Weapon_Projectile_Rate', 10, 15, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 2, extract_float),
                ('Weapon_Projectile_BurstCooldown', 10, 15, extract_int_percent),
            ],
            'number': (4, 4),
        },
        '4': {
            # UP_BOLT4#0 // PUGNEUM ENERGY LATTICE, NEUTRINO
            # UP_BOLT4#50000 // ANCIENT ENERGY LATTICE, STARLIGHT
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2, extract_int_percent),  # TODO
                ('Weapon_Projectile_ReloadTime', 10, 20, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 8, 8, extract_float),
                ('Weapon_Projectile_Rate', 10, 15, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 2, extract_float),
                ('Weapon_Projectile_BurstCooldown', 15, 15, extract_int_percent),
            ],
            'number': (4, 4),
        },
        'X': {
            # UP_BOLTX#0 // #4 #8 // COUNTERFEIT OPTICAL ENERGY LATTICE, UNLICENSED
            # UP_BOLTX#50000 // #50001 #50002 // PROHIBITED VACUUM ENERGY LATTICE, FORBIDDEN
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2, extract_int_percent),  # TODO
                ('Weapon_Projectile_ReloadTime', 5, 25, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 2, 10, extract_float),
                ('Weapon_Projectile_Rate', 0, 20, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 2, extract_float),
                ('Weapon_Projectile_BurstCooldown', 0, 20, extract_int_percent),
            ],
            'number': (2, 4),
        },
    },

    # TODO verify values
    'UP_GREN': {
        '1': {
            # UP_GREN1#0 // #, # // NAME, OTHER
            # UP_GREN1#50000 // #, # // NAME, OTHER
            'meta': [
                ('Weapon_Grenade_Damage', 1000, 2000, extract_int_percent),
                ('Weapon_Grenade_Bounce', 1, 1, extract_int_percent),
                ('Weapon_Grenade_Radius', 0, 5, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 2, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Weapon_Grenade_Damage', 2000, 3000, extract_int_percent),
                ('Weapon_Grenade_Bounce', 1, 2, extract_int_percent),
                ('Weapon_Grenade_Radius', 5, 10, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 3, extract_int_percent),
            ],
            'number': (1, 3),
        },
        '3': {
            'meta': [
                ('Weapon_Grenade_Damage', 3000, 4000, extract_int_percent),
                ('Weapon_Grenade_Bounce', 2, 3, extract_int_percent),
                ('Weapon_Grenade_Radius', 5, 10, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 3, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Weapon_Grenade_Damage', 3500, 4000, extract_int_percent),
                ('Weapon_Grenade_Bounce', 3, 3, extract_int_percent),
                ('Weapon_Grenade_Radius', 10, 15, extract_int_percent),
                ('Weapon_Grenade_Speed', 2, 3, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Weapon_Grenade_Damage', 1000, 4500, extract_int_percent),
                ('Weapon_Grenade_Bounce', 1, 4, extract_int_percent),
                ('Weapon_Grenade_Radius', 0, 20, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 4, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # TODO verify values
    'UP_TGREN': {
        '1': {
            'meta': [
                ('Weapon_Grenade_Damage', 1000, 2000, extract_int_percent),
                ('Weapon_Grenade_Radius', 10, 20, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 2, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Weapon_Grenade_Damage', 2000, 3000, extract_int_percent),
                ('Weapon_Grenade_Radius', 20, 30, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 3, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Weapon_Grenade_Damage', 3000, 4000, extract_int_percent),
                ('Weapon_Grenade_Radius', 30, 50, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 3, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Weapon_Grenade_Damage', 3500, 4000, extract_int_percent),
                ('Weapon_Grenade_Radius', 40, 50, extract_int_percent),
                ('Weapon_Grenade_Speed', 2, 3, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            'meta': [
                ('Weapon_Grenade_Damage', 1000, 4500, extract_int_percent),
                ('Weapon_Grenade_Radius', 10, 60, extract_int_percent),
                ('Weapon_Grenade_Speed', 1, 4, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    # TODO verify values
    'UP_RAIL': {
        '1': {
            'meta': [
                ('Weapon_Laser_Damage', 300, 400, extract_int_percent),
                ('Weapon_Laser_ChargeTime', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Weapon_Laser_Damage', 400, 500, extract_int_percent),
                ('Weapon_Laser_ChargeTime', 10, 15, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Weapon_Laser_Damage', 500, 600, extract_int_percent),
                ('Weapon_Laser_ChargeTime', 10, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Weapon_Laser_Damage', 600, 750, extract_int_percent),
                ('Weapon_Laser_ChargeTime', 10, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            'meta': [
                ('Weapon_Laser_Damage', 300, 850, extract_int_percent),
                ('Weapon_Laser_ChargeTime', 5, 25, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    # TODO verify values
    'UP_SHOT': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 5, 10, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 10, 15, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 8, 8, extract_int_percent),
                ('Weapon_Projectile_Rate', 0, 5, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_int_percent),
                ('Weapon_Projectile_BurstCooldown', 5, 10, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 4, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 15, 20, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 8, 8, extract_int_percent),
                ('Weapon_Projectile_Rate', 5, 10, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_int_percent),
                ('Weapon_Projectile_BurstCooldown', 10, 15, extract_int_percent),
            ],
            'number': (3, 4),
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 3, 5, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 20, 25, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 8, 8, extract_int_percent),
                ('Weapon_Projectile_Rate', 10, 15, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_int_percent),
                ('Weapon_Projectile_BurstCooldown', 15, 20, extract_int_percent),
            ],
            'number': (4, 4),
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 6, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 5, 30, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 8, 8, extract_int_percent),
                ('Weapon_Projectile_Rate', 0, 20, extract_int_percent),
                ('Weapon_Projectile_BurstCap', 1, 1, extract_int_percent),
                ('Weapon_Projectile_BurstCooldown', 5, 25, extract_int_percent),
            ],
            'number': (1, 4),
        },
    },

    # TODO verify values
    'UP_SMG': {
        '1': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 1, extract_int_percent),
                ('Weapon_Projectile_Rate', 0, 10, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 12, 12, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 2, extract_int_percent),
                ('Weapon_Projectile_Rate', 0, 10, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 0, 10, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 12, 12, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 3, extract_int_percent),
                ('Weapon_Projectile_Rate', 5, 10, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 0, 10, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 12, 12, extract_int_percent),
            ],
            'number': (3, 4),
        },
        '4': {
            'meta': [
                ('Weapon_Projectile_Damage', 2, 3, extract_int_percent),
                ('Weapon_Projectile_Rate', 10, 15, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 5, 10, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 12, 12, extract_int_percent),
            ],
            'number': (4, 4),
        },
        'X': {
            'meta': [
                ('Weapon_Projectile_Damage', 1, 4, extract_int_percent),
                ('Weapon_Projectile_Rate', 0, 20, extract_int_percent),
                ('Weapon_Projectile_ReloadTime', 0, 15, extract_int_percent),
                ('Weapon_Projectile_ClipSize', 12, 12, extract_int_percent),
            ],
            'number': (1, 4),
        },
    },

    # endregion

    # region Suit

    'UP_ENGY': {
        '1': {
            # UP_ENGY1#0 // #17 #31 // GAS PURIFIER
            'meta': [
                ('Suit_Energy', 5, 20, extract_int_percent),
                ('Suit_Energy_Regen', 0, 10, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            # UP_ENGY2#0 // HIGH-VOLUME PURIFIER
            'meta': [
                ('Suit_Energy', 20, 50, extract_int_percent),
                ('Suit_Energy_Regen', 0, 25, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            # UP_ENGY3#0 // T-GEL PURIFIER
            'meta': [
                ('Suit_Energy', 50, 100, extract_int_percent),
                ('Suit_Energy_Regen', 25, 50, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            # UP_ENGYX#0 // #4 #8 // COUNTERFEIT GAS PURIFIER
            'meta': [
                ('Suit_Energy', 5, 110, extract_int_percent),
                ('Suit_Energy_Regen', 0, 75, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    'UP_HAZ': {
        'X': {
            # UP_HAZX#0 // COUNTERFEIT CRYOSTATIC AIR PURIFIER
            'meta': [
                 ('Suit_Protection_ColdDrain', 1, 10, extract_int_percent),
                 ('Suit_Protection_HeatDrain', 1, 10, extract_int_percent),
                 ('Suit_Protection_RadDrain', 1, 10, extract_int_percent),
                 ('Suit_Protection_ToxDrain', 1, 10, extract_int_percent),
            ],
            'number': (4, 4),
        },
    },

    # TODO verify values
    'UP_JET': {
        '1': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 50, extract_int_percent),
                ('Suit_Stamina_Strength', 10, 20, extract_int_percent),
                ('Suit_Stamina_Recovery', 0, 10, extract_int_percent),
                ('Suit_Jetpack_Drain', 5, 10, extract_int_percent),
                ('Suit_Jetpack_Refill', 0, 5, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '2': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 50, extract_int_percent),
                ('Suit_Stamina_Strength', 10, 30, extract_int_percent),
                ('Suit_Stamina_Recovery', 10, 20, extract_int_percent),
                ('Suit_Jetpack_Drain', 10, 15, extract_int_percent),
                ('Suit_Jetpack_Ignition', 0, 5, extract_int_percent),
                ('Suit_Jetpack_Refill', 0, 5, extract_int_percent),
            ],
            'number': (2, 4),
        },
        '3': {
            'meta': [
                ('Suit_Jetpack_Tank', 50, 100, extract_int_percent),
                ('Suit_Stamina_Strength', 20, 50, extract_int_percent),
                ('Suit_Stamina_Recovery', 20, 30, extract_int_percent),
                ('Suit_Jetpack_Drain', 10, 20, extract_int_percent),
                ('Suit_Jetpack_Ignition', 0, 5, extract_int_percent),
                ('Suit_Jetpack_Refill', 10, 15, extract_int_percent),
            ],
            'number': (3, 4),
        },
        '4': {
            'meta': [
                ('Suit_Jetpack_Tank', 100, 125, extract_int_percent),
                ('Suit_Stamina_Strength', 40, 50, extract_int_percent),
                ('Suit_Stamina_Recovery', 30, 50, extract_int_percent),
                ('Suit_Jetpack_Drain', 10, 20, extract_int_percent),
                ('Suit_Jetpack_Ignition', 5, 10, extract_int_percent),
                ('Suit_Jetpack_Refill', 15, 25, extract_int_percent),
            ],
            'number': (4, 4),
        },
        'X': {
            'meta': [
                ('Suit_Jetpack_Tank', 0, 130, extract_int_percent),
                ('Suit_Stamina_Strength', 10, 60, extract_int_percent),
                ('Suit_Stamina_Recovery', 0, 60, extract_int_percent),
                ('Suit_Jetpack_Drain', 5, 25, extract_int_percent),
                ('Suit_Jetpack_Ignition', 0, 15, extract_int_percent),
                ('Suit_Jetpack_Refill', 5, 30, extract_int_percent),
            ],
            'number': (2, 4),
        },
    },

    # TODO verify values
    'UP_SHLD': {
        '1': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 5, 10, extract_int_percent),
                ('Suit_Armour_Health', 33, 33, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 15, extract_int_percent),
                ('Suit_Armour_Health', 33, 33, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 20, extract_int_percent),
                ('Suit_Armour_Health', 33, 33, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 10, 20, extract_int_percent),
                ('Suit_Armour_Health', 33, 33, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            'meta': [
                ('Suit_Armour_Shield_Strength', 5, 25, extract_int_percent),
                ('Suit_Armour_Health', 33, 33, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    # TODO verify values
    'UP_UNW': {
        '1': {
            'meta': [
                ('Suit_Underwater', 60, 85, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Suit_Underwater', 75, 105, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Suit_Underwater', 95, 105, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_RAD': {
        '1': {
            'meta': [
                ('Suit_Protection_Radiation', 180, 265, extract_int_percent),
                ('Suit_DamageReduce_Radiation', 0, 5, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '2': {
            'meta': [
                ('Suit_Protection_Radiation', 200, 265, extract_int_percent),
                ('Suit_DamageReduce_Radiation', 5, 15, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Suit_Protection_Radiation', 220, 265, extract_int_percent),
                ('Suit_DamageReduce_Radiation', 10, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_TOX': {
        '1': {
            'meta': [
                ('Suit_Protection_Toxic', 180, 265, extract_int_percent),
                ('Suit_DamageReduce_Toxic', 0, 5, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '2': {
            'meta': [
                ('Suit_Protection_Toxic', 200, 265, extract_int_percent),
                ('Suit_DamageReduce_Toxic', 5, 15, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Suit_Protection_Toxic', 220, 265, extract_int_percent),
                ('Suit_DamageReduce_Toxic', 10, 20, extract_int_percent),
            ],
            'number': (2, 2),
        }, },

    # TODO verify values
    'UP_COLD': {
        '1': {
            'meta': [
                ('Suit_Protection_Cold', (180, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (0, 5, extract_int_percent)),
            ],
            'number': (2, 2),
        },
        '2': {
            'meta': [
                ('Suit_Protection_Cold', (200, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (5, 15, extract_int_percent)),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Suit_Protection_Cold', (220, 265, extract_int_percent)),
                ('Suit_DamageReduce_Cold', (10, 20, extract_int_percent)),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_HOT': {
        '1': {
            'meta': [
                ('Suit_Protection_Heat', 180, 265, extract_int_percent),
                ('Suit_DamageReduce_Heat', 0, 5, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '2': {
            'meta': [
                ('Suit_Protection_Heat', 200, 265, extract_int_percent),
                ('Suit_DamageReduce_Heat', 5, 15, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Suit_Protection_Heat', 220, 265, extract_int_percent),
                ('Suit_DamageReduce_Heat', 10, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # endregion

    # region Ship

    # TODO verify values
    'UP_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 10, extract_int_percent),
                ('Ship_Boost', 0, 5, extract_int_percent),
                ('Ship_BoostManeuverability', 0, 5, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 10, 15, extract_int_percent),
                ('Ship_Boost', 5, 10, extract_int_percent),
                ('Ship_BoostManeuverability', 0, 10, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20, extract_int_percent),
                ('Ship_Boost', 5, 15, extract_int_percent),
                ('Ship_BoostManeuverability', 5, 12, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20, extract_int_percent),
                ('Ship_Boost', 10, 15, extract_int_percent),
                ('Ship_BoostManeuverability', 5, 12, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 25, extract_int_percent),
                ('Ship_Boost', 0, 20, extract_int_percent),
                ('Ship_BoostManeuverability', 0, 14, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # TODO verify values
    'UP_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200, extract_int_percent),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250, extract_int_percent),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 300, extract_int_percent),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    # TODO verify values
    'UP_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 10, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 20, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        'X': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 25, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 16, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 0.1, 1.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 1.0, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 12, 20, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 0.6, 1.6, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1.0, 2.0, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 16, 24, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1.6, 2.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 2.0, 3.0, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 20, 28, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 2.1, 2.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 3.0, 3.0, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 32, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 0.1, 2.6, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 3.5, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # TODO verify values
    'UP_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 35, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 30, 40, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 35, 55, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 40, 50, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 50, 60, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 60, 70, extract_int_percent),
            ],
            'number': (2, 2),
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 100, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 30, 80, extract_int_percent),
            ],
            'number': (1, 2),
        },
    },

    # TODO verify values
    'UP_SSHOT': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 5, 10, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1, 5, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 10, 13.5, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 5, 10, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 10, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 13.5, 15, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 10, 15, extract_int_percent),
            ],
            'number': (3, 3),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 10, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 15, 15, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 15, 15, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 12, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 5, 20, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1, 20, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # TODO verify values
    'UP_SMINI': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 5, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1, 3, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 5, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 3, 5, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 12, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 5, 10, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 5, 7, extract_int_percent),
            ],
            'number': (3, 3),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 12, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 5, 10, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 7, 9, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 14, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 15, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1, 13, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # TODO verify values
    'UP_SBLOB': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 6, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 5, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 10, 20, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 4, 10, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 5, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 20, 25, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 12, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 5, 10, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 25, 30, extract_int_percent),
            ],
            'number': (3, 3),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 10, 12, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 10, 15, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 30, 35, extract_int_percent),
            ],
            'number': (3, 3),
        },
        'X': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 2, 14, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1, 20, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 10, 40, extract_int_percent),
            ],
            'number': (1, 3),
        },
    },

    # endregion

    # region Vehicle

    # TODO verify values
    'UP_EXGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 5, 10, extract_int_percent),
                ('Vehicle_GunHeatTime', 1, 5, extract_int_percent),
                ('Vehicle_GunRate', 1, 5, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20, extract_int_percent),
                ('Vehicle_GunHeatTime', 5, 10, extract_int_percent),
                ('Vehicle_GunRate', 5, 10, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30, extract_int_percent),
                ('Vehicle_GunHeatTime', 10, 15, extract_int_percent),
                ('Vehicle_GunRate', 10, 15, extract_int_percent),
            ],
            'number': (3, 3),
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40, extract_int_percent),
                ('Vehicle_GunHeatTime', 15, 20, extract_int_percent),
                ('Vehicle_GunRate', 15, 20, extract_int_percent),
            ],
            'number': (3, 3),
        },
    },

    # TODO verify values
    'UP_EXLAS': {
        '1': {
            'meta': [
                ('Vehicle_LaserDamage', 5, 10, extract_int_percent),
                ('Vehicle_LaserHeatTime', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 10, 20, extract_int_percent),
                ('Vehicle_LaserHeatTime', 5, 10, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 20, 30, extract_int_percent),
                ('Vehicle_LaserHeatTime', 10, 15, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 30, 40, extract_int_percent),
                ('Vehicle_LaserHeatTime', 15, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_BOOST': {
        '1': {
            'meta': [
                ('Vehicle_BoostSpeed', 10, 20, extract_int_percent),
                ('Vehicle_BoostTanks', 10, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Vehicle_BoostSpeed', 20, 35, extract_int_percent),
                ('Vehicle_BoostTanks', 15, 30, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_BoostSpeed', 35, 55, extract_int_percent),
                ('Vehicle_BoostTanks', 30, 50, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_BoostSpeed', 55, 70, extract_int_percent),
                ('Vehicle_BoostTanks', 50, 60, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_EXENG': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 1, 3, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 3, 8, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 8, 15, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 10, 15, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_EXSUB': {
        '1': {
            'meta': [
                ('Vehicle_EngineFuelUse', 1, 5, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 1, 3, extract_int_percent),
                ('Vehicle_SubBoostSpeed', 10, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 3, 8, extract_int_percent),
                ('Vehicle_SubBoostSpeed', 20, 35, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 8, 15, extract_int_percent),
                ('Vehicle_SubBoostSpeed', 35, 55, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20, extract_int_percent),
                ('Vehicle_EngineTopSpeed', 10, 15, extract_int_percent),
                ('Vehicle_SubBoostSpeed', 55, 70, extract_int_percent),
            ],
            'number': (3, 3),
        },
    },

    # TODO verify values
    'UP_SUGUN': {
        '1': {
            'meta': [
                ('Vehicle_GunDamage', 5, 10, extract_int_percent),
                ('Vehicle_GunRate', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20, extract_int_percent),
                ('Vehicle_GunRate', 5, 10, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30, extract_int_percent),
                ('Vehicle_GunRate', 10, 15, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40, extract_int_percent),
                ('Vehicle_GunRate', 15, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_MCLAS': {
        '2': {
            'meta': [
                ('Vehicle_LaserDamage', 10, 20, extract_int_percent),
                ('Vehicle_LaserHeatTime', 5, 10, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Vehicle_LaserDamage', 20, 30, extract_int_percent),
                ('Vehicle_LaserHeatTime', 10, 15, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_LaserDamage', 30, 40, extract_int_percent),
                ('Vehicle_LaserHeatTime', 15, 20, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_MCGUN': {
        '2': {
            'meta': [
                ('Vehicle_GunDamage', 10, 20, extract_int_percent),
                ('Vehicle_GunHeatTime', 5, 10, extract_int_percent),
                ('Vehicle_GunRate', 5, 10, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '3': {
            'meta': [
                ('Vehicle_GunDamage', 20, 30, extract_int_percent),
                ('Vehicle_GunHeatTime', 10, 15, extract_int_percent),
                ('Vehicle_GunRate', 10, 15, extract_int_percent),
            ],
            'number': (3, 3),
        },
        '4': {
            'meta': [
                ('Vehicle_GunDamage', 30, 40, extract_int_percent),
                ('Vehicle_GunHeatTime', 15, 20, extract_int_percent),
                ('Vehicle_GunRate', 15, 20, extract_int_percent),
            ],
            'number': (3, 3),
        },
    },

    # TODO verify values
    'UP_MCENG': {
        '2': {
            'meta': [
                ('Vehicle_EngineFuelUse', 5, 10, extract_int_percent),
                ('Vehicle_BoostTanks', 10, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Vehicle_EngineFuelUse', 10, 15, extract_int_percent),
                ('Vehicle_BoostTanks', 15, 25, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '4': {
            'meta': [
                ('Vehicle_EngineFuelUse', 15, 20, extract_int_percent),
                ('Vehicle_BoostTanks', 25, 30, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # endregion

    # region Living Ship

    # TODO verify values
    'UA_PULSE': {
        '1': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 5, 10, extract_int_percent),
                ('Ship_Boost', 0, 5, extract_int_percent),
                ('Ship_BoostManeuverability', 0, 5, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 10, 15, extract_int_percent),
                ('Ship_Boost', 5, 10, extract_int_percent),
                ('Ship_BoostManeuverability', 0, 10, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '3': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 15, 20, extract_int_percent),
                ('Ship_Boost', 5, 15, extract_int_percent),
                ('Ship_BoostManeuverability', 5, 12, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Ship_PulseDrive_MiniJumpFuelSpending', 20, 20, extract_int_percent),
                ('Ship_Boost', 10, 15, extract_int_percent),
                ('Ship_BoostManeuverability', 5, 12, extract_int_percent),
                ('Ship_Maneuverability', 0.5, 0.5, extract_int_percent),
            ],
            'number': (3, 3),
        },
    },

    # TODO verify values
    'UA_LAUN': {
        '1': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 10, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 15, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Ship_Launcher_TakeOffCost', 20, 20, extract_int_percent),
                ('Ship_Launcher_AutoCharge', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UA_HYP': {
        '1': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 50, 100, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 100, 150, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 150, 200, extract_int_percent),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Ship_Hyperdrive_JumpDistance', 200, 250, extract_int_percent),
                ('Ship_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UA_S_SHL': {
        '1': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 10, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Ship_Armour_Shield_Strength', 20, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UA_SGUN': {
        '1': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 8, 16, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 0.1, 1.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 0.1, 1.0, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 12, 20, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 0.6, 1.6, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 1.0, 2.0, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 16, 24, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 1.6, 2.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 2.0, 3.0, extract_int_percent),
            ],
            'number': (2, 3),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Guns_Damage', 20, 28, extract_int_percent),
                ('Ship_Weapons_Guns_Rate', 2.1, 2.1, extract_int_percent),
                ('Ship_Weapons_Guns_HeatTime', 3.0, 3.0, extract_int_percent),
            ],
            'number': (3, 3),
        },
    },

    # TODO verify values
    'UA_SLASR': {
        '1': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 10, 35, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 30, 40, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '2': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 35, 55, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 40, 50, extract_int_percent),
            ],
            'number': (1, 2),
        },
        '3': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 55, 75, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 50, 60, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Ship_Weapons_Lasers_HeatTime', 75, 95, extract_int_percent),
                ('Ship_Weapons_Lasers_Damage', 60, 70, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # endregion

    # region Freighter

    # TODO verify values
    'UP_FRHYP': {
        '1': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 50, 100, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 100, 150, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 150, 200, extract_int_percent),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
        '4': {
            'meta': [
                ('Freighter_Hyperdrive_JumpDistance', 200, 250, extract_int_percent),
                ('Freighter_Hyperdrive_JumpsPerCell', 1, 1, extract_int_percent),
            ],
            'number': (2, 2),
        },
    },

    # TODO verify values
    'UP_FRSPE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Speed', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Speed', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Speed', 10, 14, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Speed', 15, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_FRFUE': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Fuel', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Fuel', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Fuel', 10, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Fuel', 15, 20, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_FRCOM': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Combat', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Combat', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Combat', 10, 14, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Combat', 15, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_FRTRA': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Trade', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Trade', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Trade', 10, 14, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Trade', 15, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_FREXP': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Explore', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Explore', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Explore', 10, 14, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Explore', 15, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # TODO verify values
    'UP_FRMIN': {
        '1': {
            'meta': [
                ('Freighter_Fleet_Mine', 1, 5, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '2': {
            'meta': [
                ('Freighter_Fleet_Mine', 5, 10, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '3': {
            'meta': [
                ('Freighter_Fleet_Mine', 10, 14, extract_int_percent),
            ],
            'number': (1, 1),
        },
        '4': {
            'meta': [
                ('Freighter_Fleet_Mine', 15, 15, extract_int_percent),
            ],
            'number': (1, 1),
        },
    },

    # endregion
}

# endregion

# region input

if len(sys.argv) < 5:
    print(
        'ERROR: Not enough arguments! Usage: python procedural.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_NAME ADDRESS_DESCRIPTION ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]')
    exit()

addr_id_seed = init_cheatengine_address(sys.argv[2])
addr_description = init_cheatengine_address(sys.argv[4])
addr_stats = init_cheatengine_address(sys.argv[5:])
addr_title = init_cheatengine_address(sys.argv[3])
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

if len(addr_stats) != tech_stats['number'][1]:
    print(f'ERROR: Your number of memory addresses ({len(addr_stats)}) does not match the max number of stats ({len(tech_stats)})')
    exit()

tech_stats['meta'] = init_meta(tech_stats['meta'])

addr_off = addr_id_seed + hashtag_index + 1
fieldnames = ['Seed', 'Name', 'Perfection'] + [value[0] for value in tech_stats['meta'].values()]
high_number = tech_stats['number'][1]
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
