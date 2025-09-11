# pyright: reportArgumentType=false
# pyright: reportCallIssue=false

import csv
import glob
import itertools
import os
import pandas
import pyarrow

from pandas import DataFrame
from typing import Any, Iterable

from . import configuration


# region Binary


def binary_is_413(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 0


def binary_is_520(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 1


def binary_is_561(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 2


def binary_is_602(binary_hash) -> int:
    return get_binary_hash_index(binary_hash) >= 3


def get_binary_hash_index(binary_hash) -> int:
    # get the index of current hash
    return list(configuration.KNOWN_BINARY_HASH.keys()).index(binary_hash)


# endregion


# region I/O


def convert_to_dataframe(records: list[dict[str, Any]]) -> DataFrame:
    df = pandas.DataFrame.from_records(records)

    # ensure all languages are present
    for language in configuration.LANGUAGES:  # necessary for new items
        if language not in df.columns:
            df.insert(0, language, "")  # index does not matter as order is defined by schema

    return df


def extract_previous_languages(read_rows, seed):
    # add all languages and get previous translations or empty string
    return {
        language: read_rows[seed].get(language, "")
        for language in configuration.LANGUAGES
    }


def read_existing_csv(f_name: str) -> list[dict[str, Any]]:
    if os.path.isfile(f"{f_name}.csv"):
        with open(f"{f_name}.csv", mode="r", encoding="utf-8") as f:
            f.readline()  # skip first line with delimiter indicator
            reader = csv.DictReader(f, dialect="excel")
            return list(reader)

    return []


def write_result(f_name: str, stat_fields: Iterable[str], result: DataFrame):
    linesep = "\n"  # os.linesep produces an empty line after every one written
    stat_fields = sorted(stat_fields)

    # csv
    columns = list(itertools.chain(configuration.FILE_GENERAL_COLUMNS.keys(), stat_fields, configuration.LANGUAGES))
    with open(f"{f_name}.csv", mode="w", encoding="utf-8") as f:
        f.write(f"sep=,{linesep}")
        result.to_csv(path_or_buf=f, columns=columns, index=False, lineterminator=linesep)

    # parquet
    schema_fields = [pyarrow.field(name, type_, nullable=False) for name, type_ in configuration.FILE_GENERAL_COLUMNS.items()] + [pyarrow.field(name, pyarrow.float64()) for name in stat_fields] + [pyarrow.field(name, pyarrow.string(), nullable=False) for name in configuration.LANGUAGES]
    result.to_parquet(path=f"{f_name}.parquet", schema=pyarrow.schema(schema_fields))


# endregion


# region Perfection


def calculate_comparable_perfection(inventory_type: str, item_id: str, columns_override: list[str]=None):
    columns_excluded = ("Seed", "Perfection", "Name")
    pattern = os.path.join(configuration.PI_ROOT, inventory_type, f"{item_id}*")

    # read files and collect data
    files = [f for f in glob.glob(pattern) if f.endswith(".parquet")]
    files_dataframe = {}
    stat_columns: dict[str, list[str]] = {}
    stat_ranges: dict[str, tuple[float, float]] = {}
    stat_names = set()
    stat_number = 0

    for file in files:
        df = pandas.read_parquet(file)

        files_dataframe[file] = df
        stat_columns[file] = columns_override or [c for c in df.columns if not any(c.startswith(excluded) for excluded in columns_excluded)]
        stat_names.update(stat_columns[file])
        stat_number = max(stat_number, max(df.loc[idx, stat_columns[file]].apply(pandas.notna).sum() for idx in range(int(configuration.TOTAL_SEEDS / 100))))

    # get global min/max for each stat
    for stat_name in stat_names:
        values = pandas.concat([df[stat_name] for df in files_dataframe.values() if stat_name in df], ignore_index=True)
        values = values.dropna()
        if not values.empty:
            stat_ranges[stat_name] = (values.min(), values.max())
        else:
            stat_ranges[stat_name] = (0.0, 0.0)

    # calculate weighting
    stat_weighting = get_weighting(stat_names, stat_ranges)

    # for each file, update rows with comparable perfection
    for file, df in files_dataframe.items():
        for idx, row in df.iterrows():
            perfection = get_perfection(row.to_dict(), stat_names, stat_number, stat_ranges, stat_weighting)
            df.at[idx, "PerfectionComparable"] = perfection

        write_result(file[:-8], stat_columns[file], df)


def get_perfection(row: dict[str, Any], stat_names: Iterable[str], stat_number: int, stat_ranges: dict[str, tuple[float, float]], stat_weighting: dict[str, tuple[float, float]]) -> float:
    perfections = []
    weight_total = 0

    for stat_name in stat_names:
        if stat_name not in row:
            continue

        stat_value = row[stat_name]

        if pandas.isna(stat_value):
            continue

        _, maximum = stat_ranges[stat_name]
        difference, weight = stat_weighting[stat_name]

        weight_total += weight

        p = 1.0
        if difference > 0:
            p -= (maximum - stat_value) / difference
        perfections.append(p * weight)

    if weight_total > 0 and stat_number > 0:  # ensure there is no ZeroDivisionError
        return (sum(perfections) / weight_total) * (len(perfections) / stat_number)
    return 0.0


def get_weighting(stat_names: Iterable[str], stat_ranges: dict[str, tuple[float, float]]):
    weighting = {
        stat: stat_ranges[stat][1] - stat_ranges[stat][0] + 1
        for stat in stat_names
    }
    weighting_min = min(weighting.values())

    return {
        stat: (stat_ranges[stat][1] - stat_ranges[stat][0], weighting[stat] / weighting_min)
        for stat in stat_names
    }


# endregion
