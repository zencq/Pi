# Every Item Procedural

This repository contains a collection of CSV files with values of stats for every
procedural item in [**No Man's Sky**](https://www.nomanssky.com/). This includes
mainly technology upgrades but also the products (artifacts in-game).

## Usage

Each file includes the seed, procedural name, its perfection in percent (weighted),
and the actual stats. The files itself and the stats are named with game internal
names but you can use them without any developer knowledge.

There might be an ultra-low percentage of values that are not 100% accurate. There
are also cases where the value of a stat cannot be determined exactly due to how
it is displayed (e.g. `UP_RAIL1` has a damage range from `30` to `40` but always
shows `+2%`).

Upgrades for specific environmental shielding (Toxic, Radiation, Heat, Cold, Underwater)
are not include as their stats are not visible in-game.

## You can help

As it is pretty time consuming to keep all the files up to date it would be great
to have some help! To make it as easy as possible, this repository also contains
some Python scripts that can be used to gather the data. They base on those shared
by **ICE** and **DarkWalker** in the **No Man's Sky [Creative & Sharing Hub](https://discord.gg/RSGQFQv2pP)**.

To run them properly, you need [Python 3.8](https://www.python.org) or newer.

All obfuscated saves will work, regardless of it compression state (before and after
the Frontiers update) but make sure you have no technology packages (that were added
in the Waypoint update) in your save.

After executing all steps below and successfully creating a file, please create
a [pull request](https://github.com/zencq/Pi/pulls) with a note which game version
you used and I will merge them eventually.

### Prepare your save

The first script **prepare**s your **save** by adding the seeds to it. If you need
to, you can easily split this step into multiple parts by appending the current
iteration and how many you need in total.

In general the easiest way is to make a separate (creative) save and gather everything
you need in access range around you. The required Starship type will be automatically
be set as well as the required Exocraft be made active, no need to manually switch
to the correct ship/vehicle. The script will load the items into the inventories
according to this list:
* Freighter Technology: Freighter Inventory
* Product: Cargo Inventory of Exosuit
* Regular Starship Technology: Inventory of Starship
* Living Ship Technology: Inventory of Starship
* Exosuit Technology: Exosuit Inventory
* Exocraft Technology: Inventory of Colossus
* Submarine Technology: Inventory of Nautilon
* Mech Technology: Inventory of Minotaur
* Multi-Tool Technology: Inventory of Weapon

```
python prepare_save.py PATH_TO_SAVE ITEM_ID [ITERATION TOTAL_ITERATIONS]
```

### Read the data

The second script is the main one and **read**s the procedural **data** directly
from memory. To do so, load the prepared save (may take awhile), navigate to
the prepared inventory, and hover the cursor over the first item to reveal its stats.
Then you can use [Cheat Engine](https://cheatengine.org/downloads.php) to find the
corresponding addresses of the item itself, the name, the description, and each of
the up to four stats.

To do so hover over the most top-left slot and let the pop-up appear. If it is occupied
with something else, use the first from the left in the top row. Then search in
Cheat Engine for the first seed (e.g. `UP_EXGUN1#0` or `UP_EXGUN1#50000`) and modify
the results until you see the data in the pop-up changing. Then you can search for
the other addresses shown in the example command below by switching back and forth
and trying further seeds until you found the right ones. The addresses of the stats
must be entered in the same order or as shown in the description as it is the only
indicator which stat is in which position. Do not forget to get all address of the
maximum possible number of stats. If the first seed only shows two stats but the
maximum is four, you have to find one or more seeds you can get the remaining two
addresses with.

If you know how to automate this process with a script within Cheat Engine let me
know and feel free to add it via pull request.

In the translation composition region you will find the english names of the stats
as well as templates to find the descritpion which is important to get the correct
values for each stat.

Since the Waypoint update non-uppercase-only names of the items are no longer obtainable
via the script as they are now only shown in-game when you move an item. Therefore
the script reuses the names that are already in the existing files if possible.
If its no new item, you can enter anything instead of the real address as it will
be ignored and not read from memory.

The `TOTAL_ITERATIONS` here must match those from the preparation script (that defaults
to `1` if not set). You can directly enter the addresses as they are displayed in
Cheat Engine and don't need to add the `0x`.

WARNING: Depending on the inventory type and the number of seeds you added, it may
take a few minutes until the game shows the loading screen and the stays black until
then. If it takes longer than 5 to 10 minutes you should split it up by using more
iterations.

```
python read_data.py TOTAL_ITERATIONS ADDRESS_ITEM_SEED ADDRESS_DESCRIPTION ADDRESS_NAME ADDRESS_STAT1 [ADDRESS_STAT2 [ADDRESS_STAT3 [ADDRESS_STAT4]]]
```

### Recompute if necessary

The third script **recompute**s the **perfection** of all entries in a file. This can
be necessary if you want to changed the digits or the values range is different than you
thought when you run the main script to gather the data.

Just uncomment the items inside the script and run it to recompute them.

```
python recompute_perfection.py
```
