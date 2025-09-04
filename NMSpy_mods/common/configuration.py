KNOWN_BINARY_HASH = {
    "014f5fd1837e2bd8356669b92109fd3add116137": "4.13",  # (GOG.dev)
    "239fac0224333873c733c4e5b4d9694ea6cc0b41": "5.20",  # (GOG.com)
    "0969a2aa4e7c025bf99d6e9a807da85a9110fbc2": "5.61",  # (GOG.com)
    "7024b107f0533de802e8ecfbed65d2c778d03c1f": "6.02",  # (GOG.com)
}

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

PRODUCT_FREIGHTER_DERELICT = [  # ordered by occurrence in GcProceduralProductTable
    "PROC_PASS",  # FreighterPassword
    "PROC_CAPT",  # FreighterCaptLog
    "PROC_CREW",  # FreighterCrewList
]
PRODUCT_FREIGHTER_TECH = [  # ordered by occurrence in GcProceduralProductTable
    "UP_FRHYP",  # FreighterTechHyp
    "UP_FRSPE",  # FreighterTechSpeed
    "UP_FRFUE",  # FreighterTechFuel
    "UP_FRTRA",  # FreighterTechTrade
    "UP_FRCOM",  # FreighterTechCombat
    "UP_FRMIN",  # FreighterTechMine
    "UP_FREXP",  # FreighterTechExp
]
PRODUCT_JUNK = [  # ordered by occurrence in GcProceduralProductTable
    "PROC_LUMP",  # DismantleBio
    "PROC_COG",   # DismantleTech
    "PROC_DATA",  # DismantleData
    "PROC_BOTT",  # MessageInBottle
]
PRODUCT_TREASURE = [  # ordered by occurrence in GcProceduralProductTable
    "PROC_LOOT",  # Loot
    "PROC_HIST",  # Document
    "PROC_BIO",  # BioSample
    "PROC_FOSS",  # Fossil
    "PROC_PLNT",  # Plant
    "PROC_TOOL",  # Tool
    "PROC_FARM",  # Farm
    "PROC_SEA",  # SeaLoot
    "PROC_FEAR",  # SeaHorror
    "PROC_SALV",  # Salvage
    "PROC_BONE",  # Bones
    "PROC_DARK",  # SpaceHorror
    "PROC_STAR",  # SpaceBones
    "PROC_EXH",  # ExhibitFossil
]
