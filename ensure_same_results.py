import os
import sys
from pathlib import Path

import math

os.environ.setdefault("PRINT_SPEEDUP", "0")
print_speedup = os.environ.get("PRINT_SPEEDUP") == "1"


def load_results(path: Path):
    data = {}
    with open(path, "r") as file:
        loaded_columns = file.readline().strip().split(";")
        columns = []
        for column in loaded_columns:
            column = column.replace("Lenght", "Length")
            columns.append(column)
        for line in file:
            values = line.strip().split(";")
            if values[0]:
                data[values[0]] = {}
                for column, value in zip(columns[1:], values[1:]):
                    data[values[0]][column] = value
    return columns, data


def print_with_columns_key(columns, data, filter_column=None):
    for key, values in data.items():
        print()
        print(f"{columns[0]}: {key}")
        for column, value in zip(columns[1:], values):
            if filter_column is None or filter_column(column):
                print(f"{column}: {value}")


def divergence(curr: float, prev: float):
    return ((curr / prev) - 1) * 100 if prev != 0 else 100


def compare_results(data1, data2):
    columns1, data1 = data1
    columns2, data2 = data2
    if any(map(lambda x: x not in columns1, columns2)):
        print("Missing stat in curr")
        print(set(columns2) - set(columns1))
    if any(map(lambda x: x not in data1.keys(), data2.keys())):
        print("Missing keys in curr")
        print(set(data2.keys()) - set(data1.keys()))
    different = False
    for key in data2.keys():
        if key not in data1:
            continue
        key_header = False
        duration_diff = ""
        for column in columns2[1:]:
            if (
                not column
                or column not in data1[key]
                or column.endswith("ConfInt")
                or not data2[key][column]
                or not data1[key][column]
            ):
                continue
            curr_s = data1[key][column]
            prev_s = data2[key][column]
            curr = float(curr_s)
            prev = float(prev_s)
            close = curr_s == prev_s
            close = close or math.isclose(curr, prev, rel_tol=1e-2)
            if not close:
                change = divergence(curr, prev)
                if column == "Run Duration":
                    if change < 0:
                        duration_diff = f" Speedup: {-change:+.2f}%"
                    else:
                        duration_diff = f"Slowdown: {-change:+.2f}%"
                    continue
                different = True
                if not key_header:
                    print(f"{columns2[0]}: {key}")
                    key_header = True
                print(f"\t{column}:")
                print(f"\t\tdivergence: {change:+.2f}%")
                if "Stability Check" not in column:
                    print(f"\t\tcurr: {data1[key][column]} {data1[key][column + ' ConfInt']}")
                    print(f"\t\tprev: {data2[key][column]} {data2[key][column + ' ConfInt']}")
                else:
                    print(f"\t\tcurr: {data1[key][column]}")
                    print(f"\t\tprev: {data2[key][column]}")
        if print_speedup and duration_diff:
            if not key_header:
                print(f"{columns2[0]}: {key}")
            print(
                f"\t{duration_diff} (curr: {data1[key]['Run Duration']} ; prev: {data2[key]['Run Duration']})"
            )
    if not different:
        print("Data is the same")


if __name__ == "__main__":
    # get the two paths from arguments
    path1 = Path(sys.argv[1])
    path2 = Path(sys.argv[2])
    data1 = load_results(path1)
    data2 = load_results(path2)
    # print(path1)
    # print_with_columns_key(*data1, filter_column=lambda x: 'Run Duration' in x)
    # print()
    # print(path2)
    # print_with_columns_key(*data2, filter_column=lambda x: 'Run Duration' in x)
    compare_results(data1, data2)
