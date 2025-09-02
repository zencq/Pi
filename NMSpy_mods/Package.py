# /// script
# dependencies = ["pymhf[gui]>=0.1.16", "nmspy>=147803.1"]
#
# [tool.pymhf]
# exe = "<path to install dir>/Binaries/NMS.exe"
# start_paused = true
#
# [tool.pymhf.logging]
# window_name_override = "NMS.py: Package"
# ///

# pyright: reportAssignmentType=false
# pyright: reportMissingImports=false

# built-in
import importlib
import json
import logging
import os

from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__.lower())

# pyMHF
from pymhf import Mod, ModState
from pymhf.core import _internal as pymhf_internal
from pymhf.core.memutils import map_struct
from pymhf.gui import BOOLEAN, gui_button

# local
from common.configuration import KNOWN_BINARY_HASH
from common.decorators import try_except

# dynamically import for selected version
try:
    nms_enums = importlib.import_module(f"data.{pymhf_internal.BINARY_HASH}.enums")
    nms_types = importlib.import_module(f"data.{pymhf_internal.BINARY_HASH}.types")
except ImportError as e:
    supported = ", ".join(f"{version} ({sha1})" for sha1, version in KNOWN_BINARY_HASH.items())
    message = f"Executable '{pymhf_internal.BINARY_HASH}' is not supported. This mod only works with the following GOG.com versions: {supported}"
    logger.critical(message)
    raise e
except Exception as e:
    message = f"Error while importing specific version data: {e}"
    logger.critical(message)
    raise e

# region NMS.py

# # must be ordered in the same way as KNOWN_BINARY_HASH
# PATTERNS_REALITYMANAGER_CONSTRUCT = [  # search for "Metadata/Simulation/Missions/Tables/MissionTable.mXml" around the latest offset
#     "48 8B C4 48 89 48 08 55 53 56 57 48 8D A8 88",                 # 4.13 (offset="0x0BC5AF0")
#     "48 89 4C 24 08 55 53 56 57 41 54 41 56 41 57 48 8D AC 24 E0",  # 5.20 (offset="0x0D14080")
#     "48 8B C4 48 89 48 08 55 53 56 57 41 54 41 56",                 # 5.61 (offset="0x0D61800")
# ]
# PATTERNS_REALITYMANAGER_GETHASHEDIDFORTECH = [  # currently not used as pattern is the same for all version
#     "48 89 5C 24 08 45 0F",  # 4.13 (offset="0x0BCE030")
#     "48 89 5C 24 08 45 0F",  # 5.20 (offset="0x0D20C40")
#     "48 89 5C 24 08 45 0F",  # 5.61 (offset="0x0D6E420")
# ]


# if pymhf_internal.BINARY_HASH in KNOWN_BINARY_HASH:
#     i = KNOWN_BINARY_HASH.index(pymhf_internal.BINARY_HASH)  # get index of current hash

#     call_sigs.FUNC_CALL_SIGS["cGcRealityManager::GetHashedIDForTech"] = FUNCDEF(
#         restype=ctypes.c_char_p,  # const TkID<128> *
#         argtypes=[
#             ctypes.c_ulonglong,  # cGcRealityManager *
#             # ctypes.c_ulonglong,  # TkID<128> *  # this is probably the correct one...
#             ctypes.c_char_p,  # ...but this works with the setup below
#             ctypes.c_char_p,  # const TkID<128> *
#         ]
#     )

#     patterns.FUNC_PATTERNS["cGcRealityManager::Construct"] = PATTERNS_REALITYMANAGER_CONSTRUCT[i]
#     patterns.FUNC_PATTERNS["cGcRealityManager::GetHashedIDForTech"] = "48 89 5C 24 08 45 0F"


# def GetHashedIDForTech(self, lTechID: bytes) -> bytes:
#     this = ctypes.addressof(self)
#     return call_function("cGcRealityManager::GetHashedIDForTech", this, ctypes.c_char_p(b""), lTechID)

# endregion


# region Configuration

DIRECTORY_DATABASE = os.path.realpath("<path to database dir>")  # directory with one or more database/json files created by NomBINCompiler
DIRECTORY_OUTPUT = os.path.join(os.path.dirname(__file__), "results")

TRANSFORM = {
    ord(b"\x08"): b"\\b",
    ord(b"\x09"): b"\\t",
    ord(b"\x0A"): b"\\n",
    ord(b"\x0C"): b"\\f",
    ord(b"\x0D"): b"\\r",
}

# endregion

# region Changelog

# 1.0.0 Initial Release

# 1.0.1
#       Add more escape sequence transformations

# 1.1.0
#       Printing the used database version
#       Create a database version specific JSON file next to regular one

# 1.2.0
#       Update pyMHF to 0.1.8
#       Update NMS.py to 0.7.1
#       Add handling for different executables

# 1.3.0
#       Update pyMHF to 0.1.16
#       Update NMS.py to 147803.1
#       Add autostart option

# endregion


@dataclass
class PackageModState(ModState):
    reality_manager = None

    is_autostart : bool = True  # by default just start when ready
    is_hashing_started : bool = False
    is_ready_posted : bool = False

    package_start_time : datetime = None


class PackageMod(Mod):
    __NMSPY_required_version__ = "146194.0"

    __author__ = "zencq"
    __description__ = "Hash item_id to use for technology packages."
    __version__ = "1.3.0"

    # region Property

    state = PackageModState()  # not in __init__ to survive reloading

    @property
    def is_ready(self):
        return all([self.state.reality_manager])

    # endregion

        # region Property (GUI)

    @property
    @BOOLEAN(label="Autostart when ready")
    def is_autostart(self):
        return self.state.is_autostart

    @is_autostart.setter
    def is_autostart(self, value: bool):
        self.state.is_autostart = value

    # endregion

    # region Construct

    @nms_types.cGcRealityManager.Construct.after
    def reality_manager_construct_after(self, this):
        logger.debug(f"hook_reality_manager_construct_after -> {this}")

        self.state.reality_manager = map_struct(this, nms_types.cGcRealityManager)
        self.is_ready_execution()

    def is_ready_execution(self):
        if self.is_ready and not self.state.is_ready_posted:
            self.state.is_ready_posted = True

            if self.state.is_autostart:
                if not self.state.is_hashing_started:
                    logger.info(f"Autostart is enabled. Starting hashing now...")
                    self.start_hashing()
            else:
                logger.info(f"Everything is ready. You can now start hashing.")

    # endregion

    # region Read/Write

    # read a NomBINCompiler database to get technology
    @staticmethod
    def read_technology_from_database():
        f_latest = sorted(f for f in os.listdir(DIRECTORY_DATABASE) if f.endswith(".json") and f[0].isdigit())[-1]
        f_latest = os.path.join(DIRECTORY_DATABASE, f_latest)
        if os.path.isfile(f_latest):
            with open(f_latest, mode="rt", encoding="utf-8", newline="") as f:
                content = json.load(f)
            return content["JgA"], [technology for technology in content["4Sj"].keys() if not "_DMG" in technology and not "MAINT_" in technology]

        return "", []

    @staticmethod
    def write_result(version, hashed_dict):
        # all in one output not necessary
        # f_name = os.path.join(OUTPUT_DIRECTORY, "hashed_technology.json")
        # with open(f_name, mode="wb") as f:
        #     for key, value in result.items():
        #         f.write(key.encode("utf-8"))
        #         f.write(b"\0")
        #         f.write(value)
        #         f.write(b"\0")

        # output for libNOM.io
        f_name = os.path.join(DIRECTORY_OUTPUT, "hashed_technology.bin")
        with open(f_name, mode="wb") as f:
            for value in hashed_dict.values():
                f.write(value)
                f.write(b"\0")

        # output for NomNom
        for key, value in hashed_dict.items():
            hashed_dict[key] = "".join(f"{char:02X}" for char in value)

        f_name = os.path.join(DIRECTORY_OUTPUT, "hashed_technology.json")
        with open(f_name, mode="w", encoding="utf-8", newline="") as f:
            json.dump(hashed_dict, f)

        f_name = os.path.join(DIRECTORY_OUTPUT, f"hashed_technology_{version}.json")
        with open(f_name, mode="w", encoding="utf-8") as f:
            json.dump(hashed_dict, f, indent=4)

    # endregion

    # region Hash

    @gui_button("Start Hashing")
    def start_hashing(self):
        if not self.is_ready:
            logger.warning(f"Not all required objects have been constructed yet. Ensure that the binary has been started and you got the message that everything is ready.")
            return

        if self.state.is_hashing_started:
            logger.warning(f"Please wait until the currently running hashing has finished...")
            return

        self.state.is_hashing_started = True
        self.state.package_start_time = datetime.now()

        version, technology_list = self.read_technology_from_database()

        logger.info(f"Hashing with database {version} started...")

        hashed_dict = self.start_hashing_technology_to_package(technology_list)
        self.write_result(version, hashed_dict)

        self.state.is_hashing_started = False
        logger.info(f"Hashing finished in {datetime.now() - self.state.package_start_time}!")

    @try_except
    def start_hashing_technology_to_package(self, technology_list):
        result = {}

        for item_id in technology_list:
            hashed = self.state.reality_manager.GetHashedIDForTech(b"", item_id.encode("utf-8"))
            result[item_id] = self.transform_hashed(hashed)

        return result

    @try_except
    def transform_hashed(self, hashed):
        result = bytearray()

        for byte in hashed:
            if byte < 0x20:  # to unicode escape sequence
                result.extend(TRANSFORM.get(byte, b'\\u%04X' % byte))  # pyright: ignore[reportArgumentType]
            elif byte in [0x22, 0x5C]:  # escape with \
                result.extend(b'\\%b' % byte.to_bytes(1, "big"))
            elif ord(b'a') <= byte <= ord(b'z'):  # to upper case (61 <= .. <= 7A)
                result.append(byte - 0x20)
            else:
                result.append(byte)

        return bytes(result)

    # endregion
