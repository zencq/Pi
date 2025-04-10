# pyright: reportMissingImports=false

import csv
import ctypes
import logging
import os
import pyarrow as pa
import pyarrow.parquet as pq
import re
import threading

# from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

from pymhf import FUNCDEF
from pymhf.core import _internal as pymhf_internal
from pymhf.core.memutils import map_struct
from pymhf.core.mod_loader import ModState
from pymhf.core.utils import safe_assign_enum
from pymhf.extensions.cpptypes import std
from pymhf.gui import BOOLEAN, STRING, gui_button

from nmspy import NMSMod
from nmspy.data import (
    common as nms_structs_common,
    enums as nms_enums,
    structs as nms_structs,
)
from nmspy.data.functions import call_sigs, hooks, patterns
from nmspy.decorators import on_fully_booted


# region NMS.py

# region Class


# size is one more than the last value
class eStatsType_413(IntEnum):
    Unspecified = 0x0
    Weapon_Laser = 0x1
    Weapon_Laser_Damage = 0x2
    Weapon_Laser_Mining_Speed = 0x3
    Weapon_Laser_HeatTime = 0x4
    Weapon_Laser_Bounce = 0x5
    Weapon_Laser_ReloadTime = 0x6
    Weapon_Laser_Recoil = 0x7
    Weapon_Laser_Drain = 0x8
    Weapon_Laser_StrongLaser = 0x9
    Weapon_Laser_ChargeTime = 0xA
    Weapon_Laser_MiningBonus = 0xB
    Weapon_Projectile = 0xC
    Weapon_Projectile_Damage = 0xD
    Weapon_Projectile_Range = 0xE
    Weapon_Projectile_Rate = 0xF
    Weapon_Projectile_ClipSize = 0x10
    Weapon_Projectile_ReloadTime = 0x11
    Weapon_Projectile_Recoil = 0x12
    Weapon_Projectile_Bounce = 0x13
    Weapon_Projectile_Homing = 0x14
    Weapon_Projectile_Dispersion = 0x15
    Weapon_Projectile_BulletsPerShot = 0x16
    Weapon_Projectile_MinimumCharge = 0x17
    Weapon_Projectile_MaximumCharge = 0x18
    Weapon_Projectile_BurstCap = 0x19
    Weapon_Projectile_BurstCooldown = 0x1A
    Weapon_ChargedProjectile = 0x1B
    Weapon_ChargedProjectile_ChargeTime = 0x1C
    Weapon_ChargedProjectile_CooldownDuration = 0x1D
    Weapon_ChargedProjectile_Drain = 0x1E
    Weapon_ChargedProjectile_ExtraSpeed = 0x1F
    Weapon_Rail = 0x20
    Weapon_Shotgun = 0x21
    Weapon_Burst = 0x22
    Weapon_Flame = 0x23
    Weapon_Cannon = 0x24
    Weapon_Grenade = 0x25
    Weapon_Grenade_Damage = 0x26
    Weapon_Grenade_Radius = 0x27
    Weapon_Grenade_Speed = 0x28
    Weapon_Grenade_Bounce = 0x29
    Weapon_Grenade_Homing = 0x2A
    Weapon_Grenade_Clusterbomb = 0x2B
    Weapon_TerrainEdit = 0x2C
    Weapon_SunLaser = 0x2D
    Weapon_SoulLaser = 0x2E
    Weapon_MineGrenade = 0x2F
    Weapon_FrontShield = 0x30
    Weapon_Scope = 0x31
    Weapon_Spawner = 0x32
    Weapon_SpawnerAlt = 0x33
    Weapon_Melee = 0x34
    Weapon_StunGrenade = 0x35
    Weapon_Stealth = 0x36
    Weapon_Scan = 0x37
    Weapon_Scan_Radius = 0x38
    Weapon_Scan_Recharge_Time = 0x39
    Weapon_Scan_Types = 0x3A
    Weapon_Scan_Binoculars = 0x3B
    Weapon_Scan_Discovery_Creature = 0x3C
    Weapon_Scan_Discovery_Flora = 0x3D
    Weapon_Scan_Discovery_Mineral = 0x3E
    Weapon_Scan_Secondary = 0x3F
    Weapon_Scan_Terrain_Resource = 0x40
    Weapon_Scan_Surveying = 0x41
    Weapon_Stun = 0x42
    Weapon_Stun_Duration = 0x43
    Weapon_Stun_Damage_Multiplier = 0x44
    Weapon_FireDOT = 0x45
    Weapon_FireDOT_Duration = 0x46
    Weapon_FireDOT_DPS = 0x47
    Weapon_FireDOT_Damage_Multiplier = 0x48
    Suit_Armour_Health = 0x49
    Suit_Armour_Shield = 0x4A
    Suit_Armour_Shield_Strength = 0x4B
    Suit_Energy = 0x4C
    Suit_Energy_Regen = 0x4D
    Suit_Protection = 0x4E
    Suit_Protection_Cold = 0x4F
    Suit_Protection_Heat = 0x50
    Suit_Protection_Toxic = 0x51
    Suit_Protection_Radiation = 0x52
    Suit_Underwater = 0x53
    Suit_UnderwaterLifeSupport = 0x54
    Suit_DamageReduce_Cold = 0x55
    Suit_DamageReduce_Heat = 0x56
    Suit_DamageReduce_Toxic = 0x57
    Suit_DamageReduce_Radiation = 0x58
    Suit_Protection_HeatDrain = 0x59
    Suit_Protection_ColdDrain = 0x5A
    Suit_Protection_ToxDrain = 0x5B
    Suit_Protection_RadDrain = 0x5C
    Suit_Protection_WaterDrain = 0x5D
    Suit_Stamina_Strength = 0x5E
    Suit_Stamina_Speed = 0x5F
    Suit_Stamina_Recovery = 0x60
    Suit_Jetpack = 0x61
    Suit_Jetpack_Tank = 0x62
    Suit_Jetpack_Drain = 0x63
    Suit_Jetpack_Refill = 0x64
    Suit_Jetpack_Ignition = 0x65
    Suit_Jetpack_DoubleJump = 0x66
    Suit_Jetpack_WaterEfficiency = 0x67
    Suit_Jetpack_MidairRefill = 0x68
    Suit_Refiner = 0x69
    Suit_AutoTranslator = 0x6A
    Suit_Utility = 0x6B
    Suit_RocketLocker = 0x6C
    Ship_Weapons_Guns = 0x6D
    Ship_Weapons_Guns_Damage = 0x6E
    Ship_Weapons_Guns_Rate = 0x6F
    Ship_Weapons_Guns_HeatTime = 0x70
    Ship_Weapons_Guns_CoolTime = 0x71
    Ship_Weapons_Guns_Scale = 0x72
    Ship_Weapons_Guns_BulletsPerShot = 0x73
    Ship_Weapons_Guns_Dispersion = 0x74
    Ship_Weapons_Guns_Range = 0x75
    Ship_Weapons_Guns_Damage_Radius = 0x76
    Ship_Weapons_Lasers = 0x77
    Ship_Weapons_Lasers_Damage = 0x78
    Ship_Weapons_Lasers_HeatTime = 0x79
    Ship_Weapons_Missiles = 0x7A
    Ship_Weapons_Missiles_NumPerShot = 0x7B
    Ship_Weapons_Missiles_Speed = 0x7C
    Ship_Weapons_Missiles_Damage = 0x7D
    Ship_Weapons_Missiles_Size = 0x7E
    Ship_Weapons_Shotgun = 0x7F
    Ship_Weapons_MiniGun = 0x80
    Ship_Weapons_Plasma = 0x81
    Ship_Weapons_Rockets = 0x82
    Ship_Weapons_ShieldLeech = 0x83
    Ship_Armour_Shield = 0x84
    Ship_Armour_Shield_Strength = 0x85
    Ship_Armour_Health = 0x86
    Ship_Scan = 0x87
    Ship_Scan_EconomyFilter = 0x88
    Ship_Scan_ConflictFilter = 0x89
    Ship_Hyperdrive = 0x8A
    Ship_Hyperdrive_JumpDistance = 0x8B
    Ship_Hyperdrive_JumpsPerCell = 0x8C
    Ship_Hyperdrive_QuickWarp = 0x8D
    Ship_Launcher = 0x8E
    Ship_Launcher_TakeOffCost = 0x8F
    Ship_Launcher_AutoCharge = 0x90
    Ship_PulseDrive = 0x91
    Ship_PulseDrive_MiniJumpFuelSpending = 0x92
    Ship_PulseDrive_MiniJumpSpeed = 0x93
    Ship_Boost = 0x94
    Ship_Maneuverability = 0x95
    Ship_BoostManeuverability = 0x96
    Ship_LifeSupport = 0x97
    Ship_Drift = 0x98
    Ship_Teleport = 0x99
    Ship_CargoShield = 0x9A
    Freighter_Hyperdrive = 0x9B
    Freighter_Hyperdrive_JumpDistance = 0x9C
    Freighter_Hyperdrive_JumpsPerCell = 0x9D
    Freighter_MegaWarp = 0x9E
    Freighter_Teleport = 0x9F
    Freighter_Fleet_Boost = 0xA0
    Freighter_Fleet_Speed = 0xA1
    Freighter_Fleet_Fuel = 0xA2
    Freighter_Fleet_Combat = 0xA3
    Freighter_Fleet_Trade = 0xA4
    Freighter_Fleet_Explore = 0xA5
    Freighter_Fleet_Mine = 0xA6
    Vehicle_Boost = 0xA7
    Vehicle_Engine = 0xA8
    Vehicle_Scan = 0xA9
    Vehicle_EngineFuelUse = 0xAA
    Vehicle_EngineTopSpeed = 0xAB
    Vehicle_BoostSpeed = 0xAC
    Vehicle_BoostTanks = 0xAD
    Vehicle_Grip = 0xAE
    Vehicle_SkidGrip = 0xAF
    Vehicle_SubBoostSpeed = 0xB0
    Vehicle_Laser = 0xB1
    Vehicle_LaserDamage = 0xB2
    Vehicle_LaserHeatTime = 0xB3
    Vehicle_LaserStrongLaser = 0xB4
    Vehicle_Gun = 0xB5
    Vehicle_GunDamage = 0xB6
    Vehicle_GunHeatTime = 0xB7
    Vehicle_GunRate = 0xB8
    Vehicle_StunGun = 0xB9
    Vehicle_TerrainEdit = 0xBA
    Vehicle_FuelRegen = 0xBB
    Vehicle_AutoPilot = 0xBC


class eStatsType_520(IntEnum):
    Unspecified = 0x0
    Weapon_Laser = 0x1
    Weapon_Laser_Damage = 0x2
    Weapon_Laser_Mining_Speed = 0x3
    Weapon_Laser_HeatTime = 0x4
    Weapon_Laser_Bounce = 0x5
    Weapon_Laser_ReloadTime = 0x6
    Weapon_Laser_Recoil = 0x7
    Weapon_Laser_Drain = 0x8
    Weapon_Laser_StrongLaser = 0x9
    Weapon_Laser_ChargeTime = 0xA
    Weapon_Laser_MiningBonus = 0xB
    Weapon_Projectile = 0xC
    Weapon_Projectile_Damage = 0xD
    Weapon_Projectile_Range = 0xE
    Weapon_Projectile_Rate = 0xF
    Weapon_Projectile_ClipSize = 0x10
    Weapon_Projectile_ReloadTime = 0x11
    Weapon_Projectile_Recoil = 0x12
    Weapon_Projectile_Bounce = 0x13
    Weapon_Projectile_Homing = 0x14
    Weapon_Projectile_Dispersion = 0x15
    Weapon_Projectile_BulletsPerShot = 0x16
    Weapon_Projectile_MinimumCharge = 0x17
    Weapon_Projectile_MaximumCharge = 0x18
    Weapon_Projectile_BurstCap = 0x19
    Weapon_Projectile_BurstCooldown = 0x1A
    Weapon_ChargedProjectile = 0x1B
    Weapon_ChargedProjectile_ChargeTime = 0x1C
    Weapon_ChargedProjectile_CooldownDuration = 0x1D
    Weapon_ChargedProjectile_Drain = 0x1E
    Weapon_ChargedProjectile_ExtraSpeed = 0x1F
    Weapon_Rail = 0x20
    Weapon_Shotgun = 0x21
    Weapon_Burst = 0x22
    Weapon_Flame = 0x23
    Weapon_Cannon = 0x24
    Weapon_Grenade = 0x25
    Weapon_Grenade_Damage = 0x26
    Weapon_Grenade_Radius = 0x27
    Weapon_Grenade_Speed = 0x28
    Weapon_Grenade_Bounce = 0x29
    Weapon_Grenade_Homing = 0x2A
    Weapon_Grenade_Clusterbomb = 0x2B
    Weapon_TerrainEdit = 0x2C
    Weapon_SunLaser = 0x2D
    Weapon_SoulLaser = 0x2E
    Weapon_MineGrenade = 0x2F
    Weapon_FrontShield = 0x30
    Weapon_Scope = 0x31
    Weapon_Spawner = 0x32
    Weapon_SpawnerAlt = 0x33
    Weapon_Melee = 0x34
    Weapon_StunGrenade = 0x35
    Weapon_Stealth = 0x36
    Weapon_Scan = 0x37
    Weapon_Scan_Radius = 0x38
    Weapon_Scan_Recharge_Time = 0x39
    Weapon_Scan_Types = 0x3A
    Weapon_Scan_Binoculars = 0x3B
    Weapon_Scan_Discovery_Creature = 0x3C
    Weapon_Scan_Discovery_Flora = 0x3D
    Weapon_Scan_Discovery_Mineral = 0x3E
    Weapon_Scan_Secondary = 0x3F
    Weapon_Scan_Terrain_Resource = 0x40
    Weapon_Scan_Surveying = 0x41
    Weapon_Scan_BuilderReveal = 0x42
    Weapon_Fish = 0x43
    Weapon_Stun = 0x44
    Weapon_Stun_Duration = 0x45
    Weapon_Stun_Damage_Multiplier = 0x46
    Weapon_FireDOT = 0x47
    Weapon_FireDOT_Duration = 0x48
    Weapon_FireDOT_DPS = 0x49
    Weapon_FireDOT_Damage_Multiplier = 0x4A
    Suit_Armour_Health = 0x4B
    Suit_Armour_Shield = 0x4C
    Suit_Armour_Shield_Strength = 0x4D
    Suit_Energy = 0x4E
    Suit_Energy_Regen = 0x4F
    Suit_Protection = 0x50
    Suit_Protection_Cold = 0x51
    Suit_Protection_Heat = 0x52
    Suit_Protection_Toxic = 0x53
    Suit_Protection_Radiation = 0x54
    Suit_Protection_Spook = 0x55
    Suit_Underwater = 0x56
    Suit_UnderwaterLifeSupport = 0x57
    Suit_DamageReduce_Cold = 0x58
    Suit_DamageReduce_Heat = 0x59
    Suit_DamageReduce_Toxic = 0x5A
    Suit_DamageReduce_Radiation = 0x5B
    Suit_Protection_HeatDrain = 0x5C
    Suit_Protection_ColdDrain = 0x5D
    Suit_Protection_ToxDrain = 0x5E
    Suit_Protection_RadDrain = 0x5F
    Suit_Protection_WaterDrain = 0x60
    Suit_Protection_SpookDrain = 0x61
    Suit_Stamina_Strength = 0x62
    Suit_Stamina_Speed = 0x63
    Suit_Stamina_Recovery = 0x64
    Suit_Jetpack = 0x65
    Suit_Jetpack_Tank = 0x66
    Suit_Jetpack_Drain = 0x67
    Suit_Jetpack_Refill = 0x68
    Suit_Jetpack_Ignition = 0x69
    Suit_Jetpack_DoubleJump = 0x6A
    Suit_Jetpack_WaterEfficiency = 0x6B
    Suit_Jetpack_MidairRefill = 0x6C
    Suit_Refiner = 0x6D
    Suit_AutoTranslator = 0x6E
    Suit_Utility = 0x6F
    Suit_RocketLocker = 0x70
    Suit_FishPlatform = 0x71
    Suit_Denier = 0x72
    Ship_Weapons_Guns = 0x73
    Ship_Weapons_Guns_Damage = 0x74
    Ship_Weapons_Guns_Rate = 0x75
    Ship_Weapons_Guns_HeatTime = 0x76
    Ship_Weapons_Guns_CoolTime = 0x77
    Ship_Weapons_Guns_Scale = 0x78
    Ship_Weapons_Guns_BulletsPerShot = 0x79
    Ship_Weapons_Guns_Dispersion = 0x7A
    Ship_Weapons_Guns_Range = 0x7B
    Ship_Weapons_Guns_Damage_Radius = 0x7C
    Ship_Weapons_Lasers = 0x7D
    Ship_Weapons_Lasers_Damage = 0x7E
    Ship_Weapons_Lasers_HeatTime = 0x7F
    Ship_Weapons_Missiles = 0x80
    Ship_Weapons_Missiles_NumPerShot = 0x81
    Ship_Weapons_Missiles_Speed = 0x82
    Ship_Weapons_Missiles_Damage = 0x83
    Ship_Weapons_Missiles_Size = 0x84
    Ship_Weapons_Shotgun = 0x85
    Ship_Weapons_MiniGun = 0x86
    Ship_Weapons_Plasma = 0x87
    Ship_Weapons_Rockets = 0x88
    Ship_Weapons_ShieldLeech = 0x89
    Ship_Armour_Shield = 0x8A
    Ship_Armour_Shield_Strength = 0x8B
    Ship_Armour_Health = 0x8C
    Ship_Scan = 0x8D
    Ship_Scan_EconomyFilter = 0x8E
    Ship_Scan_ConflictFilter = 0x8F
    Ship_Hyperdrive = 0x90
    Ship_Hyperdrive_JumpDistance = 0x91
    Ship_Hyperdrive_JumpsPerCell = 0x92
    Ship_Hyperdrive_QuickWarp = 0x93
    Ship_Launcher = 0x94
    Ship_Launcher_TakeOffCost = 0x95
    Ship_Launcher_AutoCharge = 0x96
    Ship_PulseDrive = 0x97
    Ship_PulseDrive_MiniJumpFuelSpending = 0x98
    Ship_PulseDrive_MiniJumpSpeed = 0x99
    Ship_Boost = 0x9A
    Ship_Maneuverability = 0x9B
    Ship_BoostManeuverability = 0x9C
    Ship_LifeSupport = 0x9D
    Ship_Drift = 0x9E
    Ship_Teleport = 0x9F
    Ship_CargoShield = 0xA0
    Ship_WaterLandingJet = 0xA1
    Freighter_Hyperdrive = 0xA2
    Freighter_Hyperdrive_JumpDistance = 0xA3
    Freighter_Hyperdrive_JumpsPerCell = 0xA4
    Freighter_MegaWarp = 0xA5
    Freighter_Teleport = 0xA6
    Freighter_Fleet_Boost = 0xA7
    Freighter_Fleet_Speed = 0xA8
    Freighter_Fleet_Fuel = 0xA9
    Freighter_Fleet_Combat = 0xAA
    Freighter_Fleet_Trade = 0xAB
    Freighter_Fleet_Explore = 0xAC
    Freighter_Fleet_Mine = 0xAD
    Vehicle_Boost = 0xAE
    Vehicle_Engine = 0xAF
    Vehicle_Scan = 0xB0
    Vehicle_EngineFuelUse = 0xB1
    Vehicle_EngineTopSpeed = 0xB2
    Vehicle_BoostSpeed = 0xB3
    Vehicle_BoostTanks = 0xB4
    Vehicle_Grip = 0xB5
    Vehicle_SkidGrip = 0xB6
    Vehicle_SubBoostSpeed = 0xB7
    Vehicle_Laser = 0xB8
    Vehicle_LaserDamage = 0xB9
    Vehicle_LaserHeatTime = 0xBA
    Vehicle_LaserStrongLaser = 0xBB
    Vehicle_Gun = 0xBC
    Vehicle_GunDamage = 0xBD
    Vehicle_GunHeatTime = 0xBE
    Vehicle_GunRate = 0xBF
    Vehicle_StunGun = 0xC0
    Vehicle_TerrainEdit = 0xC1
    Vehicle_FuelRegen = 0xC2
    Vehicle_AutoPilot = 0xC3
    Vehicle_Flame = 0xC4
    Vehicle_FlameDamage = 0xC5
    Vehicle_FlameHeatTime = 0xC6


class eStatsType_561(IntEnum):
    Unspecified = 0x0
    Weapon_Laser = 0x1
    Weapon_Laser_Damage = 0x2
    Weapon_Laser_Mining_Speed = 0x3
    Weapon_Laser_HeatTime = 0x4
    Weapon_Laser_Bounce = 0x5
    Weapon_Laser_ReloadTime = 0x6
    Weapon_Laser_Recoil = 0x7
    Weapon_Laser_Drain = 0x8
    Weapon_Laser_StrongLaser = 0x9
    Weapon_Laser_ChargeTime = 0xA
    Weapon_Laser_MiningBonus = 0xB
    Weapon_Projectile = 0xC
    Weapon_Projectile_Damage = 0xD
    Weapon_Projectile_Range = 0xE
    Weapon_Projectile_Rate = 0xF
    Weapon_Projectile_ClipSize = 0x10
    Weapon_Projectile_ReloadTime = 0x11
    Weapon_Projectile_Recoil = 0x12
    Weapon_Projectile_Bounce = 0x13
    Weapon_Projectile_Homing = 0x14
    Weapon_Projectile_Dispersion = 0x15
    Weapon_Projectile_BulletsPerShot = 0x16
    Weapon_Projectile_MinimumCharge = 0x17
    Weapon_Projectile_MaximumCharge = 0x18
    Weapon_Projectile_BurstCap = 0x19
    Weapon_Projectile_BurstCooldown = 0x1A
    Weapon_ChargedProjectile = 0x1B
    Weapon_ChargedProjectile_ChargeTime = 0x1C
    Weapon_ChargedProjectile_CooldownDuration = 0x1D
    Weapon_ChargedProjectile_Drain = 0x1E
    Weapon_ChargedProjectile_ExtraSpeed = 0x1F
    Weapon_Rail = 0x20
    Weapon_Shotgun = 0x21
    Weapon_Burst = 0x22
    Weapon_Flame = 0x23
    Weapon_Cannon = 0x24
    Weapon_Grenade = 0x25
    Weapon_Grenade_Damage = 0x26
    Weapon_Grenade_Radius = 0x27
    Weapon_Grenade_Speed = 0x28
    Weapon_Grenade_Bounce = 0x29
    Weapon_Grenade_Homing = 0x2A
    Weapon_Grenade_Clusterbomb = 0x2B
    Weapon_TerrainEdit = 0x2C
    Weapon_SunLaser = 0x2D
    Weapon_SoulLaser = 0x2E
    Weapon_MineGrenade = 0x2F
    Weapon_FrontShield = 0x30
    Weapon_Scope = 0x31
    Weapon_Spawner = 0x32
    Weapon_SpawnerAlt = 0x33
    Weapon_Melee = 0x34
    Weapon_StunGrenade = 0x35
    Weapon_Stealth = 0x36
    Weapon_Scan = 0x37
    Weapon_Scan_Radius = 0x38
    Weapon_Scan_Recharge_Time = 0x39
    Weapon_Scan_Types = 0x3A
    Weapon_Scan_Binoculars = 0x3B
    Weapon_Scan_Discovery_Creature = 0x3C
    Weapon_Scan_Discovery_Flora = 0x3D
    Weapon_Scan_Discovery_Mineral = 0x3E
    Weapon_Scan_Secondary = 0x3F
    Weapon_Scan_Terrain_Resource = 0x40
    Weapon_Scan_Surveying = 0x41
    Weapon_Scan_BuilderReveal = 0x42
    Weapon_Fish = 0x43
    Weapon_Stun = 0x44
    Weapon_Stun_Duration = 0x45
    Weapon_Stun_Damage_Multiplier = 0x46
    Weapon_FireDOT = 0x47
    Weapon_FireDOT_Duration = 0x48
    Weapon_FireDOT_DPS = 0x49
    Weapon_FireDOT_Damage_Multiplier = 0x4A
    Suit_Armour_Health = 0x4B
    Suit_Armour_Shield = 0x4C
    Suit_Armour_Shield_Strength = 0x4D
    Suit_Energy = 0x4E
    Suit_Energy_Regen = 0x4F
    Suit_Protection = 0x50
    Suit_Protection_Cold = 0x51
    Suit_Protection_Heat = 0x52
    Suit_Protection_Toxic = 0x53
    Suit_Protection_Radiation = 0x54
    Suit_Protection_Spook = 0x55
    Suit_Protection_Pressure = 0x56
    Suit_Underwater = 0x57
    Suit_UnderwaterLifeSupport = 0x58
    Suit_DamageReduce_Cold = 0x59
    Suit_DamageReduce_Heat = 0x5A
    Suit_DamageReduce_Toxic = 0x5B
    Suit_DamageReduce_Radiation = 0x5C
    Suit_Protection_HeatDrain = 0x5D
    Suit_Protection_ColdDrain = 0x5E
    Suit_Protection_ToxDrain = 0x5F
    Suit_Protection_RadDrain = 0x60
    Suit_Protection_WaterDrain = 0x61
    Suit_Protection_SpookDrain = 0x62
    Suit_Stamina_Strength = 0x63
    Suit_Stamina_Speed = 0x64
    Suit_Stamina_Recovery = 0x65
    Suit_Jetpack = 0x66
    Suit_Jetpack_Tank = 0x67
    Suit_Jetpack_Drain = 0x68
    Suit_Jetpack_Refill = 0x69
    Suit_Jetpack_Ignition = 0x6A
    Suit_Jetpack_DoubleJump = 0x6B
    Suit_Jetpack_WaterEfficiency = 0x6C
    Suit_Jetpack_MidairRefill = 0x6D
    Suit_Refiner = 0x6E
    Suit_AutoTranslator = 0x6F
    Suit_Utility = 0x70
    Suit_RocketLocker = 0x71
    Suit_FishPlatform = 0x72
    Suit_FoodUnit = 0x73
    Suit_Denier = 0x74
    Suit_Vehicle_Summon = 0x75
    Ship_Weapons_Guns = 0x76
    Ship_Weapons_Guns_Damage = 0x77
    Ship_Weapons_Guns_Rate = 0x78
    Ship_Weapons_Guns_HeatTime = 0x79
    Ship_Weapons_Guns_CoolTime = 0x7A
    Ship_Weapons_Guns_Scale = 0x78B
    Ship_Weapons_Guns_BulletsPerShot = 0x7C
    Ship_Weapons_Guns_Dispersion = 0x7D
    Ship_Weapons_Guns_Range = 0x7E
    Ship_Weapons_Guns_Damage_Radius = 0x7F
    Ship_Weapons_Lasers = 0x80
    Ship_Weapons_Lasers_Damage = 0x81
    Ship_Weapons_Lasers_HeatTime = 0x82
    Ship_Weapons_Missiles = 0x83
    Ship_Weapons_Missiles_NumPerShot = 0x84
    Ship_Weapons_Missiles_Speed = 0x85
    Ship_Weapons_Missiles_Damage = 0x86
    Ship_Weapons_Missiles_Size = 0x87
    Ship_Weapons_Shotgun = 0x88
    Ship_Weapons_MiniGun = 0x89
    Ship_Weapons_Plasma = 0x8A
    Ship_Weapons_Rockets = 0x8B
    Ship_Weapons_ShieldLeech = 0x8C
    Ship_Armour_Shield = 0x8D
    Ship_Armour_Shield_Strength = 0x8E
    Ship_Armour_Health = 0x8F
    Ship_Scan = 0x90
    Ship_Scan_EconomyFilter = 0x91
    Ship_Scan_ConflictFilter = 0x92
    Ship_Hyperdrive = 0x93
    Ship_Hyperdrive_JumpDistance = 0x94
    Ship_Hyperdrive_JumpsPerCell = 0x95
    Ship_Hyperdrive_QuickWarp = 0x96
    Ship_Launcher = 0x97
    Ship_Launcher_TakeOffCost = 0x98
    Ship_Launcher_AutoCharge = 0x99
    Ship_PulseDrive = 0x9A
    Ship_PulseDrive_MiniJumpFuelSpending = 0x9B
    Ship_PulseDrive_MiniJumpSpeed = 0x9C
    Ship_Boost = 0x9D
    Ship_Maneuverability = 0x9E
    Ship_BoostManeuverability = 0x9F
    Ship_LifeSupport = 0xA0
    Ship_Drift = 0xA1
    Ship_Teleport = 0xA2
    Ship_CargoShield = 0xA3
    Ship_WaterLandingJet = 0xA4
    Freighter_Hyperdrive = 0xA5
    Freighter_Hyperdrive_JumpDistance = 0xA6
    Freighter_Hyperdrive_JumpsPerCell = 0xA7
    Freighter_MegaWarp = 0xA8
    Freighter_Teleport = 0xA9
    Freighter_Fleet_Boost = 0xAA
    Freighter_Fleet_Speed = 0xAB
    Freighter_Fleet_Fuel = 0xAC
    Freighter_Fleet_Combat = 0xAD
    Freighter_Fleet_Trade = 0xAE
    Freighter_Fleet_Explore = 0xAF
    Freighter_Fleet_Mine = 0xB0
    Vehicle_Boost = 0xB1
    Vehicle_Engine = 0xB2
    Vehicle_Scan = 0xB3
    Vehicle_EngineFuelUse = 0xB4
    Vehicle_EngineTopSpeed = 0xB5
    Vehicle_BoostSpeed = 0xB6
    Vehicle_BoostTanks = 0xB7
    Vehicle_Grip = 0xB8
    Vehicle_SkidGrip = 0xB9
    Vehicle_SubBoostSpeed = 0xBA
    Vehicle_Laser = 0xBB
    Vehicle_LaserDamage = 0xBC
    Vehicle_LaserHeatTime = 0xBD
    Vehicle_LaserStrongLaser = 0xBE
    Vehicle_Gun = 0xBF
    Vehicle_GunDamage = 0xC0
    Vehicle_GunHeatTime = 0xC1
    Vehicle_GunRate = 0xC2
    Vehicle_StunGun = 0xC3
    Vehicle_TerrainEdit = 0xC4
    Vehicle_FuelRegen = 0xC5
    Vehicle_AutoPilot = 0xC6
    Vehicle_Flame = 0xC7
    Vehicle_FlameDamage = 0xC8
    Vehicle_FlameHeatTime = 0xC9
    Vehicle_Refiner = 0xCA


# make empty classes to already use it in the structs definition
class cGcProductData(ctypes.Structure):
    pass


class cGcRealityManager(ctypes.Structure):
    GenerateProceduralProduct = nms_structs.cGcRealityManager._GenerateProceduralProduct_2
    GenerateProceduralTechnology = nms_structs.cGcRealityManager.GenerateProceduralTechnology


class cGcStatsBonus(ctypes.Structure):
    pass


class cGcTechnology(ctypes.Structure):
    pass


# endregion

# region Structs Fields

STRUCTS_FIELDS = {
    "BaseValue": (ctypes.c_int32, 0x4),
    "Bonus": (ctypes.c_float, 0x4),
    "Description": (nms_structs_common.cTkDynamicString, 0x10),
    "Level": (ctypes.c_int32, 0x4),
    "NameLower": (nms_structs_common.cTkFixedString[0x80], 0x80),
    "PendingNewTechnologies": (std.vector[ctypes.POINTER(cGcTechnology)], 0x18),
    "Stat": (nms_structs.cGcStatsTypes, 0x4),
    "StatBonuses": (nms_structs_common.cTkDynamicArray[cGcStatsBonus], 0x10),
}

# offsets can be taken from MBINCompiler
STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_413 = [("BaseValue", 0x1E4), ("Description", 0x120), ("NameLower", 0x090)]
STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_520 = [("BaseValue", 0x16C), ("Description", 0x0F8), ("NameLower", 0x238)]
STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_561 = [("BaseValue", 0x174), ("Description", 0x100), ("NameLower", 0x24C)]

STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_413 = [("PendingNewTechnologies", 0x238)]
STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_520 = [("PendingNewTechnologies", 0x238)]  # TODO changed
STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_561 = [("PendingNewTechnologies", 0x238)]  # TODO changed again?

# must contain all fields as it is used in an array
STRUCTS_FIELDS_OFFSETS_STATSBONUS_413 = [("Bonus", 0x4), ("Level", 0x8), ("Stat", 0x0)]
STRUCTS_FIELDS_OFFSETS_STATSBONUS_520 = [("Bonus", 0x0), ("Level", 0x4), ("Stat", 0x8)]

STRUCTS_FIELDS_OFFSETS_TECHNOLOGY_413 = [("NameLower", 0x0B0), ("StatBonuses", 0x298)]
STRUCTS_FIELDS_OFFSETS_TECHNOLOGY_520 = [("NameLower", 0x244), ("StatBonuses", 0x158)]


def _class_fields(cls, structs_fields_offsets):
    if not hasattr(cls, "_fields_"):
        cls._fields_ = _generate_fields(structs_fields_offsets[_binary_hash_index()])


def _generate_fields(structs_fields_offsets: list[tuple[str, int]]):
    fields = sorted(structs_fields_offsets, key=lambda f: f[1])  # sort fields by offset
    result = []
    for i, (field, offset) in enumerate(fields):
        if i == 0:
            h = 0x0  # no previous offset
            struct, size = STRUCTS_FIELDS[field][0], 0x0  # no previous size
        else:
            previous_field, previous_offset = fields[i-1]

            h = previous_offset  # previous offset
            struct, size = STRUCTS_FIELDS[field][0], STRUCTS_FIELDS[previous_field][1]  # previous size

        padding = offset - size - h
        if padding:
            result.append((f"_padding_{i}", ctypes.c_ubyte * padding))
        result.append((field, struct))

    return result


# endregion

# region Call Signatures

FUNCDEFS_LANGUAGEMANAGERBASE_LOAD_413 = FUNCDEF(restype=None, argtypes=[ctypes.c_ulonglong                                   ])
FUNCDEFS_LANGUAGEMANAGERBASE_LOAD_520 = FUNCDEF(restype=None, argtypes=[ctypes.c_ulonglong, ctypes.c_ulonglong, ctypes.c_char])


def _call_sigs(key, func_call_sigs):
    call_sigs.FUNC_CALL_SIGS[key] = func_call_sigs[_binary_hash_index()]


# endregion

# region Patterns

# search for "LANGUAGE\\%s_%s.MBIN" around the latest offset
PATTERNS_LANGUAGEMANAGERBASE_LOAD_413 = "48 89 5C 24 18 48 89 6C 24 20 57 48 81 EC 20"
PATTERNS_LANGUAGEMANAGERBASE_LOAD_520 = "48 89 5C 24 10 57 48 81 EC 20 01 00 00 33"

# search for "Metadata/Simulation/Missions/Tables/MissionTable.mXml" around the latest offset
PATTERNS_REALITYMANAGER_CONSTRUCT_413 = "48 8B C4 48 89 48 08 55 53 56 57 48 8D A8 88"
PATTERNS_REALITYMANAGER_CONSTRUCT_520 = "48 89 4C 24 08 55 53 56 57 41 54 41 56 41 57 48 8D AC 24 E0"
PATTERNS_REALITYMANAGER_CONSTRUCT_561 = "48 8B C4 48 89 48 08 55 53 56 57 41 54 41 56"

# search for "ITEMGEN_FORMAT_FREI_PASS" around the latest offset
PATTERNS_REALITYMANAGER_GENERATEPROCEDURALPRODUCT_413 = "48 89 54 24 10 48 89 4C 24 08 55 53 41 55 48"
PATTERNS_REALITYMANAGER_GENERATEPROCEDURALPRODUCT_520 = "48 89 54 24 10 48 89 4C 24 08 55 53 41 54 48"

# search for "UI_WIKI_PROC_TECH_SUB" around the latest offset
PATTERNS_REALITYMANAGER_GENERATEPROCEDURALTECHNOLOGY_413 = "44 88 44 24 18 48 89 4C 24 08 55 56 41"
PATTERNS_REALITYMANAGER_GENERATEPROCEDURALTECHNOLOGY_520 = "44 88 44 24 18 48 89 4C 24 08 55 41"


def _patterns(key, func_patterns):
    patterns.FUNC_PATTERNS[key] = func_patterns[_binary_hash_index()]


# endregion


def _binary_hash_index() -> int:
    # get the index of current hash
    return list(KNOWN_BINARY_HASH.keys()).index(pymhf_internal.BINARY_HASH)


KNOWN_BINARY_HASH = {
    "014f5fd1837e2bd8356669b92109fd3add116137": "4.13",  # (GOG.dev)
    "239fac0224333873c733c4e5b4d9694ea6cc0b41": "5.20",  # (GOG.com)
    "0969a2aa4e7c025bf99d6e9a807da85a9110fbc2": "5.61",  # (GOG.com)
}
if pymhf_internal.BINARY_HASH in KNOWN_BINARY_HASH:
    _class_fields(cGcProductData, [
        STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_413,
        STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_520,
        STRUCTS_FIELDS_OFFSETS_PRODUCTDATA_561,
    ])
    _class_fields(cGcRealityManager, [
        STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_413,
        STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_520,
        STRUCTS_FIELDS_OFFSETS_REALITYMANAGER_561,
    ])
    _class_fields(cGcStatsBonus, [
        STRUCTS_FIELDS_OFFSETS_STATSBONUS_413,
        STRUCTS_FIELDS_OFFSETS_STATSBONUS_520,
        STRUCTS_FIELDS_OFFSETS_STATSBONUS_520,
    ])
    _class_fields(cGcTechnology, [
        STRUCTS_FIELDS_OFFSETS_TECHNOLOGY_413,
        STRUCTS_FIELDS_OFFSETS_TECHNOLOGY_520,
        STRUCTS_FIELDS_OFFSETS_TECHNOLOGY_520,
    ])

    _call_sigs("cTkLanguageManagerBase::Load", [
        FUNCDEFS_LANGUAGEMANAGERBASE_LOAD_413,
        FUNCDEFS_LANGUAGEMANAGERBASE_LOAD_520,
        FUNCDEFS_LANGUAGEMANAGERBASE_LOAD_520,
    ])

    _patterns("cTkLanguageManagerBase::Load", [
        PATTERNS_LANGUAGEMANAGERBASE_LOAD_413,  # 4.13 (offset="0x24D5E90")
        PATTERNS_LANGUAGEMANAGERBASE_LOAD_520,  # 5.20 (offset="0x23653E0")
        PATTERNS_LANGUAGEMANAGERBASE_LOAD_520,  # 5.61 (offset="0x262C940")
    ])
    _patterns("cGcRealityManager::Construct", [
        PATTERNS_REALITYMANAGER_CONSTRUCT_413,  # 4.13 (offset="0x0BC5AF0")
        PATTERNS_REALITYMANAGER_CONSTRUCT_520,  # 5.20 (offset="0x0D14080")
        PATTERNS_REALITYMANAGER_CONSTRUCT_561,  # 5.61 (offset="0x0D61800")
    ])
    _patterns("cGcRealityManager::GenerateProceduralProduct", [
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALPRODUCT_413,  # 4.13 (offset="0x0BCEAE0")
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALPRODUCT_520,  # 5.20 (offset="0x0D218B0")
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALPRODUCT_520,  # 5.61 (offset="0x0D6F0B0")
    ])
    _patterns("cGcRealityManager::GenerateProceduralTechnology", [
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALTECHNOLOGY_413,  # 4.13 (offset="0x0BD1E00")
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALTECHNOLOGY_520,  # 5.20 (offset="0x0D24F40")
        PATTERNS_REALITYMANAGER_GENERATEPROCEDURALTECHNOLOGY_520,  # 5.61 (offset="0x0D72AD0")
    ])

    enums = [
        eStatsType_413,
        eStatsType_520,
        eStatsType_561,
    ]
    eStatsType = enums[_binary_hash_index()]

# endregion


# region Configuration

FREE_MEMORY_STEPS = 250  # multiple of it should be TOTAL_SEEDS

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
}

# endregion

# region Data

PI_ROOT = os.path.realpath(f"{os.path.dirname(__file__)}\\..")  # use Pi root directory as starting point

PRODUCT = [  # ordered by occurrence in GcProceduralProductTable
    "LOOT",
    "HIST",
    "BIO",
    "FOSS",
    "PLNT",
    "TOOL",
    "FARM",
    "SEA",
    "FEAR",
    "SALV",
    "BONE",
    "DARK",
    "STAR",
    "EXH",

    # ! No treasure and therefore not really relevant for generating its value.
    # "PASS",  # FreighterPassword
    # "CAPT",  # FreighterCaptLog
    # "CREW",  # FreighterCrewList
    # "UP_FRHYP",  # FreighterTechHyp
    # "UP_FRSPE",  # FreighterTechSpeed
    # "UP_FRFUE",  # FreighterTechFuel
    # "UP_FRTRA",  # FreighterTechTrade
    # "UP_FRCOM",  # FreighterTechCombat
    # "UP_FRMIN",  # FreighterTechMine
    # "UP_FREXP",  # FreighterTechExp
    # "LUMP",  # DismantleBio
    # "COG",   # DismantleTech
    # "DATA",  # DismantleData
    # "BOTT",  # MessageInBottle
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
        "UP_MFIRE": ["2", "3", "4"],
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
    "Submarine": {
        "UP_EXSUB": ["1", "2", "3", "4"],
        "UP_SUGUN": ["1", "2", "3", "4"],
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

    def increment(self):
        self.lock.acquire()
        try:
            self.value += 1
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

            if isinstance(field, nms_structs_common.cTkDynamicArray):
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

# region Translation

LANGUAGES = [  # order defined by nms_enums.eLanguageRegion
    "Name (en)",
    "Name (fr)",
    "Name (it)",
    "Name (de)",
    "Name (es)",
    "Name (ru)",
    "Name (pl)",
    "Name (nl)",
    "Name (pt)",
    "Name (es-419)",
    "Name (pt-BR)",
    "Name (ja)",
    "Name (zh-Hans)",
    "Name (zh-Hant)",
    "Name (ko)",
]

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

# endregion


@dataclass
class PiModState(ModState):
    # does not work at the moment due to "access violation reading" (a multi threading issue)
    # executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="Pi_Executor")

    language = None  # name of column to write the name in, will be set automatically

    is_fully_booted : bool = False
    is_generation_started : bool = False
    is_reality_manager_constructed : bool = False

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


class PiMod(NMSMod):
    __NMSPY_required_version__ = "0.7.0"

    __author__ = "zencq"
    __description__ = "Generate data for all procedural items."
    __version__ = "1.2.0"

    def __init__(self):
        super().__init__()
        self.state = PiModState()

    # region Construct

    @hooks.cGcRealityManager.Construct.after
    def hook_reality_manager_construct_after(self, this):
        logging.debug(f">> Pi: hook_reality_manager_construct_after > {this}")
        self.reality_manager = map_struct(this, cGcRealityManager)
        self.state.is_reality_manager_constructed = True

    @on_fully_booted
    def enable_generation_on_fully_booted(self):
        self.state.fully_booted = True
        logging.info(f">> Pi: The game is now fully booted.")


    # endregion

    # region GUI

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

    # region Language

    def update_language(self, offset):
        language_manager = map_struct(offset, nms_structs.cTkLanguageManagerBase)
        result = original = language_manager.meRegion
        if original == nms_enums.eLanguageRegion.LR_USEnglish:
            result = nms_enums.eLanguageRegion.LR_English
        if original > 0x1:  # -1 in total
            result -= 1
        if original > 0xF:  # -2 in total
            result -= 1

        self.state.language = LANGUAGES[result]

        logging.info(f">> Pi: Language loaded is {original} > {result} > {self.state.language}")

    @hooks.cTkLanguageManagerBase.Load.after
    def hook_language_manager_load_after(self, this, *args):
        logging.debug(f">> Pi: hook_language_manager_load_after")
        self.update_language(this)

    @staticmethod
    def extract_previous_languages(read_rows, seed):
        if seed < len(read_rows):  # just in case read file has less rows than expected
            # add all languages and get previous translations or empty string
            return {
                language: read_rows[seed].get(language, "") or ("zh-Hans" in language and read_rows[seed].get("Name (zh-CN)", "")) or ("zh-Hant" in language and read_rows[seed].get("Name (zh-TW)", "")) or ""
                for language in LANGUAGES
            }

        return {}

    # endregion

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
            writer.write_table(table)

    # endregion

    @gui_button("Start Generating")
    def start_generating(self):
        if pymhf_internal.BINARY_HASH not in KNOWN_BINARY_HASH:
            logging.error(f">> Pi: The used executable is unknown. This mod only works with the following GOG.com versions: {', '.join(KNOWN_BINARY_HASH.values())}")
            return

        if not all([self.state.is_reality_manager_constructed]):
            logging.error(f">> Pi: Not all required objects could be constructed. Please ensure all functions are set up correctly, then restart and try again.")
            return

        if not self.state.fully_booted:
            logging.error(f">> Pi: The game is not fully booted yet. Try again after it says it is.")
            return

        if self.state.is_generation_started:
            logging.warning(f">> Pi: Please wait until the currently running generation has finished...")
            return

        self.state.is_generation_started = True

        if self.product_generation_enabled:
            self.start_generating_procedural_product()
        if self.technology_generation_enabled:
            self.start_generating_procedural_technology()

        self.state.is_generation_started = False

    # region Product

    @try_except
    def start_generating_procedural_product(self):
        self.state.product_counter_total = len(self.state.product_manual or PRODUCT)
        self.state.product_start_time = datetime.now()

        logging.info(f">> Pi: Generation for {self.state.product_counter_total} {'PRODUCT' if self.state.product_counter_total == 1 else 'PRODUCTS'} started...")

        for item_id in PRODUCT:
            item_name = f"PROC_{item_id}"
            if not self.state.product_manual or (item_id in self.state.product_manual) or (item_name in self.state.product_manual):
                self.state.product_counter[0].increment()
                # TODO make executor work again
                # self.state.executor.submit(self.generate_procedural_product, item_name)  # ! access violation reading 0x0000000000000018
                self.generate_procedural_product(item_name)

    @try_except
    def generate_procedural_product(self, item_name):
        available = True
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\Product\\{item_name}"

        read_rows = self.read_existing_file(f_name)

        for seed in range(TOTAL_SEEDS):
            pointer = self.reality_manager.GenerateProceduralProduct(f"{item_name}#{seed:05}".encode("utf-8"))
            try:
                generated = map_struct(pointer, cGcProductData)
            except ValueError:
                available = False
                logging.warning(f"  ! {item_name} > Product not available in your game version.")  # one space less as warning moves it one to the right
                break

            # carry over all previous translations
            row = self.extract_previous_languages(read_rows, seed)

            # add seed and current translation
            row.update({
                self.state.language: str(generated.NameLower).strip(),  # name for current language
                "Age": int(RE_PRODUCT_AGE.findall(str(generated.Description))[0]),
                "Seed": seed,
                "Value": generated.BaseValue,
            })

            # update to track meta values
            if not meta:
                logging.debug(f"     > Age > {row.get('Age')}")
                logging.debug(f"     > Value > {generated.BaseValue}")
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

            logging.info(f"   > {item_name} > {datetime.now() - item_start_time}")

        self.state.product_counter[1].increment()
        self.check_procedural_product_generation_finished()

    def check_procedural_product_generation_finished(self):
        if self.state.product_counter[0].value == self.state.product_counter[1].value == self.state.product_counter_total:
            logging.info(f">> Pi: PRODUCT generation finished in {datetime.now() - self.state.product_start_time}!")
            self.state.product_counter[0].reset()
            self.state.product_counter[1].reset()

    # endregion

    # region Technology

    @try_except
    def start_generating_procedural_technology(self):
        self.state.technology_counter_total = (self.state.technology_manual and len([True for inventory_type, items in TECHNOLOGY.items() for item_id, qualities in items.items() for quality in qualities if any((key in self.state.technology_manual) for key in [inventory_type, item_id, f"{item_id}{quality}"])])) or sum(len(qualities) for items in TECHNOLOGY.values() for qualities in items.values())
        self.state.technology_start_time = datetime.now()

        logging.info(f">> Pi: Generation for {self.state.technology_counter_total} {'TECHNOLOGY' if self.state.technology_counter_total == 1 else 'TECHNOLOGIES'} started...")

        for inventory_type, items in TECHNOLOGY.items():
            for item_id, qualities in items.items():
                for quality in qualities:
                    item_name = f"{item_id}{quality}"
                    if not self.state.technology_manual or any((key in self.state.technology_manual) for key in [inventory_type, item_id, item_name]):
                        self.state.technology_counter[0].increment()
                        # TODO make executor work again
                        # self.state.executor.submit(self.generate_procedural_technology, inventory_type, item_name)  # ! access violation reading
                        self.generate_procedural_technology(inventory_type, item_name)

    @try_except
    def generate_procedural_technology(self, inventory_type, item_name):
        available = True
        item_start_time = datetime.now()
        meta = {}  # keep track of min/max/weighting for perfection calculation
        number = 0  # maximum number of unique stats per seed
        result = []  # result for each seed

        f_name = f"{PI_ROOT}\\{inventory_type}\\{item_name}"

        read_rows = self.read_existing_file(f_name)

        for seed in range(TOTAL_SEEDS):
            pointer = self.reality_manager.GenerateProceduralTechnology(f"{item_name}#{seed:05}".encode("utf-8"), False)
            try:
                generated = map_struct(pointer, cGcTechnology)
            except ValueError:
                available = False
                logging.warning(f"  ! {item_name} > Technology not available in your game version.")  # one space less as warning moves it one to the right
                break

            number = max(number, len(generated.StatBonuses.value))
            row = self.extract_previous_languages(read_rows, seed)  # carry over all previous translations

            # add seed and current translation
            row.update({
                self.state.language: str(generated.NameLower).strip(),  # name for current language
                "Seed": seed,
            })

            # update to track meta values
            for stat_bonus in generated.StatBonuses.value:
                stat = safe_assign_enum(eStatsType, stat_bonus.Stat._meStatsType).name
                stat_value = row[stat] = self.transform_value(stat, stat_bonus.Bonus)  # add in-game like value of a stat

                if stat not in meta:
                    logging.debug(f"     > {stat} > {stat_bonus.Bonus} > {stat_value}")  # to see how the value looks
                    meta[stat] = [stat_value, stat_value]
                else:
                    meta[stat] = [
                        min(meta[stat][0], stat_value),
                        max(meta[stat][1], stat_value),
                    ]

            # add completed row to result
            result.append(row)

            if seed % FREE_MEMORY_STEPS == 0:
                # Clear the pending new technologies to free up some memory.
                # Note that this may cause some internal issues in the game, so maybe don't load the game... But maybe not? I dunno!
                self.reality_manager.PendingNewTechnologies.clear()

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

            logging.info(f"   > {item_name} > {datetime.now() - item_start_time}")

        self.state.technology_counter[1].increment()
        self.check_procedural_technology_generation_finished()

    # transform raw value to look more like in-game
    @staticmethod
    def transform_value(stat, bonus):
        if stat not in TRANSFORM:
            logging.warning(f"     > not in TRANSFORM > {stat} > {bonus}")

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
            logging.info(f">> Pi: TECHNOLOGY generation finished in {datetime.now() - self.state.technology_start_time}!")
            self.state.technology_counter[0].reset()
            self.state.technology_counter[1].reset()

    # endregion
