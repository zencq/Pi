import csv
import ctypes
import logging
import os
import re

from datetime import datetime

from nmspy.data import (
    common,
    enums as nms_enums,
    function_hooks as hooks,
)
from nmspy.hooking import disable, one_shot
from nmspy.memutils import map_struct
from nmspy.mod_loader import NMSMod
from nmspy.utils import safe_assign_enum


# region Data

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

PROGRESS_STEPS = 25000  # multiple of it should equal TOTAL_SEEDS

RE_PRODUCT_AGE = re.compile("([0-9]+)")

TECHNOLOGY = {
    "AlienShip": {
        "UA_HYP": ["1", "2", "3" , "4"],
        "UA_LAUN": ["1", "2", "3" , "4"],
        "UA_PULSE": ["1", "2", "3" , "4"],
        "UA_S_SHL": ["1", "2", "3" , "4"],
        "UA_SGUN": ["1", "2", "3" , "4"],
        "UA_SLASR": ["1", "2", "3" , "4"],
    },
    "Exocraft": {
        "UP_BOOST": ["1", "2", "3" , "4"],
        "UP_EXENG": ["1", "2", "3" , "4"],
        "UP_EXGUN": ["1", "2", "3" , "4"],
        "UP_EXLAS": ["1", "2", "3" , "4"],
    },
    "Freighter": {
        "UP_FRCOM": ["1", "2", "3" , "4"],
        "UP_FREXP": ["1", "2", "3" , "4"],
        "UP_FRFUE": ["1", "2", "3" , "4"],
        "UP_FRHYP": ["1", "2", "3" , "4"],
        "UP_FRMIN": ["1", "2", "3" , "4"],
        "UP_FRSPE": ["1", "2", "3" , "4"],
        "UP_FRTRA": ["1", "2", "3" , "4"],
    },
    "Mech": {
        "UP_MCENG": ["2", "3" , "4"],
        "UP_MCGUN": ["2", "3" , "4"],
        "UP_MCLAS": ["2", "3" , "4"],
    },
    "Ship": {
        "UP_HYP": ["1", "2", "3" , "4", "X"],
        "UP_LAUN": ["1", "2", "3" , "4", "X"],
        "UP_PULSE": ["1", "2", "3" , "4", "X"],
        "UP_S_SHL": ["1", "2", "3" , "4", "X"],
        "UP_SBLOB": ["1", "2", "3" , "4", "X"],
        "UP_SGUN": ["1", "2", "3" , "4", "X"],
        "UP_SLASR": ["1", "2", "3" , "4", "X"],
        "UP_SMINI": ["1", "2", "3" , "4", "X"],
        "UP_SSHOT": ["1", "2", "3" , "4", "X"],
    },
    "Submarine": {
        "UP_EXSUB": ["1", "2", "3" , "4"],
        "UP_SUGUN": ["1", "2", "3" , "4"],
    },
    "Suit": {
        "UP_COLD": ["1", "2", "3"],
        "UP_ENGY": ["1", "2", "3" , "X"],
        "UP_HAZ": ["X"],
        "UP_HOT": ["1", "2", "3"],
        "UP_JET": ["1", "2", "3" , "4", "X"],
        "UP_RAD": ["1", "2", "3"],
        "UP_SHLD": ["1", "2", "3" , "4", "X"],
        "UP_SNSUIT": [""],
        "UP_TOX": ["1", "2", "3"],
        "UP_UNW": ["1", "2", "3"],
    },
    "Weapon": {
        "UP_BOLT": ["1", "2", "3" , "4", "X"],
        "UP_CANN": ["1", "2", "3" , "4", "X"],
        "UP_GREN": ["1", "2", "3" , "4", "X"],
        "UP_LASER": ["1", "2", "3" , "4", "X"],
        "UP_RAIL": ["1", "2", "3" , "4", "X"],
        "UP_SCAN": ["1", "2", "3" , "4", "X"],
        "UP_SENGUN": [""],
        "UP_SHOT": ["1", "2", "3" , "4", "X"],
        "UP_SMG": ["1", "2", "3" , "4", "X"],
        "UP_TGREN": ["1", "2", "3" , "4", "X"],
    },
}
TECHNOLOGY_ITEMS_LIST = list(TECHNOLOGY.items())

TOTAL_SEEDS = 100000

TRANSLATION = {
    # region Weapon

    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_Damage): [],  # Damage (+4%) > 36.83852767944336
    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_Mining_Speed): [(1, "-"), ("*", 100)],  # Mining Speed (+17%) > 0.8384891152381897 > 16.15108847618103
    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_HeatTime): [("-", 1), ("*", 100)],  # Heat Dispersion (+46%) > 1.407882571220398 > 40.788257122039795
    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_ReloadTime): [(1, "-"), ("*", 100)],  # Overheat Downtime (-16%) > 0.8482741117477417 > 15.17258882522583
    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_Drain): [("-", 1), ("*", 100)],  # Fuel Efficiency (+21%) > 1.2000000476837158 > 20.000004768371582
    str(nms_enums.eStatsType.EStatsType_Weapon_Laser_ChargeTime): [(1, "-"), ("*", 100)],  # Time to Full Power (-20%) > 0.9363773465156555 > 6.36226534843445
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_Damage): [],  # Damage (+1%) > 3.270596981048584
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_Rate): [("-", 1), ("*", 100)],  # Fire Rate (+11%) > 1.13314688205719 > 13.314688205718994
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_ClipSize): [],  # Clip Size (+8.0) > 8.0
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_ReloadTime): [(1, "-"), ("*", 100)],  # Reload Time (-15%) > 0.8999865055084229 > 10.001349449157715
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_MaximumCharge): [],  # Ion Spheres Created (+1.0) > 1.0
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_BurstCap): [],  # Shots Per Burst (+1.3) > 1.1662184000015259
    str(nms_enums.eStatsType.EStatsType_Weapon_Projectile_BurstCooldown): [(1, "-"), ("*", 100)],  # Burst Cooldown (-6%) > 0.8500000238418579 > 14.999997615814209
    str(nms_enums.eStatsType.EStatsType_Weapon_ChargedProjectile_ChargeTime): [(1, "-"), ("*", 100)],  # Charging Speed (-22%) > 0.76045161485672 > 23.954838514328003
    str(nms_enums.eStatsType.EStatsType_Weapon_ChargedProjectile_ExtraSpeed): [],  # Ion Sphere Speed (+12%) > 12.988007545471191
    str(nms_enums.eStatsType.EStatsType_Weapon_Grenade_Damage): [],  # Damage (+38%) > 116.51052856445312
    str(nms_enums.eStatsType.EStatsType_Weapon_Grenade_Radius): [],  # Explosion Radius (+49%) > 1.1039005517959595
    str(nms_enums.eStatsType.EStatsType_Weapon_Grenade_Speed): [],  # Projectile Velocity (+103%) > 2.7219414710998535
    str(nms_enums.eStatsType.EStatsType_Weapon_Grenade_Bounce): [],  # Bounce Potential (+33%) > 1.0
    str(nms_enums.eStatsType.EStatsType_Weapon_Scan_Radius): [("-", 1), ("*", 100)],  # Scan Radius (+38%) > 1.0582551956176758 >
    str(nms_enums.eStatsType.EStatsType_Weapon_Scan_Discovery_Creature): [("*", 100)],  # Fauna Analysis Rewards (+5,071%) > 10.788254737854004 > 1078.8254737854004
    str(nms_enums.eStatsType.EStatsType_Weapon_Scan_Discovery_Flora): [("*", 100)],  # Flora Analysis Rewards (+8,220%) > 10.094901084899902 > 1009.4901084899902
    str(nms_enums.eStatsType.EStatsType_Weapon_Scan_Discovery_Mineral): [("*", 100)],  # Mineral Analysis Rewards (+7,467%) > 17.21941566467285 > 1721.9415664672852

    # endregion

    # region Suit

    str(nms_enums.eStatsType.EStatsType_Suit_Armour_Health): [],  # Core Health (+33%) > 20.0
    str(nms_enums.eStatsType.EStatsType_Suit_Armour_Shield_Strength): [("*", 100)],  # Shield Strength (+31%) > 0.13419264554977417 > 13.419264554977417
    str(nms_enums.eStatsType.EStatsType_Suit_Energy): [("*", 100)],  # Life Support Tanks (+84%) > 0.1525779366493225 > 15.257793664932251
    str(nms_enums.eStatsType.EStatsType_Suit_Energy_Regen): [("-", 1), ("*", 100)],  # Solar Panel Power (+26%) > 1.0146995782852173 > 1.4699578285217285
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_Cold): [],  # Cold Protection (?) > 230.13558959960938
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_Heat): [],  # Heat Protection (?) > 230.13558959960938
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_Toxic): [],  # Toxic Protection (?) > 230.13558959960938
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_Radiation): [],  # Radiation Protection (?) > 230.13558959960938
    str(nms_enums.eStatsType.EStatsType_Suit_Underwater): [],  # Oxygen Tank (?) > 66.08882904052734
    str(nms_enums.eStatsType.EStatsType_Suit_DamageReduce_Cold): [(1, "-"), ("*", 100)],  # Cold Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    str(nms_enums.eStatsType.EStatsType_Suit_DamageReduce_Heat): [(1, "-"), ("*", 100)],  # Heat Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    str(nms_enums.eStatsType.EStatsType_Suit_DamageReduce_Radiation): [(1, "-"), ("*", 100)],  # Radiation Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    str(nms_enums.eStatsType.EStatsType_Suit_DamageReduce_Toxic): [(1, "-"), ("*", 100)],  # Toxic Damage Shielding (?) > 0.9542275667190552 > 4.577243328094482
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_HeatDrain): [("-", 1), ("*", 100)],  # Heat Resistance (+4%) > 1.0696643590927124 > 6.96643590927124
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_ColdDrain): [("-", 1), ("*", 100)],  # Cold Resistance (+6%) > 1.0343537330627441 > 3.435373306274414
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_ToxDrain): [("-", 1), ("*", 100)],  # Toxic Resistance (+2%) > 1.0958983898162842 > 9.589838981628418
    str(nms_enums.eStatsType.EStatsType_Suit_Protection_RadDrain): [("-", 1), ("*", 100)],  # Radiation Resistance (+2%) > 1.0243568420410156 > 2.4356842041015625
    str(nms_enums.eStatsType.EStatsType_Suit_Stamina_Strength): [("*", 100)],  # Sprint Distance (+31%) > 0.1399400383234024 > 13.99400383234024
    str(nms_enums.eStatsType.EStatsType_Suit_Stamina_Recovery): [("-", 1), ("*", 100)],  # Sprint Recovery Time (+31%) > 1.0165899991989136 > 1.6589999198913574
    str(nms_enums.eStatsType.EStatsType_Suit_Jetpack_Tank): [("*", 100)],  # Jetpack Tanks (+217%) > 2.0275888442993164 > 202.75888442993164
    str(nms_enums.eStatsType.EStatsType_Suit_Jetpack_Drain): [(1, "-"), ("*", 100)],  # Fuel Efficiency (+16%) > 0.9013239741325378 > 9.867602586746216
    str(nms_enums.eStatsType.EStatsType_Suit_Jetpack_Refill): [("-", 1), ("*", 100)],  # Recharge Rate (+6%) > 1.011878252029419 > 1.1878252029418945
    str(nms_enums.eStatsType.EStatsType_Suit_Jetpack_Ignition): [("-", 1), ("*", 100)],  # Initial Boost Power (+15%) > 1.016648769378662 > 1.6648769378662

    # endregion

    # region Ship

    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_Guns_Damage): [],  # Damage (+6%) > 20.023605346679688
    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_Guns_Rate): [("-", 1), ("*", 100)],  # Fire Rate (+3%) > 1.0210000276565552 > 2.1000027656555176
    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_Guns_HeatTime): [("-", 1), ("*", 100)],  # Heat Dispersion (+3%) > 1.0299999713897705 > 2.999997138977051
    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_Lasers_Damage): [],  # Damage (+25%) > 60.78825378417969
    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_Lasers_HeatTime): [("-", 1), ("*", 100)],  # Heat Dispersion (+63%) > 1.7505900859832764 > 75.05900859832764
    str(nms_enums.eStatsType.EStatsType_Ship_Weapons_ShieldLeech): [],  # Shield recharge on impact (+105%) > 0.27219414710998535
    str(nms_enums.eStatsType.EStatsType_Ship_Armour_Shield_Strength): [],  # Shield Strength (+30%) > 0.20000000298023224
    str(nms_enums.eStatsType.EStatsType_Ship_Hyperdrive_JumpDistance): [],  # Hyperdrive Range (221 ly) > 250.77337646484375
    str(nms_enums.eStatsType.EStatsType_Ship_Hyperdrive_JumpsPerCell): [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    str(nms_enums.eStatsType.EStatsType_Ship_Launcher_TakeOffCost): [(1, "-"), ("*", 100)],  # Launch Cost (-20%) > 0.800000011920929 > 19.999998807907104
    str(nms_enums.eStatsType.EStatsType_Ship_Launcher_AutoCharge): [],  # Automatic Recharging (Enabled) > 1.0
    str(nms_enums.eStatsType.EStatsType_Ship_PulseDrive_MiniJumpFuelSpending): [(1, "-"), ("*", 100)],  # Pulse Drive Fuel Efficiency (+20%) > 0.800000011920929 > 19.999998807907104
    str(nms_enums.eStatsType.EStatsType_Ship_Boost): [("-", 1), ("*", 100)],  # Boost (+14%) > 1.1405895948410034 > 14.058959484100342
    str(nms_enums.eStatsType.EStatsType_Ship_Maneuverability): [],  # Maneuverability (?) > 1.006500005722046
    str(nms_enums.eStatsType.EStatsType_Ship_BoostManeuverability): [("-", 1), ("*", 100)],  # Maneuverability (+17%) > 1.1019220352172852 > 10.192203521728516

    # endregion

    # region Freighter

    str(nms_enums.eStatsType.EStatsType_Freighter_Hyperdrive_JumpDistance): [],  # Hyperdrive Range (209 ly) > 53.26720428466797
    str(nms_enums.eStatsType.EStatsType_Freighter_Hyperdrive_JumpsPerCell): [("*", 100)],  # Warp Cell Efficiency (+100%) > 1.0 > 100.0
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Speed): [("-", 1), ("*", 100)],  # Expedition Speed (+15%) > 1.0126137733459473 > 1.2613773345947266
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Fuel): [(1, "-"), ("*", 100)],  # Expedition Efficiency (+20%) > 0.9721637964248657 >
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Combat): [("-", 1), ("*", 100)],  # # Expedition Defenses (+15%) > 1.0126137733459473 > 1.26137733459473
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Trade): [("-", 1), ("*", 100)],  # Expedition Trade Ability (+15%) > 1.0126137733459473 > 1.2613773345947266
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Explore): [("-", 1), ("*", 100)],  # Expedition Scientific Ability (+15%) > 1.1026138067245483 > 10.261380672454834
    str(nms_enums.eStatsType.EStatsType_Freighter_Fleet_Mine): [("-", 1), ("*", 100)],  # Expedition Mining Ability (+15%) > 1.14999997615814209 > 14.999997615814209

    # endregion

    # region Vehicle

    str(nms_enums.eStatsType.EStatsType_Vehicle_EngineFuelUse): [(1, "-"), ("*", 100)],  # Fuel Usage (-17%) > 0.9888021945953369 > 1.11978054046631
    str(nms_enums.eStatsType.EStatsType_Vehicle_EngineTopSpeed): [("-", 1), ("*", 100)],  # Top Speed (+11%) > 1.0145702362060547 > 1.45702362060547
    str(nms_enums.eStatsType.EStatsType_Vehicle_BoostSpeed): [("*", 100)],  # Boost Power (+55%) > 0.16838529706001282 > 16.838529706001282
    str(nms_enums.eStatsType.EStatsType_Vehicle_BoostTanks): [("*", 100)],  # Boost Tank Size (+50%) > 0.12285126000642776 > 12.285126000642776
    str(nms_enums.eStatsType.EStatsType_Vehicle_SubBoostSpeed): [("*", 100)],  # Acceleration (+25%) > 0.11943772435188293 > 11.943772435188293
    str(nms_enums.eStatsType.EStatsType_Vehicle_LaserDamage): [],  # Mining Laser Power (+43%) > 8.419264793395996
    str(nms_enums.eStatsType.EStatsType_Vehicle_LaserHeatTime): [(1, "-"), ("*", 100)],   # Mining Laser Efficiency (+17%) > 0.9791018962860107 > 2.089810371398926
    str(nms_enums.eStatsType.EStatsType_Vehicle_GunDamage): [],  # Damage (+12%) > 5.014753341674805
    str(nms_enums.eStatsType.EStatsType_Vehicle_GunHeatTime): [(1, "-"), ("*", 100)],  # Weapon Power Efficiency (+17%) > 0.9890878200531006 > 1.09121799468994
    str(nms_enums.eStatsType.EStatsType_Vehicle_GunRate): [(1, "-"), ("*", 100)],  # Rate of Fire (+9%) > 0.9895480275154114 > 1.04519724845886

    # endregion
}

# endregion

# region Structs

# Level 0 (Inherited)

class cTkDynamicArray(common.cTkDynamicArray):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.miSize})"

    def __str__(self) -> str:  # aka remove
        return self.__repr__()

    def __len__(self) -> int:
        return self.miSize


class cTkDynamicString(common.cTkDynamicString):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.miSize})"

    def __str__(self) -> str:
        return self.value.decode("utf-8")

    def __len__(self) -> int:
        return self.miSize

# Level 1

class cGcAlienRace(ctypes.Structure):
    _fields_ = [
        ("_meAlienRace", ctypes.c_uint32),
    ]

    _meAlienRace: int

    @property
    def meAlienRace(self):
        return safe_assign_enum(nms_enums.eAlienRace, self._meAlienRace)

    def __str__(self) -> str:
        return str(self.meAlienRace)


class cGcInventoryType(ctypes.Structure):
    _fields_ = [
        ("_meInventoryType", ctypes.c_uint32),
    ]

    _meInventoryType: int

    @property
    def meInventoryType(self):
        return safe_assign_enum(nms_enums.eInventoryType, self._meInventoryType)

    def __str__(self) -> str:
        return str(self.meInventoryType)


class cGcItemPriceModifiers(ctypes.Structure):
    _fields_ = [
        ("mfSpaceStationMarkup", ctypes.c_float),
        ("mfLowPriceMod", ctypes.c_float),
        ("mfHighPriceMod", ctypes.c_float),
        ("mfBuyBaseMarkup", ctypes.c_float),
        ("mfBuyMarkupMod", ctypes.c_float),
    ]

    mfSpaceStationMarkup: float
    mfLowPriceMod: float
    mfHighPriceMod: float
    mfBuyBaseMarkup: float
    mfBuyMarkupMod: float


class cGcLegality(ctypes.Structure):
    _fields_ = [
        ("_meLegality", ctypes.c_uint32),
    ]

    _meLegality: int

    @property
    def meLegality(self):
        return safe_assign_enum(nms_enums.eLegality, self._meLegality)

    def __str__(self) -> str:
        return str(self.meLegality)


class cGcProductCategory(ctypes.Structure):
    _fields_ = [
        ("_meProductCategory", ctypes.c_uint32),
    ]

    _meProductCategory: int

    @property
    def meProductCategory(self):
        return safe_assign_enum(nms_enums.eProductCategory, self._meProductCategory)

    def __str__(self) -> str:
        return str(self.meProductCategory)


class cGcRarity(ctypes.Structure):
    _fields_ = [
        ("_meRarity", ctypes.c_uint32),
    ]

    _meRarity: int

    @property
    def meRarity(self):
        return safe_assign_enum(nms_enums.eRarity, self._meRarity)

    def __str__(self) -> str:
        return str(self.meRarity)


class cGcRealitySubstanceCategory(ctypes.Structure):
    _fields_ = [
        ("_meSubstanceCategory", ctypes.c_uint32),
    ]

    _meSubstanceCategory: int

    @property
    def meSubstanceCategory(self):
        return safe_assign_enum(nms_enums.eSubstanceCategory, self._meSubstanceCategory)

    def __str__(self) -> str:
        return str(self.meSubstanceCategory)


class cGcStatsTypes(ctypes.Structure):
    _fields_ = [
        ("_meStatsType", ctypes.c_uint32),
    ]

    _meStatsType: int

    @property
    def meStatsType(self):
        return safe_assign_enum(nms_enums.eStatsType, self._meStatsType)

    def __str__(self) -> str:
        return str(self.meStatsType)


class cGcTechnologyCategory(ctypes.Structure):
    _fields_ = [
        ("_meTechnologyCategory", ctypes.c_uint32),
    ]

    _meTechnologyCategory: int

    @property
    def meTechnologyCategory(self):
        return safe_assign_enum(nms_enums.eTechnologyCategory, self._meTechnologyCategory)

    def __str__(self) -> str:
        return str(self.meTechnologyCategory)


class cGcTechnologyRarity(ctypes.Structure):
    _fields_ = [
        ("_meTechnologyRarity", ctypes.c_uint32),
    ]

    _meTechnologyRarity: int

    @property
    def meTechnologyRarity(self):
        return safe_assign_enum(nms_enums.eTechnologyRarity, self._meTechnologyRarity)

    def __str__(self) -> str:
        return str(self.meTechnologyRarity)


class cGcTechnologyRequirement(ctypes.Structure):
    _fields_ = [
        ("mID", ctypes.c_char * 0x10),  # TkID<128>
        ("mType", cGcInventoryType),
        ("miAmount", ctypes.c_int32),
    ]

    mID: bytes
    mType: cGcInventoryType
    miAmount: int


class cGcTradeCategory(ctypes.Structure):
    _fields_ = [
        ("_meTradeCategory", ctypes.c_uint32),
    ]

    _meTradeCategory: int

    @property
    def meTradeCategory(self):
        return safe_assign_enum(nms_enums.eTradeCategory, self._meTradeCategory)

    def __str__(self) -> str:
        return str(self.meTradeCategory)


class cTkLanguageManagerBase(ctypes.Structure):
    _fields_ = [
        ("_dummy0x0", ctypes.c_ubyte * 0x8),
        ("meRegion", ctypes.c_int32),
        ("_dummy0xC", ctypes.c_ubyte * 0x221C),
    ]

    meRegion: int


class cTkModelResource(ctypes.Structure):
    _fields_ = [
        ("macFilename", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("mResHandle", ctypes.c_uint32),  # TODO cTkSmartResHandle
    ]

    macFilename: bytes

    def __str__(self) -> str:
        return self.macFilename.decode("utf-8")


class cTkTextureResource(ctypes.Structure):
    _fields_ = [
        ("macFilename", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("mResHandle", ctypes.c_uint32),  # TODO cTkSmartResHandle
    ]

    macFilename: bytes

    def __str__(self) -> str:
        return self.macFilename.decode("utf-8")

# Level 2

class cGcStatsBonus(ctypes.Structure):
    _fields_ = [
        ("mStat", cGcStatsTypes),
        ("mfBonus", ctypes.c_float),
        ("miLevel", ctypes.c_int32),
    ]

    mStat: cGcStatsTypes
    mfBonus: float
    miLevel: int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.mStat}, {self.mfBonus})"

# Level 3 (Main)

class cGcProductData(ctypes.Structure):
    _fields_ = [
        ("mID", ctypes.c_char * 0x10),  # TkID<128>
        ("macName", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("macNameLower", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("macSubtitle", cTkDynamicString),
        ("macDescription", cTkDynamicString),
        ("mHint", ctypes.c_char * 0x20),  # TkID<256>
        ("mGroupID", ctypes.c_char * 0x10),  # TkID<128>
        ("mDebrisFile", cTkModelResource),
        ("miBaseValue", ctypes.c_int32),
        ("miLevel", ctypes.c_int32),
        ("mIcon", cTkTextureResource),
        ("mHeroIcon", cTkTextureResource),
        ("_padding0x2F4", ctypes.c_ubyte * 0xC),
        ("mColour", common.Colour),
        ("mCategory", cGcTechnologyCategory),
        ("mType", cGcProductCategory),
        ("mRarity", cGcRarity),
        ("mLegality", cGcLegality),
        ("mbConsumable", ctypes.c_ubyte),
        ("_padding0x321", ctypes.c_ubyte * 0x3),
        ("miChargeValue", ctypes.c_int32),
        ("miStackMultiplier", ctypes.c_int32),
        ("miDefaultCraftAmount", ctypes.c_int32),
        ("miCraftAmountStepSize", ctypes.c_int32),
        ("miCraftAmountMultiplier", ctypes.c_int32),
        ("maRequirements", cTkDynamicArray[cGcTechnologyRequirement]),
        ("maAltRequirements", cTkDynamicArray[cGcTechnologyRequirement]),
        ("mCost", cGcItemPriceModifiers),
        ("miRecipeCost", ctypes.c_int32),
        ("mbSpecificChargeOnly", ctypes.c_ubyte),
        ("_padding0x371", ctypes.c_ubyte * 0x3),
        ("mfNormalisedValueOnWorld", ctypes.c_float),
        ("mfNormalisedValueOffWorld", ctypes.c_float),
        ("mTradeCategory", cGcTradeCategory),
        ("_meWikiCategory", ctypes.c_uint32),
        ("mbIsCraftable", ctypes.c_ubyte),
        ("_padding0x385", ctypes.c_ubyte * 0x3),
        ("mDeploysInto", ctypes.c_char * 0x10),  # TkID<128>
        ("mfEconomyInfluenceMultiplier", ctypes.c_float),
        ("_padding0x39C", ctypes.c_ubyte * 0x4),
        ("mPinObjective", ctypes.c_char * 0x20),  # TkID<256>
        ("mPinObjectiveTip", ctypes.c_char * 0x20),  # TkID<256>
        ("mbCookingIngredient", ctypes.c_ubyte),
        ("_padding0x3E1", ctypes.c_ubyte * 0x3),
        ("mfCookingValue", ctypes.c_float),
        ("mbGoodForSelling", ctypes.c_ubyte),
        ("_padding0x3E9", ctypes.c_ubyte * 0x7),
        ("mGiveRewardOnSpecialPurchase", ctypes.c_char * 0x10),  # TkID<128>
        ("mbEggModifierIngredient", ctypes.c_ubyte),
        ("mbIsTechbox", ctypes.c_ubyte),
        ("mbCanSendToOtherPlayers", ctypes.c_ubyte),
        ("_padding0x403", ctypes.c_ubyte * 0xD),
    ]

    @property
    def meWikiCategory(self):
        return safe_assign_enum(nms_enums.eWikiCategory, self._meWikiCategory)


class cGcTechnology(ctypes.Structure):
    _fields_ = [
        ("mID", ctypes.c_char * 0x10),  # TkID<128>
        ("mGroup", ctypes.c_char * 0x20),  # TkID<256>
        ("macName", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("macNameLower", ctypes.c_char * 0x80),  # cTkFixedString<128,char>
        ("macSubtitle", cTkDynamicString),
        ("macDescription", cTkDynamicString),
        ("mbTeach", ctypes.c_ubyte),
        ("_padding0x151", ctypes.c_ubyte * 0x7),
        ("mHintStart", ctypes.c_char * 0x20),  # TkID<256>
        ("mHintEnd", ctypes.c_char * 0x20),  # TkID<256>
        ("mIcon", cTkTextureResource),
        ("_padding0x21C", ctypes.c_ubyte * 0x4),
        ("mColour", common.Colour),
        ("miLevel", ctypes.c_int32),
        ("mbChargeable", ctypes.c_ubyte),
        ("_padding0x235", ctypes.c_ubyte * 0x3),
        ("miChargeAmount", ctypes.c_int32),
        ("mChargeType", cGcRealitySubstanceCategory),
        ("maChargeBy", cTkDynamicArray[ctypes.c_char * 0x10]),  # TkID<128>
        ("mfChargeMultiplier", ctypes.c_float),
        ("mbBuildFullyCharged", ctypes.c_ubyte),
        ("mbUsesAmmo", ctypes.c_ubyte),
        ("_padding0x256", ctypes.c_ubyte * 0x2),
        ("mAmmoId", ctypes.c_char * 0x10),  # TkID<128>
        ("mbPrimaryItem", ctypes.c_ubyte),
        ("mbUpgrade", ctypes.c_ubyte),
        ("mbCore", ctypes.c_ubyte),
        ("mbRepairTech", ctypes.c_ubyte),
        ("mbProcedural", ctypes.c_ubyte),
        ("_padding0x26B", ctypes.c_ubyte * 0x3),
        ("mCategory", cGcTechnologyCategory),
        ("mRarity", cGcTechnologyRarity),
        ("mfValue", ctypes.c_float),
        ("_padding0x27A", ctypes.c_ubyte * 0x4),
        ("maRequirements", cTkDynamicArray[cGcTechnologyRequirement]),
        ("mBaseStat", cGcStatsTypes),
        ("_padding0x28E", ctypes.c_ubyte * 0x4),
        ("maStatBonuses", cTkDynamicArray[cGcStatsBonus]),
        ("mRequiredTech", ctypes.c_char * 0x10),  # TkID<128>
        ("miRequiredLevel", ctypes.c_int32),
        ("_padding0x2B6", ctypes.c_ubyte * 0x4),
        ("mFocusLocator", ctypes.c_char * 0x20),  # TkID<256>
        ("mUpgradeColour", common.Colour),
        ("mLinkColour", common.Colour),
        ("mRewardGroup", ctypes.c_char * 0x10),  # TkID<128>
        ("miBaseValue", ctypes.c_int32),
        ("mCost", cGcItemPriceModifiers),
        ("miRequiredRank", ctypes.c_int32),
        ("mDispensingRace", cGcAlienRace),
        ("miFragmentCost", ctypes.c_int32),
        ("mTechShopRarity", cGcTechnologyRarity),
        ("mbWikiEnabled", ctypes.c_ubyte),
        ("_padding0x333", ctypes.c_ubyte * 0x7),
        ("macDamagedDescription", cTkDynamicString),
        ("mParentTechId", ctypes.c_char * 0x10),  # TkID<128>
        ("mbIsTemplate", ctypes.c_ubyte),
        ("_padding0x354", ctypes.c_ubyte * 0xF),
    ]


# endregion

# region Helper Methods


def extract_previous_languages(read_rows, seed):
    if seed < len(read_rows):  # just in case read file has less rows than expected
        # add all languages and get previous translations or empty string
        return {
            language: read_rows[seed].get(language, "")
            for language in LANGUAGES
        }

    return {}


def get_next_technology(iter_next):
    inventory_type, items = TECHNOLOGY_ITEMS_LIST[iter_next[0]]
    item_id, qualities = list(items.items())[iter_next[1]]

    return inventory_type, items, item_id, qualities, qualities[iter_next[2]]


def print_struct_fields(struct, level=0):
    l = max(len(f) for f, _ in struct._fields_)
    for field_name, _ in struct._fields_:
        if field_name.startswith("_"):
            continue

        field = getattr(struct, field_name)

        if isinstance(field, ctypes.Structure) and str(field).startswith("<"):
            logging.debug(f"{(' ' * 4 * level)}{field_name:{l}}")
            print_struct_fields(field, level + 1)
        else:
            if field_name.startswith("mb"):
                log_value = f"{bool(field)} ({field})"
            elif isinstance(field, common.cTkDynamicArray):
                if len(field):
                    log_value = f"{field} > 0: {field.value[0]}"
                else:
                    log_value = field
            else:
                log_value = field

            logging.debug(f"{(' ' * 4 * level)}{field_name:{l}} >> {log_value}")


# read existing file to carry over all previous translations
def read_languages(f_name):
    if os.path.isfile(f_name):
        with open(f_name, mode='r', encoding="utf-8", newline='') as f:
            f.readline()  # skip first line with delimiter indicator
            reader = csv.DictReader(f, dialect='excel')
            return list(reader)

    return []


# translate raw value to look more like in-game
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


def write_result(f_name, meta, result):
    fieldnames = ["Seed", "Perfection"] + sorted(meta.keys()) + LANGUAGES
    with open(f_name, mode="w", encoding="utf-8", newline="") as f:
        f.write("sep=,\r\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect="excel")
        writer.writeheader()
        writer.writerows(result)


# endregion


class Pi(NMSMod):
    __NMSPY_required_version__ = "0.6.3"

    __author__ = "zencq"
    __description__ = "Generate data for all procedural items."
    __version__ = "1.0.0"

    # False = disable
    # True = enable automatic iteration mode
    # isinstance(, list) = enable manual iteration mode. set a manual starting point (e.g. [1, 2, 3] for [Exocraft, UP_EXGUN, 4])
    iteration_technology = True

    # do more in less time. you are about 30% faster but you also have more work as you have to make more restarts
    # if True there will be only 1 iteration per run (4 takes 4.5 minutes), otherwise 2 or 3 (4 takes 6.25 minutes)
    iteration_more_in_less = True

    language = None  # name of column to write the name in, will be set automatically
    round_digits_product = 5
    round_digits_technology = 3

    @hooks.cTkLanguageManagerBase.Load.after
    def language_manager_load(self, this):
        result = original = map_struct(this, cTkLanguageManagerBase).meRegion
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

        logging.debug(f">> cTkLanguageManagerBase.Load: {original} > {result} > {self.language}")

    # TODO remove @disable when technology memory leak is fixed
    @one_shot
    @hooks.cGcRealityManager.GenerateProceduralProduct.overload("cGcRealityManager *, const TkID<128> *")
    @disable
    def reality_manager_generate_procedural_product(self, this, lProcProdID):
        begin = datetime.now()
        logging.info(f"Pi started generate_procedural_product at {begin}")

        try:
            for item_id in PRODUCT:
                self.generate_product(this, item_id)
        except Exception as e:
            logging.exception(e)

        end = datetime.now()
        logging.info(f"Pi finished generate_procedural_product in {end - begin}")

        return hooks.cGcRealityManager.GenerateProceduralProduct.original(this, lProcProdID)

    def generate_product(self, this, item_id):
        item_name = f"PROC_{item_id}"
        meta = {}  # keep track of min/max/weighting for perfection calculation
        result = []  # result for each seed
        middle = datetime.now()

        f_name = f"{PI_ROOT}\\Product\\{item_name}.csv"

        read_rows =  read_languages(f_name)

        logging.info(f"    {item_name}")

        for seed in range(TOTAL_SEEDS):
            pointer = hooks.cGcRealityManager.GenerateProceduralProduct.original(this, f"{item_name}#{seed:05}".encode("utf-8"))
            generated = map_struct(pointer, cGcProductData)
            row = extract_previous_languages(read_rows, seed)  # carry over all previous translations

            # add seed and current translation
            row.update({
                self.language: generated.macNameLower.decode("utf-8"),  # name for current language
                "Age": int(RE_PRODUCT_AGE.findall(str(generated.macDescription))[0]),
                "Seed": seed,
                "Value": generated.miBaseValue,
            })

            if not meta:
                logging.debug(f"      >> Age: {row['Age']}")  # check whether value correct
                logging.debug(f"      >> Value: {generated.miBaseValue}")
                meta = [generated.miBaseValue, generated.miBaseValue]
            else:
                meta = [
                    min(meta[0], generated.miBaseValue),
                    max(meta[1], generated.miBaseValue),
                ]

            # add completed row to result
            result.append(row)

            # print progress in given steps
            if (seed - (PROGRESS_STEPS - 1)) % PROGRESS_STEPS == 0:
                middle_next = datetime.now()
                logging.info(f"      {seed:>5} ({middle_next - middle}) ({middle_next})")
                middle = middle_next

        for row in result:
            row.update({
                "Perfection": round(1.0 - (meta[1] - row["Value"]) / (meta[1] - meta[0]), self.round_digits_product),
            })

        write_result(f_name, {"Age": None, "Value": None}, result)

    @one_shot
    @hooks.cGcRealityManager.GenerateProceduralTechnology
    # @disable
    def reality_manager_generate_procedural_technology(self, this, lProcTechID, lbExampleForWiki):
        begin = datetime.now()
        logging.info(f"Pi started generate_procedural_technology at {begin}")

        try:
            is_manual = False
            if self.iteration_technology or (is_manual := type(self.iteration_product) == list and len(self.iteration_technology) >= 3):
                if not is_manual:
                    f_name = f"{os.path.dirname(__file__)}\\iteration_technology"

                    # read next start index if file exists or start at the beginning
                    if os.path.isfile(f_name):
                        with open(f_name, mode="r") as f:
                            iter_next = eval(f.read().strip())
                    else:
                        iter_next = [0, 0, 0]
                else:
                    iter_next = self.iteration_technology

                inventory_type, items, item_id, qualities, quality = get_next_technology(iter_next)
                iterations = (1) if self. iteration_more_in_less else (3 if iter_next[0] == len(TECHNOLOGY) - 1 and iter_next[1] == len(items) - 1 and len(qualities[iter_next[2]:]) <= 3 else 2)

                for _ in range(iterations):
                    self.generate_technology(this, inventory_type, item_id, quality)

                    iter_next[2] += 1  # next quality

                    if iter_next[2] == len(qualities):  # start with next item
                        iter_next[1] += 1
                        iter_next[2] = 0

                    if iter_next[1] == len(items):  # start with next inventory
                        iter_next[0] += 1
                        iter_next[1] = 0

                    if iter_next[0] == len(TECHNOLOGY):  # stop it it was last inventory
                        break

                    inventory_type, items, item_id, qualities, quality = get_next_technology(iter_next)

                if not is_manual:
                    # delete file if it was the last iteration or write the next start
                    if iter_next[0] == len(TECHNOLOGY):
                        os.remove(f_name)
                    else:
                        with open(f_name, mode="w") as f:
                            f.write(str(iter_next))
            else:
                for inventory_type, items in TECHNOLOGY.items():
                    logging.info(f"  {inventory_type}")
                    for item_id, qualities in items.items():
                        for quality in qualities:
                            self.generate_technology(this, inventory_type, item_id, quality)
        except Exception as e:
            logging.exception(e)

        end = datetime.now()
        logging.info(f"Pi finished generate_procedural_technology in {end - begin}")

        return hooks.cGcRealityManager.GenerateProceduralTechnology.original(this, lProcTechID, lbExampleForWiki)

    # TODO release memory to speed up execution
    def generate_technology(self, this, inventory_type, item_id, quality):
        item_name = f"{item_id}{quality}"
        meta = {}  # keep track of min/max/weighting for perfection calculation
        number = 0  # maximum number of unique stats per seed
        result = []  # result for each seed
        middle = datetime.now()

        f_name = f"{PI_ROOT}\\{inventory_type}\\{item_name}.csv"

        read_rows =  read_languages(f_name)

        logging.info(f"    {item_name}")

        for seed in range(TOTAL_SEEDS):
            pointer = hooks.cGcRealityManager.GenerateProceduralTechnology.original(this, f"{item_name}#{seed:05}".encode("utf-8"), 0)
            generated = map_struct(pointer, cGcTechnology)
            number = max(number, len(generated.maStatBonuses.value))
            row = extract_previous_languages(read_rows, seed)  # carry over all previous translations

            # add seed and current translation
            row.update({
                self.language: generated.macNameLower.decode("utf-8"),  # name for current language
                "Seed": seed,
            })

            for stat_bonus in generated.maStatBonuses.value:
                stat = str(stat_bonus.mStat)[22:]  # skip identical-for-all prefix
                stat_value = row[stat] = translate_value(stat_bonus)  # add in-game like value of a stat

                if stat not in meta:
                    logging.debug(f"      >> {stat}: {stat_bonus.mfBonus} > {stat_value}")  # to see how the value looks
                    meta[stat] = [stat_value, stat_value]
                else:
                    meta[stat] = [
                        min(meta[stat][0], stat_value),
                        max(meta[stat][1], stat_value),
                    ]

            # add completed row to result
            result.append(row)

            # print progress in given steps
            if (seed - (PROGRESS_STEPS - 1)) % PROGRESS_STEPS == 0:
                middle_next = datetime.now()
                logging.info(f"      {seed:>5} ({middle_next - middle}) ({middle_next})")
                middle = middle_next

        weighting = [stat[1] - stat[0] + 1 for stat in meta.values()]  # max - min + 1
        weighting_min = min(weighting)

        # add weighting to each stat
        meta = {key: value + [weighting[i] / weighting_min] for i, (key, value) in enumerate(meta.items())}

        for row in result:
            perfection = []
            weighting_total = 0

            # calculate perfection for each seed
            for stat_name, stat_meta in meta.items():
                if stat_name not in row:
                    continue

                stat_value = row[stat_name]
                weight = stat_meta[2]
                weighting_total += weight

                p = 1.0
                if stat_meta[1] - stat_meta[0] > 0:
                    p -= (stat_meta[1] - stat_value) / (stat_meta[1] - stat_meta[0])
                p *= weight
                perfection.append(p)

            row.update({
                "Perfection": round(sum(perfection) / weighting_total * (len(perfection) / number), self.round_digits_technology),
            })

        write_result(f_name, meta, result)
