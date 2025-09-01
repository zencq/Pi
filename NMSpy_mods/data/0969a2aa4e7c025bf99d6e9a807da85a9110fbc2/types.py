# pyright: reportMissingImports=false
# pyright: reportReturnType=false

# built-in
import ctypes

from typing import Annotated

# pyMHF
from pymhf.core.hooking import function_hook, Structure
from pymhf.core.utils import safe_assign_enum
from pymhf.extensions.cpptypes import std
from pymhf.extensions.ctypes import c_enum32
from pymhf.utils.partial_struct import partial_struct, Field

# NMS.py
from nmspy.data import basic_types as nms_basic_types

# local
from . import enums


# region LanguageManager

@partial_struct
class cTkLanguageManagerBase(Structure):
    _Region: Annotated[enums.eLanguageRegion, Field(c_enum32[enums.eLanguageRegion], offset=0x8)]  # ("meRegion", ctypes.c_int32),

    @property
    def Region(self):
        return safe_assign_enum(enums.eLanguageRegion, self._Region)

    # search for "LANGUAGE\\%s_%s.MBIN" around the latest offset 0x262C940
    @function_hook(signature="48 89 5C 24 10 57 48 81 EC 20 01 00 00 33")
    def Load(self, this: "ctypes._Pointer[cTkLanguageManagerBase]", arg1: ctypes.c_uint64, arg2: ctypes.c_char_p) -> None:
        pass

# endregion

# region ProductData

@partial_struct
class cGcProductData(Structure):
    # offsets can be taken from https://github.com/monkeyman192/MBINCompiler/blob/v5.63.0-pre1/libMBIN/Source/NMS/GameComponents/GcProductData.cs#L8
    Description: Annotated[str, Field(nms_basic_types.cTkDynamicArray[ctypes.c_char], offset=0x100)]
    BaseValue: Annotated[int, Field(ctypes.c_int32, offset=0x174)]
    NameLower: Annotated[str, Field(nms_basic_types.cTkFixedString[0x80], offset=0x24C)]

# endregion

# region RealityManager / Technology / Stats

@partial_struct
class cGcStatsTypes(Structure):
    # offsets can be taken from https://github.com/monkeyman192/MBINCompiler/blob/v5.63.0-pre1/libMBIN/Source/NMS/GameComponents/GcStatsTypes.cs#L4
    _StatsType: Annotated[enums.eStatsType, Field(c_enum32[enums.eStatsType], offset=0x0)]  # ("_meStatsType", ctypes.c_uint32),

    @property
    def StatsType(self):
        return safe_assign_enum(enums.eStatsType, self._StatsType)


# must contain all fields as it is used in an array
@partial_struct
class cGcStatsBonus(Structure):
    # offsets can be taken from https://github.com/monkeyman192/MBINCompiler/blob/v5.63.0-pre1/libMBIN/Source/NMS/GameComponents/GcStatsBonus.cs#L6
    Bonus: Annotated[float, Field(ctypes.c_float, offset=0x0)]  # ("mfBonus", ctypes.c_float),
    Level: Annotated[int, Field(ctypes.c_int32, offset=0x4)]  # ("miLevel", ctypes.c_int32),
    Stat: Annotated[cGcStatsTypes, Field(cGcStatsTypes, offset=0x8)]  # ("mStat", cGcStatsTypes),


@partial_struct
class cGcTechnology(Structure):
    # offsets can be taken from https://github.com/monkeyman192/MBINCompiler/blob/v5.63.0-pre1/libMBIN/Source/NMS/GameComponents/GcTechnology.cs#L8
    StatBonuses: Annotated[list[cGcStatsBonus], Field(nms_basic_types.cTkDynamicArray[cGcStatsBonus], offset=0x158)]  # ("maStatBonuses", common.cTkDynamicArray[cGcStatsBonus]),
    NameLower: Annotated[str, Field(nms_basic_types.cTkFixedString[0x80], offset=0x244)]  # ("macNameLower", common.cTkFixedString[0x80]),


@partial_struct
class cGcRealityManager(Structure):
    PendingNewTechnologies: Annotated[list[int], Field(std.vector[ctypes._Pointer[cGcTechnology]], offset=0x268)]  # ("PendingNewTechnologies", std.vector[ctypes.POINTER(cGcTechnology)]),

    # search for "Metadata/Simulation/Missions/Tables/MissionTable.mXml" around the latest offset 0x0D61800
    @function_hook(signature="48 8B C4 48 89 48 08 55 53 56 57 41 54 41 56")
    def Construct(self, this: "ctypes._Pointer[cGcRealityManager]") -> None:
        pass

    # search for "ITEMGEN_FORMAT_FREI_PASS" around the latest offset 0x0D6F0B0
    @function_hook(signature="48 89 54 24 10 48 89 4C 24 08 55 53 41 54 48")
    def GenerateProceduralProduct(self, this: "ctypes._Pointer[cGcRealityManager]", lProcProdID: ctypes.c_char_p) -> ctypes.c_uint64:  # ctypes._Pointer[cGcProductData]:
        pass

    # search for "UI_WIKI_PROC_TECH_SUB" around the latest offset 0x0D72AD0
    @function_hook(signature="44 88 44 24 18 48 89 4C 24 08 55 41")
    def GenerateProceduralTechnology(self, this: "ctypes._Pointer[cGcRealityManager]", lProcTechID: ctypes.c_char_p, lbExampleForWiki: ctypes.c_bool) -> ctypes.c_uint64:  # ctypes._Pointer[cGcTechnology]:
        pass

    # offset 0x0D6E420
    @function_hook(signature="48 89 5C 24 08 45 0F")
    def GetHashedIDForTech(self, this: "ctypes._Pointer[cGcRealityManager]", result: ctypes.c_char_p, lTechID: ctypes.c_char_p) -> ctypes.c_char_p:
        pass

# endregion
