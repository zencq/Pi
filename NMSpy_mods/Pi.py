# /// script
# dependencies = ["pymhf[gui]>=0.1.16", "nmspy>=147803.1", "pyarrow"]
#
# [tool.pymhf]
# exe = "<path to install dir>/Binaries/NMS.exe"
# start_paused = true
#
# [tool.pymhf.logging]
# window_name_override = "NMS.py: Pi"
# ///

# pyright: reportAssignmentType=false
# pyright: reportMissingImports=false

# built-in
import csv
import ctypes
import importlib
import logging
import os
import pyarrow as pa
import pyarrow.parquet as pq
import re

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__.lower())

# pyMHF
from pymhf import Mod, ModState
from pymhf.core import _internal as pymhf_internal
from pymhf.core.memutils import map_struct
from pymhf.gui import BOOLEAN, STRING, gui_button

# local
try:
    from common.configuration import LANGUAGES, PRODUCT
    from common.decorators import try_except
    from common.objects import Counter
except Exception as e:
    message = f"Error while importing specific version data: {e}"
    logger.critical(message)
    raise e

# dynamically import for selected version
KNOWN_BINARY_HASH = {
    "014f5fd1837e2bd8356669b92109fd3add116137": "4.13",  # (GOG.dev)
    "239fac0224333873c733c4e5b4d9694ea6cc0b41": "5.20",  # (GOG.com)
    "0969a2aa4e7c025bf99d6e9a807da85a9110fbc2": "5.61",  # (GOG.com)
}
try:
    nms_enums = importlib.import_module(f"data.{pymhf_internal.BINARY_HASH}.enums")
    nms_types = importlib.import_module(f"data.{pymhf_internal.BINARY_HASH}.types")
except ImportError as e:
    # TODO replace , with \n with newer Python version
    supported = ", ".join(f"{version} ({sha1})" for sha1, version in KNOWN_BINARY_HASH.items())
    message = f"Executable is not supported. This mod only works with the following GOG.com versions: {supported}"
    logger.critical(message)
    raise e
except Exception as e:
    message = f"Error while importing specific version data: {e}"
    logger.critical(message)
    raise e


# region Configuration

FREE_MEMORY_STEPS = 250  # multiple of it should be TOTAL_SEEDS

PI_ROOT = os.path.realpath(f"{os.path.dirname(__file__)}\\..")  # use Pi root directory as starting point

TOTAL_SEEDS = 100000

TRANSFORM = {
    # region Weapon

    "Weapon_Laser_Damage": [],  # Damage (+???%) > 70.25779724121094
    "Weapon_Laser_Mining_Speed": [(1, "-"), ("*", 100)],  # Mining Speed (+16%) > 0.8384891152381897 > 16.15108847618103
    "Weapon_Laser_HeatTime": [("-", 1), ("*", 100)],  # Heat Dispersion (+41%) > 1.407882571220398 > 40.788257122039795
    "Weapon_Laser_ReloadTime": [(1, "-"), ("*", 100)],  # Overheat Downtime (-15%) > 0.8482741117477417 > 15.17258882522583
    "Weapon_Laser_Drain": [("-", 1), ("*", 100)],  # Fuel Efficiency (+20%) > 1.2000000476837158 > 20.000004768371582
    "Weapon_Laser_ChargeTime": [(1, "-"), ("*", 100)],  # Time to Full Power (-19%) > 0.8105689287185669 > 18.94310712814331
    "Weapon_Projectile_Damage": [],  # Damage (+???%) > 2.270596981048584
    "Weapon_Projectile_Rate": [("-", 1), ("*", 100)],  # Fire Rate (+13%) > 1.13314688205719 > 13.314688205718994
    "Weapon_Projectile_ClipSize": [],  # Clip Size (+12.0) > 12.0
    "Weapon_Projectile_ReloadTime": [(1, "-"), ("*", 100)],  # Reload Time (-6%) > 0.9432281255722046 > 5.677187442779541
    "Weapon_Projectile_MaximumCharge": [],  # Ion Spheres Created (+1.0) > 1.0
    "Weapon_Projectile_BurstCap": [],  # Shots Per Burst (+1.0) > 1.0
    "Weapon_Projectile_BurstCooldown": [(1, "-"), ("*", 100)],  # Burst Cooldown (-19%) > 0.8145824074745178 > 18.541759252548218
    "Weapon_ChargedProjectile_ChargeTime": [(1, "-"), ("*", 100)],  # Charging Speed (-10%) > 0.8965481519699097 > 10.345184803009033
    "Weapon_ChargedProjectile_ExtraSpeed": [],  # Ion Sphere Speed (+22%) > 21.99700164794922
    "Weapon_Grenade_Damage": [],  # Damage (+???%) > 350.14752197265625 > 350.14752197265625
    "Weapon_Grenade_Radius": [("-", 1), ("*", 100)],  # Explosion Radius (+41%) > 1.407882571220398 > 40.788257122039795
    "Weapon_Grenade_Speed": [("*", 100)],  # Projectile Velocity (+272%) > 2.7219414710998535 > 272.19414710998535
    "Weapon_Grenade_Bounce": [],  # Bounce Potential (+???%) > 3.0
    "Weapon_Scan_Radius": [("-", 1), ("*", 100)],  # Scan Radius (+33%) > 1.3270596265792847 > 32.70596265792847
    "Weapon_Scan_Discovery_Creature": [("*", 100)],  # Fauna Analysis Rewards (+6,775%) > 67.75889587402344 > 6775.889587402344
    "Weapon_Scan_Discovery_Flora": [("*", 100)],  # Flora Analysis Rewards (+7,897%) > 78.97901153564453 > 7897.901153564453
    "Weapon_Scan_Discovery_Mineral": [("*", 100)],  # Mineral Analysis Rewards (+9,026%) > 90.26795196533203 > 9026.795196533203
    "Weapon_FireDOT_Duration": [("-", 1), ("*", 100)],  # Impact Fire Duration (+27%) > 1.2693740129470825 > 26.93740129470825

    # endregion

    # region Suit

    "Suit_Armour_Health": [],  # Core Health (+???%) > 20.0
    "Suit_Armour_Shield_Strength": [("*", 100)],  # Shield Strength (+32%) > 0.3216187655925751 > 32.16187655925751
    "Suit_Energy": [("*", 100)],  # Life Support Tanks (+108%) > 1.0757951736450195 > 107.57951736450195
    "Suit_Energy_Regen": [("-", 1), ("*", 100)],  # Solar Panel Power (+73%) > 1.7318912744522095 > 73.18912744522095
    "Suit_Protection_Cold": [],  # Cold Protection (???) > 334.7082214355469
    "Suit_Protection_Heat": [],  # Heat Protection (???) > 334.7082214355469
    "Suit_Protection_Toxic": [],  # Toxic Protection (???) > 334.7082214355469
    "Suit_Protection_Radiation": [],  # Radiation Protection (???) > 334.7082214355469
    "Suit_Underwater": [],  # Oxygen Tank (???) > 159.639404296875
    "Suit_DamageReduce_Cold": [(1, "-"), ("*", 100)],  # Cold Damage Shielding (+19%) > 0.8105689287185669 > 18.94310712814331
    "Suit_DamageReduce_Heat": [(1, "-"), ("*", 100)],  # Heat Damage Shielding (+19%) > 0.8105689287185669 > 18.94310712814331
    "Suit_DamageReduce_Radiation": [(1, "-"), ("*", 100)],  # Radiation Damage Shielding (+19%) > 0.8105689287185669 > 18.94310712814331
    "Suit_DamageReduce_Toxic": [(1, "-"), ("*", 100)],  # Toxic Damage Shielding (+19%) > 0.8105689287185669 > 18.94310712814331
    "Suit_Protection_HeatDrain": [("-", 1), ("*", 100)],  # Heat Resistance (+7%) > 1.0696643590927124 > 6.96643590927124
    "Suit_Protection_ColdDrain": [("-", 1), ("*", 100)],  # Cold Resistance (+3%) > 1.0343537330627441 > 3.435373306274414
    "Suit_Protection_ToxDrain": [("-", 1), ("*", 100)],  # Toxic Resistance (+10%) > 1.0958983898162842 > 9.589838981628418
    "Suit_Protection_RadDrain": [("-", 1), ("*", 100)],  # Radiation Resistance (+2%) > 1.0243568420410156 > 2.4356842041015625
    "Suit_Stamina_Strength": [("*", 100)],  # Sprint Distance (+43%) > 0.431468665599823 > 43.1468665599823
    "Suit_Stamina_Recovery": [("-", 1), ("*", 100)],  # Sprint Recovery Time (+38%) > 1.3798800706863403 > 37.98800706863403
    "Suit_Jetpack_Tank": [("*", 100)],  # Jetpack Tanks (+203%) > 2.0275888442993164 > 202.75888442993164
    "Suit_Jetpack_Drain": [(1, "-"), ("*", 100)],  # Fuel Efficiency (+6%) > 0.9411903619766235 > 5.8809638023376465
    "Suit_Jetpack_Refill": [("-", 1), ("*", 100)],  # Recharge Rate (+15%) > 1.1500355005264282 > 15.003550052642822
    "Suit_Jetpack_Ignition": [("-", 1), ("*", 100)],  # Initial Boost Power (+8%) > 1.0770596265792847 > 7.705962657928467

    # endregion

    # region Freighter

    "Freighter_Hyperdrive_JumpDistance": [],  # Hyperdrive Range (230 ly) > 229.639404296875
    "Freighter_Hyperdrive_JumpsPerCell": [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    "Freighter_Fleet_Speed": [("-", 1), ("*", 100)],  # Expedition Speed (+15%) > 1.149999976158142 > 14.999997615814209
    "Freighter_Fleet_Fuel": [(1, "-"), ("*", 100)],  # Expedition Efficiency (+17%) > 0.8277047276496887 > 17.229527235031128
    "Freighter_Fleet_Combat": [("-", 1), ("*", 100)],  # Expedition Defenses (+15%) > 1.149999976158142 > 14.999997615814209
    "Freighter_Fleet_Trade": [("-", 1), ("*", 100)],  # Expedition Trade Ability (+15%) > 1.149999976158142 > 14.999997615814209
    "Freighter_Fleet_Explore": [("-", 1), ("*", 100)],  # Expedition Scientific Ability (+15%) > 1.149999976158142 > 14.999997615814209
    "Freighter_Fleet_Mine": [("-", 1), ("*", 100)],  # Expedition Mining Ability (+15%) > 1.149999976158142 > 14.999997615814209

    # endregion

    # region Vehicle

    "Vehicle_EngineFuelUse": [(1, "-"), ("*", 100)],  # Fuel Usage (-28%) > 0.7158533930778503 > 28.414660692214966
    "Vehicle_EngineTopSpeed": [("-", 1), ("*", 100)],  # Top Speed (+10%) >  1.100000023841858 > 10.000002384185791
    "Vehicle_BoostSpeed": [("*", 100)],  # Boost Power (+65%) > 0.6525779366493225 > 65.25779366493225
    "Vehicle_BoostTanks": [("*", 100)],  # Boost Tank Size (+25%) > 0.2501475214958191 > 25.01475214958191
    "Vehicle_SubBoostSpeed": [("*", 100)],  # Acceleration (+26%) > 0.26352986693382263 > 26.352986693382263
    "Vehicle_LaserDamage": [],  # Mining Laser Power (+???%) > 36.83852767944336
    "Vehicle_LaserHeatTime": [(1, "-"), ("*", 100)],   # Mining Laser Efficiency (+19%) > 0.8052845001220703 > 19.47154998779297
    "Vehicle_GunDamage": [],  # Damage (+???%) > 36.83852767944336
    "Vehicle_GunHeatTime": [(1, "-"), ("*", 100)],  # Weapon Power Efficiency (+18%) > 0.8241346478462219 > 17.586535215377808
    "Vehicle_GunRate": [(1, "-"), ("*", 100)],  # Rate of Fire (+9%) > 0.9060062170028687 > 9.399378299713135

    # endregion

    # region Ship

    "Ship_Weapons_Guns_Damage": [],  # Damage (+???%) > 6.0000176429748535
    "Ship_Weapons_Guns_Rate": [("-", 1), ("*", 100)],  # Fire Rate (+6%) > 1.0602484941482544 > 6.0248494148254395
    "Ship_Weapons_Guns_HeatTime": [("-", 1), ("*", 100)],  # Heat Dispersion (+6%) > 1.0629289150238037 > 6.292891502380371
    "Ship_Weapons_Lasers_Damage": [],  # Damage (+???%) > 60.02950668334961
    "Ship_Weapons_Lasers_HeatTime": [("-", 1), ("*", 100)],  # Heat Dispersion (+89%) > 1.8867706060409546 > 88.67706060409546
    "Ship_Weapons_ShieldLeech": [],  # Shield recharge on impact (+???%) > 0.27219414710998535
    "Ship_Armour_Shield_Strength": [],  # Shield Strength (+???%) > 0.20000000298023224
    "Ship_Hyperdrive_JumpDistance": [],  # Hyperdrive Range (251 ly) > 250.77337646484375
    "Ship_Hyperdrive_JumpsPerCell": [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    "Ship_Launcher_TakeOffCost": [(1, "-"), ("*", 100)],  # Launch Cost (-20%) > 0.800000011920929 > 19.999998807907104
    "Ship_Launcher_AutoCharge": [],  # Automatic Recharging (Enabled) > 1.0
    "Ship_PulseDrive_MiniJumpFuelSpending": [(1, "-"), ("*", 100)],  # Pulse Drive Fuel Efficiency (+20%) > 0.800000011920929 > 19.999998807907104
    "Ship_Boost": [("-", 1), ("*", 100)],  # Boost (+14%) > 1.1405895948410034 > 14.058959484100342
    "Ship_Maneuverability": [],  # Maneuverability (???) > 1.006500005722046
    "Ship_BoostManeuverability": [("-", 1), ("*", 100)],  # Maneuverability (+10%) > 1.1019220352172852 > 10.192203521728516
    "Ship_Cargo_Slots": [],  # Cargo Slots (+3) > 3.0
    #  TODO verify Ship_Cargo_Slots
    # endregion
}

# endregion

# region Data

RE_PRODUCT_AGE = re.compile("((?=[^,.\n]*\d)[0-9,.]+)")  # may contain thousands separators, but must contain at least one digit

TECHNOLOGY = {
    "Weapon": {
        "UP_BOLT": ["0", "1", "2", "3", "4", "X"],
        "UP_CANN": ["1", "2", "3", "4", "X"],
        "UP_GREN": ["1", "2", "3", "4", "X"],
        "UP_LASER": ["0", "1", "2", "3", "4", "X"],
        "UP_RAIL": ["1", "2", "3", "4", "X"],
        "UP_SCAN": ["0", "1", "2", "3", "4", "X"],
        "UP_SENGUN": [""],
        "UP_SHOT": ["1", "2", "3", "4", "X"],
        "UP_SMG": ["1", "2", "3", "4", "X"],
        "UP_TGREN": ["1", "2", "3", "4", "X"],
    },
    "Suit": {
        "UP_COLD": ["1", "2", "3"],
        "UP_ENGY": ["0", "1", "2", "3", "X"],
        "UP_HAZ": ["0", "X"],
        "UP_HOT": ["1", "2", "3"],
        "UP_JET": ["0", "1", "2", "3", "4", "X"],
        "UP_RAD": ["1", "2", "3"],
        "UP_RBSUIT": [""],
        "UP_SHLD": ["0", "1", "2", "3", "4", "X"],
        "UP_SNSUIT": [""],
        "UP_TOX": ["1", "2", "3"],
        "UP_UNW": ["1", "2", "3"],
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
    "Exocraft": {
        "UP_BOOST": ["1", "2", "3", "4"],
        "UP_EXENG": ["1", "2", "3", "4"],
        "UP_EXGUN": ["1", "2", "3", "4"],
        "UP_EXLAS": ["1", "2", "3", "4"],
    },
    "Submarine": {
        "UP_EXSUB": ["1", "2", "3", "4"],
        "UP_SUGUN": ["1", "2", "3", "4"],
    },
    "Mech": {
        "UP_MCENG": ["2", "3", "4"],
        "UP_MCGUN": ["2", "3", "4"],
        "UP_MCLAS": ["2", "3", "4"],
        "UP_MFIRE": ["2", "3", "4"],
    },
    "AlienShip": {
        "UA_HYP": ["1", "2", "3", "4"],
        "UA_LAUN": ["1", "2", "3", "4"],
        "UA_PULSE": ["1", "2", "3", "4"],
        "UA_S_SHL": ["1", "2", "3", "4"],
        "UA_SGUN": ["1", "2", "3", "4"],
        "UA_SLASR": ["1", "2", "3", "4"],
    },
    "Ship": {
        "UP_HYP": ["0", "1", "2", "3", "4", "X"],
        "UP_LAUN": ["0", "1", "2", "3", "4", "X"],
        "UP_PULSE": ["0", "1", "2", "3", "4", "X"],
        "UP_S_SHL": ["0", "1", "2", "3", "4", "X"],
        "UP_SBLOB": ["1", "2", "3", "4", "X"],
        "UP_SGUN": ["0", "1", "2", "3", "4", "X"],
        "UP_SLASR": ["1", "2", "3", "4", "X"],
        "UP_SMINI": ["1", "2", "3", "4", "X"],
        "UP_SSHOT": ["1", "2", "3", "4", "X"],
    },
    "Corvette": {
        "CV_FIT": ["1", "2", "3", "4"],
        "CV_HYP": ["2", "3"],
        "CV_INV": ["1", "2", "3", "4"],
        "CV_LAUN": ["2", "3"],
        "CV_PULSE": ["2", "3"],
        "CV_S_SHL": ["2", "3"],
        "CV_SBLOB": ["3"],
        "CV_SCI": ["1", "2", "3", "4"],
        "CV_SGUN": ["3"],
        "CV_SLASR": ["3"],
        "CV_SMINI": ["3"],
        "CV_SROC": ["3"],
        "CV_SSHOT": ["3"],
        "CV_TRA": ["1", "2", "3", "4"],
    },
}

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

# 1.1.1
#       Fixed the transformation of raw values that was not triggered due to a mismatch of the data type
#       Added missing transformation for Weapon_Grenade_Radius and Weapon_Grenade_Speed

# 1.2.0
#       Added new items from game version 5.00, 5.10, and 5.50
#       Added latin american spanish
#       Changed chinese language codes
#       Fixed a bug when using product_manual
#       Updated to NMS.py 0.7.1 that uses pyMHF 0.1.8 as backend
#       Additionally add Parquet files as output for better programmatic processing

# 1.2.1
#       Updated pyMHF to 0.1.11-dev+7bafefa83f425590c1757b349213432fe0495a80

# 1.3.0
#       Updated pyMHF to 0.1.16
#       Updated NMS.py to 147803.1
#       Added new items from game version 6.00


# TODO: add settlement perks
# TkID<128> *__fastcall cGcSettlementStateManager::GenerateProcPerkId(cGcSettlementStateManager *this, TkID<128> *result, const TkID<128> *lBasePerkId, const unsigned __int64 lBaseSeedValue)
# cGcSettlementPerkUsefulData *__fastcall cGcFrontendPageSettlementJudgement::ExtractKeyPerkData(cGcFrontendPageSettlementJudgement *this, cGcSettlementPerkUsefulData *result, const TkID<128> lPerkId)
#   PROC_BAR#12345



# endregion


@dataclass
class PiModState(ModState):
    # TODO make executor work again
    # does not work at the moment due to "access violation reading" (a multi threading issue)
    # executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="Pi_Executor")

    language = None  # name of column to write the name in, will be set automatically
    reality_manager = None

    is_fully_booted : bool = False
    is_generation_started : bool = False

    product_counter = (Counter(), Counter())  # spawned, finished
    product_counter_total : int = 0
    product_generation_enabled : bool = True
    product_manual : list = None
    product_start_time : datetime = None

    technology_counter = (Counter(), Counter())  # spawned, finished
    technology_counter_total : int = 0
    technology_generation_enabled : bool = True
    technology_manual : list = None
    technology_start_time : datetime = None


class PiMod(Mod):
    __NMSPY_required_version__ = "146194.0"

    __author__ = "zencq"
    __description__ = "Generate data for all procedural items."
    __version__ = "1.3.0"

    # region Property

    state = PiModState()  # not in __init__ to survive reloading

    @property
    def is_ready(self):
        return all([self.state.language, self.state.reality_manager])

    # endregion

    # region Property (GUI)

    @property
    @BOOLEAN(label="Products")
    def product_generation_enabled(self):
        return self.state.product_generation_enabled

    @product_generation_enabled.setter
    def product_generation_enabled(self, value: bool):
        self.state.product_generation_enabled = value

    @property
    @STRING(label="Products (overwrite)", hint="any product")
    def product_manual(self):
        return ",".join(self.state.product_manual or [])

    @product_manual.setter
    def product_manual(self, value: str):
        self.state.product_manual = [item.strip() for item in value.upper().split(",") if item.strip()]

    @property
    @BOOLEAN(label="Technologies")
    def technology_generation_enabled(self):
        return self.state.technology_generation_enabled

    @technology_generation_enabled.setter
    def technology_generation_enabled(self, value: bool):
        self.state.technology_generation_enabled = value

    @property
    @STRING(label="Technologies (overwrite)", hint="any inventory_type, item_id, and item_name")
    def technology_manual(self):
        return ",".join(self.state.technology_manual or [])

    @technology_manual.setter
    def technology_manual(self, value: str):
        self.state.technology_manual = [item.strip() for item in value.upper().split(",") if item.strip()]

    # endregion

    # region Construct

    @nms_types.cTkLanguageManagerBase.Load.after
    def language_manager_load_after(self, this: ctypes._Pointer, *args):  # args as it does not matter and to avoid multiple signatures
        logger.debug(f"hook_language_manager_load_after -> {this}")

        language_manager = map_struct(this, nms_types.cTkLanguageManagerBase)
        result = original = language_manager.Region

        # treat LR_English and LR_USEnglish as one
        if original == nms_enums.eLanguageRegion.LR_USEnglish:
            result = nms_enums.eLanguageRegion.LR_English
        if original > nms_enums.eLanguageRegion.LR_USEnglish:
            result -= 1
        # skip LR_TencentChinese
        if original > nms_enums.eLanguageRegion.LR_TencentChinese:
            result -= 1

        if self.state.language != LANGUAGES[result]:
            self.state.language = LANGUAGES[result]
            logger.info(f"Language is now '{self.state.language[6:-1]}'")

        self.log_ready_message()

    @nms_types.cGcRealityManager.Construct.after
    def reality_manager_construct_after(self, this):
        logger.debug(f"hook_reality_manager_construct_after -> {this}")

        self.state.reality_manager = map_struct(this, nms_types.cGcRealityManager)
        self.log_ready_message()

    def log_ready_message(self):
        if self.is_ready:
            logger.info(f"All required objects have been constructed. You can now start generating.")

    # endregion

    @gui_button("Start Generating")
    @try_except
    def start_generating(self):
        if not all([self.state.language, self.state.reality_manager]):
            logger.warning(f"Not all required objects have been constructed yet. You may forgot to start the binary or have to wait a few seconds longer until you get the message that everything is ready.")
            return

        if self.state.is_generation_started:
            logger.warning(f"Please wait until the currently running generation has finished...")
            return

        self.state.is_generation_started = True

        if self.product_generation_enabled:
            self.start_generating_procedural_product()
        if self.technology_generation_enabled:
            self.start_generating_procedural_technology()

        # if self.settlement_perk_generation_enabled:
        #     self.start_generating_procedural_technology()

        self.state.is_generation_started = False

    @staticmethod
    def extract_previous_languages(read_rows, seed):
        if seed < len(read_rows):  # just in case read file has less rows than expected
            # add all languages and get previous translations or empty string
            return {
                language: read_rows[seed].get(language, "") or ("zh-Hans" in language and read_rows[seed].get("Name (zh-CN)", "")) or ("zh-Hant" in language and read_rows[seed].get("Name (zh-TW)", "")) or ""
                for language in LANGUAGES
            }

        return {}

    # region Read/Write

    # read existing file to carry over all previous translations
    @staticmethod
    def read_existing_file(f_name: str) -> list:
        if os.path.isfile(f"{f_name}.csv"):
            with open(f"{f_name}.csv", mode="r", encoding="utf-8", newline="") as f:
                f.readline()  # skip first line with delimiter indicator
                reader = csv.DictReader(f, dialect="excel")
                return list(reader)

        return []

    @staticmethod
    def write_result(f_name: str, meta: dict, result : list[dict]):
        fieldnames = ["Seed", "Perfection"] + sorted(meta.keys()) + LANGUAGES

        # CSV
        with open(f"{f_name}.csv", mode="w", encoding="utf-8", newline="") as f:
            f.write("sep=,\r\n")
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect="excel")
            writer.writeheader()
            writer.writerows(result)

        # Parquet
        schema = pa.schema(
            [pa.field('Seed', pa.int32(), nullable=False), pa.field('Perfection', pa.float64(), nullable=False)]
            +
            [pa.field(column, pa.float64()) for column in meta.keys()]
            +
            [pa.field(language, pa.string(), nullable=False) for language in LANGUAGES]
        )
        table = pa.Table.from_pylist(result, schema=schema)
        with pq.ParquetWriter(f"{f_name}.parquet", schema) as writer:
            try:
                writer.write_table(table)
            except pa.lib.ArrowInvalid as e:  # pyright: ignore[reportAttributeAccessIssue]
                message = str(e)
                # also stored in CSV and recovered from there until all languages are set
                if not (message.startswith("Column 'Name (") and message.endswith(")' is declared non-nullable but contains nulls")):
                    raise e

    # endregion

    # region Product

    @try_except
    def start_generating_procedural_product(self):
        if self.state.product_manual:
            products = [
                ("Product", item_name)
                for item in self.state.product_manual
                if (item_name := f"PROC_{item}" if not item.startswith("PROC_") else item) in PRODUCT
            ]
        else:
            products = PRODUCT

        self.state.product_counter_total = len(products)
        self.state.product_start_time = datetime.now()

        logger.info(f"Generation for {self.state.product_counter_total} {'PRODUCT' if self.state.product_counter_total == 1 else 'PRODUCTS'} started...")

        for category, item_name in products:
            self.state.product_counter[0].increment()
            # TODO make executor work again
            # self.state.executor.submit(self.generate_procedural_product, item_name)  # ! access violation reading 0x0000000000000018
            self.generate_procedural_product(category, item_name)

    @try_except
    def generate_procedural_product(self, category, item_name):
        available = True
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\{category}\\{item_name}"

        read_rows = self.read_existing_file(f_name)

        for seed in range(TOTAL_SEEDS):
            pointer = self.state.reality_manager.GenerateProceduralProduct(f"{item_name}#{seed:05}".encode("utf-8"))
            try:
                generated = map_struct(pointer, nms_types.cGcProductData)
            except ValueError:
                available = False
                logger.warning(f"! {item_name} > Product not available in your game version.")
                break

            # carry over all previous translations
            row = self.extract_previous_languages(read_rows, seed)

            # add seed and current translation
            row.update({
                self.state.language: str(generated.NameLower).strip(),  # name for current language
                "Age": self._get_age(generated.Description),
                "Seed": seed,
                "Value": generated.BaseValue,
            })

            # TODO: remove when it got proper name generation
            # currently only gets a template name like "%FOSSILADJ% %FOSSILANIMAL% %FOSSILPART%" which do not add any value
            if item_name == "PROC_EXH":
                row = {
                    key: "" if key.startswith("Name (") else value
                    for key, value in row.items()
                }

            # update to track meta values
            if not meta:
                logger.debug(f"  > Age > {row.get('Age')}")
                logger.debug(f"  > Value > {generated.BaseValue}")
                meta = [generated.BaseValue, generated.BaseValue]
            else:
                meta = [
                    min(meta[0], generated.BaseValue),
                    max(meta[1], generated.BaseValue),
                ]

            # add completed row to result
            result.append(row)

        if available:
            # add calculated perfection
            for row in result:
                row.update({
                    "Perfection": 1.0 - (meta[1] - row["Value"]) / (meta[1] - meta[0]),
                })

            self.write_result(f_name, {"Age": None, "Value": None}, result)

            logger.info(f"> {item_name} > {datetime.now() - item_start_time}")

        self.state.product_counter[1].increment()
        self.check_procedural_product_generation_finished()

    @staticmethod
    def _get_age(description) -> int:
        groups = RE_PRODUCT_AGE.findall(str(description))
        age = re.sub("[^0-9]", "", groups[0])
        return int(age)

    def check_procedural_product_generation_finished(self):
        if self.state.product_counter[0].value == self.state.product_counter[1].value == self.state.product_counter_total:
            logger.info(f"PRODUCT generation finished in {datetime.now() - self.state.product_start_time}!")
            self.state.product_counter[0].reset()
            self.state.product_counter[1].reset()

    # endregion

    # region Technology

    @try_except
    def start_generating_procedural_technology(self):
        if self.state.technology_manual:
            technologies = [
                (inventory_type, item_name)
                for inventory_type, items in TECHNOLOGY.items()
                for item_id, qualities in items.items()
                for quality in qualities
                if (item_name := f"{item_id}{quality}") and any((key in self.state.technology_manual) for key in [inventory_type.upper(), item_id, item_name])
            ]
        else:
            technologies = [f"{item_id}{quality}" for items in TECHNOLOGY.values() for item_id, qualities in items.items() for quality in qualities]

        self.state.technology_counter_total = len(technologies)
        self.state.technology_start_time = datetime.now()

        logger.info(f"Generation for {self.state.technology_counter_total} {'TECHNOLOGY' if self.state.technology_counter_total == 1 else 'TECHNOLOGIES'} started...")

        for inventory_type, item_name in technologies:
            self.state.technology_counter[0].increment()
            # TODO make executor work again
            # self.state.executor.submit(self.generate_procedural_technology, inventory_type, item_name)  # ! access violation reading
            self.generate_procedural_technology(inventory_type, item_name)

    @try_except
    def generate_procedural_technology(self, category, item_name):
        available = True
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        number = 0  # maximum number of unique stats per seed
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\{category}\\{item_name}"

        read_rows = self.read_existing_file(f_name)
        for seed in range(TOTAL_SEEDS):
            pointer = self.state.reality_manager.GenerateProceduralTechnology(f"{item_name}#{seed:05}".encode("utf-8"), False)
            try:
                technology = map_struct(pointer, nms_types.cGcTechnology)
            except ValueError:
                available = False
                logger.warning(f"! {item_name} > Technology not available in your game version.")  # one space less as warning moves it one to the right
                break

            number = max(number, len(technology.StatBonuses))
            row = self.extract_previous_languages(read_rows, seed)  # carry over all previous translations

            # add seed and current translation
            row.update({
                self.state.language: str(technology.NameLower).strip(),  # name for current language
                "Seed": seed,
            })

            # update to track meta values
            for stat_bonus in technology.StatBonuses:
                stat_name = stat_bonus.Stat.StatsType.name
                stat_value = row[stat_name] = self._transform_value(stat_name, stat_bonus.Bonus)  # add in-game like value of a stat

                if stat_name not in meta:
                    logger.debug(f"  > {stat_name} > {stat_bonus.Bonus} > {stat_value}")  # to see how the value looks
                    meta[stat_name] = [stat_value, stat_value]
                else:
                    meta[stat_name] = [
                        min(meta[stat_name][0], stat_value),
                        max(meta[stat_name][1], stat_value),
                    ]

            # add completed row to result
            result.append(row)

            if seed % FREE_MEMORY_STEPS == 0:
                # Clear the pending new technologies to free up some memory.
                # Note that this may cause some internal issues in the game, so maybe don't load the game... But maybe not? I dunno!
                self.state.reality_manager.PendingNewTechnologies.clear()

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

            self.write_result(f_name, meta, result)

            logger.info(f"> {item_name} > {datetime.now() - item_start_time}")

        self.state.technology_counter[1].increment()
        self.check_procedural_technology_generation_finished()

    # transform raw value to look more like in-game
    @staticmethod
    def _transform_value(stat, bonus):
        if stat not in TRANSFORM:
            logger.warning(f"  > not in TRANSFORM > {stat} > {bonus}")

        for instruction in TRANSFORM.get(stat, []):
            if isinstance(instruction[0], str):  # operator first (bonus - 1)
                if instruction[0] == "+":
                    bonus += instruction[1]

                if instruction[0] == "-":
                    bonus -= instruction[1]

                if instruction[0] == "*":
                    bonus *= instruction[1]

                if instruction[0] == "/":
                    bonus /= instruction[1]
            else:  # operator second (1 - bonus)
                if instruction[1] == "+":
                    bonus = instruction[0] + bonus

                if instruction[1] == "-":
                    bonus = instruction[0] - bonus

                if instruction[1] == "*":
                    bonus = instruction[0] * bonus

                if instruction[1] == "/":
                    bonus = instruction[0] / bonus

        return bonus

    def check_procedural_technology_generation_finished(self):
        if self.state.technology_counter[0].value == self.state.technology_counter[1].value == self.state.technology_counter_total:
            logger.info(f"TECHNOLOGY generation finished in {datetime.now() - self.state.technology_start_time}!")
            self.state.technology_counter[0].reset()
            self.state.technology_counter[1].reset()

    # endregion
