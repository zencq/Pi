# Every Item Procedural

![Maintained](https://img.shields.io/maintenance/yes/2025)
![GitHub Release](https://img.shields.io/github/v/release/zencq/Pi?display_name=release)
[![Supported by the No Man's Sky Community Developers & Designers](https://raw.githubusercontent.com/NMSCD/About/master/badge/purple.svg)](https://nmscd.com/)

This repository contains a collection of files with values of stats for every
**P**rocedural **I**tem in [No Man's Sky](https://www.nomanssky.com/). This includes
mainly technology upgrades but also the products (treasures/artifacts in-game).

## Usage

Each item has two files, one easier for humans to read (`.csv`) and one better for
programmatic processing (`.parquet`). Each file includes the seed, its weighted
perfection in percent, the actual stats, and the procedural name in different languages.
The files itself and the stats are named with the game internal names but you can
use them without any developer knowledge.

All values are shown without rounding and without regard to its sign as it does
not matter for the purpose of this. Most, but not all, stats are shown in a in-game
like form. If not, the raw value is used (e.g. `UP_RAIL1` always showed `+2%` but
actually had a range from `30` to `40`).

There is also the `Pi.xlsx` file which is a user friendly collection of best and
most desirable seeds. It is categorized by inventory type and contains the best
values for each stat per item in addition to those already mentioned.

## Known Issues

The following items are currently *outdated* or *not available* due to changes in
a newer game version than the one currently supported. The latest supported version
can be seen in the [releases here on GitHub](https://github.com/zencq/Pi/releases).

* Rusted Upgrades are *available* since **Aquarius 5.10**
  * **Mining Beam** (UP_LASER0)
  * **Analysis Visor** (UP_SCAN0)
  * **Boltcaster** (UP_BOLT0)
  * **Life Support** (UP_ENGY0)
  * **Hazard Protection** (UP_HAZ0)
  * **Movement System** (UP_JET0)
  * **Defence Systems** (UP_SHLD0)
  * **Pulse Engine** (UP_PULSE0)
  * **Launch Thruster** (UP_LAUN0)
  * **Hyperdrive** (UP_HYP0)
  * **Deflector Shield** (UP_S_SHL0)
  * **Photon Cannon** (UP_SGUN0)
* Treasure **Exhibit Fossil Sample** (PROC_EXH) is *available* since **Worlds Part II 5.50**
* The following technology is *outdated* since **Worlds Part II 5.50**
  * Illegal **Neutron Cannon** Upgrade (UP_CANNX)
  * **Aeration Membrane** Upgrades (UP_UNW)
  * **Humboldt Drive** Upgrades (UP_EXSUB)

## How it works 2.1

The current implementation utilizes [NMS.py](https://github.com/monkeyman192/NMS.py)
by [monkeyman192](https://github.com/monkeyman192).

NMS.py (and its backend [pyMHF](https://github.com/monkeyman192/pyMHF)) is included
in this repository as submodules to ensure best compatibility. After cloning you
must also execute `git submodule update --init --recursive` in the newly created
directory to initialize them.

Currently `PiMod` is designed to work with GOG.com version 4.13 as well as 5.20
and 5.61 which cover all changes/additions since 4.13.

To run it, set up NMS.py as mentioned in its [README](https://github.com/monkeyman192/NMS.py?tab=readme-ov-file#installation)
and make sure the `mod_dir` setting is set to the absolute path to the `./NMSpy_mods`
directory. Then you just need to run it and as soon as the menu appears, the magic
can begin. When NMS.py runs, a distinct terminal window opens where some information
are logged. All output is prefixed with `>> Pi` or indented below it.

It is also possible to extend the records with the generated names for multiple
languages by running it multiple times with different language settings. After a
generation is done, you can change the in-game language and immediately start it
again without restarting. This will not overwrite existing names of other languages.
The selected/new language will be shown in the log mentioned above.

Both, technology and products, are enabled by default but and can be toggled separately.
You can do so via the little UI window that opens short after the terminal. This
is also where you start the generation which will then run a couple of minutes
(depending on your machine) in the background with some progress logging. It is
also possible to set custom values for each category to only generate those specific
items (comma separated).

## Authors

* **Christian Engelhardt** (zencq) - [GitHub](https://github.com/cengelha)

## Credits

* **monkeyman192** - Biggest thanks goes to him for creating NMS.py and the support
  while I created the mod
* **DHarhan** - Giving feedback about the desirability of certain stats and combinations
* **ICE** and **DarkWalker** - Previously used scripts based on those shared by
  them in the [Creative & Sharing Hub](https://discord.gg/RSGQFQv2pP)
