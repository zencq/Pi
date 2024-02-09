# Every Item Procedural

This repository contains a collection of CSV files with values of stats for every
procedural item in **[No Man's Sky](https://www.nomanssky.com/)**. This includes
mainly technology upgrades but also the products (artifacts in-game).

## Usage

Each file includes the seed, its weighted perfection in percent, the actual stats,
and procedural name for different languages. The files itself and the stats are
named with game internal names but you can use them without any developer knowledge.

All values are shown without rounding and without regard to its sign as it does
not matter for the purpose of this. Most, but not all, stats are shown in a in-game
like form (e.g. `UP_RAIL1` always shows `+2%` but has actually a range from `30`
to `40`).

There is also the `Pi.xlsx` file which is a user friendly collection of best and
most desirable seeds. It is categorized by inventory type and contains the best
values for each stat per item in addition to those already mentioned.

## You can help 2.0

If you notice that some files are outdated you can help updating them! The current
implementation utilizes [NMS.py](https://github.com/monkeyman192/NMS.py) by [monkeyman192](https://github.com/monkeyman192).

NMS.py is included in this repository as submodule to ensure best compatibility.
After cloning you must also execute `git submodule update --init --recursive` in
the newly created directory to initialize it.

To run an update set up NMS.py and copy the `Pi.py` in its `mods` directory
(`cp Pi.py NMS.py/mods`). Then you just need to run NMS.py and as soon as the save
selection appears, the magic can begin. When NMS.py runs, a distinct terminal window
opens where some information are logged. All output is prefixed with `>> Pi` or
indented below it.

It is also possible to extend the records with the generated names for your language
by running it with the game set to your language. This will not overwrite existing
names of other languages. The selected language will be shown in the log mentioned
above.

Both, technology and products, are enabled by default but and can be toggled separately.
You can toggle the technology generation by pressing `[T]` and the one for products
with `[P]`. To actually start the generation press `[Space]` and it will run a couple of
minutes (depending on your machine) in the background with some progress logging.

After the generation is done you can start it again to add another lang for example.

After everything is done, please create a [pull request](https://github.com/zencq/Pi/pulls)
with a note what you updated and which game version you used and it will be merged
eventually.

## Authors

* **Christian Engelhardt** (zencq) - [GitHub](https://github.com/cengelha)

## Credits

* Biggest thanks goes to **monkeyman192** for creating NMS.py and the support he
  did while I created the mod!

* Another thanks goes to **DHarhan** for giving feedback about the desirability
  of certain stats and combinations.

* Previously used scripts based on those shared by **ICE** and **DarkWalker** in
  the **No Man's Sky [Creative & Sharing Hub](https://discord.gg/RSGQFQv2pP)**.
