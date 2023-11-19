# Every Item Procedural

This repository contains a collection of CSV files with values of stats for every
procedural item in [**No Man's Sky**](https://www.nomanssky.com/). This includes
mainly technology upgrades but also the products (artifacts in-game).

## Usage

Each file includes the seed, its perfection in percent (weighted), the actual stats,
and procedural name for different languages. The files itself and the stats are
named with game internal names but you can use them without any developer knowledge.

All values are shown without rounding and without regard to its sign as it does
not matter for the purpose of this. Most, but not all stats are shown in a in-game
like form (e.g. `UP_RAIL1` always shows `+2%` but has actually a range from `30`
to `40`).

There is also the `Pi.xlsx` file which is a user friendly collection of all the
best seeds. It is categorized by inventory type and contains the overall best and
the best for each stat for every item.

## You can help 2.0

If you notice that some files are outdated you can help updating them! The current
implementation utilizes [NMS.py](https://github.com/monkeyman192/NMS.py) by [monkeyman192](https://github.com/monkeyman192).

It is also possible to extend the records with the generated names for your language
by running it with the game set to your language. This will not overwrite existing
names of other languages.

NMS.py is included in this repository as submodule to ensure best compatibility.
After cloning you must also execute `git submodule update --init --recursive` in
the newly created directory to initialize it.

To run an update set up NMS.py and copy the `Pi.py` in its `mod` directory
(`cp Pi.py NMS.py/mods`). Then you need to run NMS.py and load a save. The magic
begins and it will take about 30 to 45 minutes[*](#known-issues) until it is done
and the actual loading screen appears. The game window will not respond until the
update is finished but you can follow the progress in the popup with the log messages.

After everthing is done, please create a [pull request](https://github.com/zencq/Pi/pulls)
with a note what you updated and which game version you used and it will be merged
eventually.

## Known Issues

There is some sort of memory leak or so when generating the technology that makes
the execution slower and slower.

As workaround, there is an iteration mode that can be activated. It will keep track
on its own and you only have to restart the game and load a save until you are done
with all items.

To not always rewrite the products while doing this, they are disabled by default.

Iteration mode is enabled by default but you can disable it in the mod file by setting `iteration_technology` to `False`.

## Authors

* **Christian Engelhardt** (zencq) - [GitHub](https://github.com/cengelha)

## Credits

Biggest thanks goes to **monkeyman192** for creating NMS.py and the support he did
while I created the mod!

Previously used scripts based on those shared by **ICE** and **DarkWalker** in the
**No Man's Sky [Creative & Sharing Hub](https://discord.gg/RSGQFQv2pP)**.
