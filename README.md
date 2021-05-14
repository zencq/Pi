# Every Item Procedural

This repository contains a collection of CSV files with values of stats for
every procedural item in [**No Man's Sky**](https://www.nomanssky.com/). This
includes mainly technology upgrades but also the products (artifacts in game).

## Preamble

Each file includes the seed, procedural name, its perfection in percent and the
actual values of the stats.

## Usage

This repository also contains two Python scripts that can be used to generate
these CSV files by yourself. These scripts are based on those shared by **Ice#8413** and **DarkWalker#7721** in the **No Man's Sky [Seed Central](https://discord.gg/AEXcap6) Discord**.

To run them, I suggest [**Python 3.7**](https://www.python.org) or newer.

The first script **prepare**s your save by adding up to 100,000 seeds to it.
If your save wont load or for any other reason you can easily split this step into
multiple parts by appending the current iteration and how many you need in total.

```
python procedural_prepare.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_ITERATIONS]
```

This preperation is necessary as the game needs to load the data of a seed into memory
to read them with the next script.

The second script reads the **procedural** data directly from memory. To do so,
you need to hover the cursor over the first item to reveal its stats. Then you can use
[Cheat Engine](https://cheatengine.org/downloads.php) to find the coresponding
addresses of the item/seed itself, the name, the description, and each of the up to
four stats.

For me the following worked best:
1. Scan for the first seed that controls the UI (e.g. `UP_BOLT4#0`).
1. Scan for the procedural name which should result in a single address after second search.
1. Scan for the description by searching for the listed stats (e.g. `improve <STELLAR>Damage<>, <STELLAR>Clip Size<>`).
   You may end up with 2 addresses but you're looking for the one before and closest to
   the address of the name.
1. Scan for the value of each stat (e.g. `+12%`). There might be occurrences of a not changing value.
   Then scan for the others first and check on that later. All addresses for the values
   are close together and in the order you see in the description.

The `TOTAL_ITERATIONS` here should match those from the preparation script. You can
directly enter the addresses as they are displayed in Cheat Engine and don't need to prepend
a `0x`.

```
python procedural.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_TITLE ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]
```
