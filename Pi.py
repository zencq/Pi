import csv
import ctypes
import logging
import os
import re
import threading

import nmspy.common as nms

from datetime import datetime

from nmspy.data import (
    common as nms_common_structs,
    enums as nms_enums,
    function_hooks as hooks,
    structs as nms_structs,
)
from nmspy.hooking import disable, on_fully_booted, on_key_release
from nmspy.memutils import map_struct, map_struct_temp
from nmspy.mod_loader import NMSMod


# region Data

FREE_MEMORY_STEPS = 250  # multiple of it should be TOTAL_SEEDS

LANGUAGES = [
    "Name (en)",
    "Name (fr)",
    "Name (it)",
    "Name (de)",
    "Name (es)",
    "Name (ru)",
    "Name (pl)",
    "Name (nl)",
    "Name (pt)",
    "Name (pt-BR)",
    "Name (ja)",
    "Name (zh-CN)",
    "Name (zh-TW)",
    "Name (ko)",
]

PI_ROOT = os.path.realpath(f"{os.path.dirname(__file__)}\\..\\..")  # use Pi root directory as starting point

PRODUCT = [
    "BIO",
    "BONE",
    "DARK",
    "FARM",
    "FEAR",
    "FOSS",
    "HIST",
    "LOOT",
    "PLNT",
    "SALV",
    "SEA",
    "STAR",
    "TOOL",
]

RE_PRODUCT_AGE = re.compile("([0-9]+)")

TECHNOLOGY = {
    "AlienShip": {
        "UA_HYP": ["1", "2", "3", "4"],
        "UA_LAUN": ["1", "2", "3", "4"],
        "UA_PULSE": ["1", "2", "3", "4"],
        "UA_S_SHL": ["1", "2", "3", "4"],
        "UA_SGUN": ["1", "2", "3", "4"],
        "UA_SLASR": ["1", "2", "3", "4"],
    },
    "Exocraft": {
        "UP_BOOST": ["1", "2", "3", "4"],
        "UP_EXENG": ["1", "2", "3", "4"],
        "UP_EXGUN": ["1", "2", "3", "4"],
        "UP_EXLAS": ["1", "2", "3", "4"],
    },
    "Freighter": {
        "UP_FRCOM": ["1", "2", "3", "4"],
        "UP_FREXP": ["1", "2", "3", "4"],
        "UP_FRFUE": ["1", "2", "3", "4"],
        "UP_FRHYP": ["1", "2", "3", "4"],
        "UP_FRMIN": ["1", "2", "3", "4"],
        "UP_FRSPE": ["1", "2", "3", "4"],
        "UP_FRTRA": ["1", "2", "3", "4"],
    },
    "Mech": {
        "UP_MCENG": ["2", "3", "4"],
        "UP_MCGUN": ["2", "3", "4"],
        "UP_MCLAS": ["2", "3", "4"],
    },
    "Ship": {
        "UP_HYP": ["1", "2", "3", "4", "X"],
        "UP_LAUN": ["1", "2", "3", "4", "X"],
        "UP_PULSE": ["1", "2", "3", "4", "X"],
        "UP_S_SHL": ["1", "2", "3", "4", "X"],
        "UP_SBLOB": ["1", "2", "3", "4", "X"],
        "UP_SGUN": ["1", "2", "3", "4", "X"],
        "UP_SLASR": ["1", "2", "3", "4", "X"],
        "UP_SMINI": ["1", "2", "3", "4", "X"],
        "UP_SSHOT": ["1", "2", "3", "4", "X"],
    },
    "Submarine": {
        "UP_EXSUB": ["1", "2", "3", "4"],
        "UP_SUGUN": ["1", "2", "3", "4"],
    },
    "Suit": {
        "UP_COLD": ["1", "2", "3"],
        "UP_ENGY": ["1", "2", "3", "X"],
        "UP_HAZ": ["X"],
        "UP_HOT": ["1", "2", "3"],
        "UP_JET": ["1", "2", "3", "4", "X"],
        "UP_RAD": ["1", "2", "3"],
        "UP_RBSUIT": [""],
        "UP_SHLD": ["1", "2", "3", "4", "X"],
        "UP_SNSUIT": [""],
        "UP_TOX": ["1", "2", "3"],
        "UP_UNW": ["1", "2", "3"],
    },
    "Weapon": {
        "UP_BOLT": ["1", "2", "3", "4", "X"],
        "UP_CANN": ["1", "2", "3", "4", "X"],
        "UP_GREN": ["1", "2", "3", "4", "X"],
        "UP_LASER": ["1", "2", "3", "4", "X"],
        "UP_RAIL": ["1", "2", "3", "4", "X"],
        "UP_SCAN": ["1", "2", "3", "4", "X"],
        "UP_SENGUN": [""],
        "UP_SHOT": ["1", "2", "3", "4", "X"],
        "UP_SMG": ["1", "2", "3", "4", "X"],
        "UP_TGREN": ["1", "2", "3", "4", "X"],
    },
}

TOTAL_SEEDS = 100000

TRANSLATION = {
    # region Weapon

    nms_enums.eStatsType.Weapon_Laser_Damage: [],  # Damage (+4%) > 36.83852767944336
    nms_enums.eStatsType.Weapon_Laser_Mining_Speed: [(1, "-"), ("*", 100)],  # Mining Speed (+17%) > 0.8384891152381897 > 16.15108847618103
    nms_enums.eStatsType.Weapon_Laser_HeatTime: [("-", 1), ("*", 100)],  # Heat Dispersion (+46%) > 1.407882571220398 > 40.788257122039795
    nms_enums.eStatsType.Weapon_Laser_ReloadTime: [(1, "-"), ("*", 100)],  # Overheat Downtime (-16%) > 0.8482741117477417 > 15.17258882522583
    nms_enums.eStatsType.Weapon_Laser_Drain: [("-", 1), ("*", 100)],  # Fuel Efficiency (+21%) > 1.2000000476837158 > 20.000004768371582
    nms_enums.eStatsType.Weapon_Laser_ChargeTime: [(1, "-"), ("*", 100)],  # Time to Full Power (-20%) > 0.9363773465156555 > 6.36226534843445
    nms_enums.eStatsType.Weapon_Projectile_Damage: [],  # Damage (+1%) > 3.270596981048584
    nms_enums.eStatsType.Weapon_Projectile_Rate: [("-", 1), ("*", 100)],  # Fire Rate (+11%) > 1.13314688205719 > 13.314688205718994
    nms_enums.eStatsType.Weapon_Projectile_ClipSize: [],  # Clip Size (+8.0) > 8.0
    nms_enums.eStatsType.Weapon_Projectile_ReloadTime: [(1, "-"), ("*", 100)],  # Reload Time (-15%) > 0.8999865055084229 > 10.001349449157715
    nms_enums.eStatsType.Weapon_Projectile_MaximumCharge: [],  # Ion Spheres Created (+1.0) > 1.0
    nms_enums.eStatsType.Weapon_Projectile_BurstCap: [],  # Shots Per Burst (+1.3) > 1.1662184000015259
    nms_enums.eStatsType.Weapon_Projectile_BurstCooldown: [(1, "-"), ("*", 100)],  # Burst Cooldown (-6%) > 0.8500000238418579 > 14.999997615814209
    nms_enums.eStatsType.Weapon_ChargedProjectile_ChargeTime: [(1, "-"), ("*", 100)],  # Charging Speed (-22%) > 0.76045161485672 > 23.954838514328003
    nms_enums.eStatsType.Weapon_ChargedProjectile_ExtraSpeed: [],  # Ion Sphere Speed (+12%) > 12.988007545471191
    nms_enums.eStatsType.Weapon_Grenade_Damage: [],  # Damage (+38%) > 116.51052856445312
    nms_enums.eStatsType.Weapon_Grenade_Radius: [],  # Explosion Radius (+49%) > 1.1039005517959595
    nms_enums.eStatsType.Weapon_Grenade_Speed: [],  # Projectile Velocity (+103%) > 2.7219414710998535
    nms_enums.eStatsType.Weapon_Grenade_Bounce: [],  # Bounce Potential (+33%) > 1.0
    nms_enums.eStatsType.Weapon_Scan_Radius: [("-", 1), ("*", 100)],  # Scan Radius (+38%) > 1.0582551956176758 >
    nms_enums.eStatsType.Weapon_Scan_Discovery_Creature: [("*", 100)],  # Fauna Analysis Rewards (+5,071%) > 10.788254737854004 > 1078.8254737854004
    nms_enums.eStatsType.Weapon_Scan_Discovery_Flora: [("*", 100)],  # Flora Analysis Rewards (+8,220%) > 10.094901084899902 > 1009.4901084899902
    nms_enums.eStatsType.Weapon_Scan_Discovery_Mineral: [("*", 100)],  # Mineral Analysis Rewards (+7,467%) > 17.21941566467285 > 1721.9415664672852

    # endregion

    # region Suit

    nms_enums.eStatsType.Suit_Armour_Health: [],  # Core Health (+33%) > 20.0
    nms_enums.eStatsType.Suit_Armour_Shield_Strength: [("*", 100)],  # Shield Strength (+31%) > 0.13419264554977417 > 13.419264554977417
    nms_enums.eStatsType.Suit_Energy: [("*", 100)],  # Life Support Tanks (+84%) > 0.1525779366493225 > 15.257793664932251
    nms_enums.eStatsType.Suit_Energy_Regen: [("-", 1), ("*", 100)],  # Solar Panel Power (+26%) > 1.0146995782852173 > 1.4699578285217285
    nms_enums.eStatsType.Suit_Protection_Cold: [],  # Cold Protection (?) > 230.13558959960938
    nms_enums.eStatsType.Suit_Protection_Heat: [],  # Heat Protection (?) > 230.13558959960938
    nms_enums.eStatsType.Suit_Protection_Toxic: [],  # Toxic Protection (?) > 230.13558959960938
    nms_enums.eStatsType.Suit_Protection_Radiation: [],  # Radiation Protection (?) > 230.13558959960938
    nms_enums.eStatsType.Suit_Underwater: [],  # Oxygen Tank (?) > 66.08882904052734
    nms_enums.eStatsType.Suit_DamageReduce_Cold: [(1, "-"), ("*", 100)],  # Cold Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    nms_enums.eStatsType.Suit_DamageReduce_Heat: [(1, "-"), ("*", 100)],  # Heat Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    nms_enums.eStatsType.Suit_DamageReduce_Radiation: [(1, "-"), ("*", 100)],  # Radiation Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    nms_enums.eStatsType.Suit_DamageReduce_Toxic: [(1, "-"), ("*", 100)],  # Toxic Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    nms_enums.eStatsType.Suit_Protection_HeatDrain: [("-", 1), ("*", 100)],  # Heat Resistance (+4%) > 1.0696643590927124 > 6.96643590927124
    nms_enums.eStatsType.Suit_Protection_ColdDrain: [("-", 1), ("*", 100)],  # Cold Resistance (+6%) > 1.0343537330627441 > 3.435373306274414
    nms_enums.eStatsType.Suit_Protection_ToxDrain: [("-", 1), ("*", 100)],  # Toxic Resistance (+2%) > 1.0958983898162842 > 9.589838981628418
    nms_enums.eStatsType.Suit_Protection_RadDrain: [("-", 1), ("*", 100)],  # Radiation Resistance (+2%) > 1.0243568420410156 > 2.4356842041015625
    nms_enums.eStatsType.Suit_Stamina_Strength: [("*", 100)],  # Sprint Distance (+31%) > 0.1399400383234024 > 13.99400383234024
    nms_enums.eStatsType.Suit_Stamina_Recovery: [("-", 1), ("*", 100)],  # Sprint Recovery Time (+31%) > 1.0165899991989136 > 1.6589999198913574
    nms_enums.eStatsType.Suit_Jetpack_Tank: [("*", 100)],  # Jetpack Tanks (+217%) > 2.0275888442993164 > 202.75888442993164
    nms_enums.eStatsType.Suit_Jetpack_Drain: [(1, "-"), ("*", 100)],  # Fuel Efficiency (+16%) > 0.9013239741325378 > 9.867602586746216
    nms_enums.eStatsType.Suit_Jetpack_Refill: [("-", 1), ("*", 100)],  # Recharge Rate (+6%) > 1.011878252029419 > 1.1878252029418945
    nms_enums.eStatsType.Suit_Jetpack_Ignition: [("-", 1), ("*", 100)],  # Initial Boost Power (+15%) > 1.016648769378662 > 1.6648769378662

    # endregion

    # region Ship

    nms_enums.eStatsType.Ship_Weapons_Guns_Damage: [],  # Damage (+6%) > 20.023605346679688
    nms_enums.eStatsType.Ship_Weapons_Guns_Rate: [("-", 1), ("*", 100)],  # Fire Rate (+3%) > 1.0210000276565552 > 2.1000027656555176
    nms_enums.eStatsType.Ship_Weapons_Guns_HeatTime: [("-", 1), ("*", 100)],  # Heat Dispersion (+3%) > 1.0299999713897705 > 2.999997138977051
    nms_enums.eStatsType.Ship_Weapons_Lasers_Damage: [],  # Damage (+25%) > 60.78825378417969
    nms_enums.eStatsType.Ship_Weapons_Lasers_HeatTime: [("-", 1), ("*", 100)],  # Heat Dispersion (+63%) > 1.7505900859832764 > 75.05900859832764
    nms_enums.eStatsType.Ship_Weapons_ShieldLeech: [],  # Shield recharge on impact (+105%) > 0.27219414710998535
    nms_enums.eStatsType.Ship_Armour_Shield_Strength: [],  # Shield Strength (+30%) > 0.20000000298023224
    nms_enums.eStatsType.Ship_Hyperdrive_JumpDistance: [],  # Hyperdrive Range (221 ly) > 250.77337646484375
    nms_enums.eStatsType.Ship_Hyperdrive_JumpsPerCell: [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    nms_enums.eStatsType.Ship_Launcher_TakeOffCost: [(1, "-"), ("*", 100)],  # Launch Cost (-20%) > 0.800000011920929 > 19.999998807907104
    nms_enums.eStatsType.Ship_Launcher_AutoCharge: [],  # Automatic Recharging (Enabled) > 1.0
    nms_enums.eStatsType.Ship_PulseDrive_MiniJumpFuelSpending: [(1, "-"), ("*", 100)],  # Pulse Drive Fuel Efficiency (+20%) > 0.800000011920929 > 19.999998807907104
    nms_enums.eStatsType.Ship_Boost: [("-", 1), ("*", 100)],  # Boost (+14%) > 1.1405895948410034 > 14.058959484100342
    nms_enums.eStatsType.Ship_Maneuverability: [],  # Maneuverability (?) > 1.006500005722046
    nms_enums.eStatsType.Ship_BoostManeuverability: [("-", 1), ("*", 100)],  # Maneuverability (+17%) > 1.1019220352172852 > 10.192203521728516

    # endregion

    # region Freighter

    nms_enums.eStatsType.Freighter_Hyperdrive_JumpDistance: [],  # Hyperdrive Range (209 ly) > 53.26720428466797
    nms_enums.eStatsType.Freighter_Hyperdrive_JumpsPerCell: [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    nms_enums.eStatsType.Freighter_Fleet_Speed: [("-", 1), ("*", 100)],  # Expedition Speed (+15%) > 1.0126137733459473 > 1.2613773345947266
    nms_enums.eStatsType.Freighter_Fleet_Fuel: [(1, "-"), ("*", 100)],  # Expedition Efficiency (+20%) > 0.9721637964248657 >
    nms_enums.eStatsType.Freighter_Fleet_Combat: [("-", 1), ("*", 100)],  # # Expedition Defenses (+15%) > 1.0126137733459473 > 1.26137733459473
    nms_enums.eStatsType.Freighter_Fleet_Trade: [("-", 1), ("*", 100)],  # Expedition Trade Ability (+15%) > 1.0126137733459473 > 1.2613773345947266
    nms_enums.eStatsType.Freighter_Fleet_Explore: [("-", 1), ("*", 100)],  # Expedition Scientific Ability (+15%) > 1.1026138067245483 > 10.261380672454834
    nms_enums.eStatsType.Freighter_Fleet_Mine: [("-", 1), ("*", 100)],  # Expedition Mining Ability (+15%) > 1.14999997615814209 > 14.999997615814209

    # endregion

    # region Vehicle

    nms_enums.eStatsType.Vehicle_EngineFuelUse: [(1, "-"), ("*", 100)],  # Fuel Usage (-17%) > 0.9888021945953369 > 1.11978054046631
    nms_enums.eStatsType.Vehicle_EngineTopSpeed: [("-", 1), ("*", 100)],  # Top Speed (+11%) > 1.0145702362060547 > 1.45702362060547
    nms_enums.eStatsType.Vehicle_BoostSpeed: [("*", 100)],  # Boost Power (+55%) > 0.16838529706001282 > 16.838529706001282
    nms_enums.eStatsType.Vehicle_BoostTanks: [("*", 100)],  # Boost Tank Size (+50%) > 0.12285126000642776 > 12.285126000642776
    nms_enums.eStatsType.Vehicle_SubBoostSpeed: [("*", 100)],  # Acceleration (+25%) > 0.11943772435188293 > 11.943772435188293
    nms_enums.eStatsType.Vehicle_LaserDamage: [],  # Mining Laser Power (+43%) > 8.419264793395996
    nms_enums.eStatsType.Vehicle_LaserHeatTime: [(1, "-"), ("*", 100)],   # Mining Laser Efficiency (+17%) > 0.9791018962860107 > 2.089810371398926
    nms_enums.eStatsType.Vehicle_GunDamage: [],  # Damage (+12%) > 5.014753341674805
    nms_enums.eStatsType.Vehicle_GunHeatTime: [(1, "-"), ("*", 100)],  # Weapon Power Efficiency (+17%) > 0.9890878200531006 > 1.09121799468994
    nms_enums.eStatsType.Vehicle_GunRate: [(1, "-"), ("*", 100)],  # Rate of Fire (+9%) > 0.9895480275154114 > 1.04519724845886

    # endregion
}

# endregion

# region Helper


class Counter(object):
    def __init__(self, start=0):
        self.lock = threading.Lock()
        self.start = start
        self.value = start

    def __str__(self) -> str:
        return str(self.value)

    @property
    def is_incremented(self):
        return self.value != self.start

    def increment(self):
        self.lock.acquire()
        try:
            self.value = self.value + 1
        finally:
            self.lock.release()

    def reset(self):
        self.lock.acquire()
        try:
            self.value = self.start
        finally:
            self.lock.release()


def print_struct_fields(struct: ctypes.Structure, level=0):
    l = max(len(f) for f, _ in struct._fields_)
    for field_name, _ in struct._fields_:
        if field_name.startswith("_"):
            continue

        try:
            field = getattr(struct, field_name)

            if isinstance(field, nms_common_structs.cTkDynamicArray):
                logging.debug(f"{(' ' * 4 * level)}{field_name:{l}} >> {field}")
                if len(field):
                    for i, item in enumerate(field.value):
                        logging.debug(f"{(' ' * 4 * level)}{i:{len(field)}}:")
                        print_struct_fields(item, level + 1)
            elif isinstance(field, ctypes.Structure) and str(field).startswith("<"):
                logging.debug(f"{(' ' * 4 * level)}{field_name:{l}}")
                print_struct_fields(field, level + 1)
            else:
                if field_name.startswith("mb"):
                    log_value = f"{bool(field)} ({field})"
                else:
                    log_value = field

                logging.debug(f"{(' ' * 4 * level)}{field_name:{l}} >> {log_value}")
        except Exception as e:
            logging.exception(e)


# decorator to wrap an entire method. useful as exceptions raised in mod methods will not be visible otherwise
def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)

    return wrapper


# endregion

# region Changelog

# 1.0.0 Initial Release
# 1.1.0
#       UP_RBSUIT added incl. a warning when an item is not available in the running game
#       Fixed memory leak thanks to NMS.py version 0.6.5
#       Removed most of the iteration mode code thanks to the fixed leak and replaced with the possibility to run a single items up to entire inventories
#       All required structs are now included in NMS.py itself
#       Use the new executor to execute generation in the background without blocking the game
#       Use a new hook to toggle product and technology and start via button press
#       Taking into account how desirable certain stats and combinations are

# endregion


class Pi(NMSMod):
    __NMSPY_required_version__ = "0.6.7"

    __author__ = "zencq"
    __description__ = "Generate data for all procedural items."
    __version__ = "1.1.0"

    def __init__(self):
        super().__init__()

        self.language = None  # name of column to write the name in, will be set automatically
        self.is_fully_booted = False
        self.is_generation_started = False
        self.product_counter = (Counter(), Counter())   # spawned, finished
        self.product_generation_enabled = True
        self.product_start_time = None
        self.technology_counter = (Counter(), Counter())   # spawned, finished
        self.technology_generation_enabled = True
        self.technology_start_time = None

        # properties for manual configuration
        self.product_manual = []  # set to items of PRODUCT
        self.technology_manual = []  # set to items of TECHNOLOGY. can be any inventory_type, item_id, and item_name

    # read existing file to carry over all previous translations
    @staticmethod
    def read_existing_file(f_name):
        if os.path.isfile(f_name):
            with open(f_name, mode="r", encoding="utf-8", newline="") as f:
                f.readline()  # skip first line with delimiter indicator
                reader = csv.DictReader(f, dialect="excel")
                return list(reader)

        return []

    @staticmethod
    def write_result(f_name, meta, result):
        fieldnames = ["Seed", "Perfection"] + sorted(meta.keys()) + LANGUAGES
        with open(f_name, mode="w", encoding="utf-8", newline="") as f:
            f.write("sep=,\r\n")
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect="excel")
            writer.writeheader()
            writer.writerows(result)

    # region Language

    @hooks.cTkLanguageManagerBase.Load.after
    def language_changed(self, this):
        result = original = map_struct(this, nms_structs.cTkLanguageManagerBase).meRegion
        if original == nms_enums.eLanguageRegion.LR_USEnglish:
            result = nms_enums.eLanguageRegion.LR_English
        if original == nms_enums.eLanguageRegion.LR_LatinAmericanSpanish:
            result = nms_enums.eLanguageRegion.LR_Spanish
        if original > 0x1:  # -1 in total
            result -= 1
        if original > 0xA:  # -2 in total
            result -= 1
        if original > 0xF:  # -3 in total
            result -= 1

        self.language = LANGUAGES[result]

        logging.debug(f">> Pi: Language loaded is {original} > {result} > {self.language}")

    @staticmethod
    def extract_previous_languages(read_rows, seed):
        if seed < len(read_rows):  # just in case read file has less rows than expected
            # add all languages and get previous translations or empty string
            return {
                language: read_rows[seed].get(language, "")
                for language in LANGUAGES
            }

        return {}

    # endregion

    @on_fully_booted
    def enable_generation_on_fully_booted(self):
        self.fully_booted = True
        logging.info(f">> Pi: The game is now fully booted.")

    @on_key_release("d")
    @disable
    def toggle_product(self):
        pass

    @on_key_release("p")
    def toggle_product(self):
        self.product_generation_enabled = not self.product_generation_enabled
        logging.info(f">> Pi: Product generation is now {('enabled' if self.product_generation_enabled else 'disabled')}.")

    @on_key_release("t")
    def toggle_technology(self):
        self.technology_generation_enabled = not self.technology_generation_enabled
        logging.info(f">> Pi: Technology generation is now {('enabled' if self.technology_generation_enabled else 'disabled')}.")

    @on_key_release("space")
    def start_generating(self):
        if not self.fully_booted:
            logging.info(f">> Pi: Please wait until the game is fully booted.")
            return

        if not self.is_generation_started:
            self.is_generation_started = True

            if self.product_generation_enabled:
                logging.info(f">> Pi: Product generation started")
                self.start_generating_procedural_product()
            if self.technology_generation_enabled:
                logging.info(f">> Pi: Technology generation started")
                self.start_generating_procedural_technology()

    # region Product

    def start_generating_procedural_product(self):
        self.product_start_time = datetime.now()

        for item_id in PRODUCT:
            if not self.technology_manual or (item_id in self.product_manual):
                self.product_counter[0].increment()
                nms.executor.submit(self.generate_procedural_product, item_id)

    def generate_procedural_product(self, item_id):
        available = True
        item_name = f"PROC_{item_id}"
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        reality_manager = nms.GcApplication.data.contents.RealityManager
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\Product\\{item_name}.csv"

        read_rows = self.read_existing_file(f_name)

        for seed in range(TOTAL_SEEDS):
            pointer = reality_manager.GenerateProceduralProduct["cGcRealityManager *, const TkID<128> *"](f"{item_name}#{seed:05}".encode("utf-8"))
            try:
                generated = map_struct(pointer, nms_structs.cGcProductData)
            except ValueError:
                available = False
                logging.warning(f"  ! Warning: Product '{item_name}' is not available in your game version.")
                break

            # carry over all previous translations
            row = self.extract_previous_languages(read_rows, seed)

            # add seed and current translation
            row.update({
                self.language: str(generated.macNameLower),  # name for current language
                "Age": int(RE_PRODUCT_AGE.findall(str(generated.macDescription))[0]),
                "Seed": seed,
                "Value": generated.miBaseValue,
            })

            # update to track meta values
            if not meta:
                logging.debug(f"     > Age > {row.get('Age')}")
                logging.debug(f"     > Value > {generated.miBaseValue}")
                meta = [generated.miBaseValue, generated.miBaseValue]
            else:
                meta = [
                    min(meta[0], generated.miBaseValue),
                    max(meta[1], generated.miBaseValue),
                ]

            # add completed row to result
            result.append(row)

        if available:
            # add calculated perfection
            for row in result:
                row.update({
                    "Perfection": 1.0 - (meta[1] - row["Value"]) / (meta[1] - meta[0]),
                })

            logging.debug(f"   > {item_name} > {datetime.now() - item_start_time}")

            self.write_result(f_name, {"Age": None, "Value": None}, result)

        self.product_counter[1].increment()
        self.check_procedural_product_generation_finished()

    def check_procedural_product_generation_finished(self):
        if self.product_counter[0].value == self.product_counter[1].value:
            logging.info(f">> Pi: Product generation finished in {datetime.now() - self.product_start_time}!")
            self.product_counter[0].reset()
            self.product_counter[1].reset()
            if not (self.technology_counter[0].is_incremented or self.technology_counter[1].is_incremented):
                self.is_generation_started = False

    # endregion

    # region Technology

    def start_generating_procedural_technology(self):
        self.technology_start_time = datetime.now()

        for inventory_type, items in TECHNOLOGY.items():
            for item_id, qualities in items.items():
                for quality in qualities:
                    item_name = f"{item_id}{quality}"
                    if not self.technology_manual or any((key in self.technology_manual) for key in [inventory_type, item_id, item_name]):
                        self.technology_counter[0].increment()
                        nms.executor.submit(self.generate_procedural_technology, inventory_type, item_name)

    @try_except
    def generate_procedural_technology(self, inventory_type, item_name):
        available = True
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        number = 0  # maximum number of unique stats per seed
        reality_manager = nms.GcApplication.data.contents.RealityManager
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\{inventory_type}\\{item_name}.csv"

        read_rows = self.read_existing_file(f_name)

        for seed in range(TOTAL_SEEDS):
            pointer = reality_manager.GenerateProceduralTechnology(f"{item_name}#{seed:05}".encode("utf-8"), False)

            try:
                with map_struct_temp(pointer, nms_structs.cGcTechnology) as generated:
                    number = max(number, len(generated.maStatBonuses.value))
                    row = self.extract_previous_languages(read_rows, seed)  # carry over all previous translations

                    # add seed and current translation
                    row.update({
                        self.language: str(generated.macNameLower),  # name for current language
                        "Seed": seed,
                    })

                    # update to track meta values
                    for stat_bonus in generated.maStatBonuses.value:
                        stat = nms_enums.eStatsType(stat_bonus.mStat.meStatsType).name
                        stat_value = row[stat] = self.translate_value(stat_bonus)  # add in-game like value of a stat

                        if stat not in meta:
                            logging.debug(f"     > {stat} > {stat_bonus.mfBonus} > {stat_value}")  # to see how the value looks
                            meta[stat] = [stat_value, stat_value]
                        else:
                            meta[stat] = [
                                min(meta[stat][0], stat_value),
                                max(meta[stat][1], stat_value),
                            ]

                    # add completed row to result
                    result.append(row)
            except ValueError:
                available = False
                logging.warning(f"  ! Warning: Technology '{item_name}' is not available in your game version.")
                break

            if seed % FREE_MEMORY_STEPS == 0:
                # Clear the pending new technologies to free up some memory.
                # Note that this may cause some internal issues in the game, so maybe don't load the game... But maybe not? I dunno!
                reality_manager.PendingNewTechnologies.clear()

        if available:
            weighting = [stat[1] - stat[0] + 1 for stat in meta.values()]  # max - min + 1
            weighting_min = min(weighting)

            # add weighting to each stat
            meta = {key: value + [value[1] - value [0], weighting[i] / weighting_min] for i, (key, value) in enumerate(meta.items())}

            for row in result:
                perfection = []
                weighting_total = 0

                # calculate perfection for each seed
                for stat_name, stat_meta in meta.items():
                    if stat_name not in row:
                        continue

                    stat_value = row[stat_name]
                    weight = stat_meta[3]
                    weighting_total += weight

                    p = 1.0
                    if stat_meta[2] > 0:
                        p -= (stat_meta[1] - stat_value) / stat_meta[2]
                    perfection.append(p * weight)

                # add calculated perfection
                row.update({
                    "Perfection": (sum(perfection) / weighting_total) * (len(perfection) / number),
                })

            logging.info(f"   > {item_name} > {datetime.now() - item_start_time}")

            self.write_result(f_name, meta, result)

        self.technology_counter[1].increment()
        self.check_procedural_technology_generation_finished()

    # translate raw value to look more like in-game
    @staticmethod
    def translate_value(stat_bonus):
        instructions = TRANSLATION.get(str(stat_bonus.mStat), [])
        value = stat_bonus.mfBonus

        for instruction in instructions:
            if isinstance(instruction[0], str):  # operator first (value - 1)
                if instruction[0] == "+":
                    value += instruction[1]

                if instruction[0] == "-":
                    value -= instruction[1]

                if instruction[0] == "*":
                    value *= instruction[1]

                if instruction[0] == "/":
                    value /= instruction[1]
            else:  # operator second (1 - value)
                if instruction[1] == "+":
                    value = instruction[0] + value

                if instruction[1] == "-":
                    value = instruction[0] - value

                if instruction[1] == "*":
                    value = instruction[0] * value

                if instruction[1] == "/":
                    value = instruction[0] / value

        return value

    def check_procedural_technology_generation_finished(self):
        if self.technology_counter[0].value == self.technology_counter[1].value:
            logging.info(f">> Pi: Technology generation finished in {datetime.now() - self.technology_start_time}!")
            self.technology_counter[0].reset()
            self.technology_counter[1].reset()
            if not (self.product_counter[0].is_incremented or self.product_counter[1].is_incremented):
                self.is_generation_started = False

    # endregion
